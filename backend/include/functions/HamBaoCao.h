#ifndef HAM_BAO_CAO_H
#define HAM_BAO_CAO_H

#include "../model/KhaiBao.h"

void InDanhSachSinhVienDangKy(
    const DS_LTC& dsLTC,
    const DS_LOP& dsLop,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom
);

void InDanhSachSinhVienCuaLop(
    const DS_LOP& dsLop,
    const string& maLop
);

void InDanhSachMonHoc(treeMH dsMonHoc);

void InBangDiemLopTinChi(
    const DS_LTC& dsLTC,
    const DS_LOP& dsLop,
    treeMH dsMonHoc,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom
);

bool TimDiemCaoNhatCuaMon(
    const DS_LTC& dsLTC,
    const string& maSV,
    const string& maMH,
    float& diemCaoNhat
);

float TinhDiemTrungBinhTheoTinChi(
    const DS_LTC& dsLTC,
    treeMH dsMonHoc,
    const string& maSV,
    bool& coDiem
);

void InDiemTrungBinhKhoaHoc(
    const DS_LOP& dsLop,
    const DS_LTC& dsLTC,
    treeMH dsMonHoc,
    const string& maLop
);

int LayDanhSachMaMonDaHoc(
    const DS_LTC& dsLTC,
    PTRSV dsSinhVien,
    string dsMaMH[],
    int kichThuocToiDa
);

void SapXepMaMonHoc(string dsMaMH[], int soLuong);

void InBangDiemTongKet(
    const DS_LOP& dsLop,
    const DS_LTC& dsLTC,
    const string& maLop
);

#endif
