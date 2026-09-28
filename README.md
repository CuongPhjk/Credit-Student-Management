# Quản lý tín chỉ sinh viên
Thành viên nhóm: 
- Nguyễn Chí Bảo - MSSV: N24DECE004
- Nguyễn Thanh Cường - MSSV: N24DECE006 

Ứng dụng desktop quản lý môn học, lớp niên chế, sinh viên, lớp tín chỉ, đăng ký học và điểm thi. Giao diện được viết bằng **Python/PyQt6**; nghiệp vụ và lưu dữ liệu được viết bằng **C++17**, kết nối qua **pybind11**. Dữ liệu nằm trong các tệp UTF-8 tại `backend/data/`.

## Chức năng hiện có

| Màn hình | Chức năng |
| --- | --- |
| Trang chủ | Xem số lượng sinh viên, lớp, môn học, lớp tín chỉ; theo dõi lớp tín chỉ thiếu sĩ số hoặc đã hủy; mở nhanh các màn hình nghiệp vụ. |
| Môn học | Tìm kiếm, thêm, sửa, xóa môn học và quản lý tín chỉ lý thuyết/thực hành. |
| Lớp và sinh viên | Tìm kiếm, thêm, sửa, xóa lớp niên chế; xem danh sách và quản lý sinh viên trong từng lớp. |
| Lớp tín chỉ | Mở, tìm kiếm, lọc theo niên khóa/nhóm/học kỳ, sửa và xóa lớp tín chỉ. |
| Đăng ký học | Tra cứu sinh viên, xem lớp đang mở theo niên khóa và học kỳ, đăng ký hoặc hủy đăng ký. |
| Nhập điểm | Chọn niên khóa, học kỳ, môn và nhóm; nhập hoặc sửa điểm cho sinh viên có đăng ký còn hiệu lực. |

Các thao tác thêm, sửa, xóa và đăng ký được kiểm tra ở backend. Một số ràng buộc chính:

- Mã môn học, mã lớp và mã sinh viên phải duy nhất. Lớp tín chỉ có mã số tự sinh và không được trùng tổ hợp môn học, niên khóa, học kỳ, nhóm.
- Niên khóa có dạng `YYYY-YYYY` với hai năm liên tiếp. Khi mở hoặc sửa lớp tín chỉ, niên khóa không được cũ hơn niên khóa hiện tại. Học kỳ từ 1 đến 3, nhóm lớn hơn 0 và sĩ số thỏa `0 < tối thiểu <= tối đa`.
- Sinh viên không thể đăng ký hai nhóm của cùng một môn trong cùng niên khóa và học kỳ, đăng ký vào lớp đã hủy hoặc lớp đã đủ chỗ.
- Không thể xóa môn học đã được dùng bởi lớp tín chỉ, lớp tín chỉ đã có dữ liệu đăng ký, lớp niên chế còn sinh viên, hoặc sinh viên đã có dữ liệu đăng ký.
- Điểm hợp lệ từ 0 đến 10. Trạng thái “đã có điểm” phân biệt điểm 0 với điểm chưa nhập.

## Cài đặt và chạy

### Yêu cầu

- Python **3.10+** có `pip` và thư viện trong `requirements.txt` (`PyQt6`, `pybind11`).
- Trình biên dịch C++ hỗ trợ C++17, cùng CMake 3.15+. Trên Windows có thể dùng MSVC hoặc MinGW; script build sẽ ưu tiên MinGW nếu tìm thấy `g++.exe` và `mingw32-make.exe`.
- Dùng **cùng một Python** để build extension và chạy ứng dụng. Extension `.pyd` có sẵn trong một checkout, nếu có, chỉ phù hợp với phiên bản Python và kiến trúc tương ứng; khi không import được hãy build lại.

Mở terminal tại thư mục gốc của project.

**Windows (PowerShell):**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\build_backend.ps1 -PythonPath (Resolve-Path .\.venv\Scripts\python.exe)
.\.venv\Scripts\python.exe app.py
```

`build_backend.ps1` cài dependencies và CMake nếu cần, cấu hình tại `build/cmake`, rồi tạo `bridge/_credit_backend*.pyd`.

**Build thủ công (Windows, Linux hoặc macOS):**

```bash
python -m pip install -r requirements.txt
cmake -S . -B build/cmake -DPython_EXECUTABLE=/path/to/python
cmake --build build/cmake --config Release
python app.py
```

Thay `/path/to/python` bằng đường dẫn Python dùng để chạy app. Trên Windows, ví dụ `-DPython_EXECUTABLE=C:/path/to/.venv/Scripts/python.exe`. CMake tạo **module Python** trong `bridge/`, không tạo chương trình console riêng. Khi khởi động, ứng dụng nạp ba tệp dữ liệu từ `backend/data/`; nếu extension hoặc dữ liệu không đọc được, giao diện sẽ hiển thị cảnh báo.

## Dữ liệu

Ứng dụng đọc và ghi ba tệp sau:

| Tệp | Nội dung |
| --- | --- |
| `backend/data/monhoc.txt` | Mỗi dòng: `Mã môn|Tên môn|TC lý thuyết|TC thực hành`. |
| `backend/data/lopsinhvien.txt` | Mỗi khối gồm `Mã lớp|Tên lớp`, các dòng `Mã SV|Họ|Tên|Phái|Số điện thoại`, rồi dòng `#`. |
| `backend/data/loptinchi.txt` | Mỗi khối gồm `Mã LTC|Mã môn|Niên khóa|Học kỳ|Nhóm|SV tối thiểu|SV tối đa|Hủy lớp`, các dòng `Mã SV|Điểm|Hủy đăng ký|Đã có điểm`, rồi dòng `#`. |

Các cờ trạng thái dùng `0` hoặc `1`. Khối không có bản ghi con vẫn cần dòng `#`. Mỗi lần lưu, backend ghi toàn bộ nội dung tệp liên quan vào tệp `.tmp` bên cạnh, sau đó thay thế tệp gốc; nếu lưu lỗi, thao tác trên bộ nhớ được hoàn tác. **Sao lưu `backend/data/` trước khi nhập hoặc thay dữ liệu thật.**

`tools/migrate_grouped_data.py` chuyển bộ dữ liệu cũ gồm năm tệp `MonHoc.txt`, `Lop.txt`, `SinhVien.txt`, `LopTinChi.txt`, `DangKy.txt` sang định dạng ba tệp trên và tạo bản sao ZIP trong `backups/`. Chỉ chạy công cụ này khi còn đủ năm tệp cũ; nó từ chối ghi đè nếu `lopsinhvien.txt` đã tồn tại:

```bash
python tools/migrate_grouped_data.py
```

Có thể truyền `--data-dir` và `--backup-dir` để dùng thư mục khác.

## Cấu trúc project

```text
app.py                   Điểm khởi chạy giao diện
frontend/pages/          Các màn hình PyQt6
frontend/components/     Thành phần giao diện dùng chung
frontend/resources/      Ảnh, biểu tượng và stylesheet
bridge/Bindings.cpp      Binding pybind11 cho các manager C++
bridge/__init__.py       Nạp extension và báo trạng thái backend
backend/include/model/   Kiểu dữ liệu và AppData
backend/include/functions/ và backend/src/functions/  Nghiệp vụ C++
backend/manager/ và backend/src/manager/  Manager được gọi từ Python
backend/src/file/        Đọc và ghi dữ liệu
backend/data/            Ba tệp dữ liệu UTF-8
tests/cpp/ và tests/python/  Kiểm thử C++ và Python
tools/                   Công cụ chuyển đổi dữ liệu cũ
CMakeLists.txt           Build backend và đăng ký kiểm thử C++
build_backend.ps1        Script build trên Windows
```

Backend dùng cây nhị phân tìm kiếm cho môn học; mảng cho lớp niên chế và lớp tín chỉ; danh sách liên kết đơn cho sinh viên và đăng ký. Giới hạn trong mã nguồn là 10.000 lớp niên chế và 10.000 lớp tín chỉ.

## Kiểm thử

Sau khi build backend, chạy từ thư mục gốc:

```bash
ctest --test-dir build/cmake -C Release --output-on-failure
python -m unittest discover -s tests/python -p 'test_*.py'
```

Bộ Python cần import được `PyQt6` và extension `bridge._credit_backend` bằng đúng Python đã dùng để build. Một số kiểm thử giao diện cần môi trường có thể khởi tạo Qt.

## Ghi chú

Project hiện chưa có tệp giấy phép trong repository. Giao diện không có chức năng báo cáo hoặc đăng nhập; module backend cũng không cung cấp executable chạy console.
