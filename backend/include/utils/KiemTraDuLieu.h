#ifndef KIEM_TRA_DU_LIEU_H
#define KIEM_TRA_DU_LIEU_H

#include <string>

using std::string;

bool LaChuoiRong(const string& chuoi);

bool MaHopLe(const string& ma, int doDaiToiDa);

bool MaSinhVienHopLe(const string& maSV);

bool SoDienThoaiHopLe(const string& soDienThoai);

bool PhaiHopLe(const string& phai);

bool NienKhoaHopLe(const string& nienKhoa);

bool HocKyHopLe(int hocKy);

bool NhomHopLe(int nhom);

bool SoTinChiHopLe(int stcLyThuyet, int stcThucHanh);

bool SiSoHopLe(int soSVMin, int soSVMax);

bool DiemHopLe(float diem);

#endif
