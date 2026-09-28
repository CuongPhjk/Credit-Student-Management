#ifndef XU_LY_CHUOI_H
#define XU_LY_CHUOI_H

#include <cstddef>
#include <string>

using std::string;

string XoaKhoangTrangDauCuoi(const string& chuoi);

string XoaKhoangTrangThua(const string& chuoi);

string ChuyenThanhChuHoa(const string& chuoi);

string ChuyenThanhChuThuong(const string& chuoi);

string ChuanHoaMa(const string& ma);

string ChuanHoaHoTen(const string& hoTen);

bool ChuyenSangSoNguyen(const string& chuoi, int& ketQua);

bool TachChuoi(
    const string& chuoi,
    char kyTuPhanCach,
    string dsKetQua[],
    int soPhanTu
);

bool LaChuoiUtf8HopLe(const string& chuoi);

std::size_t DemSoKyTuUtf8(const string& chuoi);

int SoSanhKhongPhanBietHoaThuong(
    const string& chuoi1,
    const string& chuoi2
);

#endif
