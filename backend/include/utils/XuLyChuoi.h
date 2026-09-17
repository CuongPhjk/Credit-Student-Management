#ifndef XU_LY_CHUOI_H
#define XU_LY_CHUOI_H

#include <string>

using std::string;

string XoaKhoangTrangDauCuoi(const string& chuoi);

string XoaKhoangTrangThua(const string& chuoi);

string ChuyenThanhChuHoa(const string& chuoi);

string ChuyenThanhChuThuong(const string& chuoi);

string ChuanHoaMa(const string& ma);

string ChuanHoaHoTen(const string& hoTen);

int SoSanhKhongPhanBietHoaThuong(
    const string& chuoi1,
    const string& chuoi2
);

#endif
