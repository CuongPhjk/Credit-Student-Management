#include "../KhaiBao.h"
#include "../utils/MergeSort.h"

Sinhvien ChuanHoaSinhVien(Sinhvien sinhVien) {
    Sinhvien ketQua = sinhVien;
    ketQua.MASV = ChuanHoaMa(sinhVien.MASV);
    ketQua.HO = ChuanHoaHoTen(sinhVien.HO);
    ketQua.TEN = ChuanHoaHoTen(sinhVien.TEN);
    ketQua.PHAI = ChuanHoaHoTen(sinhVien.PHAI);
    ketQua.SODT = XoaKhoangTrangDauCuoi(sinhVien.SODT);
    return ketQua;
}

void ChenDau(PTRSV& dsSV, PTRSV p){
    if (p==nullptr) return;
    p->next = dsSV;
    dsSV = p;
}
void ChenSau(PTRSV p, PTRSV q) {
    if (p == nullptr || q == nullptr) return;
    q->next = p->next;
    p->next = q;
}
void ChenNodeSinhVienTheoTen(PTRSV& dsSV, PTRSV nodeMoi) {
    if (dsSV == nullptr
        || SoSanhSinhVienTheoTen(nodeMoi->sv, dsSV->sv) < 0) {
        ChenDau(dsSV,nodeMoi);
        return;
    }
    PTRSV nodeTruoc = dsSV;
    while (nodeTruoc->next != nullptr
           && SoSanhSinhVienTheoTen(
               nodeTruoc->next->sv, nodeMoi->sv
           ) <= 0) {
        nodeTruoc = nodeTruoc->next;
    }
    ChenSau(nodeTruoc,nodeMoi);
}

void GoNodeSinhVien(PTRSV& dsSV, PTRSV q) {
    if (dsSV == q) {
        dsSV = q->next;
    } else {
        PTRSV p = dsSV;
        while (p->next != q) {
            p = p->next;
        }
        p->next = q->next;
    }
    q->next = nullptr;
}

PTRSV TimSinhVienTrongLop(PTRSV dsSV, string maSV) {
    string maDaChuanHoa = ChuanHoaMa(maSV);
    for (PTRSV node = dsSV; node != nullptr; node = node->next) {
        if (node->sv.MASV == maDaChuanHoa) {
            return node;
        }
    }
    return nullptr;
}

PTRSV TimSinhVienToanTruong(
    DS_LOP& dsLop,
    string maSV,
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

int SoSanhSinhVienTheoTen(Sinhvien sv1, Sinhvien sv2) {
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

void ChenSinhVienTheoTen(Lop& lop, Sinhvien sinhVien) {
    PTRSV nodeMoi = new nodeSV{sinhVien, nullptr};
    ChenNodeSinhVienTheoTen(lop.dssv, nodeMoi);
    ++lop.soSinhVien;
}

bool ThemSinhVien(
    DS_LOP& dsLop,
    string maLop,
    Sinhvien sinhVien,
    string& loi
) {
    loi.clear();
    Lop* lop = TimLop(dsLop, maLop);
    if (lop == nullptr) {
        loi = "Mã lớp không tồn tại.";
        return false;
    }
    Sinhvien sv = ChuanHoaSinhVien(sinhVien);
    int viTriLop;
    if (TimSinhVienToanTruong(dsLop, sv.MASV, viTriLop) != nullptr) {
        loi = "Mã sinh viên đã tồn tại trong toàn trường.";
        return false;
    }
    ChenSinhVienTheoTen(*lop, sv);
    ++dsLop.phienBan;
    return true;
}

bool HieuChinhSinhVien(
    DS_LOP& dsLop,
    string maSV,
    Sinhvien duLieuMoi,
    string& loi
) {
    loi.clear();
    int viTriLop;
    PTRSV nodeCanSua = TimSinhVienToanTruong(dsLop, maSV, viTriLop); 
    if (nodeCanSua == nullptr) {
        loi = "Không tìm thấy sinh viên.";
        return false;
    }
    Sinhvien daChuanHoa = ChuanHoaSinhVien(duLieuMoi);
    daChuanHoa.MASV = nodeCanSua->sv.MASV;
    if (SoSanhSinhVienTheoTen(nodeCanSua->sv, daChuanHoa) == 0) {
        nodeCanSua->sv = daChuanHoa;
        return true;
    }

    PTRSV& dau = dsLop.nodes[viTriLop].dssv;
    GoNodeSinhVien(dau, nodeCanSua);
    nodeCanSua->sv = daChuanHoa;
    ChenNodeSinhVienTheoTen(dau, nodeCanSua);
    return true;
}

bool SinhVienDaDangKy(DS_LTC& dsLTC, string maSV) {
    string maDaChuanHoa = ChuanHoaMa(maSV);
    for (int i = 0; i < dsLTC.n; ++i) {
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
    DS_LTC& dsLTC,
    string maSV,
    string& loi
) {
    loi.clear();
    int viTriLop;
    PTRSV nodeCanXoa = TimSinhVienToanTruong(dsLop, maSV, viTriLop);
    if (nodeCanXoa == nullptr) {
        loi = "Không tìm thấy sinh viên.";
        return false;
    }
    if (SinhVienDaDangKy(dsLTC, nodeCanXoa->sv.MASV)) {
        loi = "Không thể xóa sinh viên đã có dữ liệu đăng ký.";
        return false;
    }
    PTRSV& dau = dsLop.nodes[viTriLop].dssv;
    GoNodeSinhVien(dau,nodeCanXoa);
    delete nodeCanXoa;
    --dsLop.nodes[viTriLop].soSinhVien;
    ++dsLop.phienBan;
    return true;
}


PTRSV* LayDanhSachSinhVien(Lop& lop, int& soLuong) {
    soLuong = lop.soSinhVien;
    if (soLuong == 0) return nullptr;
    PTRSV* ketQua = new PTRSV[soLuong];
    int i = 0;
    for (PTRSV node = lop.dssv; node != nullptr; node = node->next)
        ketQua[i++] = node;
    return ketQua;
}

bool SinhVienDungTruoc(PTRSV a, PTRSV b) {
    return a->sv.MASV < b->sv.MASV;
}

void SapXepConTroSinhVienTheoMa(PTRSV danhSach[], int soLuong) {
    MergeSort(danhSach, soLuong, SinhVienDungTruoc);
}
