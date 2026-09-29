#include "../../include/functions/HamLop.h"

#include "../../include/utils/KiemTraDuLieu.h"
#include "../../include/utils/XuLyChuoi.h"

int TimViTriLop(const DS_LOP& dsLop, const string& maLop) {
    const string maDaChuanHoa = ChuanHoaMa(maLop);

    int trai = 0;
    int phai = dsLop.n - 1;

    while (trai <= phai) {
        int giua = trai + (phai - trai) / 2;

        if (dsLop.nodes[giua].MALOP == maDaChuanHoa) {
            return giua;
        }

        if (dsLop.nodes[giua].MALOP < maDaChuanHoa) {
            trai = giua + 1;
        } else {
            phai = giua - 1;
        }
    }

    return -1;
}

Lop* TimLop(DS_LOP& dsLop, const string& maLop) {
    const int viTri = TimViTriLop(dsLop, maLop);
    return viTri < 0 ? nullptr : &dsLop.nodes[viTri];
}

bool KiemTraTrungMaLop(const DS_LOP& dsLop, const string& maLop) {
    return TimViTriLop(dsLop, maLop) >= 0;
}

bool ThemLop(DS_LOP& dsLop, const Lop& lop, string& loi) {
    loi.clear();
    if (dsLop.n >= MAXLOP) {
        loi = "Danh sach lop da day.";
        return false;
    }
    Lop daChuanHoa = lop;
    daChuanHoa.MALOP = ChuanHoaMa(lop.MALOP);
    daChuanHoa.TENLOP = XoaKhoangTrangThua(lop.TENLOP);
    daChuanHoa.dssv = nullptr;
    if (!MaHopLe(daChuanHoa.MALOP, 15)) {
        loi = "Ma lop khong hop le, toi da 15 ky tu.";
        return false;
    }
    if (!TenLopHopLe(daChuanHoa.TENLOP, loi)) {
        return false;
    }
    if (KiemTraTrungMaLop(dsLop, daChuanHoa.MALOP)) {
        loi = "Ma lop da ton tai.";
        return false;
    }

    int viTriChen = dsLop.n;
    while (viTriChen > 0
           && dsLop.nodes[viTriChen - 1].MALOP > daChuanHoa.MALOP) {
        dsLop.nodes[viTriChen] = dsLop.nodes[viTriChen - 1];
        --viTriChen;
    }
    dsLop.nodes[viTriChen] = daChuanHoa;
    ++dsLop.n;
    return true;
}

bool HieuChinhLop(
    DS_LOP& dsLop,
    const string& maLop,
    const string& tenLopMoi,
    string& loi
) {
    loi.clear();
    Lop* lop = TimLop(dsLop, maLop);
    if (lop == nullptr) {
        loi = "Khong tim thay lop.";
        return false;
    }
    const string tenDaChuanHoa = XoaKhoangTrangThua(tenLopMoi);
    if (!TenLopHopLe(tenDaChuanHoa, loi)) {
        return false;
    }
    lop->TENLOP = tenDaChuanHoa;
    return true;
}

bool XoaLop(DS_LOP& dsLop, const string& maLop, string& loi) {
    loi.clear();
    const int viTri = TimViTriLop(dsLop, maLop);
    if (viTri < 0) {
        loi = "Khong tim thay lop.";
        return false;
    }
    if (dsLop.nodes[viTri].dssv != nullptr) {
        loi = "Khong the xoa lop dang co sinh vien.";
        return false;
    }
    for (int i = viTri; i < dsLop.n - 1; ++i) {
        dsLop.nodes[i] = dsLop.nodes[i + 1];
    }
    dsLop.nodes[--dsLop.n] = Lop{};
    return true;
}


