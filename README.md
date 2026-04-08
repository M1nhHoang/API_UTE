# API_UTE V2

Đại Học Sư Phạm Kĩ Thuật - Đà Nẵng - 2025

Tool tự động đăng ký môn học trên hệ thống [qldt1.ute.udn.vn](https://qldt1.ute.udn.vn).

## Tính năng

- Tự động đăng nhập hệ thống QLDT
- Crawl và cache danh sách môn học có thể đăng ký
- Spam đăng ký + xác nhận môn học theo batch
- Theo dõi trạng thái đăng ký realtime

## Installation

1. Clone the project.
   ```bash
   git clone https://github.com/M1nhHoang/API_UTE.git
   ```
2. Install dependencies.
   ```bash
   pip install -r requirements.txt
   ```
3. Chỉnh sửa thông tin tài khoản và danh sách môn học trong `config.json`.
4. Run `apiUTEV2.py`.
   ```bash
   python apiUTEV2.py
   ```

## Cấu hình

Chỉnh sửa file `config.json`:

```json
{
    "student_id": "YOUR_STUDENT_ID",
    "password": "YOUR_PASSWORD",
    "class_names_to_register": [
        "125CNC01",
        "125CNTP01"
    ],
    "cache_file": "all_subjects_cache.json",
    "force_refresh_cache": false,
    "batch_size": 20,
    "check_interval": 2
}
```

| Trường | Mô tả |
|---|---|
| `student_id` | Mã sinh viên (tài khoản đăng nhập) |
| `password` | Mật khẩu |
| `class_names_to_register` | Danh sách tên lớp học phần cần đăng ký (VD: `125CNC01`) |
| `cache_file` | File cache danh sách môn học |
| `force_refresh_cache` | `true` để crawl lại danh sách môn học từ web, `false` để dùng cache |
| `batch_size` | Số lần spam đăng ký/xác nhận |
| `check_interval` | Thời gian chờ giữa các lần kiểm tra trạng thái (giây) |
