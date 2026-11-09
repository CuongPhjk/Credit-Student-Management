# Quản lý tín chỉ sinh viên
Thành viên nhóm: 
- Nguyễn Chí Bảo - MSSV: N24DECE004
- Nguyễn Thanh Cường - MSSV: N24DECE006 

Ứng dụng desktop quản lý môn học, lớp niên chế, sinh viên, lớp tín chỉ, đăng ký học. Giao diện được viết bằng **Python/PyQt6**; nghiệp vụ và lưu dữ liệu được viết bằng **C++17**, kết nối qua **pybind11**. Dữ liệu nằm trong các tệp UTF-8 tại `backend/data/`.

## Chức năng hiện có

| Màn hình | Chức năng |
| --- | --- |
| Trang chủ | Xem số lượng sinh viên, lớp, môn học, lớp tín chỉ; theo dõi lớp tín chỉ thiếu sĩ số hoặc đã hủy; mở nhanh các màn hình nghiệp vụ. |
| Môn học | Tìm kiếm, thêm, sửa, xóa môn học và quản lý tín chỉ lý thuyết/thực hành. |
| Lớp và sinh viên | Tìm kiếm, thêm, sửa, xóa lớp niên chế; xem danh sách và quản lý sinh viên trong từng lớp. |
| Lớp tín chỉ | Mở, tìm kiếm, lọc theo niên khóa/nhóm/học kỳ, sửa và xóa lớp tín chỉ. |
| Đăng ký học | Tra cứu sinh viên, xem lớp đang mở theo niên khóa và học kỳ, đăng ký hoặc hủy đăng ký. |
| Hoàn tác (Undo) | Khôi phục thao tác thêm, sửa, xóa và thay đổi đăng ký gần nhất bằng nút trên thanh đầu trang hoặc Ctrl+Z. |

Giao diện kiểm tra dữ liệu nhập (rỗng, độ dài, ký tự, định dạng và khoảng số) trước khi gọi C++. Backend giữ kiểm tra nghiệp vụ như trùng mã, dữ liệu tồn tại và điều kiện sửa/xóa/đăng ký. Luồng đọc file kiểm tra dữ liệu riêng vì không đi qua form. Các hàm thêm/sửa C++ giả định đầu vào đã được giao diện xác nhận hợp lệ. Một số ràng buộc chính:

- Mã môn học, mã lớp và mã sinh viên phải duy nhất. Lớp tín chỉ có mã số tự sinh và không được trùng tổ hợp môn học, niên khóa, học kỳ, nhóm.
- Niên khóa có dạng `YYYY-YYYY` với hai năm liên tiếp. Khi mở hoặc sửa lớp tín chỉ, niên khóa không được cũ hơn niên khóa hiện tại. Học kỳ từ 1 đến 3, nhóm lớn hơn 0 và sĩ số thỏa `0 < tối thiểu <= tối đa`.
- Sinh viên không thể đăng ký hai nhóm của cùng một môn trong cùng niên khóa và học kỳ, đăng ký vào lớp đã hủy hoặc lớp đã đủ chỗ.
- Không thể xóa môn học đã được dùng bởi lớp tín chỉ, lớp tín chỉ đã có dữ liệu đăng ký, lớp niên chế còn sinh viên, hoặc sinh viên đã có dữ liệu đăng ký.
- Dữ liệu đăng ký vẫn giữ trường điểm: `DIEM = -1` biểu thị chưa nhập điểm; `0` là điểm 0 đã nhập. Chức năng nhập điểm hiện được lưu riêng trong patch.

## Hoàn tác (Undo)

- Nhấn **Hoàn tác (N)** trên thanh đầu trang hoặc **Ctrl+Z** để hoàn tác thao tác đã lưu gần nhất. Di chuột vào nút để xem mô tả thao tác; `N` là số thao tác còn trong lịch sử. Trong ô nhập văn bản, Ctrl+Z vẫn hoàn tác nội dung đang gõ; dùng nút Hoàn tác để hoàn tác dữ liệu đã lưu.
- Lịch sử dùng chung cho môn học, lớp niên chế, sinh viên, lớp tín chỉ và đăng ký/hủy đăng ký, theo thứ tự mới nhất trước (LIFO). Hủy đồng thời các lớp thiếu sĩ số là một bước Undo.
- Khi hoàn tác, chương trình lưu lại tệp liên quan, cập nhật các bảng và thống kê, đóng biểu mẫu đang mở. Sinh viên được đưa lại vào đúng thứ tự tên; lớp được phục hồi đúng vị trí và mã; điểm và trạng thái đăng ký được giữ nguyên.
- Thao tác lỗi hoặc sửa mà không thay đổi dữ liệu không tạo lịch sử. Nếu lưu sau Undo thất bại, dữ liệu hiện tại và bước Undo được giữ lại để thử lại.
- Lịch sử chỉ tồn tại trong phiên chạy, được xóa khi gọi đọc lại tệp (kể cả lần đọc lỗi vì quá trình đọc có thể đã thay dữ liệu), `AppData.clear()` hoặc thoát chương trình. Chưa hỗ trợ Redo.

Backend dùng `UndoNode`/`UndoStack` liên kết đơn với `PushUndo`, `PopUndo`, `ClearUndo` và `ThucHienUndo`, tương tự ví dụ tham khảo. Phần triển khai nằm trong `backend/src/manager/Undo.h` và `Undo.cpp`; các manager chụp dữ liệu trước thao tác và đẩy vào stack sau khi lưu thành công. Binding cung cấp `AppData.undo()`, `so_thao_tac_undo`, `mo_ta_undo` và `clear_undo()`. Gọi hàm lõi trực tiếp không ghi lịch sử; các thao tác của ứng dụng đi qua manager.

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
| `backend/data/loptinchi.txt` | Mỗi khối gồm `Mã LTC|Mã môn|Niên khóa|Học kỳ|Nhóm|SV tối thiểu|SV tối đa|Hủy lớp`, các dòng `Mã SV|Điểm|Hủy đăng ký`, rồi dòng `#`. |

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

Đúp vào một lớp tín chỉ để xem danh sách đăng ký gồm Mã sinh viên, Họ tên và Trạng thái. Đăng ký mới được nối cuối danh sách; lỗi đăng ký được kiểm tra ở backend. File đăng ký bốn cột cũ vẫn đọc được và được ghi thành ba cột ở lần lưu tiếp theo.

Trang sinh viên hỗ trợ thứ tự tên tăng dần, mã tăng dần và mã giảm dần. Backend dùng Merge Sort tự viết trên mảng con trỏ lấy từ `LayDanhSachSinhVien()`, giữ nguyên liên kết theo tên. `LopSinhVienManager` giữ một mảng mã tăng dần của lớp đang xem; giảm dần đọc ngược mảng đó. Đổi chiều hoặc tạm chuyển trang không sắp xếp lại. Sửa họ tên/phái/điện thoại không làm mất mảng theo mã vì mã và địa chỉ node giữ nguyên.

Thêm/xóa sinh viên, thay đổi danh sách lớp hoặc đọc lại dữ liệu sẽ làm mảng cũ không còn hợp lệ. Manager giải phóng cache của mình sau thao tác thay đổi thành công; mỗi lần dùng cache cũng kiểm tra `DS_LOP.phienBan` để bỏ con trỏ cũ nếu dữ liệu bị đổi bởi manager khác, hàm lõi hoặc `AppData::clear()`. Mảng được giải phóng khi đổi lớp, quay về danh sách lớp hoặc hủy manager. Binding chỉ sao chép dữ liệu sang Python và không xóa mảng cache. Patch `features/sap_xep_sinh_vien_theo_ma.patch` là bản lưu của cách cũ, không áp dụng lên tính năng đang hoạt động này.

Chức năng nhập điểm được tạm gỡ và lưu tại `features/nhap_diem.patch`, gồm C++, manager, binding, giao diện, menu, nhắc lưu và kiểm thử. Dữ liệu điểm hiện có vẫn được đọc và ghi cùng đăng ký. Để khôi phục, chạy từ thư mục gốc:

```powershell
git apply --check features/nhap_diem.patch
git apply features/nhap_diem.patch
```

Sau đó build lại backend và khởi động lại ứng dụng. Nếu các file liên quan đã thay đổi, cần kiểm tra ngữ cảnh patch trước khi áp dụng.

Khi đọc tệp môn học, chương trình mở tệp thành công rồi giải phóng cây hiện tại và chèn trực tiếp vào cây trong AppData. Nếu gặp dòng lỗi hoặc lỗi đọc, cây được giải phóng về rỗng để có thể đọc lại từ đầu; nếu không mở được tệp, cây hiện tại được giữ nguyên.

Đọc tệp lớp sinh viên và lớp tín chỉ cũng thao tác trực tiếp lên danh sách gốc trong AppData: mở tệp thành công mới giải phóng dữ liệu cũ; lỗi trong khi đọc sẽ giải phóng dữ liệu đã đọc về danh sách rỗng.

`AppData` là struct giữ dữ liệu công khai: cây môn học `dsMonHoc` và số môn `n`, mảng lớp `dsLop`, mảng con trỏ lớp tín chỉ `dsLopTinChi`, cùng ba đường dẫn file. Mỗi `Lop` giữ `soSinhVien`; số lượng được cập nhật khi thêm/xóa, đọc file và hoàn tác, không duyệt đếm lại khi xuất danh sách môn học hoặc sinh viên.

Các hàm xuất môn học (`treeMH*`), sinh viên (`PTRSV*`) và đăng ký (`PTRDK*`) trả mảng động chứa địa chỉ node gốc: bên gọi chỉ `delete[]` mảng, không xóa node. Xuất lớp tín chỉ trả trực tiếp mảng con trỏ gốc, không được `delete[]`. Danh sách lớp vẫn trả mảng bản sao. Binding sao chép dữ liệu sang Python trước khi giải phóng mảng tạm nên giao diện giữ nguyên cách dùng. Mảng địa chỉ chỉ dùng trong lúc chuyển dữ liệu; không giữ lại qua thao tác thay đổi hoặc giải phóng dữ liệu gốc.
