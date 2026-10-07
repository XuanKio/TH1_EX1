"""Kiểm thử thủ công: python tests/smoke_test.py (cần Internet).

Chỉ gửi dữ liệu giả. Mỗi lần chạy dùng mã riêng trên topic của bài tập.
"""

import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONIOENCODING": "cp1252", "PYTHONUNBUFFERED": "1",
       "MQTT_HOST": "test.mosquitto.org", "MQTT_PORT": "1883", "MQTT_TLS": "false"}
ENV.pop("MQTT_USERNAME", None)
ENV.pop("MQTT_PASSWORD", None)
IDENTITY = ["--name", "Sinh vien kiem thu", "--student-id", "TEST001"]


def run(script, *args, env=None):
    return subprocess.run([sys.executable, str(ROOT / script), *args], cwd=ROOT,
                          env=env or ENV, capture_output=True, text=True,
                          encoding="utf-8", timeout=18)


def main():
    # stdin điều khiển SIGINT trong chính tiến trình con; dùng được trên Windows.
    wrapper = (
        "import _thread,runpy,sys,threading; "
        "threading.Thread(target=lambda: (sys.stdin.readline(), "
        "_thread.interrupt_main()), daemon=True).start(); "
        "runpy.run_path('subscriber.py', run_name='__main__')"
    )
    subscriber = subprocess.Popen([sys.executable, "-u", "-c", wrapper], cwd=ROOT,
                                  env=ENV, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    lines = queue.Queue()
    threading.Thread(target=lambda: [lines.put(line) for line in subscriber.stdout],
                     daemon=True).start()
    observed = []

    def await_text(predicate, seconds=15):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            try:
                observed.append(lines.get(timeout=0.2))
            except queue.Empty:
                if subscriber.poll() is not None:
                    raise AssertionError("Subscriber kết thúc trước khi đủ dữ liệu")
            if predicate("".join(observed)):
                return
        raise AssertionError("Hết thời gian chờ dữ liệu từ subscriber")

    try:
        await_text(lambda output: "Sẵn sàng nhận tin" in output)
        marker = "smoke-" + uuid.uuid4().hex
        result = run("publisher.py", *IDENTITY, "--count", "3", "--interval", "0.1",
                     "--message", marker)
        assert result.returncode == 0, result.stderr
        assert result.stdout.count("broker đã xác nhận") == 3
        pattern = re.compile(r"Topic: iot/lab/message\nPayload: " + marker +
                             r" - TEST001 - Sinh vien kiem thu\nTime: \d{2}:\d{2}:\d{2}")
        await_text(lambda output: len(pattern.findall(output)) >= 3)
        subscriber.stdin.write("\n")
        subscriber.stdin.flush()
        assert subscriber.wait(timeout=5) == 0
        print("PASS: 3 broker-acknowledged messages received with topic/payload/time")
        print("PASS: subscriber SIGINT (Ctrl+C) exits with code 0")
    finally:
        if subscriber.poll() is None:
            subscriber.kill()
            subscriber.wait(timeout=5)

    for option, value in [("--count", "0"), ("--interval", "-1"), ("--interval", "nan"),
                          ("--message", ""), ("--name", ""), ("--student-id", "")]:
        result = run("publisher.py", *IDENTITY, option, value)
        assert result.returncode != 0 and "Traceback" not in result.stderr, (option, value)
    print("PASS: 6 invalid argument cases fail cleanly")

    result = run("publisher.py", "--help")
    assert result.returncode == 0 and "Họ tên" in result.stdout
    print("PASS: Vietnamese help and program output work with cp1252 environment")

    for script in ("publisher.py", "subscriber.py"):
        result = run(script, *(IDENTITY if script == "publisher.py" else []),
                     env={**ENV, "MQTT_HOST": "127.0.0.1", "MQTT_PORT": "1"})
        assert result.returncode == 1 and "Hết thời gian" in result.stderr, script
        assert "Traceback" not in result.stderr
    print("PASS: both programs time out cleanly when broker is unavailable")


if __name__ == "__main__":
    main()
