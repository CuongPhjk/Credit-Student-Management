#ifndef HAM_SINH_VIEN_H
#define HAM_SINH_VIEN_H

#include "../model/KhaiBao.h"

PTRSV TimSinhVienTrongLop(PTRSV dsSV, const string& maSV);

PTRSV TimSinhVienToanTruong(
    DS_LOP& dsLop,
    const string& maSV,
    int& viTriLop
);

bool KiemTraTrungMaSinhVien(const DS_LOP& dsLop, const string& maSV);

int SoSanhSinhVienTheoTen(const Sinhvien& sv1, const Sinhvien& sv2);

void ChenSinhVienTheoTen(PTRSV& dsSV, const Sinhvien& sinhVien);

bool ThemSinhVien(
    DS_LOP& dsLop,
    const string& maLop,
    const Sinhvien& sinhVien,
    string& loi
);

bool HieuChinhSinhVien(
    DS_LOP& dsLop,
    const string& maSV,
    const Sinhvien& duLieuMoi,
    string& loi
);

bool SinhVienDaDangKy(const DS_LTC& dsLTC, const string& maSV);

bool XoaSinhVien(
    DS_LOP& dsLop,
    const DS_LTC& dsLTC,
    const string& maSV,
    string& loi
);

int DemSinhVien(PTRSV dsSV);

void SaoChepSinhVienSangMang(
    PTRSV dsSV,
    Sinhvien dsKetQua[],
    int& soLuong
);

void SapXepSinhVienTheoMa(Sinhvien dsSinhVien[], int soLuong);

void GiaiPhongDanhSachSinhVien(PTRSV& dsSV);

#endif
