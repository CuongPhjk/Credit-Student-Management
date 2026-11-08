#include "../KhaiBao.h"

#include <limits>



void ChuanHoaThongTinLopTinChi(Loptinchi& lopTinChi) {
    lopTinChi.MAMH = ChuanHoaMa(lopTinChi.MAMH);
    lopTinChi.NIENKHOA = XoaKhoangTrangDauCuoi(lopTinChi.NIENKHOA);
}

bool CungThongTinMoLop(
    Loptinchi lopTinChi,
    Loptinchi lopKhac
) {
    return lopTinChi.NIENKHOA == lopKhac.NIENKHOA
        && lopTinChi.HOCKY == lopKhac.HOCKY
        && lopTinChi.MAMH == lopKhac.MAMH
        && lopTinChi.NHOM == lopKhac.NHOM;
}

bool KiemTraTrungLopNoiBo(
    DS_LTC& dsLTC,
    Loptinchi lopTinChi,
    int maLopBoQua
) {
    for (int i = 0; i < dsLTC.n; ++i) {
        Loptinchi* lopHienTai = dsLTC.nodes[i];
        if (lopHienTai->MALOPTC != maLopBoQua
            && CungThongTinMoLop(*lopHienTai, lopTinChi)) {
            return true;
        }
    }
    return false;
}

int TimViTriLopTheoMaNoiBo(DS_LTC& dsLTC, int maLopTC) {
    for (int i = 0; i < dsLTC.n; ++i) {
        if (dsLTC.nodes[i]->MALOPTC == maLopTC) {
            return i;
        }
    }
    return -1;
}

int DemDangKyConHieuLuc(PTRDK danhSachDangKy) {
    int soLuong = 0;
    for (PTRDK node = danhSachDangKy; node != nullptr; node = node->next) {
        if (!node->dk.HUYDK) {
            ++soLuong;
        }
    }
    return soLuong;
}

bool ThayDoiThongTinDinhDanh(
    Loptinchi lopHienTai,
    Loptinchi duLieuMoi
) {
    return lopHienTai.MAMH != duLieuMoi.MAMH
        || lopHienTai.NIENKHOA != duLieuMoi.NIENKHOA
        || lopHienTai.HOCKY != duLieuMoi.HOCKY
        || lopHienTai.NHOM != duLieuMoi.NHOM;
}

Loptinchi* TimLopTinChiTheoMa(DS_LTC& dsLTC, int maLopTC) {
    int viTri = TimViTriLopTheoMaNoiBo(dsLTC, maLopTC);
    return viTri < 0 ? nullptr : dsLTC.nodes[viTri];
}

Loptinchi* TimLopTinChi(
    DS_LTC& dsLTC,
    string nienKhoa,
    int hocKy,
    string maMH,
    int nhom
) {
    string maDaChuanHoa = ChuanHoaMa(maMH);
    string nienKhoaDaChuanHoa = XoaKhoangTrangDauCuoi(nienKhoa);
    for (int i = 0; i < dsLTC.n; ++i) {
        Loptinchi* lop = dsLTC.nodes[i];
        if (lop->MAMH == maDaChuanHoa
            && lop->NIENKHOA == nienKhoaDaChuanHoa
            && lop->HOCKY == hocKy && lop->NHOM == nhom) {
            return lop;
        }
    }
    return nullptr;
}

bool ThemLopTinChi(
    DS_LTC& dsLTC,
    treeMH dsMonHoc,
    Loptinchi lopTinChi,
    string& loi
) {
    loi.clear();
    if (dsLTC.n >= MAXLTC) {
        loi = "Danh sách lớp tín chỉ đã đầy.";
        return false;
    }
    ChuanHoaThongTinLopTinChi(lopTinChi);
    if (TimMonHoc(dsMonHoc, lopTinChi.MAMH) == nullptr) {
        loi = "Mã môn học không tồn tại.";
        return false;
    }
    if (KiemTraTrungLopNoiBo(dsLTC, lopTinChi, -1)) {
        loi = "Lớp tín chỉ đã tồn tại trong cùng niên khóa, học kỳ và nhóm.";
        return false;
    }
    if (dsLTC.maTiepTheo <= 0
        || dsLTC.maTiepTheo == std::numeric_limits<int>::max()) {
        loi = "Không thể tạo thêm mã lớp tín chỉ.";
        return false;
    }
    lopTinChi.MALOPTC = dsLTC.maTiepTheo++;
    lopTinChi.HUYLOP = false;
    lopTinChi.dssvdk = nullptr;
    Loptinchi* lopMoi = new Loptinchi(lopTinChi);
    dsLTC.nodes[dsLTC.n] = lopMoi;
    ++dsLTC.n;
    return true;
}

bool HieuChinhLopTinChi(
    DS_LTC& dsLTC,
    treeMH dsMonHoc,
    int maLopTC,
    Loptinchi duLieuMoi,
    string& loi
) {
    loi.clear();
    int viTri = TimViTriLopTheoMaNoiBo(dsLTC, maLopTC);
    if (viTri < 0) {
        loi = "Không tìm thấy lớp tín chỉ.";
        return false;
    }
    Loptinchi daChuanHoa = duLieuMoi;
    ChuanHoaThongTinLopTinChi(daChuanHoa);
    if (TimMonHoc(dsMonHoc, daChuanHoa.MAMH) == nullptr) {
        loi = "Mã môn học không tồn tại.";
        return false;
    }
    if (KiemTraTrungLopNoiBo(dsLTC, daChuanHoa, maLopTC)) {
        loi = "Lớp tín chỉ đã tồn tại trong cùng niên khóa, học kỳ và nhóm.";
        return false;
    }
    Loptinchi& lopHienTai = *dsLTC.nodes[viTri];
    if (lopHienTai.dssvdk != nullptr
        && ThayDoiThongTinDinhDanh(lopHienTai, daChuanHoa)) {
        loi = "Không thể đổi môn học, niên khóa, học kỳ hoặc nhóm khi đã có đăng ký.";
        return false;
    }
    if (DemDangKyConHieuLuc(lopHienTai.dssvdk) > daChuanHoa.SOSVMAX) {
        loi = "Sĩ số tối đa mới nhỏ hơn số sinh viên đăng ký hiện tại.";
        return false;
    }
    lopHienTai.MAMH = daChuanHoa.MAMH;
    lopHienTai.NIENKHOA = daChuanHoa.NIENKHOA;
    lopHienTai.HOCKY = daChuanHoa.HOCKY;
    lopHienTai.NHOM = daChuanHoa.NHOM;
    lopHienTai.SOSVMIN = daChuanHoa.SOSVMIN;
    lopHienTai.SOSVMAX = daChuanHoa.SOSVMAX;
    return true;
}

bool XoaLopTinChi(DS_LTC& dsLTC, int maLopTC, string& loi) {
    loi.clear();
    int viTri = TimViTriLopTheoMaNoiBo(dsLTC, maLopTC);
    if (viTri < 0) {
        loi = "Không tìm thấy lớp tín chỉ.";
        return false;
    }
    if (dsLTC.nodes[viTri]->dssvdk != nullptr) {
        loi = "Không thể xóa lớp tín chỉ đã có dữ liệu đăng ký.";
        return false;
    }

    delete dsLTC.nodes[viTri];
    for (int i = viTri; i < dsLTC.n - 1; ++i) {
        dsLTC.nodes[i] = dsLTC.nodes[i + 1];
    }
    dsLTC.nodes[--dsLTC.n] = nullptr;
    return true;
}

int DemSoSinhVienDangKy(Loptinchi lopTinChi) {
    return DemDangKyConHieuLuc(lopTinChi.dssvdk);
}

int TinhSoChoTrong(Loptinchi lopTinChi) {
    int soChoTrong = lopTinChi.SOSVMAX
        - DemSoSinhVienDangKy(lopTinChi);
    return soChoTrong > 0 ? soChoTrong : 0;
}

bool HuyLopTinChi(DS_LTC& dsLTC, int maLopTC, string& loi) {
    loi.clear();
    Loptinchi* lop = TimLopTinChiTheoMa(dsLTC, maLopTC);
    if (lop == nullptr) {
        loi = "Không tìm thấy lớp tín chỉ.";
        return false;
    }
    if (lop->HUYLOP) {
        loi = "Lớp tín chỉ đã bị hủy trước đó.";
        return false;
    }
    lop->HUYLOP = true;
    return true;
}

Loptinchi** LayDanhSachLopTinChi(DS_LTC& dsLTC, int& soLuong) {
    soLuong = dsLTC.n;
    return soLuong == 0 ? nullptr : dsLTC.nodes;
}
