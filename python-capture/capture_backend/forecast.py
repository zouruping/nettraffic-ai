from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
from sqlalchemy import text


os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")


@dataclass
class ForecastResult:
    history_points: list[tuple[datetime, float]]
    forecast_points: list[tuple[datetime, float]]
    model_name: str
    fallback_used: bool
    train_samples: int


def fetch_traffic_series(
    session,
    *,
    history_minutes: int,
    interval_minutes: int,
) -> list[tuple[datetime, float]]:
    bucket_seconds = interval_minutes * 60
    rows = list(
        session.execute(
            text(
                """
                SELECT
                    FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(captured_at) / :bucket_seconds) * :bucket_seconds) AS bucket_time,
                    SUM(packet_len) AS byte_count
                FROM captured_packets
                WHERE captured_at >= DATE_SUB(NOW(), INTERVAL :history_minutes MINUTE)
                GROUP BY bucket_time
                ORDER BY bucket_time ASC
                """
            ),
            {"bucket_seconds": bucket_seconds, "history_minutes": history_minutes},
        ).mappings()
    )
    if not rows:
        # If recent-window data is empty, fall back to the latest buckets in history.
        max_buckets = max(history_minutes // max(interval_minutes, 1), 180)
        rows = list(
            session.execute(
                text(
                    """
                    SELECT t.bucket_time, t.byte_count
                    FROM (
                        SELECT
                            FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(captured_at) / :bucket_seconds) * :bucket_seconds) AS bucket_time,
                            SUM(packet_len) AS byte_count
                        FROM captured_packets
                        GROUP BY bucket_time
                        ORDER BY bucket_time DESC
                        LIMIT :max_buckets
                    ) AS t
                    ORDER BY t.bucket_time ASC
                    """
                ),
                {"bucket_seconds": bucket_seconds, "max_buckets": max_buckets},
            ).mappings()
        )
    if not rows:
        return []

    by_time = {}
    for row in rows:
        bucket_time = row["bucket_time"]
        if isinstance(bucket_time, str):
            bucket_time = datetime.fromisoformat(bucket_time)
        by_time[bucket_time] = float(row["byte_count"] or 0) / (1024 * 1024)

    times = sorted(by_time.keys())
    current = times[0]
    end = times[-1]
    step = timedelta(minutes=interval_minutes)
    filled = []
    while current <= end:
        filled.append((current, round(by_time.get(current, 0.0), 4)))
        current += step
    return filled


def _lstm_predict(
    values: list[float],
    *,
    forecast_steps: int,
    window_size: int,
    epochs: int,
) -> tuple[list[float], int]:
    # Lazy import to keep API process usable even if TF is not installed.
    try:
        from tensorflow.keras import Sequential
        from tensorflow.keras.layers import Dense, LSTM
    except Exception as exc:
        raise RuntimeError(
            "TensorFlow is not installed. Please install it to enable LSTM forecasting."
        ) from exc

    if len(values) < window_size + 2:
        raise ValueError("Not enough history points for LSTM training.")

    arr = np.array(values, dtype=np.float32)
    min_v = float(arr.min())
    max_v = float(arr.max())
    if max_v - min_v < 1e-8:
        return [round(float(values[-1]), 4)] * forecast_steps, 0

    norm = (arr - min_v) / (max_v - min_v)
    x_train = []
    y_train = []
    for i in range(len(norm) - window_size):
        x_train.append(norm[i : i + window_size])
        y_train.append(norm[i + window_size])

    x = np.array(x_train, dtype=np.float32).reshape(-1, window_size, 1)
    y = np.array(y_train, dtype=np.float32)

    model = Sequential(
        [
            LSTM(32, input_shape=(window_size, 1)),
            Dense(16, activation="relu"),
            Dense(1),
        ]
    )
    model.compile(optimizer="adam", loss="mse")
    model.fit(x, y, epochs=epochs, batch_size=8, verbose=0)

    seq = norm[-window_size:].tolist()
    pred_norm = []
    for _ in range(forecast_steps):
        x_in = np.array(seq[-window_size:], dtype=np.float32).reshape(1, window_size, 1)
        next_value = float(model.predict(x_in, verbose=0)[0][0])
        next_value = max(0.0, min(1.0, next_value))
        pred_norm.append(next_value)
        seq.append(next_value)

    pred = [round((p * (max_v - min_v) + min_v), 4) for p in pred_norm]
    return pred, len(x_train)


def forecast_traffic_with_lstm(
    session,
    *,
    history_minutes: int,
    forecast_steps: int,
    interval_minutes: int,
    window_size: int,
    epochs: int,
) -> ForecastResult:
    history = fetch_traffic_series(
        session,
        history_minutes=history_minutes,
        interval_minutes=interval_minutes,
    )
    if not history:
        return ForecastResult(
            history_points=[],
            forecast_points=[],
            model_name="lstm",
            fallback_used=True,
            train_samples=0,
        )

    history_values = [v for _, v in history]
    step = timedelta(minutes=interval_minutes)
    start_time = history[-1][0]

    fallback_used = False
    train_samples = 0
    try:
        pred_values, train_samples = _lstm_predict(
            history_values,
            forecast_steps=forecast_steps,
            window_size=window_size,
            epochs=epochs,
        )
    except ValueError:
        fallback_used = True
        pred_values = [round(float(history_values[-1]), 4)] * forecast_steps

    forecast = []
    for i, value in enumerate(pred_values, start=1):
        forecast.append((start_time + i * step, value))

    return ForecastResult(
        history_points=history,
        forecast_points=forecast,
        model_name="lstm",
        fallback_used=fallback_used,
        train_samples=train_samples,
    )
