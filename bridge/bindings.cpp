#include <string>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "../backend/src/KhaiBao.h"

namespace py = pybind11;

namespace {


template <typename T>
py::list chuyenMangThanhDanhSach(T* danhSach, int soLuong) {
    py::list ketQua;
    for (int i = 0; i < soLuong; ++i)
        ketQua.append(py::cast(danhSach[i]));
    delete[] danhSach;
    return ketQua;
}

Monhoc taoMonHocMacDinh() {
    return Monhoc{"", "", 0, 0};
}

bool themMonHoc(MonHocManager& manager, Monhoc monHoc) {
    std::string loi;
    if (!manager.themMonHoc(monHoc, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool capNhatMonHoc(
    MonHocManager& manager,
    std::string maMH,
    Monhoc duLieuMoi
) {
    std::string loi;
    if (!manager.capNhatMonHoc(maMH, duLieuMoi, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool xoaMonHoc(MonHocManager& manager, std::string maMH) {
    std::string loi;
    if (!manager.xoaMonHoc(maMH, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool docDanhSachMonHoc(MonHocManager& manager, std::string tenFile) {
    std::string loi;
    if (!manager.docDanhSachMonHoc(tenFile, loi)) {
        throw std::runtime_error(loi);
    }
    return true;
}

py::object timMonHoc(MonHocManager& manager, std::string maMH) {
    Monhoc ketQua = taoMonHocMacDinh();
    if (!manager.timMonHoc(maMH, ketQua)) {
        return py::none();
    }
    return py::cast(ketQua);
}

py::list layDanhSachMonHoc(MonHocManager& manager) {
    int soLuong;
    treeMH* danhSach = manager.layDanhSachMonHoc(soLuong);
    py::list ketQua;
    for (int i = 0; i < soLuong; ++i)
        ketQua.append(py::cast(danhSach[i]->mh, py::return_value_policy::copy));
    delete[] danhSach;
    return ketQua;
}

py::list layMonHocTheoTen(MonHocManager& manager, bool giamDan) {
    int soLuong;
    treeMH* danhSach = manager.layMonHocTheoTen(soLuong);
    py::list ketQua;
    int viTri = giamDan ? soLuong - 1 : 0;
    int buoc = giamDan ? -1 : 1;
    for (int i = 0; i < soLuong; ++i, viTri += buoc) {
        ketQua.append(py::cast(danhSach[viTri]->mh, py::return_value_policy::copy));
    }
    return ketQua;
}

py::list layLopThieuSiSo(LopTinChiManager& manager, string nienKhoa, int hocKy) {
    py::list ketQua;
    for (auto& muc : manager.layLopThieuSiSo(nienKhoa, hocKy)) {
        Loptinchi& lop = *muc.lop;
        ketQua.append(py::make_tuple(lop.MALOPTC, lop.MAMH, lop.NHOM, muc.soDangKy, lop.SOSVMIN));
    }
    return ketQua;
}

void huyLopThieuSiSo(
    LopTinChiManager& manager, string nienKhoa, int hocKy, std::vector<int> maDaXacNhan
) {
    string loi;
    if (!manager.huyLopThieuSiSo(nienKhoa, hocKy, maDaXacNhan, loi)) {
        throw py::value_error(loi);
    }
}

Loptinchi taoLopTinChiMacDinh() {
    return Loptinchi{0, "", "", 1, 1, 1, 1, false, nullptr};
}

bool themLopTinChi(LopTinChiManager& manager, Loptinchi lopTinChi) {
    std::string loi;
    if (!manager.themLopTinChi(lopTinChi, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool capNhatLopTinChi(
    LopTinChiManager& manager,
    int maLopTC,
    Loptinchi duLieuMoi
) {
    std::string loi;
    if (!manager.capNhatLopTinChi(maLopTC, duLieuMoi, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool xoaLopTinChi(LopTinChiManager& manager, int maLopTC) {
    std::string loi;
    if (!manager.xoaLopTinChi(maLopTC, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool docDanhSachLopTinChi(
    LopTinChiManager& manager,
    std::string tenFile
) {
    std::string loi;
    if (!manager.docDanhSachLopTinChi(tenFile, loi)) {
        throw std::runtime_error(loi);
    }
    return true;
}

py::object timLopTinChi(LopTinChiManager& manager, int maLopTC) {
    Loptinchi ketQua = taoLopTinChiMacDinh();
    if (!manager.timLopTinChi(maLopTC, ketQua)) {
        return py::none();
    }
    return py::cast(ketQua);
}

py::list layDanhSachLopTinChi(LopTinChiManager& manager) {
    int soLuong;
    Loptinchi** danhSach = manager.layDanhSachLopTinChi(soLuong);
    py::list ketQua;
    for (int i = 0; i < soLuong; ++i)
        ketQua.append(py::cast(*danhSach[i], py::return_value_policy::copy));
    return ketQua;  // Borrowed original array: do not delete[].
}

Lop taoLopMacDinh() {
    return Lop{"", "", nullptr};
}

Sinhvien taoSinhVienMacDinh() {
    return Sinhvien{"", "", "", "", ""};
}

bool docDanhSachLopSinhVien(
    LopSinhVienManager& manager,
    std::string tenFile
) {
    std::string loi;
    if (!manager.docDanhSachLopSinhVien(tenFile, loi)) {
        throw std::runtime_error(loi);
    }
    return true;
}

bool themLop(LopSinhVienManager& manager, Lop lop) {
    std::string loi;
    if (!manager.themLop(lop, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool capNhatLop(
    LopSinhVienManager& manager,
    std::string maLop,
    std::string tenLopMoi
) {
    std::string loi;
    if (!manager.capNhatLop(maLop, tenLopMoi, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool xoaLop(LopSinhVienManager& manager, std::string maLop) {
    std::string loi;
    if (!manager.xoaLop(maLop, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

py::object timLop(
    LopSinhVienManager& manager,
    std::string maLop
) {
    Lop ketQua = taoLopMacDinh();
    if (!manager.timLop(maLop, ketQua)) {
        return py::none();
    }
    return py::cast(ketQua);
}

py::list layDanhSachLop(LopSinhVienManager& manager) {
    int soLuong;
    Lop* danhSach = manager.layDanhSachLop(soLuong);
    return chuyenMangThanhDanhSach(danhSach, soLuong);
}

bool themSinhVien(
    LopSinhVienManager& manager,
    std::string maLop,
    Sinhvien sinhVien
) {
    std::string loi;
    if (!manager.themSinhVien(maLop, sinhVien, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool capNhatSinhVien(
    LopSinhVienManager& manager,
    std::string maSV,
    Sinhvien duLieuMoi
) {
    std::string loi;
    if (!manager.capNhatSinhVien(maSV, duLieuMoi, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool xoaSinhVien(
    LopSinhVienManager& manager,
    std::string maSV
) {
    std::string loi;
    if (!manager.xoaSinhVien(maSV, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

py::object timSinhVien(
    LopSinhVienManager& manager,
    std::string maSV
) {
    Sinhvien ketQua = taoSinhVienMacDinh();
    std::string maLop;
    if (!manager.timSinhVien(maSV, ketQua, maLop)) {
        return py::none();
    }
    return py::cast(ketQua);
}

py::object timThongTinSinhVien(
    LopSinhVienManager& manager,
    std::string maSV
) {
    Sinhvien ketQua = taoSinhVienMacDinh();
    std::string maLop;
    if (!manager.timSinhVien(maSV, ketQua, maLop)) {
        return py::none();
    }
    py::dict thongTin;
    thongTin["sinh_vien"] = py::cast(ketQua);
    thongTin["ma_lop"] = maLop;
    return thongTin;
}

py::list layDanhSachSinhVien(
    LopSinhVienManager& manager, string maLop
) {
    int soLuong;
    PTRSV* danhSach = manager.layDanhSachSinhVien(maLop, soLuong);
    py::list ketQua;
    for (int i = 0; i < soLuong; ++i)
        ketQua.append(py::cast(danhSach[i]->sv, py::return_value_policy::copy));
    delete[] danhSach;
    return ketQua;
}

py::list laySinhVienTheoMa(LopSinhVienManager& manager, string maLop, bool giamDan) {
    int soLuong;
    PTRSV* danhSach = manager.laySinhVienTheoMa(maLop, soLuong);
    py::list ketQua;
    for (int i = 0; i < soLuong; ++i) {
        int viTri = giamDan ? soLuong - 1 - i : i;
        ketQua.append(py::cast(danhSach[viTri]->sv, py::return_value_policy::copy));
    }
    return ketQua;  // Manager owns the cached array; do not delete[].
}

bool dangKyLop(
    DangKyManager& manager,
    int maLopTC,
    std::string maSV
) {
    std::string loi;
    if (!manager.dangKy(maLopTC, maSV, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool huyDangKyLop(
    DangKyManager& manager,
    int maLopTC,
    std::string maSV
) {
    std::string loi;
    if (!manager.huyDangKy(maLopTC, maSV, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

py::list laySinhVienDangKy(DangKyManager& manager, int maLopTC) {
    int soLuong;
    string loi;
    PTRDK* danhSach = manager.layDanhSach(maLopTC, soLuong, loi);
    if (soLuong < 0) throw py::value_error(loi);
    py::list ketQua;
    try {
        for (int i = 0; i < soLuong; ++i) {
            Sinhvien sv;
            if (!manager.timSinhVien(danhSach[i]->dk.MASV, sv))
                throw py::value_error("Không tìm thấy thông tin sinh viên " + danhSach[i]->dk.MASV);
            py::dict dong;
            dong["ma_sv"] = danhSach[i]->dk.MASV;
            dong["ho_ten"] = sv.HO + " " + sv.TEN;
            dong["da_huy"] = danhSach[i]->dk.HUYDK;
            ketQua.append(dong);
        }
    } catch (...) { delete[] danhSach; throw; }
    delete[] danhSach;
    return ketQua;
}

}  // namespace

PYBIND11_MODULE(_credit_backend, module) {
    module.doc() = "Binding C++ cho he thong quan ly tin chi sinh vien";

    py::class_<Monhoc>(module, "MonHoc")
        .def(py::init(&taoMonHocMacDinh))
        .def(
            py::init([](
                std::string maMH,
                std::string tenMH,
                int stcLT,
                int stcTH
            ) {
                return Monhoc{maMH, tenMH, stcLT, stcTH};
            }),
            py::arg("ma_mh"),
            py::arg("ten_mh"),
            py::arg("stc_lt"),
            py::arg("stc_th") = 0
        )
        .def_readwrite("ma_mh", &Monhoc::MAMH)
        .def_readwrite("ten_mh", &Monhoc::TENMH)
        .def_readwrite("stc_lt", &Monhoc::STCLT)
        .def_readwrite("stc_th", &Monhoc::STCTH)
        .def_property_readonly(
            "tong_tin_chi",
            [](Monhoc monHoc) {
                return monHoc.STCLT + monHoc.STCTH;
            }
        );

    py::class_<Loptinchi>(module, "LopTinChi")
        .def(py::init(&taoLopTinChiMacDinh))
        .def(
            py::init([](
                std::string maMH,
                std::string nienKhoa,
                int hocKy,
                int nhom,
                int soSVMin,
                int soSVMax
            ) {
                return Loptinchi{
                    0, maMH, nienKhoa, hocKy, nhom,
                    soSVMin, soSVMax, false, nullptr
                };
            }),
            py::arg("ma_mh"),
            py::arg("nien_khoa"),
            py::arg("hoc_ky"),
            py::arg("nhom"),
            py::arg("so_sv_min"),
            py::arg("so_sv_max")
        )
        .def_readonly("ma_lop_tc", &Loptinchi::MALOPTC)
        .def_readwrite("ma_mh", &Loptinchi::MAMH)
        .def_readwrite("nien_khoa", &Loptinchi::NIENKHOA)
        .def_readwrite("hoc_ky", &Loptinchi::HOCKY)
        .def_readwrite("nhom", &Loptinchi::NHOM)
        .def_readwrite("so_sv_min", &Loptinchi::SOSVMIN)
        .def_readwrite("so_sv_max", &Loptinchi::SOSVMAX)
        .def_readonly("huy_lop", &Loptinchi::HUYLOP)
        .def_property_readonly(
            "so_sv_dang_ky",
            [](Loptinchi lopTinChi) {
                return DemSoSinhVienDangKy(lopTinChi);
            }
        )
        .def_property_readonly(
            "trang_thai",
            [](Loptinchi lopTinChi) {
                if (lopTinChi.HUYLOP) {
                    return std::string(u8"Đã hủy");
                }
                return std::string(u8"Đang mở");
            }
        );

    py::class_<Lop>(module, "Lop")
        .def(py::init(&taoLopMacDinh))
        .def(
            py::init([](
                std::string maLop,
                std::string tenLop
            ) { return Lop{maLop, tenLop, nullptr}; }),
            py::arg("ma_lop"),
            py::arg("ten_lop")
        )
        .def_readwrite("ma_lop", &Lop::MALOP)
        .def_readwrite("ten_lop", &Lop::TENLOP)
        .def_property_readonly(
            "so_sinh_vien",
            [](Lop lop) { return lop.soSinhVien; }
        );

    py::class_<Sinhvien>(module, "SinhVien")
        .def(py::init(&taoSinhVienMacDinh))
        .def(
            py::init([](
                std::string maSV,
                std::string ho,
                std::string ten,
                std::string phai,
                std::string soDT
            ) { return Sinhvien{maSV, ho, ten, phai, soDT}; }),
            py::arg("ma_sv"),
            py::arg("ho"),
            py::arg("ten"),
            py::arg("phai"),
            py::arg("so_dt")
        )
        .def_readwrite("ma_sv", &Sinhvien::MASV)
        .def_readwrite("ho", &Sinhvien::HO)
        .def_readwrite("ten", &Sinhvien::TEN)
        .def_readwrite("phai", &Sinhvien::PHAI)
        .def_readwrite("so_dt", &Sinhvien::SODT)
        .def_property_readonly(
            "ho_ten",
            [](Sinhvien sinhVien) {
                return sinhVien.HO + " " + sinhVien.TEN;
            }
        );

    py::class_<AppData>(module, "AppData")
        .def(py::init<>())
        .def("clear", &AppData::clear);

    py::class_<MonHocManager>(module, "MonHocManager")
        .def(
            py::init<AppData&>(),
            py::arg("app_data"),
            py::keep_alive<1, 2>()
        )
        .def("them_mon_hoc", &themMonHoc, py::arg("mon_hoc"))
        .def(
            "cap_nhat_mon_hoc",
            &capNhatMonHoc,
            py::arg("ma_mh"),
            py::arg("du_lieu_moi")
        )
        .def("xoa_mon_hoc", &xoaMonHoc, py::arg("ma_mh"))
        .def(
            "doc_danh_sach_mon_hoc",
            &docDanhSachMonHoc,
            py::arg("ten_file")
        )
        .def("tim_mon_hoc", &timMonHoc, py::arg("ma_mh"))
        .def("lay_danh_sach_mon_hoc", &layDanhSachMonHoc)
        .def("lay_mon_hoc_theo_ten", &layMonHocTheoTen, py::arg("giam_dan") = false)
        .def("tong_so_mon_hoc", &MonHocManager::tongSoMonHoc);

    py::class_<LopTinChiManager>(module, "LopTinChiManager")
        .def(
            py::init<AppData&>(),
            py::arg("app_data"),
            py::keep_alive<1, 2>()
        )
        .def("them_lop_tin_chi", &themLopTinChi, py::arg("lop_tin_chi"))
        .def(
            "cap_nhat_lop_tin_chi",
            &capNhatLopTinChi,
            py::arg("ma_lop_tc"),
            py::arg("du_lieu_moi")
        )
        .def("xoa_lop_tin_chi", &xoaLopTinChi, py::arg("ma_lop_tc"))
        .def(
            "doc_danh_sach_lop_tin_chi",
            &docDanhSachLopTinChi,
            py::arg("ten_file")
        )
        .def("tim_lop_tin_chi", &timLopTinChi, py::arg("ma_lop_tc"))
        .def("lay_danh_sach_lop_tin_chi", &layDanhSachLopTinChi)
        .def("lay_lop_thieu_si_so", &layLopThieuSiSo,
             py::arg("nien_khoa"), py::arg("hoc_ky"))
        .def("huy_lop_thieu_si_so", &huyLopThieuSiSo,
             py::arg("nien_khoa"), py::arg("hoc_ky"), py::arg("ma_da_xac_nhan"))
        .def("tong_so_lop_tin_chi", &LopTinChiManager::tongSoLopTinChi);

    py::class_<LopSinhVienManager>(module, "LopSinhVienManager")
        .def(
            py::init<AppData&>(),
            py::arg("app_data"),
            py::keep_alive<1, 2>()
        )
        .def("doc_danh_sach_lop_sinh_vien", &docDanhSachLopSinhVien, py::arg("ten_file"))
        .def("them_lop", &themLop, py::arg("lop"))
        .def(
            "cap_nhat_lop", &capNhatLop,
            py::arg("ma_lop"), py::arg("ten_lop_moi")
        )
        .def("xoa_lop", &xoaLop, py::arg("ma_lop"))
        .def("tim_lop", &timLop, py::arg("ma_lop"))
        .def("lay_danh_sach_lop", &layDanhSachLop)
        .def("tong_so_lop", &LopSinhVienManager::tongSoLop)
        .def(
            "them_sinh_vien", &themSinhVien,
            py::arg("ma_lop"), py::arg("sinh_vien")
        )
        .def(
            "cap_nhat_sinh_vien", &capNhatSinhVien,
            py::arg("ma_sv"), py::arg("du_lieu_moi")
        )
        .def("xoa_sinh_vien", &xoaSinhVien, py::arg("ma_sv"))
        .def("tim_sinh_vien", &timSinhVien, py::arg("ma_sv"))
        .def(
            "tim_thong_tin_sinh_vien",
            &timThongTinSinhVien,
            py::arg("ma_sv")
        )
        .def(
            "lay_danh_sach_sinh_vien",
            [](LopSinhVienManager& m, string ma) { return layDanhSachSinhVien(m, ma); },
            py::arg("ma_lop")
        )
        .def(
            "tong_so_sinh_vien_trong_lop",
            &LopSinhVienManager::tongSoSinhVienTrongLop,
            py::arg("ma_lop")
        )
        .def("giai_phong_thu_tu_sinh_vien", &LopSinhVienManager::giaiPhongThuTuSinhVien)
        .def("lay_sinh_vien_ma_tang", [](LopSinhVienManager& m, string ma) {
            return laySinhVienTheoMa(m, ma, false);
        }, py::arg("ma_lop"))
        .def("lay_sinh_vien_ma_giam", [](LopSinhVienManager& m, string ma) {
            return laySinhVienTheoMa(m, ma, true);
        }, py::arg("ma_lop"))
        .def("tong_so_sinh_vien", &LopSinhVienManager::tongSoSinhVien);

    py::class_<DangKyManager>(module, "DangKyManager")
        .def(
            py::init<AppData&>(),
            py::arg("app_data"),
            py::keep_alive<1, 2>()
        )
        .def(
            "dang_ky", &dangKyLop,
            py::arg("ma_lop_tc"), py::arg("ma_sv")
        )
        .def(
            "huy_dang_ky", &huyDangKyLop,
            py::arg("ma_lop_tc"), py::arg("ma_sv")
        )
        .def("lay_danh_sach_dang_ky", &laySinhVienDangKy, py::arg("ma_lop_tc"))
        .def(
            "da_dang_ky", &DangKyManager::daDangKy,
            py::arg("ma_lop_tc"), py::arg("ma_sv")
        );



}
