#ifndef XU_LY_TEP_H
#define XU_LY_TEP_H

#include "../model/KhaiBao.h"

bool DocDanhSachMonHoc(
    const string& tenFile,
    treeMH& dsMonHoc,
    string& loi
);

bool GhiDanhSachMonHoc(
    const string& tenFile,
    treeMH dsMonHoc,
    string& loi
);

bool DocDanhSachLop(
    const string& tenFile,
    DS_LOP& dsLop,
    string& loi
);

bool GhiDanhSachLop(
    const string& tenFile,
    const DS_LOP& dsLop,
    string& loi
);

bool DocDanhSachSinhVien(
    const string& tenFile,
    DS_LOP& dsLop,
    string& loi
);

bool GhiDanhSachSinhVien(
    const string& tenFile,
    const DS_LOP& dsLop,
    string& loi
);

bool DocDanhSachLopTinChi(
    const string& tenFile,
    DS_LTC& dsLTC,
    string& loi
);

bool GhiDanhSachLopTinChi(
    const string& tenFile,
    const DS_LTC& dsLTC,
    string& loi
);

bool DocDanhSachDangKy(
    const string& tenFile,
    DS_LTC& dsLTC,
    string& loi
);

bool GhiDanhSachDangKy(
    const string& tenFile,
    const DS_LTC& dsLTC,
    string& loi
);

bool DocTatCaDuLieu(
    treeMH& dsMonHoc,
    DS_LOP& dsLop,
    DS_LTC& dsLTC,
    string& loi
);

bool GhiTatCaDuLieu(
    treeMH dsMonHoc,
    const DS_LOP& dsLop,
    const DS_LTC& dsLTC,
    string& loi
);

#endif
