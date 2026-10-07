"""Cấu hình dùng chung cho hai chương trình MQTT."""

import os
import sys
import uuid

import paho.mqtt.client as mqtt

TOPIC = "iot/lab/message"
TIMEOUT = 10  # Số giây tối đa chờ kết nối hoặc xác nhận từ broker.


def configure_console():
    """Giữ tiếng Việt khi chạy trên Windows hoặc chuyển đầu ra vào file."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def create_client(role):
    """Đọc biến môi trường và tạo client có mã riêng để tránh trùng kết nối."""
    host = os.getenv("MQTT_HOST", "test.mosquitto.org").strip()
    if not host:
        raise ValueError("MQTT_HOST không được để trống.")
    try:
        port = int(os.getenv("MQTT_PORT", "1883"))
    except ValueError as exc:
        raise ValueError("MQTT_PORT phải là số nguyên.") from exc
    if not 1 <= port <= 65535:
        raise ValueError("MQTT_PORT phải nằm trong khoảng 1–65535.")

    tls = os.getenv("MQTT_TLS", "false").strip().lower()
    if tls not in ("true", "false", "1", "0"):
        raise ValueError("MQTT_TLS phải là true, false, 1 hoặc 0.")

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"lab-{role}-{uuid.uuid4().hex[:8]}",
        protocol=mqtt.MQTTv311,
    )
    client.connect_timeout = TIMEOUT
    client.reconnect_delay_set(min_delay=1, max_delay=10)
    username = os.getenv("MQTT_USERNAME")
    password = os.getenv("MQTT_PASSWORD")
    if password and not username:
        raise ValueError("Cần đặt MQTT_USERNAME khi sử dụng MQTT_PASSWORD.")
    if username:
        client.username_pw_set(username, password)
    if tls in ("true", "1"):
        client.tls_set()  # Kiểm tra chứng chỉ broker bằng CA của hệ thống.
    return client, host, port
