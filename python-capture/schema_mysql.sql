CREATE DATABASE IF NOT EXISTS nettraffic_ai DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nettraffic_ai;

CREATE TABLE IF NOT EXISTS captured_packets (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    captured_at DATETIME(6) NOT NULL,
    interface VARCHAR(64) NOT NULL,
    protocol_l3 VARCHAR(16) NOT NULL,
    protocol_l4 VARCHAR(16) NOT NULL,
    app_protocol VARCHAR(32) NOT NULL,
    src_mac VARCHAR(32) NULL,
    dst_mac VARCHAR(32) NULL,
    src_ip VARCHAR(45) NULL,
    dst_ip VARCHAR(45) NULL,
    src_port INT NULL,
    dst_port INT NULL,
    packet_len INT NOT NULL,
    direction_hint VARCHAR(32) NOT NULL,
    payload_hex LONGTEXT NULL,
    INDEX idx_captured_at (captured_at),
    INDEX idx_src_ip (src_ip),
    INDEX idx_dst_ip (dst_ip),
    INDEX idx_app_protocol (app_protocol)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS active_hosts (
    mac_address VARCHAR(32) PRIMARY KEY,
    first_seen DATETIME(6) NOT NULL,
    last_seen DATETIME(6) NOT NULL,
    packet_count BIGINT NOT NULL DEFAULT 0,
    byte_count BIGINT NOT NULL DEFAULT 0,
    INDEX idx_last_seen (last_seen)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS active_ips (
    ip_address VARCHAR(45) PRIMARY KEY,
    first_seen DATETIME(6) NOT NULL,
    last_seen DATETIME(6) NOT NULL,
    packet_count BIGINT NOT NULL DEFAULT 0,
    byte_count BIGINT NOT NULL DEFAULT 0,
    INDEX idx_last_seen (last_seen),
    INDEX idx_byte_count (byte_count)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS protocol_metrics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    protocol_layer VARCHAR(8) NOT NULL,
    protocol_name VARCHAR(32) NOT NULL,
    packet_count BIGINT NOT NULL DEFAULT 0,
    byte_count BIGINT NOT NULL DEFAULT 0,
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    UNIQUE KEY uq_protocol_layer_name (protocol_layer, protocol_name),
    INDEX idx_protocol_layer (protocol_layer)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS alert_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    alert_type VARCHAR(32) NOT NULL,
    severity VARCHAR(16) NOT NULL DEFAULT 'MEDIUM',
    target_value VARCHAR(128) NOT NULL,
    message VARCHAR(255) NOT NULL,
    packet_count BIGINT NOT NULL DEFAULT 0,
    byte_count BIGINT NOT NULL DEFAULT 0,
    first_seen DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    last_seen DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    INDEX idx_alert_status (status),
    INDEX idx_alert_target (target_value)
) ENGINE=InnoDB;
