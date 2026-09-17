# QUẢN LÝ ĐIỂM SINH VIÊN THEO HỆ TÍN CHỈ
*(Credit-based Student Grade Management System)*

[![Language: C++](https://img.shields.io/badge/Backend-C%2B%2B17-blue.svg)](https://isocpp.org/)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](#)

Hệ thống phần mềm quản lý sinh viên, môn học, mở lớp tín chỉ, đăng ký môn và quản lý điểm số theo mô hình đào tạo theo hệ thống tín chỉ. Hệ thống áp dụng tối ưu các cấu trúc dữ liệu kinh điển (Cây nhị phân tìm kiếm, Danh sách liên kết đơn, Danh sách tuyến tính, Mảng con trỏ) nhằm tối ưu hiệu năng và tốc độ truy vấn.

---

## 📑 MỤC LỤC

1. [Tổng Quan Đề Tài](#1-tổng-quan-đề-tài)
2. [Cấu Trúc Dữ Liệu Chi Tiết](#2-cấu-trúc-dữ-liệu-chi-tiết)
3. [Danh Sách Chức Năng Nghiệp Vụ](#3-danh-sách-chức-năng-nghiệp-vụ)
4. [Khuôn Mẫu Báo Cáo & Kết Xuất](#4-khuôn-mẫu-báo-cáo--kết-xuất)
5. [Quy Tắc Nghiệp Vụ & Toàn Vẹn Dữ Liệu](#5-quy-tắc-nghiệp-vụ--toàn-vẹn-dữ-liệu)
6. [Cấu Trúc Thư Mục Dự Án](#6-cấu-trúc-thư-mục-dự-án)
7. [Hướng Dẫn Cài Đặt & Chạy Ứng Dụng](#7-hướng-dẫn-cài-đặt--chạy-ứng-dụng)

---

## 1. TỔNG QUAN ĐỀ TÀI

Dự án hướng đến việc số hóa quy trình quản lý học vụ theo học chế tín chỉ:
- Quản trị danh mục môn học, lớp học và hồ sơ sinh viên.
- Điều phối mở các lớp học phần (lớp tín chỉ) theo từng niên khóa, học kỳ.
- Xử lý quá trình sinh viên đăng ký môn, hủy đăng ký hoặc hủy lớp tín chỉ không đủ sĩ số tối thiểu.
- Nhập điểm thi, xử lý tính toán điểm trung bình học kỳ, điểm trung bình tích lũy và xuất bảng điểm tổng kết toàn khóa.
- Lưu trữ an toàn và phục hồi dữ liệu từ tệp tin (File Persistence).

---

## 2. CẤU TRÚC DỮ LIỆU CHI TIẾT

Hệ thống được tổ chức từ 5 cấu trúc dữ liệu trọng tâm:

```
[DS Môn Học] (Cây BST)
      |
[DS Lớp] (Mảng tuyến tính <= 10000)
      └──> [DS Sinh Viên] (Danh sách liên kết đơn, sắp xếp theo Tên)
      
[DS Lớp Tín Chỉ] (Mảng con trỏ tuyến tính <= 10000)
      └──> [DS Đăng Ký] (Danh sách liên kết đơn: MASV, Điểm, Hủy)
```

### 2.1. Danh sách Môn học (DSMH)
* **Cấu trúc lưu trữ**: Cây nhị phân tìm kiếm (**Binary Search Tree - BST**).
* **Khóa tìm kiếm**: `MAMH`.
* **Thành phần dữ liệu**:
  - `MAMH`: Mã môn học (Tối đa 10 ký tự - C10).
  - `TENMH`: Tên môn học (Tối đa 50 ký tự - C50).
  - `STCLT`: Số tín chỉ lý thuyết (Số nguyên dương > 0).
  - `STCTH`: Số tín chỉ thực hành (Số nguyên >= 0).

### 2.2. Danh sách Lớp (DSLOP)
* **Cấu trúc lưu trữ**: Danh sách tuyến tính / Mảng tĩnh (Tối đa 10,000 lớp).
* **Thành phần dữ liệu**:
  - `MALOP`: Mã lớp (Chuỗi ký tự).
  - `TENLOP`: Tên lớp (Chuỗi ký tự).
  - `dssv`: Con trỏ trỏ đến danh sách sinh viên thuộc lớp đó (`PTR_DSSV`).

### 2.3. Danh sách Sinh viên (DSSV)
* **Cấu trúc lưu trữ**: Danh sách liên kết đơn (**Singly Linked List**).
* **Đặc trưng**: Luôn được duy trì theo thứ tự tăng dần theo tên sinh viên (và họ nếu trùng tên).
* **Thành phần dữ liệu**:
  - `MASV`: Mã sinh viên (Chuỗi ký tự duy nhất).
  - `HO`: Họ và tên đệm (Chuỗi ký tự).
  - `TEN`: Tên (Chuỗi ký tự).
  - `PHAI`: Phái / Giới tính (Chuỗi: `Nam` / `Nữ`).
  - `SODT`: Số điện thoại liên lạc (Chuỗi số hợp lệ).

### 2.4. Danh sách Lớp Tín chỉ (DSLTC)
* **Cấu trúc lưu trữ**: Mảng con trỏ tuyến tính (Tối đa 10,000 phần tử).
* **Thành phần dữ liệu**:
  - `MALOPTC`: Mã lớp tín chỉ (Số nguyên tự động tăng).
  - `MAMH`: Mã môn học (Phải tồn tại trong Cây môn học).
  - `NienKhoa`: Niên khóa (Ví dụ: `2023-2024`).
  - `HocKy`: Học kỳ (`1`, `2`, `3`).
  - `Nhom`: Nhóm học phần (Số nguyên >= 1).
  - `SoSVMin`: Số lượng sinh viên đăng ký tối thiểu để mở lớp.
  - `SoSVMax`: Số lượng sinh viên đăng ký tối đa cho phép.
  - `HuyLop`: Trạng thái lớp (`true`: Đã hủy; `false`: Hoạt động).
  - `dssvdk`: Con trỏ trỏ đến danh sách sinh viên đăng ký lớp tín chỉ này (`PTR_DSDK`).

### 2.5. Danh sách Đăng ký (DSDK)
* **Cấu trúc lưu trữ**: Danh sách liên kết đơn (**Singly Linked List**).
* **Thành phần dữ liệu**:
  - `MASV`: Mã sinh viên đăng ký.
  - `DIEM`: Điểm thi của sinh viên (Số thực `float`, thang điểm `0.0 - 10.0`).
  - `HuyDangKy`: Trạng thái hủy môn của sinh viên (`bool`).

---

## 3. DANH SÁCH CHỨC NĂNG NGHIỆP VỤ

### a. Mở Lớp Tín Chỉ
- Cho phép quản trị viên thực hiện đầy đủ 3 chức năng: **Thêm**, **Xóa**, **Hiệu chỉnh** thông tin lớp tín chỉ.
- Tự động sinh mã `MALOPTC` tăng dần.
- Kiểm tra điều kiện: Mã môn học phải tồn tại, `SoSVMin` <= `SoSVMax`, không bị trùng nhóm trong cùng môn học - niên khóa - học kỳ.

### b. In Danh Sách Sinh Viên Đã Đăng Ký Lớp Tín Chỉ
- **Đầu vào**: `Niên khóa`, `Học kỳ`, `Mã môn học`, `Nhóm`.
- **Đầu ra**: Hiển thị bảng danh sách các sinh viên đã đăng ký:
  - Cột dữ liệu: `Mã SV`, `Họ tên`, `Trạng thái (Đã hủy)`.

### c. Nhập Sinh Viên (NhapSV)
- Cho phép cập nhật sinh viên theo từng lớp: Nhập `MALOP` trước, sau đó lần lượt nhập thông tin sinh viên cho lớp đó.
- Cung cấp đầy đủ 3 thao tác: **Thêm**, **Xóa**, **Hiệu chỉnh**.
- **Quy tắc sắp xếp**: Danh sách sinh viên luôn được tự động chèn và duy trì theo thứ tự tăng dần theo Tên sinh viên (và Họ nếu cùng Tên).
- **Điều kiện dừng**: Quá trình nhập sinh viên mới sẽ kết thúc khi người dùng nhập `MASV` là chuỗi rỗng.

### d. In Danh Sách Sinh Viên Của Một Lớp
- **Đầu vào**: `MALOP`.
- **Đầu ra**: In toàn bộ sinh viên thuộc lớp được chỉ định theo thứ tự bảng chữ cái (**Alphabet**) tăng dần của Mã sinh viên (`MASV`).

### e. Nhập Môn Học
- Quản lý danh mục môn học trên cây BST với 3 thao tác: **Thêm**, **Xóa**, **Hiệu chỉnh**.
- Kiểm tra `MAMH` không được trùng lặp. Khi xóa môn học, chỉ cho phép nếu môn học đó chưa được mở trong bất kỳ lớp tín chỉ nào.

### f. In Danh Sách Môn Học
- Duyệt cây nhị phân tìm kiếm để kết xuất toàn bộ danh sách môn học theo thứ tự tăng dần theo **Tên môn học** (`TENMH`).

### g. Đăng Ký Lớp Tín Chỉ
- Sinh viên nhập `MASV` của mình: Hệ thống kiểm tra và in thông tin chi tiết của sinh viên.
- Sinh viên nhập `Niên khóa`, `Học kỳ`: Hệ thống tự động lọc và hiển thị danh sách các lớp tín chỉ mở trong kỳ đó còn hiệu lực (`HuyLop == false`).
- **Thông tin hiển thị**: `MAMH`, `TENMH`, `NHOM`, `Số SV đã đăng ký`, `Số slot còn trống` (`SoSVMax - SoSV_HienTai`).
- Cho phép sinh viên chọn đăng ký hoặc hủy đăng ký môn học đã đăng ký trong kỳ.

### h. Hủy Lớp Tín Chỉ
- Chức năng duyệt và tự động hủy các lớp tín chỉ có số sinh viên đăng ký < `SoSVMin` trong một Niên khóa và Học kỳ được chỉ định.
- **Ràng buộc an toàn**: Bắt buộc phải có bước xác nhận từ phía người dùng trước khi thực thi hủy lớp.

### i. Nhập Điểm Thi
- **Đầu vào**: `Niên khóa`, `Học kỳ`, `Môn học`, `Nhóm`.
- Hệ thống lọc ra danh sách sinh viên đã đăng ký hợp lệ, hiển thị sẵn 4 cột: `STT`, `MASV`, `HO`, `TEN`.
- Người dùng nhập hoặc hiệu chỉnh điểm số trực tiếp trên cột `DIEM` (`0.0 <= DIEM <= 10.0`).

### j. In Bảng Điểm Môn Học Của Một Lớp Tín Chỉ
- **Đầu vào**: `Niên khóa`, `Học kỳ`, `Môn học`, `Nhóm`.
- Xuất bảng điểm môn học đã thi gồm thông tin lớp và bảng điểm đầy đủ của các sinh viên.

### k. In Điểm Trung Bình Khóa Học Của Một Lớp
- **Đầu vào**: `MALOP`.
- Tính điểm trung bình tích lũy cho từng sinh viên trong lớp theo công thức trọng số số tín chỉ:
  $$\text{Điểm TB} = \frac{\sum (\text{Điểm môn} \times \text{Tổng số tín chỉ môn})}{\sum \text{Tổng số tín chỉ}}$$
  *(Trong đó: Tổng số tín chỉ = STCLT + STCTH)*
- Xuất bảng thống kê điểm trung bình khóa học xếp theo từng sinh viên.

### l. Bảng Điểm Tổng Kết Các Môn Của Lớp
- **Đầu vào**: `MALOP`.
- Kết xuất bảng điểm tổng kết ma trận: Các hàng là danh sách sinh viên, các cột là các môn học đã học.
- **Quy tắc điểm**: Trường hợp sinh viên học/thi lại môn đó nhiều lần, bảng tổng kết chỉ lấy và hiển thị **điểm thi lớn nhất** của từng môn.

---

## 4. KHUÔN MẪU BÁO CÁO & KẾT XUẤT

### 4.1. Nhập Điểm / Bảng Điểm Môn Học (Chức năng i, j)
```text
BẢNG ĐIỂM MÔN HỌC: <Tên Môn Học>
Niên khóa: <YYYY-YYYY>    Học kỳ: <K>    Nhóm: <N>

STT    MASV       HO                 TEN        DIEM
1      N20DCCN001 Nguyen Van         An         8.5
2      N20DCCN002 Tran Thi           Binh       7.0
...
```

### 4.2. Bảng Thống Kê Điểm Trung Bình Khóa Học (Chức năng k)
```text
BẢNG THỐNG KÊ ĐIỂM TRUNG BÌNH KHÓA HỌC
Lớp: <Mã Lớp>

STT    MASV       HO                 TEN        Điểm TB
1      N20DCCN001 Nguyen Van         An         8.25
2      N20DCCN002 Tran Thi           Binh       7.40
...
```

### 4.3. Bảng Điểm Tổng Kết Các Môn Của Một Lớp (Chức năng l)
```text
BẢNG ĐIỂM TỔNG KẾT
Lớp: <Mã Lớp>

STT  Mã SV       Họ Tên            INT101  INT102  BAS101  BAS102  ...
1    N20DCCN001  Nguyen Van An     8.5     9.0     7.0     8.0
2    N20DCCN002  Tran Thi Binh     7.0     6.5     8.0     7.5
...
```

---

## 5. QUY TẮC NGHIỆP VỤ & TOÀN VẸN DỮ LIỆU

1. **Tính Toàn Vẹn Khóa & Tham Chiếu**:
   - `MASV`, `MALOP`, `MAMH`, `MALOPTC` phải là duy nhất.
   - Khi mở Lớp tín chỉ, `MAMH` bắt buộc phải tồn tại trong Cây Môn học.
   - Khi xóa Môn học hoặc Lớp học, phải kiểm tra dữ liệu liên đới (không xóa nếu đã có sinh viên hoặc đã có lớp tín chỉ liên quan).
2. **Ràng Buộc Đăng Ký Môn**:
   - Một sinh viên không thể đăng ký 2 lớp tín chỉ trùng môn học trong cùng 1 học kỳ.
   - Không cho phép đăng ký khi số lượng đăng ký đã đạt `SoSVMax`.
   - Sinh viên đã hủy lớp tín chỉ (`HuyDangKy == true`) không được tính vào sĩ số khả dụng.
3. **Kiểm Tra Dữ Liệu Đầu Vào (Input Validation)**:
   - Điểm số hợp lệ: Số thực từ `0.0` đến `10.0`.
   - Số tín chỉ: `STCLT > 0`, `STCTH >= 0`.
   - Số sinh viên: `0 < SoSVMin <= SoSVMax`.
   - Chuẩn hóa chuỗi văn bản: Xóa khoảng trắng thừa, viết hoa tên riêng và mã đối tượng.
4. **Lưu Trữ Dữ Liệu (File I/O)**:
   - Hệ thống tự động ghi nhận dữ liệu vào các tệp tin trong thư mục `data/` sau mỗi lần cập nhật hoặc khi thoát chương trình.
   - Tự động tải và dựng lại cấu trúc bộ nhớ khi khởi động phần mềm.

---

## 6. CẤU TRÚC THƯ MỤC DỰ ÁN

```bash
credit-student-management/
├── CMakeLists.txt        # Cấu hình biên dịch dự án (C++ / CMake)
├── README.md             # Tài liệu mô tả dự án và đặc tả nghiệp vụ
├── app.py                # Điểm khởi chạy ứng dụng / Giao diện chính
├── requirements.txt      # Thư viện phụ trợ nếu dùng Python Frontend/Bridge
├── backend/              # Mã nguồn C++ xử lý dữ liệu và thuật toán
│   ├── include/          # Thư mục header files (.h, .hpp)
│   │   ├── BSTree.h      # Cây nhị phân tìm kiếm quản lý Môn học
│   │   ├── LinkedList.h  # Danh sách liên kết đơn cho DSSV và DSDK
│   │   ├── LinearList.h  # Danh sách tuyến tính cho DSLOP và DSLTC
│   │   └── Models.h      # Định nghĩa các struct / class dữ liệu
│   └── src/              # Triển khai thuật toán và hàm xử lý (.cpp)
├── bridge/               # Tầng liên kết Backend C++ và Frontend
├── data/                 # Thư mục chứa các tệp tin lưu trữ dữ liệu
│   ├── monhoc.dat
│   ├── lop.dat
│   ├── sinhvien.dat
│   └── ltc.dat
├── frontend/             # Tầng giao diện người dùng (Console / UI)
└── tests/                # Bộ kiểm thử đơn vị (Unit Tests)
```

---

## 7. HƯỚNG DẪN CÀI ĐẶT & CHẠY ỨNG DỤNG

### 7.1. Yêu Cầu Môi Trường
- **C++ Compiler**: GCC / Clang / MSVC hỗ trợ chuẩn C++17 trở lên.
- **CMake**: Phiên bản 3.15 trở lên.
- **Python** (tùy chọn): Phiên bản 3.8+ nếu sử dụng ứng dụng kèm Python GUI/Bridge.

### 7.2. Biên Dịch & Chạy Backend (C++)
```bash
# Tạo thư mục build và cấu hình CMake
cmake -B build -S .

# Biên dịch dự án
cmake --build build --config Release

# Khởi chạy ứng dụng console
./build/Release/credit_management.exe   # Trên Windows
# hoặc ./build/credit_management       # Trên Linux/macOS
```

### 7.3. Chạy Với Python Frontend (Nếu có)
```bash
# Cài đặt thư viện phụ thuộc
pip install -r requirements.txt

# Khởi chạy giao diện chính
python app.py
```

---

## 👥 ĐÓNG GÓP & BẢN QUYỀN
- Đề tài môn học: **Cấu Trúc Dữ Liệu & Giải Thuật (Data Structures and Algorithms)**.
- Mọi đóng góp xin vui lòng tạo **Pull Request** hoặc gửi phản hồi tại mục **Issues**.
