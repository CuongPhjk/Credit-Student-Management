#include "../KhaiBao.h"

#include <string>


MonHocManager::MonHocManager(AppData& appData)
    : appData_(appData) {}

bool MonHocManager::docDanhSachMonHoc(
    std::string tenFile,
    std::string& loi
) {
    boThuTuTheoTen();
    if (!DocDanhSachMonHoc(tenFile, appData_.dsMonHoc, appData_.n, loi)) {
        return false;
    }
    appData_.tenFileMonHoc = tenFile;
    return true;
}

bool MonHocManager::themMonHoc(Monhoc monHoc, std::string& loi) {
    loi.clear();
    if (!ThemMonHoc(appData_.dsMonHoc, appData_.n, monHoc, loi)) {
        return false;
    }
    boThuTuTheoTen();
    if (appData_.tenFileMonHoc.empty()
        || GhiDanhSachMonHoc(appData_.tenFileMonHoc, appData_.dsMonHoc, loi)) {
        return true;
    }

    std::string loiGhiFile = loi;
    std::string loiKhoiPhuc;
    XoaMonHoc(appData_.dsMonHoc, appData_.n,
        appData_.dsLopTinChi,
        ChuanHoaMa(monHoc.MAMH),
        loiKhoiPhuc
    );
    loi = loiGhiFile;
    return false;
}

bool MonHocManager::capNhatMonHoc(
    std::string maMH,
    Monhoc duLieuMoi,
    std::string& loi
) {
    loi.clear();
    std::string normalizedCode = ChuanHoaMa(maMH);

    treeMH nodeHienTai = TimMonHoc(appData_.dsMonHoc, normalizedCode);
    if (nodeHienTai == nullptr) {
        loi = "Không tìm thấy môn học.";
        return false;
    }
    Monhoc duLieuCu = nodeHienTai->mh;

    if (!HieuChinhMonHoc(
        appData_.dsMonHoc,
        normalizedCode,
        duLieuMoi,
        loi
    )) {
        return false;
    }
    if (nodeHienTai->mh.TENMH != duLieuCu.TENMH) {
        boThuTuTheoTen();
    }
    if (appData_.tenFileMonHoc.empty()
        || GhiDanhSachMonHoc(appData_.tenFileMonHoc, appData_.dsMonHoc, loi)) {
        return true;
    }

    std::string loiGhiFile = loi;
    std::string loiKhoiPhuc;
    HieuChinhMonHoc(
        appData_.dsMonHoc,
        normalizedCode,
        duLieuCu,
        loiKhoiPhuc
    );
    loi = loiGhiFile;
    return false;
}

bool MonHocManager::xoaMonHoc(std::string maMH, std::string& loi) {
    loi.clear();
    std::string normalizedCode = ChuanHoaMa(maMH);
    treeMH nodeHienTai = TimMonHoc(appData_.dsMonHoc, normalizedCode);
    if (nodeHienTai == nullptr) {
        loi = "Không tìm thấy môn học.";
        return false;
    }
    Monhoc duLieuCu = nodeHienTai->mh;

    if (!XoaMonHoc(appData_.dsMonHoc, appData_.n,
        appData_.dsLopTinChi,
        normalizedCode,
        loi
    )) {
        return false;
    }
    boThuTuTheoTen();
    if (appData_.tenFileMonHoc.empty()
        || GhiDanhSachMonHoc(appData_.tenFileMonHoc, appData_.dsMonHoc, loi)) {
        return true;
    }

    std::string loiGhiFile = loi;
    std::string loiKhoiPhuc;
    ThemMonHoc(appData_.dsMonHoc, appData_.n, duLieuCu, loiKhoiPhuc);
    loi = loiGhiFile;
    return false;
}

bool MonHocManager::timMonHoc(
    std::string maMH,
    Monhoc& ketQua
) {
    treeMH node = TimMonHoc(appData_.dsMonHoc, ChuanHoaMa(maMH));
    if (node == nullptr) {
        return false;
    }
    ketQua = node->mh;
    return true;
}

treeMH* MonHocManager::layDanhSachMonHoc(int& soLuong) {
    return LayDanhSachMonHoc(appData_.dsMonHoc, appData_.n, soLuong);
}

int MonHocManager::tongSoMonHoc() {
    return appData_.n;
}

void MonHocManager::boThuTuTheoTen() {
    ++appData_.phienBanMonHoc;
    dsTheoTen_.reset();
}

treeMH* MonHocManager::layMonHocTheoTen(int& soLuong) {
    if (!dsTheoTen_ || phienBanDangGiu_ != appData_.phienBanMonHoc) {
        std::unique_ptr<treeMH[]> danhSach(LayDanhSachMonHoc(appData_.dsMonHoc, appData_.n, soLuong));
        SapXepConTroMonHocTheoTen(danhSach.get(), soLuong);
        dsTheoTen_.swap(danhSach);
        phienBanDangGiu_ = appData_.phienBanMonHoc;
    }
    soLuong = appData_.n;
    return dsTheoTen_.get();
}
