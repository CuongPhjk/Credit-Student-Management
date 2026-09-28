"""Giao diện Python của backend C++.

Extension ``_credit_backend`` được tạo bởi CMake và đặt cạnh file này.
"""

import os
import shutil
from pathlib import Path


_DLL_DIRECTORIES = []
if os.name == "nt" and hasattr(os, "add_dll_directory"):
    # Python 3.8+ không tự tìm DLL của MinGW từ PATH khi nạp extension.
    # Giữ handle tồn tại trong suốt vòng đời module.
    compiler = shutil.which("g++.exe")
    if compiler:
        compiler_directory = Path(compiler).resolve().parent
        try:
            _DLL_DIRECTORIES.append(os.add_dll_directory(compiler_directory))
        except OSError:
            pass

try:
    from ._credit_backend import (
        AppData,
        DangKyManager,
        DiemManager,
        LopTinChi,
        LopTinChiManager,
        Lop,
        LopSinhVienManager,
        MonHoc,
        MonHocManager,
        SinhVien,
    )
except ImportError as exc:
    _IMPORT_ERROR = exc
    AppData = None
    DangKyManager = None
    DiemManager = None
    MonHoc = None
    MonHocManager = None
    LopTinChi = None
    LopTinChiManager = None
    Lop = None
    LopSinhVienManager = None
    SinhVien = None
else:
    _IMPORT_ERROR = None


def backend_available() -> bool:
    """Trả về True khi extension C++ đã được build và có thể import."""
    return _IMPORT_ERROR is None


def require_backend() -> None:
    """Báo lỗi rõ ràng nếu ứng dụng chạy trước khi build extension."""
    if _IMPORT_ERROR is not None:
        raise RuntimeError(
            "Backend C++ chưa được build. Hãy cấu hình và build project bằng CMake."
        ) from _IMPORT_ERROR


__all__ = [
    "AppData",
    "DangKyManager",
    "DiemManager",
    "MonHoc",
    "MonHocManager",
    "LopTinChi",
    "LopTinChiManager",
    "Lop",
    "LopSinhVienManager",
    "SinhVien",
    "backend_available",
    "require_backend",
]
