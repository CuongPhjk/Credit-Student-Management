#include "../KhaiBao.h"


namespace {

void XoaDangKyNoiBo(Loptinchi& lop, std::string maSV) {
    PTRDK* lienKet = &lop.dssvdk;
    while (*lienKet != nullptr && (*lienKet)->dk.MASV != maSV) {
        lienKet = &((*lienKet)->next);
    }
    if (*lienKet != nullptr) {
        PTRDK nodeCanXoa = *lienKet;
        *lienKet = nodeCanXoa->next;
        delete nodeCanXoa;
    }
}

}  // namespace

DangKyManager::DangKyManager(AppData& appData)
    : appData_(appData) {}

bool DangKyManager::luu(std::string& loi) {
    return appData_.tenFileLopTinChi.empty()
        || GhiDanhSachLopTinChi(
            appData_.tenFileLopTinChi, appData_.dsLopTinChi, loi
        );
}

bool DangKyManager::dangKy(
    int maLopTC,
    std::string maSV,
    std::string& loi
) {
    Loptinchi* lop = TimLopTinChiTheoMa(
        appData_.dsLopTinChi, maLopTC
    );
    PTRDK dangKyCu = lop == nullptr ? nullptr : TimDangKy(lop->dssvdk, maSV);
    bool daTonTai = dangKyCu != nullptr;
    DangKy duLieuCu = daTonTai ? dangKyCu->dk : DangKy{};
    if (!DangKyLopTinChi(
        appData_.dsLopTinChi, appData_.dsLop, maLopTC, maSV, loi
    )) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }
    if (lop != nullptr) {
        PTRDK dangKySau = TimDangKy(lop->dssvdk, maSV);
        if (daTonTai && dangKySau != nullptr) {
            dangKySau->dk = duLieuCu;
        } else if (!daTonTai) {
            XoaDangKyNoiBo(*lop, ChuanHoaMa(maSV));
        }
    }
    return false;
}

bool DangKyManager::huyDangKy(
    int maLopTC,
    std::string maSV,
    std::string& loi
) {
    Loptinchi* lop = TimLopTinChiTheoMa(
        appData_.dsLopTinChi, maLopTC
    );
    PTRDK dangKyCu = lop == nullptr ? nullptr : TimDangKy(lop->dssvdk, maSV);
    DangKy duLieuCu = dangKyCu == nullptr ? DangKy{} : dangKyCu->dk;
    if (!HuyDangKy(appData_.dsLopTinChi, maLopTC, maSV, loi)) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }
    PTRDK dangKySau = lop == nullptr ? nullptr : TimDangKy(lop->dssvdk, maSV);
    if (dangKySau != nullptr) {
        dangKySau->dk = duLieuCu;
    }
    return false;
}

bool DangKyManager::daDangKy(
    int maLopTC,
    std::string maSV
) {
    Loptinchi* lop = TimLopTinChiTheoMa(
        appData_.dsLopTinChi, maLopTC
    );
    return lop != nullptr && !lop->HUYLOP && SinhVienDangKyLopTinChi(*lop, maSV);
}

PTRDK* DangKyManager::layDanhSach(int maLopTC, int& soLuong, string& loi) {
    loi.clear();
    Loptinchi* lop = TimLopTinChiTheoMa(appData_.dsLopTinChi, maLopTC);
    if (!lop) { soLuong = -1; loi = "Không tìm thấy lớp tín chỉ."; return nullptr; }
    return LayDanhSachDangKy(*lop, soLuong);
}

bool DangKyManager::timSinhVien(string maSV, Sinhvien& ketQua) {
    for (int i = 0; i < appData_.dsLop.n; ++i)
        for (PTRSV node = appData_.dsLop.nodes[i].dssv; node; node = node->next)
            if (node->sv.MASV == maSV) { ketQua = node->sv; return true; }
    return false;
}
