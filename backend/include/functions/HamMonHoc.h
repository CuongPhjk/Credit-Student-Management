#ifndef HAM_MON_HOC_H
#define HAM_MON_HOC_H

#include "../model/KhaiBao.h"

void SapXepMonHocTheoTen(Monhoc dsMonHoc[], int soLuong);

int TongSoTinChi(const Monhoc& monHoc);

void GiaiPhongCayMonHoc(treeMH& root);

treeMH TimMonHoc(treeMH root, const string& maMH);

bool KiemTraTrungMaMonHoc(treeMH root, const string& maMH);

bool MonHocDaMoLopTinChi(const DS_LTC& dsLTC, const string& maMH);

int DemMonHoc(treeMH root);

void ChuyenCayMonHocSangMang(
    treeMH root,
    Monhoc dsMonHoc[],
    int& soLuong
);
bool ThemMonHoc(treeMH& root, const Monhoc& monHoc, string& loi);

bool HieuChinhMonHoc(
    treeMH& root,
    const string& maMH,
    const Monhoc& duLieuMoi,
    string& loi
);

bool XoaMonHoc(
    treeMH& root,
    const DS_LTC& dsLTC,
    const string& maMH,
    string& loi
);


#endif
