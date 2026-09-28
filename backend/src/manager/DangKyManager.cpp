#include "../../manager/DangKyManager.h"

#include "../../include/file/XuLyTep.h"
#include "../../include/functions/HamDangKy.h"
#include "../../include/functions/HamLopTinChi.h"
#include "../../include/utils/XuLyChuoi.h"

namespace {

void XoaDangKyNoiBo(Loptinchi& lop, const std::string& maSV) {
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

bool DangKyManager::luu(std::string& loi) const {
    return appData_.tenFileLopTinChi().empty()
        || GhiDanhSachLopTinChi(
            appData_.tenFileLopTinChi(), appData_.dsLopTinChi(), loi
        );
}

bool DangKyManager::dangKy(
    int maLopTC,
    const std::string& maSV,
    std::string& loi
) {
    Loptinchi* lop = TimLopTinChiTheoMa(
        appData_.dsLopTinChi(), maLopTC
    );
    PTRDK dangKyCu = lop == nullptr ? nullptr : TimDangKy(lop->dssvdk, maSV);
    const bool daTonTai = dangKyCu != nullptr;
    const Dangky duLieuCu = daTonTai ? dangKyCu->dk : Dangky{};
    if (!DangKyLopTinChi(
        appData_.dsLopTinChi(), appData_.dsLop(), maLopTC, maSV, loi
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
    const std::string& maSV,
    std::string& loi
) {
    Loptinchi* lop = TimLopTinChiTheoMa(
        appData_.dsLopTinChi(), maLopTC
    );
    PTRDK dangKyCu = lop == nullptr ? nullptr : TimDangKy(lop->dssvdk, maSV);
    const Dangky duLieuCu = dangKyCu == nullptr ? Dangky{} : dangKyCu->dk;
    if (!HuyDangKy(appData_.dsLopTinChi(), maLopTC, maSV, loi)) {
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
    const std::string& maSV
) const {
    const Loptinchi* lop = TimLopTinChiTheoMa(
        appData_.dsLopTinChi(), maLopTC
    );
    return lop != nullptr && SinhVienDangKyLopTinChi(*lop, maSV);
}
