#include "../KhaiBao.h"


LopSinhVienManager::LopSinhVienManager(AppData& appData)
    : appData_(appData) {}

bool LopSinhVienManager::docDanhSachLopSinhVien(
    std::string tenFile,
    std::string& loi
) {
    giaiPhongThuTuSinhVien();
    if (!DocDanhSachLopSinhVien(tenFile, appData_.dsLop, loi)) {
        return false;
    }
    appData_.tenFileLopSinhVien = tenFile;
    return true;
}

bool LopSinhVienManager::luu(std::string& loi) {
    return appData_.tenFileLopSinhVien.empty()
        || GhiDanhSachLopSinhVien(appData_.tenFileLopSinhVien, appData_.dsLop, loi);
}

bool LopSinhVienManager::themLop(Lop lop, std::string& loi) {
    if (!ThemLop(appData_.dsLop, lop, loi)) {
        return false;
    }
    giaiPhongThuTuSinhVien();
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    XoaLop(appData_.dsLop, lop.MALOP, loiKhoiPhuc);
    return false;
}

bool LopSinhVienManager::capNhatLop(
    std::string maLop,
    std::string tenLopMoi,
    std::string& loi
) {
    Lop* lop = TimLop(appData_.dsLop, maLop);
    if (lop == nullptr) {
        loi = "Không tìm thấy lớp.";
        return false;
    }
    std::string tenCu = lop->TENLOP;
    if (!HieuChinhLop(appData_.dsLop, maLop, tenLopMoi, loi)) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    HieuChinhLop(appData_.dsLop, maLop, tenCu, loiKhoiPhuc);
    return false;
}

bool LopSinhVienManager::xoaLop(
    std::string maLop,
    std::string& loi
) {
    Lop* lop = TimLop(appData_.dsLop, maLop);
    if (lop == nullptr) {
        loi = "Không tìm thấy lớp.";
        return false;
    }
    Lop duLieuCu = *lop;
    if (!XoaLop(appData_.dsLop, maLop, loi)) {
        return false;
    }
    giaiPhongThuTuSinhVien();
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    ThemLop(appData_.dsLop, duLieuCu, loiKhoiPhuc);
    return false;
}

bool LopSinhVienManager::timLop(
    std::string maLop,
    Lop& ketQua
) {
    Lop* lop = TimLop(appData_.dsLop, maLop);
    if (lop == nullptr) {
        return false;
    }
    ketQua = *lop;
    return true;
}

Lop* LopSinhVienManager::layDanhSachLop(int& soLuong) {
    return LayDanhSachLop(appData_.dsLop, soLuong);
}

int LopSinhVienManager::tongSoLop() {
    return appData_.dsLop.n;
}

bool LopSinhVienManager::themSinhVien(
    std::string maLop,
    Sinhvien sinhVien,
    std::string& loi
) {
    if (!ThemSinhVien(appData_.dsLop, maLop, sinhVien, loi)) {
        return false;
    }
    giaiPhongThuTuSinhVien();
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    XoaSinhVien(
        appData_.dsLop, appData_.dsLopTinChi,
        sinhVien.MASV, loiKhoiPhuc
    );
    return false;
}

bool LopSinhVienManager::capNhatSinhVien(
    std::string maSV,
    Sinhvien duLieuMoi,
    std::string& loi
) {
    int viTriLop = -1;
    PTRSV node = TimSinhVienToanTruong(
        appData_.dsLop, maSV, viTriLop
    );
    if (node == nullptr) {
        loi = "Không tìm thấy sinh viên.";
        return false;
    }
    Sinhvien duLieuCu = node->sv;
    if (!HieuChinhSinhVien(appData_.dsLop, maSV, duLieuMoi, loi)) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    HieuChinhSinhVien(
        appData_.dsLop, maSV, duLieuCu, loiKhoiPhuc
    );
    return false;
}

bool LopSinhVienManager::xoaSinhVien(
    std::string maSV,
    std::string& loi
) {
    int viTriLop = -1;
    PTRSV node = TimSinhVienToanTruong(
        appData_.dsLop, maSV, viTriLop
    );
    if (node == nullptr) {
        loi = "Không tìm thấy sinh viên.";
        return false;
    }
    Sinhvien duLieuCu = node->sv;
    if (!XoaSinhVien(
        appData_.dsLop, appData_.dsLopTinChi, maSV, loi
    )) {
        return false;
    }
    giaiPhongThuTuSinhVien();
    if (luu(loi)) {
        return true;
    }
    ChenSinhVienTheoTen(
        appData_.dsLop.nodes[viTriLop], duLieuCu
    );
    return false;
}

bool LopSinhVienManager::timSinhVien(
    std::string maSV,
    Sinhvien& ketQua,
    std::string& maLop
) {
    DS_LOP& danhSach = appData_.dsLop;
    for (int i = 0; i < danhSach.n; ++i) {
        PTRSV node = TimSinhVienTrongLop(
            danhSach.nodes[i].dssv, maSV
        );
        if (node != nullptr) {
            ketQua = node->sv;
            maLop = danhSach.nodes[i].MALOP;
            return true;
        }
    }
    return false;
}

PTRSV* LopSinhVienManager::layDanhSachSinhVien(string maLop, int& soLuong) {
    if (maLopDangGiu_ != ChuanHoaMa(maLop)
        || phienBanDangGiu_ != appData_.dsLop.phienBan) {
        giaiPhongThuTuSinhVien();
    }
    soLuong = 0;
    Lop* lop = TimLop(appData_.dsLop, maLop);
    return lop == nullptr ? nullptr : LayDanhSachSinhVien(*lop, soLuong);
}

int LopSinhVienManager::tongSoSinhVienTrongLop(
    std::string maLop
) {
    Lop* lop = TimLop(appData_.dsLop, maLop);
    return lop == nullptr ? 0 : lop->soSinhVien;
}

int LopSinhVienManager::tongSoSinhVien() {
    int tong = 0;
    DS_LOP& danhSach = appData_.dsLop;
    for (int i = 0; i < danhSach.n; ++i) {
        tong += danhSach.nodes[i].soSinhVien;
    }
    return tong;
}


LopSinhVienManager::~LopSinhVienManager() {
    giaiPhongThuTuSinhVien();
}

void LopSinhVienManager::giaiPhongThuTuSinhVien() {
    delete[] dsTheoMa_;
    dsTheoMa_ = nullptr;
    soLuongTheoMa_ = 0;
    maLopDangGiu_.clear();
    phienBanDangGiu_ = 0;
}

PTRSV* LopSinhVienManager::laySinhVienTheoMa(string maLop, int& soLuong) {
    string ma = ChuanHoaMa(maLop);
    // Other managers, direct core calls, file reads and AppData::clear may have
    // freed old nodes. Check the revision before reading any cached pointer.
    if (maLopDangGiu_ != ma || phienBanDangGiu_ != appData_.dsLop.phienBan) {
        giaiPhongThuTuSinhVien();
        Lop* lop = TimLop(appData_.dsLop, ma);
        if (lop == nullptr) {
            soLuong = 0;
            return nullptr;
        }
        int soLuongMoi;
        dsTheoMa_ = LayDanhSachSinhVien(*lop, soLuongMoi);
        SapXepConTroSinhVienTheoMa(dsTheoMa_, soLuongMoi);
        soLuongTheoMa_ = soLuongMoi;
        maLopDangGiu_ = ma;
        phienBanDangGiu_ = appData_.dsLop.phienBan;
    }
    soLuong = soLuongTheoMa_;
    return dsTheoMa_;
}
