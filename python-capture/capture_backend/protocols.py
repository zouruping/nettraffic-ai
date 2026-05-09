from __future__ import annotations

APP_PROTOCOL_PORT_MAP = {
    20: "FTP_DATA",
    21: "FTP",
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    123: "NTP",
    143: "IMAP",
    161: "SNMP",
    443: "HTTPS",
    3306: "MYSQL",
    6379: "REDIS",
    8080: "HTTP_ALT",
    1883: "MQTT",
}


def classify_application_protocol(
    protocol_l4: str,
    src_port: int | None,
    dst_port: int | None,
) -> str:
    if protocol_l4 not in {"TCP", "UDP"}:
        return "OTHER"

    for port in (dst_port, src_port):
        if port is None:
            continue
        if port in APP_PROTOCOL_PORT_MAP:
            return APP_PROTOCOL_PORT_MAP[port]
    return "OTHER"
