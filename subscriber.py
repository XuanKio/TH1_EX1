"""Lắng nghe liên tục và hiển thị thông điệp MQTT cho đến khi nhấn Ctrl+C."""

from datetime import datetime
import sys
import threading
import time

import paho.mqtt.client as mqtt

from config import TIMEOUT, TOPIC, configure_console, create_client


def main():
    configure_console()
    client = None
    try:
        client, host, port = create_client("sub")
        ready = threading.Event()
        startup_errors = []

        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code.is_failure:
                startup_errors.append(f"Broker từ chối kết nối: {reason_code}")
                ready.set()
                return
            # Đăng ký lại cả khi thư viện tự kết nối lại sau mất mạng.
            result, _ = client.subscribe(TOPIC, qos=1)
            if result != mqtt.MQTT_ERR_SUCCESS:
                startup_errors.append(f"Không đăng ký được topic: {mqtt.error_string(result)}")
                ready.set()

        def on_subscribe(client, userdata, mid, reason_codes, properties):
            if any(code.is_failure for code in reason_codes):
                startup_errors.append("Broker từ chối đăng ký topic.")
            else:
                print(f"Đã đăng ký {TOPIC}. Sẵn sàng nhận tin (Ctrl+C để dừng).", flush=True)
            ready.set()  # Chỉ báo sẵn sàng khi đã nhận SUBACK từ broker.

        def on_message(client, userdata, message):
            payload = message.payload.decode("utf-8", errors="replace")
            received_at = datetime.now().strftime("%H:%M:%S")
            print(
                f"\nNhan duoc message:\nTopic: {message.topic}\n"
                f"Payload: {payload}\nTime: {received_at}\n",
                flush=True,
            )

        def on_disconnect(client, userdata, flags, reason_code, properties):
            if reason_code.is_failure:
                print(f"Mất kết nối ({reason_code}); đang thử kết nối lại...", flush=True)

        client.on_connect = on_connect
        client.on_subscribe = on_subscribe
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        print(f"Đang kết nối {host}:{port}...", flush=True)
        client.connect_async(host, port, keepalive=60)
        client.loop_start()
        if not ready.wait(TIMEOUT):
            raise TimeoutError("Hết thời gian chờ kết nối hoặc đăng ký topic.")
        while True:
            if startup_errors:
                raise ConnectionError(startup_errors[0])
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nĐã dừng subscriber.")
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Lỗi subscriber: {exc}", file=sys.stderr)
        return 1
    finally:
        if client is not None:
            client.disconnect()
            client.loop_stop()


if __name__ == "__main__":
    sys.exit(main())
