# Bài 1: Python MQTT

- Phạm vi: publisher, subscriber, cấu hình broker, requirements, README tiếng Việt.
- Hợp đồng: MQTT 3.1.1, topic `iot/lab/message`, payload UTF-8 dạng `lời chào - mã sinh viên - họ tên`, QoS 1, retain false.
- Publisher: nhập thông tin hoặc truyền tham số; gửi một/nhiều thông điệp; chờ broker xác nhận trước khi báo gửi thành công.
- Subscriber: báo sẵn sàng sau SUBACK, in topic/payload/thời điểm nhận, chạy đến Ctrl+C và đăng ký lại sau reconnect.
- Kiểm chứng: kiểm tra cú pháp/CLI và chạy gửi–nhận thật với dữ liệu sinh viên giả; không công bố dữ liệu cá nhân trong thử nghiệm.

Quyết định: bài thực hành độc lập, áp dụng cook với --no-plane và --no-tree; không tạo công việc trên hệ thống công ty. Họ tên/MSSV chưa có thì nhập lúc chạy. Không push khi chưa được yêu cầu.

Tiến độ: hoàn thành. Thông tin mặc định: Hoàng Xuân Cường, MSSV B23DCCN109. Kiểm tra cú pháp và smoke test đạt: 3 bản tin gửi–nhận qua broker thật, topic/payload/time, SIGINT, tham số sai, UTF-8 trên Windows và broker không kết nối được. Đã rà soát độc lập; chưa push GitHub.
