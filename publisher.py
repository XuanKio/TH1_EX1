"""Gửi lời chào chứa họ tên và mã sinh viên lên MQTT broker."""

import argparse
import math
import sys
import threading
import time

import paho.mqtt.client as mqtt

from config import TIMEOUT, TOPIC, configure_console, create_client


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="Hoàng Xuân Cường", help="Họ tên sinh viên")
    parser.add_argument("--student-id", default="B23DCCN109", help="Mã sinh viên")
    parser.add_argument("--message", default="Xin chao tu client Python MQTT")
    parser.add_argument("--count", type=int, default=1, help="Số thông điệp (mặc định: 1)")
    parser.add_argument("--interval", type=float, default=1, help="Khoảng cách gửi, giây (mặc định: 1)")
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count phải lớn hơn hoặc bằng 1.")
    if not math.isfinite(args.interval) or args.interval < 0:
        parser.error("--interval phải là số hữu hạn lớn hơn hoặc bằng 0.")
    if not args.message.strip():
        parser.error("--message không được để trống.")
    return args


def main():
    configure_console()
    args = parse_args()
    client = None
    try:
        name = args.name.strip()
        student_id = args.student_id.strip()
        if not name or not student_id:
            raise ValueError("Họ tên và mã sinh viên không được để trống.")
        payload = f"{args.message.strip()} - {student_id} - {name}"
        client, host, port = create_client("pub")
        connected = threading.Event()
        connection_errors = []

        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code.is_failure:
                connection_errors.append(f"Broker từ chối kết nối: {reason_code}")
            connected.set()

        client.on_connect = on_connect
        print(f"Đang kết nối {host}:{port}...", flush=True)
        client.connect_async(host, port, keepalive=60)
        client.loop_start()  # Xử lý gói MQTT và phản hồi broker ở luồng nền.
        if not connected.wait(TIMEOUT):
            raise TimeoutError("Hết thời gian chờ broker xác nhận kết nối.")
        if connection_errors:
            raise ConnectionError(connection_errors[0])

        for index in range(1, args.count + 1):
            result = client.publish(TOPIC, payload, qos=1, retain=False)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                raise ConnectionError(f"Không gửi được: {mqtt.error_string(result.rc)}")
            result.wait_for_publish(timeout=TIMEOUT)
            if not result.is_published():
                raise TimeoutError("Hết thời gian chờ broker xác nhận thông điệp.")
            print(f"Đã gửi {index}/{args.count} (broker đã xác nhận):", flush=True)
            print(f"Topic: {TOPIC}\nPayload: {payload}\n", flush=True)
            if index < args.count:
                time.sleep(args.interval)
        return 0
    except KeyboardInterrupt:
        print("\nĐã dừng publisher.")
        return 0
    except (OSError, ValueError, RuntimeError, EOFError) as exc:
        print(f"Lỗi publisher: {exc}", file=sys.stderr)
        return 1
    finally:
        if client is not None:
            client.disconnect()
            client.loop_stop()


if __name__ == "__main__":
    sys.exit(main())
