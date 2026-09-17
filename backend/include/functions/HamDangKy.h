#ifndef HAM_DANG_KY_H
#define HAM_DANG_KY_H

#include "../model/KhaiBao.h"

PTRDK TimDangKy(PTRDK dsDangKy, const string& maSV);

bool SinhVienDangKyLopTinChi(
    const Loptinchi& lopTinChi,
    const string& maSV
);

bool SinhVienDaDangKyMonTrongHocKy(
    const DS_LTC& dsLTC,
    const string& maSV,
    const string& maMH,
    const string& nienKhoa,
    int hocKy,
    int maLopTCBoQua = -1
);

bool LopTinChiConCho(const Loptinchi& lopTinChi);

bool DangKyLopTinChi(
    DS_LTC& dsLTC,
    const DS_LOP& dsLop,
    int maLopTC,
    const string& maSV,
    string& loi
);

bool HuyDangKy(
    DS_LTC& dsLTC,
    int maLopTC,
    const string& maSV,
    string& loi
);

int LayDanhSachDangKy(
    const Loptinchi& lopTinChi,
    Dangky dsKetQua[],
    int kichThuocToiDa,
    bool layCaDaHuy
);

void GiaiPhongDanhSachDangKy(PTRDK& dsDangKy);

#endif
