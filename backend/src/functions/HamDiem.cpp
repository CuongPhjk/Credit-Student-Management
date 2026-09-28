#include "../../include/functions/HamDiem.h"

#include <cmath>

#include "../../include/functions/HamDangKy.h"
#include "../../include/functions/HamLopTinChi.h"
#include "../../include/utils/KiemTraDuLieu.h"
#include "../../include/utils/XuLyChuoi.h"

namespace {

const Loptinchi* TimLopNhapDiem(
    const DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom,
    string& loi
) {
    const string nienKhoaDaChuanHoa = XoaKhoangTrangDauCuoi(nienKhoa);
    const string maMonDaChuanHoa = ChuanHoaMa(maMH);
    if (!NienKhoaHopLe(nienKhoaDaChuanHoa)) {
        loi = "Nien khoa phai co dang YYYY-YYYY va hai nam lien tiep.";
        return nullptr;
    }
    if (!HocKyHopLe(hocKy)) {
        loi = "Hoc ky chi duoc nhan gia tri tu 1 den 3.";
        return nullptr;
    }
    if (!MaHopLe(maMonDaChuanHoa, 10)) {
        loi = "Ma mon hoc khong hop le, toi da 10 ky tu.";
        return nullptr;
    }
    if (!NhomHopLe(nhom)) {
        loi = "Nhom lop tin chi phai lon hon 0.";
        return nullptr;
    }

    const Loptinchi* lop = TimLopTinChi(
        dsLTC, nienKhoaDaChuanHoa, hocKy, maMonDaChuanHoa, nhom
    );
    if (lop == nullptr) {
        loi = "Khong tim thay lop tin chi phu hop.";
        return nullptr;
    }
    if (lop->HUYLOP) {
        loi = "Khong the nhap diem cho lop tin chi da bi huy.";
        return nullptr;
    }
    return lop;
}

const Sinhvien* TimSinhVienTheoMa(
    const DS_LOP& dsLop,
    const string& maSV
) {
    const string maDaChuanHoa = ChuanHoaMa(maSV);
    for (int i = 0; i < dsLop.n; ++i) {
        for (PTRSV node = dsLop.nodes[i].dssv;
             node != nullptr;
             node = node->next) {
            if (node->sv.MASV == maDaChuanHoa) {
                return &node->sv;
            }
        }
    }
    return nullptr;
}

}  // namespace

bool KiemTraDiemHopLe(float diem) {
    return std::isfinite(diem) && DiemHopLe(diem);
}

bool SinhVienDuocNhapDiem(
    const Loptinchi& lopTinChi,
    const string& maSV
) {
    if (lopTinChi.HUYLOP) {
        return false;
    }
    PTRDK dangKy = TimDangKy(lopTinChi.dssvdk, maSV);
    return dangKy != nullptr && !dangKy->dk.HUYDK;
}

bool NhapDiem(
    DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom,
    const string& maSV,
    float diem,
    string& loi
) {
    loi.clear();
    const Loptinchi* lopKiemTra = TimLopNhapDiem(
        dsLTC, nienKhoa, hocKy, maMH, nhom, loi
    );
    if (lopKiemTra == nullptr) {
        return false;
    }
    if (!KiemTraDiemHopLe(diem)) {
        loi = "Diem phai la so nam trong khoang tu 0 den 10.";
        return false;
    }

    Loptinchi* lop = TimLopTinChi(
        dsLTC, nienKhoa, hocKy, maMH, nhom
    );
    PTRDK dangKy = lop == nullptr ? nullptr : TimDangKy(lop->dssvdk, maSV);
    if (dangKy == nullptr || dangKy->dk.HUYDK) {
        loi = "Sinh vien khong co dang ky con hieu luc trong lop tin chi.";
        return false;
    }
    dangKy->dk.DIEM = diem;
    dangKy->dk.DADIEM = true;
    return true;
}

bool HieuChinhDiem(
    DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom,
    const string& maSV,
    float diemMoi,
    string& loi
) {
    return NhapDiem(
        dsLTC, nienKhoa, hocKy, maMH, nhom, maSV, diemMoi, loi
    );
}

int DemSinhVienNhapDiem(
    const DS_LTC& dsLTC,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom,
    string& loi
) {
    loi.clear();
    const Loptinchi* lop = TimLopNhapDiem(
        dsLTC, nienKhoa, hocKy, maMH, nhom, loi
    );
    if (lop == nullptr) {
        return -1;
    }
    int soLuong = 0;
    for (PTRDK node = lop->dssvdk; node != nullptr; node = node->next) {
        if (!node->dk.HUYDK) {
            ++soLuong;
        }
    }
    return soLuong;
}

int LayDanhSachSinhVienNhapDiem(
    const DS_LTC& dsLTC,
    const DS_LOP& dsLop,
    const string& nienKhoa,
    int hocKy,
    const string& maMH,
    int nhom,
    Diemsinhvien dsKetQua[],
    int kichThuocToiDa,
    string& loi
) {
    loi.clear();
    const Loptinchi* lop = TimLopNhapDiem(
        dsLTC, nienKhoa, hocKy, maMH, nhom, loi
    );
    if (lop == nullptr) {
        return -1;
    }
    if (kichThuocToiDa < 0
        || (kichThuocToiDa > 0 && dsKetQua == nullptr)) {
        loi = "Vung nho nhan danh sach diem khong hop le.";
        return -1;
    }

    int soLuong = 0;
    for (PTRDK node = lop->dssvdk; node != nullptr; node = node->next) {
        if (node->dk.HUYDK) {
            continue;
        }
        const Sinhvien* sinhVien = TimSinhVienTheoMa(dsLop, node->dk.MASV);
        if (sinhVien == nullptr) {
            loi = "Khong tim thay thong tin sinh vien "
                + node->dk.MASV + ".";
            return -1;
        }
        if (soLuong >= kichThuocToiDa) {
            loi = "Vung nho nhan danh sach diem khong du.";
            return -1;
        }
        dsKetQua[soLuong++] = Diemsinhvien{
            sinhVien->MASV, sinhVien->HO, sinhVien->TEN,
            node->dk.DIEM, node->dk.DADIEM
        };
    }
    return soLuong;
}
