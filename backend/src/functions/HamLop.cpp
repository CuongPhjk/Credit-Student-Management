#include "../KhaiBao.h"


int TimViTriLop(DS_LOP& dsLop, string maLop) {
     string maCanTim = ChuanHoaMa(maLop);

    for (int i = 0; i < dsLop.n; ++i) {
        if (dsLop.nodes[i].MALOP == maCanTim) {
            return i;
        }
    }
    return -1;
}

Lop* TimLop(DS_LOP& dsLop, string maLop) {
    int viTri = TimViTriLop(dsLop, maLop);
    return viTri < 0 ? nullptr : &dsLop.nodes[viTri];
}

bool KiemTraTrungMaLop(DS_LOP& dsLop, string maLop) {
    return TimViTriLop(dsLop, maLop) >= 0;
}

bool ThemLop(DS_LOP& dsLop, Lop lop, string& loi) {
    loi.clear();

    if (dsLop.n >= MAXLOP) {
        loi = "Danh sách lớp đã đầy.";
        return false;
    }

    Lop daChuanHoa = lop;
    daChuanHoa.MALOP = ChuanHoaMa(lop.MALOP);
    daChuanHoa.TENLOP = XoaKhoangTrangThua(lop.TENLOP);
    daChuanHoa.dssv = nullptr;
    daChuanHoa.soSinhVien = 0;

    if (KiemTraTrungMaLop(dsLop, daChuanHoa.MALOP)) {
        loi = "Mã lớp đã tồn tại.";
        return false;
    }

    dsLop.nodes[dsLop.n] = daChuanHoa;
    ++dsLop.n;
    ++dsLop.phienBan;

    return true;
}

bool HieuChinhLop(
    DS_LOP& dsLop,
    string maLop,
    string tenLopMoi,
    string& loi
) {
    loi.clear();
    Lop* lop = TimLop(dsLop, maLop);
    if (lop == nullptr) {
        loi = "Không tìm thấy lớp.";
        return false;
    }
    string tenDaChuanHoa = XoaKhoangTrangThua(tenLopMoi);
    lop->TENLOP = tenDaChuanHoa;
    return true;
}

bool XoaLop(DS_LOP& dsLop, string maLop, string& loi) {
    loi.clear();
    int viTri = TimViTriLop(dsLop, maLop);
    if (viTri < 0) {
        loi = "Không tìm thấy lớp.";
        return false;
    }
    if (dsLop.nodes[viTri].dssv != nullptr) {
        loi = "Không thể xóa lớp đang có sinh viên.";
        return false;
    }
    for (int i = viTri; i < dsLop.n - 1; ++i) {
        dsLop.nodes[i] = dsLop.nodes[i + 1];
    }
    dsLop.nodes[--dsLop.n] = Lop{};
    ++dsLop.phienBan;
    return true;
}

Lop* LayDanhSachLop(DS_LOP& dsLop, int& soLuong) {
    soLuong = dsLop.n;
    if (soLuong == 0) return nullptr;
    Lop* ketQua = new Lop[soLuong];
    for (int i = 0; i < soLuong; ++i) ketQua[i] = dsLop.nodes[i];
    return ketQua;
}

