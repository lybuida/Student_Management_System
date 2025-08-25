# 🎓 Student Management System (Hệ thống Quản lý Học sinh)

Website quản lý học sinh được xây dựng để hỗ trợ nhà trường trong việc:
- Tiếp nhận hồ sơ học sinh
- Lập & điều chỉnh danh sách lớp
- Quản lý điểm số và xuất bảng điểm
- Quản lý môn học và thay đổi quy định
- Thống kê, báo cáo kết quả học tập

Dự án phát triển trong khuôn khổ môn **Công nghệ phần mềm** tại Trường Đại học Mở TP.HCM.

---

## 📑 Mục lục
- [Chức năng](#-chức-năng)
- [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [Cấu trúc thư mục](#-cấu-trúc-thư-mục)
- [Hướng dẫn cài đặt & chạy](#-hướng-dẫn-cài-đặt--chạy)
- [Thành viên nhóm](#-thành-viên-nhóm)
- [License](#-license)

---

## 🚀 Chức năng
### 👨‍💼 Nhân viên
- Tiếp nhận học sinh (nhập thông tin, lưu dữ liệu, tìm kiếm, xoá)
- Xem danh sách lớp
- Điều chỉnh lớp học (chuyển học sinh giữa các lớp)

### 👨‍🏫 Giáo viên
- Nhập điểm (15 phút, 1 tiết, cuối kỳ) với tính năng **Lưu nháp** và **Lưu chính thức**
- Xuất điểm trung bình theo lớp, học kỳ, năm học
- Xuất báo cáo ra file Excel

### 👩‍💻 Quản trị viên
- Quản lý môn học (thêm, sửa, xoá, tìm kiếm)
- Thay đổi quy định (tuổi, sĩ số lớp tối đa, số lượng cột điểm)
- Thống kê báo cáo (bảng + biểu đồ bằng Chart.js, xuất Excel)

---

## 🛠 Công nghệ sử dụng
- **Backend:** Python 3, Flask
- **Frontend:** HTML5, CSS3, JavaScript (Bootstrap 5, Chart.js, ExcelJS)
- **Database:** SQLite / MySQL (cấu hình linh hoạt qua `init_db.py`)
- **ORM:** SQLAlchemy
- **Authentication & Roles:** Flask-Login (Admin / Staff / Teacher)

---

## 🏗 Kiến trúc hệ thống
- **Presentation Layer (routes, templates)**: giao diện web, xử lý request/response
- **Business Logic (services, utils)**: xử lý nghiệp vụ (phân lớp, tính điểm, áp dụng quy định)
- **Data Access Layer (dao)**: truy xuất dữ liệu qua SQLAlchemy
- **Database**: các bảng Student, Teacher, Classroom, Subject, ScoreSheet, DraftScore, Regulation, ...

---

## 📂 Cấu trúc thư mục
StudentManagementApp/
- dao/ # Data Access (CRUD)
- routes/ # Các route Flask cho Admin, Teacher, Staff
- static/ # CSS, JS, ảnh
- templates/ # Giao diện (HTML, Jinja2)
- models.py # Định nghĩa bảng DB (SQLAlchemy)
- init_db.py # Tạo database & seed data
- run.py # Điểm khởi chạy Flask app
- utils.py # Hàm tiện ích

---

## ⚙️ Hướng dẫn cài đặt & chạy

### 1) Yêu cầu môi trường
- Python 3.10+
- pip, virtualenv

### 2) Cài đặt
# Clone repo
git clone https://github.com/your-username/Student-Management-System.git
cd Student-Management-System/StudentManagementApp

# Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac

# Cài đặt dependencies
pip install -r ../requirements.txt

### 3) Khởi tạo database
python init_db.py

### 4) Chạy ứng dụng
- python run.py
- Truy cập: http://127.0.0.1:5000/

## 👥 Thành viên nhóm
2254052042 – Bùi Dạ Lý

2254050009 – Huỳnh Lệ Giang

2254052008 – Võ Thị Ngọc Chi

---

## 📄 License
Dự án chỉ sử dụng cho mục đích học tập và nghiên cứu. Không sử dụng cho mục đích thương mại.

