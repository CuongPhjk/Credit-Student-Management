#include "../../include/functions/HamLopTinChi.h"

#include <limits>

#include "../../include/functions/HamMonHoc.h"
#include "../../include/utils/KiemTraDuLieu.h"
#include "../../include/utils/XuLyChuoi.h"


void ChuanHoaThongTinLopTinChi(Loptinchi& lopTinChi) {
    lopTinChi.MAMH = ChuanHoaMa(lopTinChi.MAMH);
    lopTinChi.NIENKHOA = XoaKhoangTrangDauCuoi(lopTinChi.NIENKHOA);
}

bool KiemTraThongTinLopTinChi(
    treeMH dsMonHoc,
    const Loptinchi& lopTinChi,
    string& loi
) {
    if (TimMonHoc(dsMonHoc, lopTinChi.MAMH) == nullptr) {
        loi = "Ma mon hoc khong ton tai.";
        return false;
    }
    if (!NienKhoaHopLe(lopTinChi.NIENKHOA)) {
        loi = "Nien khoa phai co dang YYYY-YYYY va hai nam lien tiep.";
        return false;
    }
    if (!NienKhoaKhongCuHonHienTai(lopTinChi.NIENKHOA)) {
        loi = "Nien khoa khong duoc cu hon nien khoa hien tai "
            + NienKhoaHienTai() + ".";
        return false;
    }
    if (!HocKyHopLe(lopTinChi.HOCKY)) {
        loi = "Hoc ky chi duoc nhan gia tri tu 1 den 3.";
        return false;
    }
    if (!NhomHopLe(lopTinChi.NHOM)) {
        loi = "Nhom lop tin chi phai lon hon 0.";
        return false;
    }
    if (!SiSoHopLe(lopTinChi.SOSVMIN, lopTinChi.SOSVMAX)) {
        loi = "Si so phai thoa man 0 < so sinh vien toi thieu <= toi da.";
        return false;
    }
    return true;
}

bool CungThongTinMoLop(
    const Loptinchi& lopTinChi,
    const Loptinchi& lopKhac
) {
    return lopTinChi.NIENKHOA == lopKhac.NIENKHOA
        && lopTinChi.HOCKY == lopKhac.HOCKY
        && lopTinChi.MAMH == lopKhac.MAMH
        && lopTinChi.NHOM == lopKhac.NHOM;
}

bool KiemTraTrungLopNoiBo(
    const DS_LTC& dsLTC,
    const Loptinchi& lopTinChi,
    int maLopBoQua
) {
    for (int i = 0; i < dsLTC.n; ++i) {
        const Loptinchi* lopHienTai = dsLTC.nodes[i];
        if (lopHienTai == nullptr) {
            continue;
        }
        if (lopHienTai->MALOPTC != maLopBoQua
            && CungThongTinMoLop(*lopHienTai, lopTinChi)) {
            return true;
        }
    }
    return false;
}

int TimViTriLopTheoMaNoiBo(const DS_LTC& dsLTC, int maLopTC) {
    for (int i = 0; i < dsLTC.n; ++i) {
        if (dsLTC.nodes[i] != nullptr
            && dsLTC.nodes[i]->MALOPTC == maLopTC) {
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
    const Loptinchi& lopHienTai,
    const Loptinchi& duLieuMoi
) {
    return lopHienTai.MAMH != duLieuMoi.MAMH
        || lopHienTai.NIENKHOA != duLieuMoi.NIENKHOA
        || lopHienTai.HOCKY != duLieuMoi.HOCKY
        || lopHienTai.NHOM != duLieuMoi.NHOM;
}

int TimViTriLopTinChiTheoMa(const DS_LTC& dsLTC, int maLopTC) {
    return TimViTriLopTheoMaNoiBo(dsLTC, maLopTC);
}

Loptinchi* TimLopTinChiTheoMa(DS_LTC& dsLTC, int maLopTC) {
    const int viTri = TimViTriLopTheoMaNoiBo(dsLTC, maLopTC);
    return viTri < 0 ? nullptr : dsLTC.nodes[viTri];
}

const Loptinchi* TimLopTinChiTheoMa(
    const DS_LTC& dsLTC,
    int maLopTC
) {
    const int viTri = TimViTriLopTheoMaNoiBo(dsLTC, maLopTC);
    return viTri < 0 ? nullptr : dsLTC.nodes[viTri];
}

Loptinchi* TimLopTinChi(
    DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom
) {
    const string maDaChuanHoa = ChuanHoaMa(maMH);
    const string nienKhoaDaChuanHoa = XoaKhoangTrangDauCuoi(nienKhoa);
    for (int i = 0; i < dsLTC.n; ++i) {
        Loptinchi* lop = dsLTC.nodes[i];
        if (lop != nullptr && lop->MAMH == maDaChuanHoa
            && lop->NIENKHOA == nienKhoaDaChuanHoa
            && lop->HOCKY == hocKy && lop->NHOM == nhom) {
            return lop;
        }
    }
    return nullptr;
}

const Loptinchi* TimLopTinChi(
    const DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom
) {
    const string maDaChuanHoa = ChuanHoaMa(maMH);
    const string nienKhoaDaChuanHoa = XoaKhoangTrangDauCuoi(nienKhoa);
    for (int i = 0; i < dsLTC.n; ++i) {
        const Loptinchi* lop = dsLTC.nodes[i];
        if (lop != nullptr && lop->MAMH == maDaChuanHoa
            && lop->NIENKHOA == nienKhoaDaChuanHoa
            && lop->HOCKY == hocKy && lop->NHOM == nhom) {
            return lop;
        }
    }
    return nullptr;
}

bool KiemTraTrungLopTinChi(
    const DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom,
    int maLopBoQua
) {
    Loptinchi canKiemTra{
        maLopBoQua, ChuanHoaMa(maMH), XoaKhoangTrangDauCuoi(nienKhoa),
        hocKy, nhom, 1, 1, false, nullptr
    };
    return KiemTraTrungLopNoiBo(dsLTC, canKiemTra, maLopBoQua);
}

int TimMaLopTinChiLonNhat(const DS_LTC& dsLTC) {
    int maLonNhat = 0;
    for (int i = 0; i < dsLTC.n; ++i) {
        if (dsLTC.nodes[i] != nullptr
            && dsLTC.nodes[i]->MALOPTC > maLonNhat) {
            maLonNhat = dsLTC.nodes[i]->MALOPTC;
        }
    }
    return maLonNhat;
}

int TaoMaLopTinChi(const DS_LTC& dsLTC) {
    const int maLonNhat = TimMaLopTinChiLonNhat(dsLTC);
    return maLonNhat == std::numeric_limits<int>::max()
        ? -1 : maLonNhat + 1;
}



bool ThemLopTinChi(
    DS_LTC& dsLTC,
    treeMH dsMonHoc,
    Loptinchi lopTinChi,
    string& loi
) {
    loi.clear();
    if (dsLTC.n >= MAXLTC) {
        loi = "Danh sach lop tin chi da day.";
        return false;
    }

    ChuanHoaThongTinLopTinChi(lopTinChi);
    if (!KiemTraThongTinLopTinChi(dsMonHoc, lopTinChi, loi)) {
        return false;
    }
    if (KiemTraTrungLopNoiBo(dsLTC, lopTinChi, -1)) {
        loi = "Lop tin chi da ton tai trong cung nien khoa, hoc ky va nhom.";
        return false;
    }

    if (dsLTC.maTiepTheo <= 0
        || dsLTC.maTiepTheo == std::numeric_limits<int>::max()) {
        loi = "Khong the tao them ma lop tin chi.";
        return false;
    }
    lopTinChi.MALOPTC = dsLTC.maTiepTheo++;
    lopTinChi.HUYLOP = false;
    lopTinChi.dssvdk = nullptr;
    dsLTC.nodes[dsLTC.n++] = new Loptinchi(lopTinChi);
    return true;
}

bool HieuChinhLopTinChi(
    DS_LTC& dsLTC,
    treeMH dsMonHoc,
    int maLopTC,
    const Loptinchi& duLieuMoi,
    string& loi
) {
    loi.clear();
    const int viTri = TimViTriLopTheoMaNoiBo(dsLTC, maLopTC);
    if (viTri < 0) {
        loi = "Khong tim thay lop tin chi.";
        return false;
    }

    Loptinchi daChuanHoa = duLieuMoi;
    ChuanHoaThongTinLopTinChi(daChuanHoa);
    if (!KiemTraThongTinLopTinChi(dsMonHoc, daChuanHoa, loi)) {
        return false;
    }
    if (KiemTraTrungLopNoiBo(dsLTC, daChuanHoa, maLopTC)) {
        loi = "Lop tin chi da ton tai trong cung nien khoa, hoc ky va nhom.";
        return false;
    }

    Loptinchi& lopHienTai = *dsLTC.nodes[viTri];
    if (lopHienTai.dssvdk != nullptr
        && ThayDoiThongTinDinhDanh(lopHienTai, daChuanHoa)) {
        loi = "Khong the doi mon hoc, nien khoa, hoc ky hoac nhom khi da co dang ky.";
        return false;
    }
    if (DemDangKyConHieuLuc(lopHienTai.dssvdk) > daChuanHoa.SOSVMAX) {
        loi = "Si so toi da moi nho hon so sinh vien dang ky hien tai.";
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
    const int viTri = TimViTriLopTheoMaNoiBo(dsLTC, maLopTC);
    if (viTri < 0) {
        loi = "Khong tim thay lop tin chi.";
        return false;
    }
    if (dsLTC.nodes[viTri]->dssvdk != nullptr) {
        loi = "Khong the xoa lop tin chi da co du lieu dang ky.";
        return false;
    }

    delete dsLTC.nodes[viTri];
    for (int i = viTri; i < dsLTC.n - 1; ++i) {
        dsLTC.nodes[i] = dsLTC.nodes[i + 1];
    }
    dsLTC.nodes[--dsLTC.n] = nullptr;
    return true;
}

int DemSoSinhVienDangKy(const Loptinchi& lopTinChi) {
    return DemDangKyConHieuLuc(lopTinChi.dssvdk);
}

int TinhSoChoTrong(const Loptinchi& lopTinChi) {
    const int soChoTrong = lopTinChi.SOSVMAX
        - DemSoSinhVienDangKy(lopTinChi);
    return soChoTrong > 0 ? soChoTrong : 0;
}

int LocLopTinChiTheoNienKhoaHocKy(
    DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    Loptinchi* dsKetQua[],
    int kichThuocToiDa
) {
    if (dsKetQua == nullptr || kichThuocToiDa <= 0) {
        return 0;
    }
    const string nienKhoaDaChuanHoa = XoaKhoangTrangDauCuoi(nienKhoa);
    int soLuong = 0;
    for (int i = 0; i < dsLTC.n && soLuong < kichThuocToiDa; ++i) {
        Loptinchi* lop = dsLTC.nodes[i];
        if (lop != nullptr && lop->NIENKHOA == nienKhoaDaChuanHoa
            && lop->HOCKY == hocKy) {
            dsKetQua[soLuong++] = lop;
        }
    }
    return soLuong;
}

int LocLopTinChiKhongDuSiSo(
    DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    Loptinchi* dsKetQua[],
    int kichThuocToiDa
) {
    if (dsKetQua == nullptr || kichThuocToiDa <= 0) {
        return 0;
    }
    const string nienKhoaDaChuanHoa = XoaKhoangTrangDauCuoi(nienKhoa);
    int soLuong = 0;
    for (int i = 0; i < dsLTC.n && soLuong < kichThuocToiDa; ++i) {
        Loptinchi* lop = dsLTC.nodes[i];
        if (lop != nullptr && !lop->HUYLOP
            && lop->NIENKHOA == nienKhoaDaChuanHoa
            && lop->HOCKY == hocKy
            && DemSoSinhVienDangKy(*lop) < lop->SOSVMIN) {
            dsKetQua[soLuong++] = lop;
        }
    }
    return soLuong;
}

bool HuyLopTinChi(DS_LTC& dsLTC, int maLopTC, string& loi) {
    loi.clear();
    Loptinchi* lop = TimLopTinChiTheoMa(dsLTC, maLopTC);
    if (lop == nullptr) {
        loi = "Khong tim thay lop tin chi.";
        return false;
    }
    if (lop->HUYLOP) {
        loi = "Lop tin chi da bi huy truoc do.";
        return false;
    }
    lop->HUYLOP = true;
    return true;
}
