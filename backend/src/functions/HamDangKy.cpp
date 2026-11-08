#include "../KhaiBao.h"


Loptinchi* TimLopTinChiNoiBo(DS_LTC& dsLTC, int maLopTC) {
    for (int i = 0; i < dsLTC.n; ++i) {
        if (dsLTC.nodes[i]->MALOPTC == maLopTC) {
            return dsLTC.nodes[i];
        }
    }
    return nullptr;
}

int DemDangKyHieuLuc(PTRDK danhSach) {
    int soLuong = 0;
    for (PTRDK node = danhSach; node != nullptr; node = node->next) {
        if (!node->dk.HUYDK) {
            ++soLuong;
        }
    }
    return soLuong;
}

PTRDK TimDangKy(PTRDK dsDangKy, string maSV) {
    string maDaChuanHoa = ChuanHoaMa(maSV);
    for (PTRDK node = dsDangKy; node != nullptr; node = node->next) {
        if (node->dk.MASV == maDaChuanHoa) {
            return node;
        }
    }
    return nullptr;
}

bool SinhVienDangKyLopTinChi(
    Loptinchi lopTinChi,
    string maSV
) {
    PTRDK dangKy = TimDangKy(lopTinChi.dssvdk, maSV);
    return dangKy != nullptr && !dangKy->dk.HUYDK;
}

bool SinhVienDaDangKyMonTrongHocKy(
    DS_LTC& dsLTC,
    string maSV,
    string maMH,
    string nienKhoa,
    int hocKy,
    int maLopTCBoQua
) {
    string maMonDaChuanHoa = ChuanHoaMa(maMH);
    string nienKhoaDaChuanHoa = XoaKhoangTrangDauCuoi(nienKhoa);
    for (int i = 0; i < dsLTC.n; ++i) {
        Loptinchi* lop = dsLTC.nodes[i];
        if (lop->MALOPTC != maLopTCBoQua
            && !lop->HUYLOP
            && lop->MAMH == maMonDaChuanHoa
            && lop->NIENKHOA == nienKhoaDaChuanHoa
            && lop->HOCKY == hocKy
            && SinhVienDangKyLopTinChi(*lop, maSV)) {
            return true;
        }
    }
    return false;
}

bool LopTinChiConCho(Loptinchi lopTinChi) {
    return !lopTinChi.HUYLOP
        && DemDangKyHieuLuc(lopTinChi.dssvdk) < lopTinChi.SOSVMAX;
}

bool DangKyLopTinChi(
    DS_LTC& dsLTC,
    DS_LOP& dsLop,
    int maLopTC,
    string maSV,
    string& loi
) {
    loi.clear();
    string maDaChuanHoa = ChuanHoaMa(maSV);
    int viTriLop;
    if (TimSinhVienToanTruong(dsLop, maDaChuanHoa, viTriLop) == nullptr) {
        loi = "Mã sinh viên không tồn tại.";
        return false;
    }
    Loptinchi* lop = TimLopTinChiNoiBo(dsLTC, maLopTC);
    if (lop == nullptr) {
        loi = "Không tìm thấy lớp tín chỉ.";
        return false;
    }
    if (lop->HUYLOP) {
        loi = "Lớp tín chỉ đã bị hủy.";
        return false;
    }
    PTRDK dangKyCu = TimDangKy(lop->dssvdk, maDaChuanHoa);
    if (dangKyCu != nullptr && !dangKyCu->dk.HUYDK) {
        loi = "Sinh viên đã đăng ký lớp tín chỉ này.";
        return false;
    }
    if (!LopTinChiConCho(*lop)) {
        loi = "Lớp tín chỉ đã hết chỗ.";
        return false;
    }
    if (SinhVienDaDangKyMonTrongHocKy(
        dsLTC, maDaChuanHoa, lop->MAMH,
        lop->NIENKHOA, lop->HOCKY, lop->MALOPTC
    )) {
        loi = "Sinh viên đã đăng ký môn học này trong cùng học kỳ.";
        return false;
    }
    if (dangKyCu != nullptr) {
        dangKyCu->dk.HUYDK = false;
        dangKyCu->dk.DIEM = -1.0F;
        return true;
    }

    PTRDK nodeMoi = new nodeDK{{maDaChuanHoa, -1.0F, false}, nullptr};
    if (lop->dssvdk == nullptr) {
        lop->dssvdk = nodeMoi;
    } else {
        PTRDK cuoi = lop->dssvdk;
        while (cuoi->next != nullptr) cuoi = cuoi->next;
        cuoi->next = nodeMoi;
    }
    return true;
}

bool HuyDangKy(
    DS_LTC& dsLTC,
    int maLopTC,
    string maSV,
    string& loi
) {
    loi.clear();
    Loptinchi* lop = TimLopTinChiNoiBo(dsLTC, maLopTC);
    if (lop == nullptr) {
        loi = "Không tìm thấy lớp tín chỉ.";
        return false;
    }
    PTRDK dangKy = TimDangKy(lop->dssvdk, maSV);
    if (dangKy == nullptr || dangKy->dk.HUYDK) {
        loi = "Sinh viên chưa đăng ký lớp tín chỉ này.";
        return false;
    }
    dangKy->dk.HUYDK = true;
    return true;
}

PTRDK* LayDanhSachDangKy(
    Loptinchi& lopTinChi, int& soLuong
) {
    soLuong = 0;
    for (PTRDK node = lopTinChi.dssvdk; node != nullptr; node = node->next) {
        ++soLuong;
    }
    if (soLuong == 0) return nullptr;
    PTRDK* ketQua = new PTRDK[soLuong];
    int i = 0;
    for (PTRDK node = lopTinChi.dssvdk; node != nullptr; node = node->next) {
        ketQua[i++] = node;
    }
    return ketQua;
}

