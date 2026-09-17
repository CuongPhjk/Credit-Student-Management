#ifndef HAM_DIEM_H
#define HAM_DIEM_H

#include "../model/KhaiBao.h"

bool KiemTraDiemHopLe(float diem);

bool SinhVienDuocNhapDiem(
    const Loptinchi& lopTinChi,
    const string& maSV
);

bool NhapDiem(
    DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom,
    const string& maSV,
    float diem,
    string& loi
);

bool HieuChinhDiem(
    DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom,
    const string& maSV,
    float diemMoi,
    string& loi
);

#endif
