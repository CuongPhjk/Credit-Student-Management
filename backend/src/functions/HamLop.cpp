#include "../../include/functions/HamLop.h"

#include "../../include/utils/KiemTraDuLieu.h"
#include "../../include/utils/XuLyChuoi.h"

int TimViTriLop(const DS_LOP& dsLop, const string& maLop) {
    const string maDaChuanHoa = ChuanHoaMa(maLop);
    for (int i = 0; i < dsLop.n; ++i) {
        if (dsLop.nodes[i].MALOP == maDaChuanHoa) {
            return i;
        }
    }
    return -1;
}

Lop* TimLop(DS_LOP& dsLop, const string& maLop) {
    const int viTri = TimViTriLop(dsLop, maLop);
    return viTri < 0 ? nullptr : &dsLop.nodes[viTri];
}

const Lop* TimLop(const DS_LOP& dsLop, const string& maLop) {
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
    if (daChuanHoa.TENLOP.empty()
        || DemSoKyTuUtf8(daChuanHoa.TENLOP) > 50
        || daChuanHoa.TENLOP.find('|') != string::npos) {
        loi = "Ten lop khong hop le, toi da 50 ky tu va khong chua |.";
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
    if (tenDaChuanHoa.empty()
        || DemSoKyTuUtf8(tenDaChuanHoa) > 50
        || tenDaChuanHoa.find('|') != string::npos) {
        loi = "Ten lop khong hop le, toi da 50 ky tu va khong chua |.";
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

bool LopCoSinhVien(const DS_LOP& dsLop, const string& maLop) {
    const Lop* lop = TimLop(dsLop, maLop);
    return lop != nullptr && lop->dssv != nullptr;
}
