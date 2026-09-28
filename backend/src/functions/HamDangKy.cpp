#include "../../include/functions/HamDangKy.h"

#include "../../include/functions/HamSinhVien.h"
#include "../../include/utils/XuLyChuoi.h"

namespace {

Loptinchi* TimLopTinChiNoiBo(DS_LTC& dsLTC, int maLopTC) {
    for (int i = 0; i < dsLTC.n; ++i) {
        if (dsLTC.nodes[i] != nullptr
            && dsLTC.nodes[i]->MALOPTC == maLopTC) {
            return dsLTC.nodes[i];
        }
    }
    return nullptr;
}

int DemDangKyHieuLuc(PTRDK danhSach) {
    int soLuong = 0;
    for (PTRDK node = danhSach; node != nullptr; node = node->next) {
        if (!node->dk.HUYDK) {
            ++soLuong;
        }
    }
    return soLuong;
}

}  // namespace

PTRDK TimDangKy(PTRDK dsDangKy, const string& maSV) {
    const string maDaChuanHoa = ChuanHoaMa(maSV);
    for (PTRDK node = dsDangKy; node != nullptr; node = node->next) {
        if (node->dk.MASV == maDaChuanHoa) {
            return node;
        }
    }
    return nullptr;
}

bool SinhVienDangKyLopTinChi(
    const Loptinchi& lopTinChi,
    const string& maSV
) {
    PTRDK dangKy = TimDangKy(lopTinChi.dssvdk, maSV);
    return dangKy != nullptr && !dangKy->dk.HUYDK;
}

bool SinhVienDaDangKyMonTrongHocKy(
    const DS_LTC& dsLTC,
    const string& maSV,
    const string& maMH,
    const string& nienKhoa,
    int hocKy,
    int maLopTCBoQua
) {
    const string maMonDaChuanHoa = ChuanHoaMa(maMH);
    const string nienKhoaDaChuanHoa = XoaKhoangTrangDauCuoi(nienKhoa);
    for (int i = 0; i < dsLTC.n; ++i) {
        const Loptinchi* lop = dsLTC.nodes[i];
        if (lop != nullptr
            && lop->MALOPTC != maLopTCBoQua
            && !lop->HUYLOP
            && lop->MAMH == maMonDaChuanHoa
            && lop->NIENKHOA == nienKhoaDaChuanHoa
            && lop->HOCKY == hocKy
            && SinhVienDangKyLopTinChi(*lop, maSV)) {
            return true;
        }
    }
    return false;
}

bool LopTinChiConCho(const Loptinchi& lopTinChi) {
    return !lopTinChi.HUYLOP
        && DemDangKyHieuLuc(lopTinChi.dssvdk) < lopTinChi.SOSVMAX;
}

bool DangKyLopTinChi(
    DS_LTC& dsLTC,
    const DS_LOP& dsLop,
    int maLopTC,
    const string& maSV,
    string& loi
) {
    loi.clear();
    const string maDaChuanHoa = ChuanHoaMa(maSV);
    if (!KiemTraTrungMaSinhVien(dsLop, maDaChuanHoa)) {
        loi = "Ma sinh vien khong ton tai.";
        return false;
    }
    Loptinchi* lop = TimLopTinChiNoiBo(dsLTC, maLopTC);
    if (lop == nullptr) {
        loi = "Khong tim thay lop tin chi.";
        return false;
    }
    if (lop->HUYLOP) {
        loi = "Lop tin chi da bi huy.";
        return false;
    }
    PTRDK dangKyCu = TimDangKy(lop->dssvdk, maDaChuanHoa);
    if (dangKyCu != nullptr && !dangKyCu->dk.HUYDK) {
        loi = "Sinh vien da dang ky lop tin chi nay.";
        return false;
    }
    if (!LopTinChiConCho(*lop)) {
        loi = "Lop tin chi da het cho.";
        return false;
    }
    if (SinhVienDaDangKyMonTrongHocKy(
        dsLTC, maDaChuanHoa, lop->MAMH,
        lop->NIENKHOA, lop->HOCKY, lop->MALOPTC
    )) {
        loi = "Sinh vien da dang ky mon hoc nay trong cung hoc ky.";
        return false;
    }
    if (dangKyCu != nullptr) {
        dangKyCu->dk.HUYDK = false;
        dangKyCu->dk.DIEM = 0.0F;
        dangKyCu->dk.DADIEM = false;
        return true;
    }

    PTRDK nodeMoi = new nodeDK{{maDaChuanHoa, 0.0F, false}, nullptr};
    PTRDK* viTriChen = &lop->dssvdk;
    while (*viTriChen != nullptr
           && (*viTriChen)->dk.MASV < maDaChuanHoa) {
        viTriChen = &((*viTriChen)->next);
    }
    nodeMoi->next = *viTriChen;
    *viTriChen = nodeMoi;
    return true;
}

bool HuyDangKy(
    DS_LTC& dsLTC,
    int maLopTC,
    const string& maSV,
    string& loi
) {
    loi.clear();
    Loptinchi* lop = TimLopTinChiNoiBo(dsLTC, maLopTC);
    if (lop == nullptr) {
        loi = "Khong tim thay lop tin chi.";
        return false;
    }
    PTRDK dangKy = TimDangKy(lop->dssvdk, maSV);
    if (dangKy == nullptr || dangKy->dk.HUYDK) {
        loi = "Sinh vien chua dang ky lop tin chi nay.";
        return false;
    }
    dangKy->dk.HUYDK = true;
    return true;
}

int LayDanhSachDangKy(
    const Loptinchi& lopTinChi,
    Dangky dsKetQua[],
    int kichThuocToiDa,
    bool layCaDaHuy
) {
    if (dsKetQua == nullptr || kichThuocToiDa <= 0) {
        return 0;
    }
    int soLuong = 0;
    for (PTRDK node = lopTinChi.dssvdk;
         node != nullptr && soLuong < kichThuocToiDa;
         node = node->next) {
        if (layCaDaHuy || !node->dk.HUYDK) {
            dsKetQua[soLuong++] = node->dk;
        }
    }
    return soLuong;
}

void GiaiPhongDanhSachDangKy(PTRDK& dsDangKy) {
    while (dsDangKy != nullptr) {
        PTRDK nodeCanXoa = dsDangKy;
        dsDangKy = dsDangKy->next;
        delete nodeCanXoa;
    }
}
