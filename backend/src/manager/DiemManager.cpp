#include "../../manager/DiemManager.h"

#include <memory>

#include "../../include/file/XuLyTep.h"
#include "../../include/functions/HamDangKy.h"
#include "../../include/functions/HamDiem.h"
#include "../../include/functions/HamLopTinChi.h"
#include "../../include/functions/HamSinhVien.h"
#include "../../include/utils/KiemTraDuLieu.h"
#include "../../include/utils/XuLyChuoi.h"

DiemManager::DiemManager(AppData& appData)
    : appData_(appData) {}

bool DiemManager::luu(std::string& loi) const {
    return appData_.tenFileLopTinChi().empty()
        || GhiDanhSachLopTinChi(
            appData_.tenFileLopTinChi(), appData_.dsLopTinChi(), loi
        );
}

int DiemManager::demSinhVien(
    const std::string& nienKhoa,
    int hocKy,
    const std::string& maMH,
    int nhom,
    std::string& loi
) const {
    return DemSinhVienNhapDiem(
        appData_.dsLopTinChi(), nienKhoa, hocKy, maMH, nhom, loi
    );
}

int DiemManager::layDanhSachSinhVien(
    const std::string& nienKhoa,
    int hocKy,
    const std::string& maMH,
    int nhom,
    Diemsinhvien dsKetQua[],
    int kichThuocToiDa,
    std::string& loi
) const {
    return LayDanhSachSinhVienNhapDiem(
        appData_.dsLopTinChi(), appData_.dsLop(),
        nienKhoa, hocKy, maMH, nhom,
        dsKetQua, kichThuocToiDa, loi
    );
}

bool DiemManager::capNhatDiem(
    const std::string& nienKhoa,
    int hocKy,
    const std::string& maMH,
    int nhom,
    const std::string& maSV,
    float diemMoi,
    std::string& loi
) {
    const Diemcapnhat motDiem{maSV, diemMoi};
    return capNhatDanhSachDiem(
        nienKhoa, hocKy, maMH, nhom, &motDiem, 1, loi
    );
}

bool DiemManager::capNhatDanhSachDiem(
    const std::string& nienKhoa,
    int hocKy,
    const std::string& maMH,
    int nhom,
    const Diemcapnhat dsDiemMoi[],
    int soLuong,
    std::string& loi
) {
    loi.clear();
    if (dsDiemMoi == nullptr || soLuong <= 0) {
        loi = "Danh sach diem cap nhat khong duoc de trong.";
        return false;
    }

    // Goi ham dem truoc de kiem tra day du bo loc va trang thai lop.
    if (DemSinhVienNhapDiem(
        appData_.dsLopTinChi(), nienKhoa, hocKy, maMH, nhom, loi
    ) < 0) {
        return false;
    }
    Loptinchi* lop = TimLopTinChi(
        appData_.dsLopTinChi(), nienKhoa, hocKy, maMH, nhom
    );
    if (lop == nullptr) {
        loi = "Khong tim thay lop tin chi phu hop.";
        return false;
    }

    std::unique_ptr<std::string[]> maDaChuanHoa(
        new std::string[soLuong]
    );
    std::unique_ptr<float[]> diemCu(new float[soLuong]);
    std::unique_ptr<bool[]> trangThaiDiemCu(new bool[soLuong]);
    for (int i = 0; i < soLuong; ++i) {
        maDaChuanHoa[i] = ChuanHoaMa(dsDiemMoi[i].MASV);
        if (!MaSinhVienHopLe(maDaChuanHoa[i])) {
            loi = "Ma sinh vien tai dong " + std::to_string(i + 1)
                + " khong hop le.";
            return false;
        }
        for (int j = 0; j < i; ++j) {
            if (maDaChuanHoa[j] == maDaChuanHoa[i]) {
                loi = "Ma sinh vien " + maDaChuanHoa[i]
                    + " bi lap trong danh sach cap nhat.";
                return false;
            }
        }
        if (!KiemTraDiemHopLe(dsDiemMoi[i].DIEM)) {
            loi = "Diem cua sinh vien " + maDaChuanHoa[i]
                + " phai nam trong khoang tu 0 den 10.";
            return false;
        }
        if (!KiemTraTrungMaSinhVien(appData_.dsLop(), maDaChuanHoa[i])) {
            loi = "Khong tim thay sinh vien " + maDaChuanHoa[i] + ".";
            return false;
        }
        PTRDK dangKy = TimDangKy(lop->dssvdk, maDaChuanHoa[i]);
        if (dangKy == nullptr || dangKy->dk.HUYDK) {
            loi = "Sinh vien " + maDaChuanHoa[i]
                + " khong co dang ky con hieu luc trong lop tin chi.";
            return false;
        }
        diemCu[i] = dangKy->dk.DIEM;
        trangThaiDiemCu[i] = dangKy->dk.DADIEM;
    }

    int soDiemDaDoi = 0;
    for (int i = 0; i < soLuong; ++i) {
        if (!HieuChinhDiem(
            appData_.dsLopTinChi(), nienKhoa, hocKy, maMH, nhom,
            maDaChuanHoa[i], dsDiemMoi[i].DIEM, loi
        )) {
            for (int j = 0; j < soDiemDaDoi; ++j) {
                std::string loiKhoiPhuc;
                HieuChinhDiem(
                    appData_.dsLopTinChi(), nienKhoa, hocKy, maMH, nhom,
                    maDaChuanHoa[j], diemCu[j], loiKhoiPhuc
                );
                PTRDK dangKyKhoiPhuc = TimDangKy(
                    lop->dssvdk, maDaChuanHoa[j]
                );
                if (dangKyKhoiPhuc != nullptr) {
                    dangKyKhoiPhuc->dk.DADIEM = trangThaiDiemCu[j];
                }
            }
            return false;
        }
        ++soDiemDaDoi;
    }

    if (luu(loi)) {
        return true;
    }
    for (int i = 0; i < soLuong; ++i) {
        std::string loiKhoiPhuc;
        HieuChinhDiem(
            appData_.dsLopTinChi(), nienKhoa, hocKy, maMH, nhom,
            maDaChuanHoa[i], diemCu[i], loiKhoiPhuc
        );
        PTRDK dangKyKhoiPhuc = TimDangKy(
            lop->dssvdk, maDaChuanHoa[i]
        );
        if (dangKyKhoiPhuc != nullptr) {
            dangKyKhoiPhuc->dk.DADIEM = trangThaiDiemCu[i];
        }
    }
    return false;
}
