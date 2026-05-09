from __future__ import annotations

from typing import Optional

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import DATETIME as MYSQL_DATETIME
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class CapturedPacket(Base):
    __tablename__ = "captured_packets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    captured_at: Mapped[DateTime] = mapped_column(MYSQL_DATETIME(fsp=6), index=True)
    interface: Mapped[str] = mapped_column(String(64))
    protocol_l3: Mapped[str] = mapped_column(String(16))
    protocol_l4: Mapped[str] = mapped_column(String(16))
    app_protocol: Mapped[str] = mapped_column(String(32), index=True)
    src_mac: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    dst_mac: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    src_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True, index=True)
    dst_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True, index=True)
    src_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dst_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    packet_len: Mapped[int] = mapped_column(Integer)
    direction_hint: Mapped[str] = mapped_column(String(32))
    payload_hex: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class ActiveHost(Base):
    __tablename__ = "active_hosts"

    mac_address: Mapped[str] = mapped_column(String(32), primary_key=True)
    first_seen: Mapped[DateTime] = mapped_column(MYSQL_DATETIME(fsp=6))
    last_seen: Mapped[DateTime] = mapped_column(MYSQL_DATETIME(fsp=6), index=True)
    packet_count: Mapped[int] = mapped_column(BigInteger, default=0)
    byte_count: Mapped[int] = mapped_column(BigInteger, default=0)


class ActiveIp(Base):
    __tablename__ = "active_ips"

    ip_address: Mapped[str] = mapped_column(String(45), primary_key=True)
    first_seen: Mapped[DateTime] = mapped_column(MYSQL_DATETIME(fsp=6))
    last_seen: Mapped[DateTime] = mapped_column(MYSQL_DATETIME(fsp=6), index=True)
    packet_count: Mapped[int] = mapped_column(BigInteger, default=0)
    byte_count: Mapped[int] = mapped_column(BigInteger, default=0)


class ProtocolMetric(Base):
    __tablename__ = "protocol_metrics"
    __table_args__ = (
        UniqueConstraint("protocol_layer", "protocol_name", name="uq_protocol_layer_name"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    protocol_layer: Mapped[str] = mapped_column(String(8), index=True)
    protocol_name: Mapped[str] = mapped_column(String(32))
    packet_count: Mapped[int] = mapped_column(BigInteger, default=0)
    byte_count: Mapped[int] = mapped_column(BigInteger, default=0)
    updated_at: Mapped[DateTime] = mapped_column(
        MYSQL_DATETIME(fsp=6),
        server_default=func.now(),
        onupdate=func.now(),
    )


class AlertRecord(Base):
    __tablename__ = "alert_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    alert_type: Mapped[str] = mapped_column(String(32), index=True)
    severity: Mapped[str] = mapped_column(String(16), default="MEDIUM")
    target_value: Mapped[str] = mapped_column(String(128), index=True)
    message: Mapped[str] = mapped_column(String(255))
    packet_count: Mapped[int] = mapped_column(BigInteger, default=0)
    byte_count: Mapped[int] = mapped_column(BigInteger, default=0)
    first_seen: Mapped[DateTime] = mapped_column(MYSQL_DATETIME(fsp=6), server_default=func.now())
    last_seen: Mapped[DateTime] = mapped_column(MYSQL_DATETIME(fsp=6), server_default=func.now())
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE", index=True)
