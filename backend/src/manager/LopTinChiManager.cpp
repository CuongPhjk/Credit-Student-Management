#include "../../manager/LopTinChiManager.h"

#include "../../include/file/XuLyTep.h"
#include "../../include/functions/HamLopTinChi.h"

namespace {

Loptinchi* timTheoMa(DS_LTC& danhSach, int maLopTC) {
    for (int i = 0; i < danhSach.n; ++i) {
        if (danhSach.nodes[i] != nullptr
            && danhSach.nodes[i]->MALOPTC == maLopTC) {
            return danhSach.nodes[i];
        }
    }
    return nullptr;
}

}  // namespace

LopTinChiManager::LopTinChiManager(AppData& appData)
    : appData_(appData) {}

bool LopTinChiManager::docDanhSachLopTinChi(
    const std::string& tenFile,
    std::string& loi
) {
    if (!DocDanhSachLopTinChi(tenFile, appData_.dsLopTinChi(), loi)) {
        return false;
    }
    appData_.tenFileLopTinChi() = tenFile;
    return true;
}

bool LopTinChiManager::luu(std::string& loi) const {
    return appData_.tenFileLopTinChi().empty()
        || GhiDanhSachLopTinChi(
            appData_.tenFileLopTinChi(), appData_.dsLopTinChi(), loi
        );
}

bool LopTinChiManager::themLopTinChi(
    const Loptinchi& lopTinChi,
    std::string& loi
) {
    const int maTiepTheoCu = appData_.dsLopTinChi().maTiepTheo;
    if (!ThemLopTinChi(
        appData_.dsLopTinChi(), appData_.dsMonHoc(), lopTinChi, loi
    )) {
        return false;
    }
    const int maMoi = appData_.dsLopTinChi()
        .nodes[appData_.dsLopTinChi().n - 1]->MALOPTC;
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    XoaLopTinChi(appData_.dsLopTinChi(), maMoi, loiKhoiPhuc);
    appData_.dsLopTinChi().maTiepTheo = maTiepTheoCu;
    return false;
}

bool LopTinChiManager::capNhatLopTinChi(
    int maLopTC,
    const Loptinchi& duLieuMoi,
    std::string& loi
) {
    Loptinchi* hienTai = timTheoMa(appData_.dsLopTinChi(), maLopTC);
    if (hienTai == nullptr) {
        loi = "Khong tim thay lop tin chi.";
        return false;
    }
    const Loptinchi duLieuCu = *hienTai;
    if (!HieuChinhLopTinChi(
        appData_.dsLopTinChi(), appData_.dsMonHoc(),
        maLopTC, duLieuMoi, loi
    )) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }
    std::string loiKhoiPhuc;
    HieuChinhLopTinChi(
        appData_.dsLopTinChi(), appData_.dsMonHoc(),
        maLopTC, duLieuCu, loiKhoiPhuc
    );
    return false;
}

bool LopTinChiManager::xoaLopTinChi(int maLopTC, std::string& loi) {
    Loptinchi* hienTai = timTheoMa(appData_.dsLopTinChi(), maLopTC);
    if (hienTai == nullptr) {
        loi = "Khong tim thay lop tin chi.";
        return false;
    }
    const Loptinchi duLieuCu = *hienTai;
    if (!XoaLopTinChi(appData_.dsLopTinChi(), maLopTC, loi)) {
        return false;
    }
    if (luu(loi)) {
        return true;
    }

    DS_LTC& danhSach = appData_.dsLopTinChi();
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
) const {
    const Loptinchi* lop = timTheoMa(appData_.dsLopTinChi(), maLopTC);
    if (lop == nullptr) {
        return false;
    }
    ketQua = *lop;
    return true;
}

int LopTinChiManager::layDanhSachLopTinChi(
    Loptinchi dsKetQua[],
    int kichThuocToiDa
) const {
    if (dsKetQua == nullptr || kichThuocToiDa <= 0) {
        return 0;
    }
    const DS_LTC& danhSach = appData_.dsLopTinChi();
    const int soLuong = danhSach.n < kichThuocToiDa
        ? danhSach.n : kichThuocToiDa;
    for (int i = 0; i < soLuong; ++i) {
        dsKetQua[i] = *danhSach.nodes[i];
    }
    return soLuong;
}

int LopTinChiManager::tongSoLopTinChi() const {
    return appData_.dsLopTinChi().n;
}
