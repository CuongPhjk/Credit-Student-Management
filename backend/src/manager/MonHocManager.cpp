#include "../../manager/MonHocManager.h"

#include <string>

#include "../../include/functions/HamMonHoc.h"
#include "../../include/file/XuLyTep.h"
#include "../../include/utils/XuLyChuoi.h"

namespace {

bool kiemTraDuLieuMonHoc(const Monhoc& monHoc, std::string& loi) {
    if (monHoc.MAMH.empty()) {
        loi = "Ma mon hoc khong duoc de trong.";
        return false;
    }
    if (monHoc.MAMH.size() > 10) {
        loi = "Ma mon hoc toi da 10 ky tu.";
        return false;
    }
    if (monHoc.TENMH.empty()) {
        loi = "Ten mon hoc khong duoc de trong.";
        return false;
    }
    if (DemSoKyTuUtf8(monHoc.TENMH) > 50) {
        loi = "Ten mon hoc toi da 50 ky tu.";
        return false;
    }
    if (monHoc.MAMH.find('|') != std::string::npos
        || monHoc.TENMH.find('|') != std::string::npos) {
        loi = "Ma va ten mon hoc khong duoc chua ky tu |.";
        return false;
    }
    if (monHoc.STCLT <= 0) {
        loi = "So tin chi ly thuyet phai lon hon 0.";
        return false;
    }
    if (monHoc.STCTH < 0) {
        loi = "So tin chi thuc hanh khong duoc am.";
        return false;
    }
    return true;
}

void saoChepCayVaoMang(
    treeMH root,
    Monhoc dsKetQua[],
    int kichThuocToiDa,
    int& soLuong
) {
    if (root == nullptr || soLuong >= kichThuocToiDa) {
        return;
    }
    saoChepCayVaoMang(root->left, dsKetQua, kichThuocToiDa, soLuong);
    if (soLuong < kichThuocToiDa) {
        dsKetQua[soLuong++] = root->mh;
    }
    saoChepCayVaoMang(root->right, dsKetQua, kichThuocToiDa, soLuong);
}

}  // namespace

MonHocManager::MonHocManager(AppData& appData)
    : appData_(appData) {}

bool MonHocManager::docDanhSachMonHoc(
    const std::string& tenFile,
    std::string& loi
) {
    if (!DocDanhSachMonHoc(tenFile, appData_.dsMonHoc(), loi)) {
        return false;
    }
    tenFileMonHoc_ = tenFile;
    return true;
}

bool MonHocManager::themMonHoc(const Monhoc& monHoc, std::string& loi) {
    loi.clear();
    Monhoc normalized = monHoc;
    normalized.MAMH = ChuanHoaMa(monHoc.MAMH);
    normalized.TENMH = XoaKhoangTrangThua(monHoc.TENMH);

    if (!kiemTraDuLieuMonHoc(normalized, loi)) {
        return false;
    }
    if (!ThemMonHoc(appData_.dsMonHoc(), normalized, loi)) {
        return false;
    }
    if (tenFileMonHoc_.empty()
        || GhiDanhSachMonHoc(tenFileMonHoc_, appData_.dsMonHoc(), loi)) {
        return true;
    }

    const std::string loiGhiFile = loi;
    std::string loiKhoiPhuc;
    XoaMonHoc(
        appData_.dsMonHoc(),
        appData_.dsLopTinChi(),
        normalized.MAMH,
        loiKhoiPhuc
    );
    loi = loiGhiFile;
    return false;
}

bool MonHocManager::capNhatMonHoc(
    const std::string& maMH,
    const Monhoc& duLieuMoi,
    std::string& loi
) {
    loi.clear();
    const std::string normalizedCode = ChuanHoaMa(maMH);
    if (normalizedCode.empty()) {
        loi = "Ma mon hoc khong duoc de trong.";
        return false;
    }

    Monhoc normalized = duLieuMoi;
    normalized.MAMH = normalizedCode;
    normalized.TENMH = XoaKhoangTrangThua(duLieuMoi.TENMH);
    if (!kiemTraDuLieuMonHoc(normalized, loi)) {
        return false;
    }
    treeMH nodeHienTai = TimMonHoc(appData_.dsMonHoc(), normalizedCode);
    if (nodeHienTai == nullptr) {
        loi = "Khong tim thay mon hoc.";
        return false;
    }
    const Monhoc duLieuCu = nodeHienTai->mh;

    if (!HieuChinhMonHoc(
        appData_.dsMonHoc(),
        normalizedCode,
        normalized,
        loi
    )) {
        return false;
    }
    if (tenFileMonHoc_.empty()
        || GhiDanhSachMonHoc(tenFileMonHoc_, appData_.dsMonHoc(), loi)) {
        return true;
    }

    const std::string loiGhiFile = loi;
    std::string loiKhoiPhuc;
    HieuChinhMonHoc(
        appData_.dsMonHoc(),
        normalizedCode,
        duLieuCu,
        loiKhoiPhuc
    );
    loi = loiGhiFile;
    return false;
}

bool MonHocManager::xoaMonHoc(const std::string& maMH, std::string& loi) {
    loi.clear();
    const std::string normalizedCode = ChuanHoaMa(maMH);
    treeMH nodeHienTai = TimMonHoc(appData_.dsMonHoc(), normalizedCode);
    if (nodeHienTai == nullptr) {
        loi = "Khong tim thay mon hoc.";
        return false;
    }
    const Monhoc duLieuCu = nodeHienTai->mh;

    if (!XoaMonHoc(
        appData_.dsMonHoc(),
        appData_.dsLopTinChi(),
        normalizedCode,
        loi
    )) {
        return false;
    }
    if (tenFileMonHoc_.empty()
        || GhiDanhSachMonHoc(tenFileMonHoc_, appData_.dsMonHoc(), loi)) {
        return true;
    }

    const std::string loiGhiFile = loi;
    std::string loiKhoiPhuc;
    ThemMonHoc(appData_.dsMonHoc(), duLieuCu, loiKhoiPhuc);
    loi = loiGhiFile;
    return false;
}

bool MonHocManager::timMonHoc(
    const std::string& maMH,
    Monhoc& ketQua
) const {
    treeMH node = TimMonHoc(appData_.dsMonHoc(), ChuanHoaMa(maMH));
    if (node == nullptr) {
        return false;
    }
    ketQua = node->mh;
    return true;
}

int MonHocManager::layDanhSachMonHoc(
    Monhoc dsKetQua[],
    int kichThuocToiDa
) const {
    if (dsKetQua == nullptr || kichThuocToiDa <= 0) {
        return 0;
    }
    int soLuong = 0;
    saoChepCayVaoMang(
        appData_.dsMonHoc(),
        dsKetQua,
        kichThuocToiDa,
        soLuong
    );
    return soLuong;
}

int MonHocManager::tongSoMonHoc() const {
    return DemMonHoc(appData_.dsMonHoc());
}
