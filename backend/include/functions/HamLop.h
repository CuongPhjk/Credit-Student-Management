#ifndef HAM_LOP_H
#define HAM_LOP_H

#include "../model/KhaiBao.h"

int TimViTriLop(const DS_LOP& dsLop, const string& maLop);

Lop* TimLop(DS_LOP& dsLop, const string& maLop);


bool KiemTraTrungMaLop(const DS_LOP& dsLop, const string& maLop);

bool ThemLop(DS_LOP& dsLop, const Lop& lop, string& loi);

bool HieuChinhLop(
    DS_LOP& dsLop,
    const string& maLop,
    const string& tenLopMoi,
    string& loi
);

bool XoaLop(DS_LOP& dsLop, const string& maLop, string& loi);


#endif
