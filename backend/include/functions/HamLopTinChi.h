#ifndef HAM_LOP_TIN_CHI_H
#define HAM_LOP_TIN_CHI_H

#include "../model/KhaiBao.h"

int TimViTriLopTinChiTheoMa(const DS_LTC& dsLTC, int maLopTC);

Loptinchi* TimLopTinChiTheoMa(DS_LTC& dsLTC, int maLopTC);
const Loptinchi* TimLopTinChiTheoMa(const DS_LTC& dsLTC, int maLopTC);

Loptinchi* TimLopTinChi(
    DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom
);

const Loptinchi* TimLopTinChi(
    const DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom
);

bool KiemTraTrungLopTinChi(
    const DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom,
    int maLopBoQua = -1
);

int TimMaLopTinChiLonNhat(const DS_LTC& dsLTC);
int TaoMaLopTinChi(const DS_LTC& dsLTC);

bool ThemLopTinChi(
    DS_LTC& dsLTC,
    treeMH dsMonHoc,
    Loptinchi lopTinChi,
    string& loi
);

bool HieuChinhLopTinChi(
    DS_LTC& dsLTC,
    treeMH dsMonHoc,
    int maLopTC,
    const Loptinchi& duLieuMoi,
    string& loi
);

bool XoaLopTinChi(DS_LTC& dsLTC, int maLopTC, string& loi);

int DemSoSinhVienDangKy(const Loptinchi& lopTinChi);
int TinhSoChoTrong(const Loptinchi& lopTinChi);

int LocLopTinChiTheoNienKhoaHocKy(
    DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    Loptinchi* dsKetQua[],
    int kichThuocToiDa
);

int LocLopTinChiKhongDuSiSo(
    DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    Loptinchi* dsKetQua[],
    int kichThuocToiDa
);

bool HuyLopTinChi(DS_LTC& dsLTC, int maLopTC, string& loi);

#endif
