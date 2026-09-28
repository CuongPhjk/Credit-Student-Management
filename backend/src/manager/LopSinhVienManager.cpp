#include "../../manager/LopSinhVienManager.h"

#include "../../include/file/XuLyTep.h"
#include "../../include/functions/HamLop.h"
#include "../../include/functions/HamSinhVien.h"

LopSinhVienManager::LopSinhVienManager(AppData& appData)
    : appData_(appData) {}

bool LopSinhVienManager::docDanhSachLopSinhVien(
    const std::string& tenFile,
    std::string& loi
) {
    if (!DocDanhSachLopSinhVien(tenFile, appData_.dsLop(), loi)) {
        return false;
    }
    tenFileLopSinhVien_ = tenFile;
    return true;
}

bool LopSinhVienManager::luu(std::string& loi) const {
    return tenFileLopSinhVien_.empty()
        || GhiDanhSachLopSinhVien(tenFileLopSinhVien_, appData_.dsLop(), loi);
}

bool LopSinhVienManager::themLop(const Lop& lop, std::string& loi) {
    if (!ThemLop(appData_.dsLop(), lop, loi)) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    XoaLop(appData_.dsLop(), lop.MALOP, loiKhoiPhuc);
    return false;
}

bool LopSinhVienManager::capNhatLop(
    const std::string& maLop,
    const std::string& tenLopMoi,
    std::string& loi
) {
    Lop* lop = TimLop(appData_.dsLop(), maLop);
    if (lop == nullptr) {
        loi = "Khong tim thay lop.";
        return false;
    }
    const std::string tenCu = lop->TENLOP;
    if (!HieuChinhLop(appData_.dsLop(), maLop, tenLopMoi, loi)) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    HieuChinhLop(appData_.dsLop(), maLop, tenCu, loiKhoiPhuc);
    return false;
}

bool LopSinhVienManager::xoaLop(
    const std::string& maLop,
    std::string& loi
) {
    Lop* lop = TimLop(appData_.dsLop(), maLop);
    if (lop == nullptr) {
        loi = "Khong tim thay lop.";
        return false;
    }
    const Lop duLieuCu = *lop;
    if (!XoaLop(appData_.dsLop(), maLop, loi)) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    ThemLop(appData_.dsLop(), duLieuCu, loiKhoiPhuc);
    return false;
}

bool LopSinhVienManager::timLop(
    const std::string& maLop,
    Lop& ketQua
) const {
    const Lop* lop = TimLop(appData_.dsLop(), maLop);
    if (lop == nullptr) {
        return false;
    }
    ketQua = *lop;
    return true;
}

int LopSinhVienManager::layDanhSachLop(
    Lop dsKetQua[],
    int kichThuocToiDa
) const {
    if (dsKetQua == nullptr || kichThuocToiDa <= 0) {
        return 0;
    }
    const DS_LOP& danhSach = appData_.dsLop();
    const int soLuong = danhSach.n < kichThuocToiDa
        ? danhSach.n : kichThuocToiDa;
    for (int i = 0; i < soLuong; ++i) {
        dsKetQua[i] = danhSach.nodes[i];
    }
    return soLuong;
}

int LopSinhVienManager::tongSoLop() const {
    return appData_.dsLop().n;
}

bool LopSinhVienManager::themSinhVien(
    const std::string& maLop,
    const Sinhvien& sinhVien,
    std::string& loi
) {
    if (!ThemSinhVien(appData_.dsLop(), maLop, sinhVien, loi)) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    XoaSinhVien(
        appData_.dsLop(), appData_.dsLopTinChi(),
        sinhVien.MASV, loiKhoiPhuc
    );
    return false;
}

bool LopSinhVienManager::capNhatSinhVien(
    const std::string& maSV,
    const Sinhvien& duLieuMoi,
    std::string& loi
) {
    int viTriLop = -1;
    PTRSV node = TimSinhVienToanTruong(
        appData_.dsLop(), maSV, viTriLop
    );
    if (node == nullptr) {
        loi = "Khong tim thay sinh vien.";
        return false;
    }
    const Sinhvien duLieuCu = node->sv;
    if (!HieuChinhSinhVien(appData_.dsLop(), maSV, duLieuMoi, loi)) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    HieuChinhSinhVien(
        appData_.dsLop(), maSV, duLieuCu, loiKhoiPhuc
    );
    return false;
}

bool LopSinhVienManager::xoaSinhVien(
    const std::string& maSV,
    std::string& loi
) {
    int viTriLop = -1;
    PTRSV node = TimSinhVienToanTruong(
        appData_.dsLop(), maSV, viTriLop
    );
    if (node == nullptr) {
        loi = "Khong tim thay sinh vien.";
        return false;
    }
    const Sinhvien duLieuCu = node->sv;
    if (!XoaSinhVien(
        appData_.dsLop(), appData_.dsLopTinChi(), maSV, loi
    )) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }
    ChenSinhVienTheoTen(
        appData_.dsLop().nodes[viTriLop].dssv, duLieuCu
    );
    return false;
}

bool LopSinhVienManager::timSinhVien(
    const std::string& maSV,
    Sinhvien& ketQua,
    std::string& maLop
) const {
    const DS_LOP& danhSach = appData_.dsLop();
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

int LopSinhVienManager::layDanhSachSinhVien(
    const std::string& maLop,
    Sinhvien dsKetQua[],
    int kichThuocToiDa
) const {
    if (dsKetQua == nullptr || kichThuocToiDa <= 0) {
        return 0;
    }
    const Lop* lop = TimLop(appData_.dsLop(), maLop);
    if (lop == nullptr) {
        return 0;
    }
    int soLuong = 0;
    for (PTRSV node = lop->dssv;
         node != nullptr && soLuong < kichThuocToiDa;
         node = node->next) {
        dsKetQua[soLuong++] = node->sv;
    }
    return soLuong;
}

int LopSinhVienManager::tongSoSinhVienTrongLop(
    const std::string& maLop
) const {
    const Lop* lop = TimLop(appData_.dsLop(), maLop);
    return lop == nullptr ? 0 : DemSinhVien(lop->dssv);
}

int LopSinhVienManager::tongSoSinhVien() const {
    int tong = 0;
    const DS_LOP& danhSach = appData_.dsLop();
    for (int i = 0; i < danhSach.n; ++i) {
        tong += DemSinhVien(danhSach.nodes[i].dssv);
    }
    return tong;
}
