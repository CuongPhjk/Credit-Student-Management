#include "../KhaiBao.h"


namespace {

Loptinchi* timTheoMa(DS_LTC& danhSach, int maLopTC) {
    for (int i = 0; i < danhSach.n; ++i) {
        if (danhSach.nodes[i]->MALOPTC == maLopTC) {
            return danhSach.nodes[i];
        }
    }
    return nullptr;
}

}  // namespace

LopTinChiManager::LopTinChiManager(AppData& appData)
    : appData_(appData) {}

bool LopTinChiManager::docDanhSachLopTinChi(
    std::string tenFile,
    std::string& loi
) {
    if (!DocDanhSachLopTinChi(tenFile, appData_.dsLopTinChi, loi)) {
        return false;
    }
    appData_.tenFileLopTinChi = tenFile;
    return true;
}

bool LopTinChiManager::luu(std::string& loi) {
    return appData_.tenFileLopTinChi.empty()
        || GhiDanhSachLopTinChi(
            appData_.tenFileLopTinChi, appData_.dsLopTinChi, loi
        );
}

bool LopTinChiManager::themLopTinChi(
    Loptinchi lopTinChi,
    std::string& loi
) {
    int maTiepTheoCu = appData_.dsLopTinChi.maTiepTheo;
    if (!ThemLopTinChi(
        appData_.dsLopTinChi, appData_.dsMonHoc, lopTinChi, loi
    )) {
        return false;
    }
    int maMoi = appData_.dsLopTinChi
        .nodes[appData_.dsLopTinChi.n - 1]->MALOPTC;
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    XoaLopTinChi(appData_.dsLopTinChi, maMoi, loiKhoiPhuc);
    appData_.dsLopTinChi.maTiepTheo = maTiepTheoCu;
    return false;
}

bool LopTinChiManager::capNhatLopTinChi(
    int maLopTC,
    Loptinchi duLieuMoi,
    std::string& loi
) {
    Loptinchi* hienTai = timTheoMa(appData_.dsLopTinChi, maLopTC);
    if (hienTai == nullptr) {
        loi = "Không tìm thấy lớp tín chỉ.";
        return false;
    }
    Loptinchi duLieuCu = *hienTai;
    if (!HieuChinhLopTinChi(
        appData_.dsLopTinChi, appData_.dsMonHoc,
        maLopTC, duLieuMoi, loi
    )) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    HieuChinhLopTinChi(
        appData_.dsLopTinChi, appData_.dsMonHoc,
        maLopTC, duLieuCu, loiKhoiPhuc
    );
    return false;
}

bool LopTinChiManager::xoaLopTinChi(int maLopTC, std::string& loi) {
    Loptinchi* hienTai = timTheoMa(appData_.dsLopTinChi, maLopTC);
    if (hienTai == nullptr) {
        loi = "Không tìm thấy lớp tín chỉ.";
        return false;
    }
    Loptinchi duLieuCu = *hienTai;
    if (!XoaLopTinChi(appData_.dsLopTinChi, maLopTC, loi)) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }

    DS_LTC& danhSach = appData_.dsLopTinChi;
    int viTriChen = 0;
    while (viTriChen < danhSach.n
           && danhSach.nodes[viTriChen]->MALOPTC < maLopTC) {
        ++viTriChen;
    }
    for (int i = danhSach.n; i > viTriChen; --i) {
        danhSach.nodes[i] = danhSach.nodes[i - 1];
    }
    danhSach.nodes[viTriChen] = new Loptinchi(duLieuCu);
    ++danhSach.n;
    return false;
}

bool LopTinChiManager::timLopTinChi(
    int maLopTC,
    Loptinchi& ketQua
) {
    Loptinchi* lop = timTheoMa(appData_.dsLopTinChi, maLopTC);
    if (lop == nullptr) {
        return false;
    }
    ketQua = *lop;
    return true;
}

Loptinchi** LopTinChiManager::layDanhSachLopTinChi(int& soLuong) {
    return LayDanhSachLopTinChi(appData_.dsLopTinChi, soLuong);
}

int LopTinChiManager::tongSoLopTinChi() {
    return appData_.dsLopTinChi.n;
}

std::vector<LopTinChiManager::LopThieuSiSo> LopTinChiManager::layLopThieuSiSo(
    string nienKhoa, int hocKy
) {
    std::vector<LopThieuSiSo> ketQua;
    DS_LTC& danhSach = appData_.dsLopTinChi;
    nienKhoa = XoaKhoangTrangDauCuoi(nienKhoa);
    for (int i = 0; i < danhSach.n; ++i) {
        Loptinchi* lop = danhSach.nodes[i];
        if (lop->HUYLOP || lop->NIENKHOA != nienKhoa || lop->HOCKY != hocKy) {
            continue;
        }
        int soDangKy = DemSoSinhVienDangKy(*lop);
        if (soDangKy < lop->SOSVMIN) {
            ketQua.push_back({lop, soDangKy});
        }
    }
    return ketQua;
}

bool LopTinChiManager::huyLopThieuSiSo(
    string nienKhoa, int hocKy, const std::vector<int>& maDaXacNhan, string& loi
) {
    loi.clear();
    if (maDaXacNhan.empty()) {
        loi = "Không có lớp tín chỉ nào được xác nhận hủy.";
        return false;
    }
    auto danhSach = layLopThieuSiSo(nienKhoa, hocKy);
    if (danhSach.size() == maDaXacNhan.size()) {
        size_t i = 0;
        while (i < danhSach.size() && danhSach[i].lop->MALOPTC == maDaXacNhan[i]) {
            ++i;
        }
        if (i == danhSach.size()) {
            for (auto& muc : danhSach) muc.lop->HUYLOP = true;
            if (luu(loi)) return true;

            for (auto& muc : danhSach) muc.lop->HUYLOP = false;
            return false;
        }
    }
    loi = "Danh sách lớp thiếu sĩ số đã thay đổi. Vui lòng xem lại trước khi hủy.";
    return false;
}
