# Bài 1 — Gửi và nhận thông điệp MQTT bằng Python

Hai chương trình Python minh họa cơ chế publisher/subscriber qua topic `iot/lab/message`.
Publisher gửi lời chào, họ tên và mã sinh viên. Subscriber in topic, payload và thời điểm nhận trên máy đang chạy.

Sinh viên: **Hoàng Xuân Cường** — Mã sinh viên: **B23DCCN109**.

## 1. Cài đặt (Windows PowerShell)

Cần Python 3.8 trở lên và kết nối tới một MQTT broker. Mở terminal tại thư mục dự án:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Các lệnh dưới đây dùng trực tiếp Python trong môi trường ảo, không cần kích hoạt môi trường.
Trên Linux/macOS, tạo môi trường bằng `python3 -m venv .venv` và thay `.\.venv\Scripts\python.exe` bằng `.venv/bin/python`.

## 2. Chạy gửi và nhận

Mở **hai terminal** tại cùng thư mục dự án. Cả hai chương trình mặc định dùng `test.mosquitto.org:1883`.

**Terminal 1 — chạy subscriber trước:**

```powershell
.\.venv\Scripts\python.exe subscriber.py
```

Đợi dòng `Đã đăng ký iot/lab/message. Sẵn sàng nhận tin` rồi tiếp tục.

**Terminal 2 — chạy publisher với thông tin sinh viên đã cấu hình:**

```powershell
.\.venv\Scripts\python.exe publisher.py
```

Có thể truyền thông tin bằng tham số và gửi nhiều lần:

```powershell
.\.venv\Scripts\python.exe publisher.py --name "Hoàng Xuân Cường" --student-id "B23DCCN109" --count 3 --interval 1
```

Tùy chọn `--message "Lời chào của bạn"` thay nội dung lời chào. `--count` mặc định là `1`; `--interval` mặc định là `1` giây và được phép bằng `0`. Xem các tham số bằng `publisher.py --help`.

Kết quả minh họa tại subscriber:

```text
Nhan duoc message:
Topic: iot/lab/message
Payload: Xin chao tu client Python MQTT - B23DCCN109 - Hoàng Xuân Cường
Time: 10:15:20
```

Publisher báo gửi thành công khi broker đã xác nhận. Nhấn **Ctrl+C** để dừng subscriber hoặc ngắt publisher đang gửi nhiều tin.

## 3. Cấu hình MQTT broker

Cấu hình được đọc từ biến môi trường; cần đặt trong **cả hai terminal** trước khi chạy.

| Biến | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `MQTT_HOST` | `test.mosquitto.org` | Tên miền hoặc IP broker |
| `MQTT_PORT` | `1883` | Cổng MQTT TCP |
| `MQTT_USERNAME` | Không có | Tài khoản, nếu broker yêu cầu |
| `MQTT_PASSWORD` | Không có | Mật khẩu tương ứng |
| `MQTT_TLS` | `false` | `true`/`1` bật TLS; `false`/`0` tắt TLS |

**Broker công cộng (chạy nhanh):**

```powershell
$env:MQTT_HOST = "test.mosquitto.org"
$env:MQTT_PORT = "1883"
$env:MQTT_TLS = "false"
```

Broker công cộng này không yêu cầu tài khoản. Hai chương trình cần dùng cùng địa chỉ broker và cổng.

**Broker Mosquitto trên máy cá nhân (tùy chọn):**

Sau khi cài [Eclipse Mosquitto](https://mosquitto.org/download/), chạy broker chỉ phục vụ máy cá nhân bằng một terminal riêng:

```powershell
& "C:\Program Files\mosquitto\mosquitto.exe" -p 1883 -v
```

Nếu dịch vụ Mosquitto đã chạy ở cổng 1883, dùng dịch vụ đó, không khởi chạy thêm. Trong hai terminal của ứng dụng:

```powershell
$env:MQTT_HOST = "localhost"
$env:MQTT_PORT = "1883"
$env:MQTT_TLS = "false"
```

**Broker riêng có tài khoản hoặc TLS:**

```powershell
$env:MQTT_HOST = "dia-chi-broker-cua-ban"
$env:MQTT_PORT = "8883"
$env:MQTT_TLS = "true"
$env:MQTT_USERNAME = "tai-khoan-cua-ban"
$env:MQTT_PASSWORD = "mat-khau-cua-ban"
```

Đặt cổng và TLS theo cấu hình thực tế của broker. Chương trình đọc trực tiếp biến môi trường, không tự đọc file `.env`. Khi đổi về broker không xác thực, xóa thông tin tài khoản bằng:

```powershell
Remove-Item Env:MQTT_USERNAME, Env:MQTT_PASSWORD -ErrorAction SilentlyContinue
```

## 4. Mô hình và mã nguồn

```text
Thiết bị Python publisher → MQTT broker → Thiết bị Python subscriber
                           iot/lab/message
Payload: lời chào - mã sinh viên - họ tên
```

| Tệp | Vai trò |
| --- | --- |
| `publisher.py` | Cấu hình thông tin sinh viên, kết nối và gửi một hoặc nhiều thông điệp |
| `subscriber.py` | Đăng ký topic, in dữ liệu và thời điểm nhận; tự đăng ký lại sau khi kết nối lại |
| `config.py` | Đọc cấu hình broker, tạo client ID riêng, thiết lập xác thực/TLS |
| `requirements.txt` | Cố định thư viện `paho-mqtt==2.1.0` |

Hai chương trình dùng MQTT 3.1.1 và payload UTF-8. Publisher gửi với QoS 1 và chờ broker xác nhận tiếp nhận. Subscriber đăng ký topic `iot/lab/message`, hiển thị nội dung cùng thời điểm nhận và chạy liên tục đến khi nhấn Ctrl+C.
