#include <memory>
#include <string>

#include <pybind11/pybind11.h>

#include "AppData.h"
#include "DangKyManager.h"
#include "DiemManager.h"
#include "HamLopTinChi.h"
#include "HamSinhVien.h"
#include "LopSinhVienManager.h"
#include "LopTinChiManager.h"
#include "MonHocManager.h"

namespace py = pybind11;

namespace {

Monhoc taoMonHocMacDinh() {
    return Monhoc{"", "", 0, 0};
}

bool themMonHoc(MonHocManager& manager, const Monhoc& monHoc) {
    std::string loi;
    if (!manager.themMonHoc(monHoc, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool capNhatMonHoc(
    MonHocManager& manager,
    const std::string& maMH,
    const Monhoc& duLieuMoi
) {
    std::string loi;
    if (!manager.capNhatMonHoc(maMH, duLieuMoi, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool xoaMonHoc(MonHocManager& manager, const std::string& maMH) {
    std::string loi;
    if (!manager.xoaMonHoc(maMH, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool docDanhSachMonHoc(MonHocManager& manager, const std::string& tenFile) {
    std::string loi;
    if (!manager.docDanhSachMonHoc(tenFile, loi)) {
        throw std::runtime_error(loi);
    }
    return true;
}

py::object timMonHoc(const MonHocManager& manager, const std::string& maMH) {
    Monhoc ketQua = taoMonHocMacDinh();
    if (!manager.timMonHoc(maMH, ketQua)) {
        return py::none();
    }
    return py::cast(ketQua);
}

py::list layDanhSachMonHoc(const MonHocManager& manager) {
    const int soLuong = manager.tongSoMonHoc();
    py::list ketQua;
    if (soLuong <= 0) {
        return ketQua;
    }

    std::unique_ptr<Monhoc[]> dsMonHoc(new Monhoc[soLuong]);
    const int soPhanTuDaGhi = manager.layDanhSachMonHoc(
        dsMonHoc.get(),
        soLuong
    );
    for (int i = 0; i < soPhanTuDaGhi; ++i) {
        const Monhoc& monHoc = dsMonHoc[i];
        ketQua.append(py::cast(Monhoc{
            monHoc.MAMH,
            monHoc.TENMH,
            monHoc.STCLT,
            monHoc.STCTH
        }));
    }
    return ketQua;
}

Loptinchi taoLopTinChiMacDinh() {
    return Loptinchi{0, "", "", 1, 1, 1, 1, false, nullptr};
}

bool themLopTinChi(LopTinChiManager& manager, const Loptinchi& lopTinChi) {
    std::string loi;
    if (!manager.themLopTinChi(lopTinChi, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool capNhatLopTinChi(
    LopTinChiManager& manager,
    int maLopTC,
    const Loptinchi& duLieuMoi
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
    const std::string& tenFile
) {
    std::string loi;
    if (!manager.docDanhSachLopTinChi(tenFile, loi)) {
        throw std::runtime_error(loi);
    }
    return true;
}

py::object timLopTinChi(const LopTinChiManager& manager, int maLopTC) {
    Loptinchi ketQua = taoLopTinChiMacDinh();
    if (!manager.timLopTinChi(maLopTC, ketQua)) {
        return py::none();
    }
    return py::cast(ketQua);
}

py::list layDanhSachLopTinChi(const LopTinChiManager& manager) {
    const int soLuong = manager.tongSoLopTinChi();
    py::list ketQua;
    if (soLuong <= 0) {
        return ketQua;
    }
    std::unique_ptr<Loptinchi[]> danhSach(new Loptinchi[soLuong]);
    const int daGhi = manager.layDanhSachLopTinChi(
        danhSach.get(), soLuong
    );
    for (int i = 0; i < daGhi; ++i) {
        ketQua.append(py::cast(danhSach[i]));
    }
    return ketQua;
}

Lop taoLopMacDinh() {
    return Lop{"", "", nullptr};
}

Sinhvien taoSinhVienMacDinh() {
    return Sinhvien{"", "", "", "", ""};
}

bool docDanhSachLopSinhVien(
    LopSinhVienManager& manager,
    const std::string& tenFile
) {
    std::string loi;
    if (!manager.docDanhSachLopSinhVien(tenFile, loi)) {
        throw std::runtime_error(loi);
    }
    return true;
}

bool themLop(LopSinhVienManager& manager, const Lop& lop) {
    std::string loi;
    if (!manager.themLop(lop, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool capNhatLop(
    LopSinhVienManager& manager,
    const std::string& maLop,
    const std::string& tenLopMoi
) {
    std::string loi;
    if (!manager.capNhatLop(maLop, tenLopMoi, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool xoaLop(LopSinhVienManager& manager, const std::string& maLop) {
    std::string loi;
    if (!manager.xoaLop(maLop, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

py::object timLop(
    const LopSinhVienManager& manager,
    const std::string& maLop
) {
    Lop ketQua = taoLopMacDinh();
    if (!manager.timLop(maLop, ketQua)) {
        return py::none();
    }
    return py::cast(ketQua);
}

py::list layDanhSachLop(const LopSinhVienManager& manager) {
    const int soLuong = manager.tongSoLop();
    py::list ketQua;
    if (soLuong <= 0) {
        return ketQua;
    }
    std::unique_ptr<Lop[]> danhSach(new Lop[soLuong]);
    const int daGhi = manager.layDanhSachLop(danhSach.get(), soLuong);
    for (int i = 0; i < daGhi; ++i) {
        ketQua.append(py::cast(danhSach[i]));
    }
    return ketQua;
}

bool themSinhVien(
    LopSinhVienManager& manager,
    const std::string& maLop,
    const Sinhvien& sinhVien
) {
    std::string loi;
    if (!manager.themSinhVien(maLop, sinhVien, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool capNhatSinhVien(
    LopSinhVienManager& manager,
    const std::string& maSV,
    const Sinhvien& duLieuMoi
) {
    std::string loi;
    if (!manager.capNhatSinhVien(maSV, duLieuMoi, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

bool xoaSinhVien(
    LopSinhVienManager& manager,
    const std::string& maSV
) {
    std::string loi;
    if (!manager.xoaSinhVien(maSV, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

py::object timSinhVien(
    const LopSinhVienManager& manager,
    const std::string& maSV
) {
    Sinhvien ketQua = taoSinhVienMacDinh();
    std::string maLop;
    if (!manager.timSinhVien(maSV, ketQua, maLop)) {
        return py::none();
    }
    return py::cast(ketQua);
}

py::object timThongTinSinhVien(
    const LopSinhVienManager& manager,
    const std::string& maSV
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
    const LopSinhVienManager& manager,
    const std::string& maLop
) {
    const int soLuong = manager.tongSoSinhVienTrongLop(maLop);
    py::list ketQua;
    if (soLuong <= 0) {
        return ketQua;
    }
    std::unique_ptr<Sinhvien[]> danhSach(new Sinhvien[soLuong]);
    const int daGhi = manager.layDanhSachSinhVien(
        maLop, danhSach.get(), soLuong
    );
    for (int i = 0; i < daGhi; ++i) {
        ketQua.append(py::cast(danhSach[i]));
    }
    return ketQua;
}

bool dangKyLop(
    DangKyManager& manager,
    int maLopTC,
    const std::string& maSV
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
    const std::string& maSV
) {
    std::string loi;
    if (!manager.huyDangKy(maLopTC, maSV, loi)) {
        throw py::value_error(loi);
    }
    return true;
}

py::list layDanhSachSinhVienNhapDiem(
    const DiemManager& manager,
    const std::string& nienKhoa,
    int hocKy,
    const std::string& maMH,
    int nhom
) {
    std::string loi;
    const int soLuong = manager.demSinhVien(
        nienKhoa, hocKy, maMH, nhom, loi
    );
    if (soLuong < 0) {
        throw py::value_error(loi);
    }

    py::list ketQua;
    if (soLuong == 0) {
        return ketQua;
    }
    std::unique_ptr<Diemsinhvien[]> danhSach(
        new Diemsinhvien[soLuong]
    );
    const int daGhi = manager.layDanhSachSinhVien(
        nienKhoa, hocKy, maMH, nhom,
        danhSach.get(), soLuong, loi
    );
    if (daGhi < 0) {
        throw std::runtime_error(loi);
    }
    for (int i = 0; i < daGhi; ++i) {
        py::dict dong;
        dong["ma_sv"] = danhSach[i].MASV;
        dong["ho"] = danhSach[i].HO;
        dong["ten"] = danhSach[i].TEN;
        dong["diem"] = danhSach[i].DIEM;
        dong["da_co_diem"] = danhSach[i].DADIEM;
        ketQua.append(dong);
    }
    return ketQua;
}

bool capNhatDanhSachDiem(
    DiemManager& manager,
    const std::string& nienKhoa,
    int hocKy,
    const std::string& maMH,
    int nhom,
    const py::list& danhSachDiem
) {
    const int soLuong = static_cast<int>(py::len(danhSachDiem));
    if (soLuong <= 0) {
        throw py::value_error("Danh sach diem cap nhat khong duoc de trong.");
    }
    std::unique_ptr<Diemcapnhat[]> danhSachMoi(
        new Diemcapnhat[soLuong]
    );
    for (int i = 0; i < soLuong; ++i) {
        py::handle muc = danhSachDiem[i];
        if (!py::isinstance<py::dict>(muc)) {
            throw py::value_error(
                "Moi dong cap nhat diem phai gom ma_sv va diem."
            );
        }
        py::dict dong = py::reinterpret_borrow<py::dict>(muc);
        if (!dong.contains("ma_sv") || !dong.contains("diem")) {
            throw py::value_error(
                "Moi dong cap nhat diem phai gom ma_sv va diem."
            );
        }
        try {
            danhSachMoi[i].MASV = py::cast<std::string>(dong["ma_sv"]);
            danhSachMoi[i].DIEM = py::cast<float>(dong["diem"]);
        } catch (const py::cast_error&) {
            throw py::value_error(
                "Ma sinh vien phai la chuoi va diem phai la so."
            );
        }
    }

    std::string loi;
    if (!manager.capNhatDanhSachDiem(
        nienKhoa, hocKy, maMH, nhom,
        danhSachMoi.get(), soLuong, loi
    )) {
        throw py::value_error(loi);
    }
    return true;
}

}  // namespace

PYBIND11_MODULE(_credit_backend, module) {
    module.doc() = "Binding C++ cho he thong quan ly tin chi sinh vien";

    py::class_<Monhoc>(module, "MonHoc")
        .def(py::init(&taoMonHocMacDinh))
        .def(
            py::init([](
                const std::string& maMH,
                const std::string& tenMH,
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
            [](const Monhoc& monHoc) {
                return monHoc.STCLT + monHoc.STCTH;
            }
        );

    py::class_<Loptinchi>(module, "LopTinChi")
        .def(py::init(&taoLopTinChiMacDinh))
        .def(
            py::init([](
                const std::string& maMH,
                const std::string& nienKhoa,
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
            [](const Loptinchi& lopTinChi) {
                return DemSoSinhVienDangKy(lopTinChi);
            }
        )
        .def_property_readonly(
            "trang_thai",
            [](const Loptinchi& lopTinChi) {
                if (lopTinChi.HUYLOP) {
                    return std::string(u8"Đã hủy");
                }
                if (DemSoSinhVienDangKy(lopTinChi) < lopTinChi.SOSVMIN) {
                    return std::string(u8"Thiếu sĩ số");
                }
                return std::string(u8"Đang mở");
            }
        );

    py::class_<Lop>(module, "Lop")
        .def(py::init(&taoLopMacDinh))
        .def(
            py::init([](
                const std::string& maLop,
                const std::string& tenLop
            ) { return Lop{maLop, tenLop, nullptr}; }),
            py::arg("ma_lop"),
            py::arg("ten_lop")
        )
        .def_readwrite("ma_lop", &Lop::MALOP)
        .def_readwrite("ten_lop", &Lop::TENLOP)
        .def_property_readonly(
            "so_sinh_vien",
            [](const Lop& lop) { return DemSinhVien(lop.dssv); }
        );

    py::class_<Sinhvien>(module, "SinhVien")
        .def(py::init(&taoSinhVienMacDinh))
        .def(
            py::init([](
                const std::string& maSV,
                const std::string& ho,
                const std::string& ten,
                const std::string& phai,
                const std::string& soDT
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
            [](const Sinhvien& sinhVien) {
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
            &layDanhSachSinhVien,
            py::arg("ma_lop")
        )
        .def(
            "tong_so_sinh_vien_trong_lop",
            &LopSinhVienManager::tongSoSinhVienTrongLop,
            py::arg("ma_lop")
        )
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
        .def(
            "da_dang_ky", &DangKyManager::daDangKy,
            py::arg("ma_lop_tc"), py::arg("ma_sv")
        );

    py::class_<DiemManager>(module, "DiemManager")
        .def(
            py::init<AppData&>(),
            py::arg("app_data"),
            py::keep_alive<1, 2>()
        )
        .def(
            "lay_danh_sach_sinh_vien", &layDanhSachSinhVienNhapDiem,
            py::arg("nien_khoa"), py::arg("hoc_ky"),
            py::arg("ma_mh"), py::arg("nhom")
        )
        .def(
            "cap_nhat_danh_sach_diem", &capNhatDanhSachDiem,
            py::arg("nien_khoa"), py::arg("hoc_ky"),
            py::arg("ma_mh"), py::arg("nhom"),
            py::arg("danh_sach_diem")
        );

}
