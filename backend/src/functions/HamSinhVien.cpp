#include "../../include/functions/HamSinhVien.h"

#include "../../include/functions/HamLop.h"
#include "../../include/utils/KiemTraDuLieu.h"
#include "../../include/utils/XuLyChuoi.h"

namespace {

Sinhvien ChuanHoaSinhVien(const Sinhvien& sinhVien) {
    Sinhvien ketQua = sinhVien;
    ketQua.MASV = ChuanHoaMa(sinhVien.MASV);
    ketQua.HO = ChuanHoaHoTen(sinhVien.HO);
    ketQua.TEN = ChuanHoaHoTen(sinhVien.TEN);
    ketQua.PHAI = ChuanHoaHoTen(sinhVien.PHAI);
    ketQua.SODT = XoaKhoangTrangDauCuoi(sinhVien.SODT);
    return ketQua;
}

bool KiemTraThongTinSinhVien(const Sinhvien& sinhVien, string& loi) {
    if (!MaSinhVienHopLe(sinhVien.MASV)) {
        loi = "Ma sinh vien khong hop le, toi da 15 ky tu.";
        return false;
    }
    if (sinhVien.HO.empty() || sinhVien.TEN.empty()
        || DemSoKyTuUtf8(sinhVien.HO) > 40
        || DemSoKyTuUtf8(sinhVien.TEN) > 15
        || sinhVien.HO.find('|') != string::npos
        || sinhVien.TEN.find('|') != string::npos) {
        loi = "Ho hoac ten sinh vien khong hop le.";
        return false;
    }
    if (!PhaiHopLe(sinhVien.PHAI)) {
        loi = u8"Phai chi duoc la Nam hoac Nữ.";
        return false;
    }
    if (!SoDienThoaiHopLe(sinhVien.SODT)) {
        loi = "So dien thoai phai gom tu 9 den 11 chu so.";
        return false;
    }
    return true;
}

void ChenNodeSinhVienTheoTen(PTRSV& dsSV, PTRSV nodeMoi) {
    if (dsSV == nullptr
        || SoSanhSinhVienTheoTen(nodeMoi->sv, dsSV->sv) < 0) {
        nodeMoi->next = dsSV;
        dsSV = nodeMoi;
        return;
    }
    PTRSV nodeTruoc = dsSV;
    while (nodeTruoc->next != nullptr
           && SoSanhSinhVienTheoTen(
               nodeTruoc->next->sv, nodeMoi->sv
           ) <= 0) {
        nodeTruoc = nodeTruoc->next;
    }
    nodeMoi->next = nodeTruoc->next;
    nodeTruoc->next = nodeMoi;
}

}  // namespace

PTRSV TimSinhVienTrongLop(PTRSV dsSV, const string& maSV) {
    const string maDaChuanHoa = ChuanHoaMa(maSV);
    for (PTRSV node = dsSV; node != nullptr; node = node->next) {
        if (node->sv.MASV == maDaChuanHoa) {
            return node;
        }
    }
    return nullptr;
}

PTRSV TimSinhVienToanTruong(
    DS_LOP& dsLop,
    const string& maSV,
    int& viTriLop
) {
    viTriLop = -1;
    for (int i = 0; i < dsLop.n; ++i) {
        PTRSV ketQua = TimSinhVienTrongLop(dsLop.nodes[i].dssv, maSV);
        if (ketQua != nullptr) {
            viTriLop = i;
            return ketQua;
        }
    }
    return nullptr;
}

bool KiemTraTrungMaSinhVien(const DS_LOP& dsLop, const string& maSV) {
    const string maDaChuanHoa = ChuanHoaMa(maSV);
    for (int i = 0; i < dsLop.n; ++i) {
        for (PTRSV node = dsLop.nodes[i].dssv;
             node != nullptr;
             node = node->next) {
            if (node->sv.MASV == maDaChuanHoa) {
                return true;
            }
        }
    }
    return false;
}

int SoSanhSinhVienTheoTen(const Sinhvien& sv1, const Sinhvien& sv2) {
    int ketQua = SoSanhKhongPhanBietHoaThuong(sv1.TEN, sv2.TEN);
    if (ketQua != 0) {
        return ketQua;
    }
    ketQua = SoSanhKhongPhanBietHoaThuong(sv1.HO, sv2.HO);
    if (ketQua != 0) {
        return ketQua;
    }
    return SoSanhKhongPhanBietHoaThuong(sv1.MASV, sv2.MASV);
}

void ChenSinhVienTheoTen(PTRSV& dsSV, const Sinhvien& sinhVien) {
    PTRSV nodeMoi = new nodeSV{sinhVien, nullptr};
    ChenNodeSinhVienTheoTen(dsSV, nodeMoi);
}

bool ThemSinhVien(
    DS_LOP& dsLop,
    const string& maLop,
    const Sinhvien& sinhVien,
    string& loi
) {
    loi.clear();
    Lop* lop = TimLop(dsLop, maLop);
    if (lop == nullptr) {
        loi = "Ma lop khong ton tai.";
        return false;
    }
    const Sinhvien daChuanHoa = ChuanHoaSinhVien(sinhVien);
    if (!KiemTraThongTinSinhVien(daChuanHoa, loi)) {
        return false;
    }
    if (KiemTraTrungMaSinhVien(dsLop, daChuanHoa.MASV)) {
        loi = "Ma sinh vien da ton tai trong toan truong.";
        return false;
    }
    ChenSinhVienTheoTen(lop->dssv, daChuanHoa);
    return true;
}

bool HieuChinhSinhVien(
    DS_LOP& dsLop,
    const string& maSV,
    const Sinhvien& duLieuMoi,
    string& loi
) {
    loi.clear();
    int viTriLop = -1;
    PTRSV nodeCanSua = TimSinhVienToanTruong(dsLop, maSV, viTriLop);
    if (nodeCanSua == nullptr) {
        loi = "Khong tim thay sinh vien.";
        return false;
    }
    Sinhvien daChuanHoa = ChuanHoaSinhVien(duLieuMoi);
    daChuanHoa.MASV = nodeCanSua->sv.MASV;
    if (!KiemTraThongTinSinhVien(daChuanHoa, loi)) {
        return false;
    }

    PTRSV* lienKet = &dsLop.nodes[viTriLop].dssv;
    while (*lienKet != nodeCanSua) {
        lienKet = &((*lienKet)->next);
    }
    *lienKet = nodeCanSua->next;
    nodeCanSua->sv = daChuanHoa;
    nodeCanSua->next = nullptr;
    ChenNodeSinhVienTheoTen(dsLop.nodes[viTriLop].dssv, nodeCanSua);
    return true;
}

bool SinhVienDaDangKy(const DS_LTC& dsLTC, const string& maSV) {
    const string maDaChuanHoa = ChuanHoaMa(maSV);
    for (int i = 0; i < dsLTC.n; ++i) {
        if (dsLTC.nodes[i] == nullptr) {
            continue;
        }
        for (PTRDK node = dsLTC.nodes[i]->dssvdk;
             node != nullptr;
             node = node->next) {
            if (node->dk.MASV == maDaChuanHoa) {
                return true;
            }
        }
    }
    return false;
}

bool XoaSinhVien(
    DS_LOP& dsLop,
    const DS_LTC& dsLTC,
    const string& maSV,
    string& loi
) {
    loi.clear();
    int viTriLop = -1;
    PTRSV nodeCanXoa = TimSinhVienToanTruong(dsLop, maSV, viTriLop);
    if (nodeCanXoa == nullptr) {
        loi = "Khong tim thay sinh vien.";
        return false;
    }
    if (SinhVienDaDangKy(dsLTC, nodeCanXoa->sv.MASV)) {
        loi = "Khong the xoa sinh vien da co du lieu dang ky.";
        return false;
    }
    PTRSV* lienKet = &dsLop.nodes[viTriLop].dssv;
    while (*lienKet != nodeCanXoa) {
        lienKet = &((*lienKet)->next);
    }
    *lienKet = nodeCanXoa->next;
    delete nodeCanXoa;
    return true;
}

int DemSinhVien(PTRSV dsSV) {
    int soLuong = 0;
    for (PTRSV node = dsSV; node != nullptr; node = node->next) {
        ++soLuong;
    }
    return soLuong;
}

void GiaiPhongDanhSachSinhVien(PTRSV& dsSV) {
    while (dsSV != nullptr) {
        PTRSV nodeCanXoa = dsSV;
        dsSV = dsSV->next;
        delete nodeCanXoa;
    }
}
