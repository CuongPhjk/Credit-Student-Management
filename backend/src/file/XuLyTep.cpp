#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#endif

#include "../../include/file/XuLyTep.h"

#include <algorithm>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iomanip>
#include <limits>
#include <memory>


#include "../../include/model/AppData.h"
#include "../../include/functions/HamMonHoc.h"
#include "../../include/functions/HamLop.h"
#include "../../include/functions/HamSinhVien.h"
#include "../../include/utils/KiemTraDuLieu.h"
#include "../../include/utils/XuLyChuoi.h"

namespace {

void ChuanHoaDong(string& dong, int soDong) {
    if (!dong.empty() && dong.back() == '\r') dong.pop_back();
    if (soDong == 1 && dong.compare(0, 3, "\xEF\xBB\xBF") == 0) {
        dong.erase(0, 3);
    }
}

// Write the complete snapshot beside the destination, then replace it atomically.
// A failed write or replacement leaves the original file intact.
bool GhiAnToan(const string& tenFile,
               const std::function<bool(ofstream&)>& ghi, string& loi) {
    loi.clear();
    const auto dich = filesystem::u8path(tenFile);
    auto tam = dich;
    tam += ".tmp";
    ofstream tep(tam, ios::out | ios::trunc);
    if (!tep.is_open()) {
        loi = "Khong the tao file tam: " + tam.u8string();
        return false;
    }
    tep << std::setprecision(std::numeric_limits<float>::max_digits10);
    const bool daGhi = ghi(tep);
    tep.flush();
    const bool dayDu = daGhi && tep.good();
    tep.close();
    error_code ec;
    if (!dayDu || tep.fail()) {
        filesystem::remove(tam, ec);
        loi = "Khong the ghi day du file tam: " + tam.u8string();
        return false;
    }
#ifdef _WIN32
    const bool daThay = MoveFileExW(tam.c_str(), dich.c_str(),
        MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH) != 0;
#else
    filesystem::rename(tam, dich, ec);
    const bool daThay = !ec;
#endif
    if (!daThay) {
        filesystem::remove(tam, ec);
        loi = "Khong the thay the file du lieu: " + tenFile;
        return false;
    }
    return true;
}

bool DocMotDongMonHoc(
    const string& dong,
    Monhoc& monHoc,
    string& loi
) {
    if (!LaChuoiUtf8HopLe(dong)) {
        loi = "Du lieu mon hoc phai dung ma hoa UTF-8.";
        return false;
    }

    string cot[4];
    if (!TachChuoi(dong, '|', cot, 4)) {
        loi = "Moi dong mon hoc phai co dung 4 cot, ngan cach boi ky tu |.";
        return false;
    }

    monHoc.MAMH = ChuanHoaMa(cot[0]);
    monHoc.TENMH = XoaKhoangTrangThua(cot[1]);
    if (!ChuyenSangSoNguyen(cot[2], monHoc.STCLT)
        || !ChuyenSangSoNguyen(cot[3], monHoc.STCTH)) {
        loi = "So tin chi ly thuyet va thuc hanh phai la so nguyen.";
        return false;
    }
    return true;
}

bool GhiCayMonHoc(ofstream& tep, treeMH goc) {
    if (goc == nullptr) {
        return true;
    }
    if (!GhiCayMonHoc(tep, goc->left)) {
        return false;
    }
    tep << goc->mh.MAMH << '|'
        << goc->mh.TENMH << '|'
        << goc->mh.STCLT << '|'
        << goc->mh.STCTH << '\n';
    if (!tep.good()) {
        return false;
    }
    return GhiCayMonHoc(tep, goc->right);
}

void GiaiPhongDanhSachDangKyNoiBo(PTRDK& danhSach) {
    while (danhSach != nullptr) {
        PTRDK nodeCanXoa = danhSach;
        danhSach = danhSach->next;
        delete nodeCanXoa;
    }
}

void GiaiPhongDanhSachLopTinChiNoiBo(DS_LTC& dsLTC) {
    for (int i = 0; i < dsLTC.n; ++i) {
        if (dsLTC.nodes[i] == nullptr) {
            continue;
        }
        GiaiPhongDanhSachDangKyNoiBo(dsLTC.nodes[i]->dssvdk);
        delete dsLTC.nodes[i];
        dsLTC.nodes[i] = nullptr;
    }
    dsLTC.n = 0;
    dsLTC.maTiepTheo = 1;
}

bool DocMotDongLopTinChi(
    const string& dong,
    Loptinchi& lopTinChi,
    string& loi
) {
    if (!LaChuoiUtf8HopLe(dong)) {
        loi = "Du lieu lop tin chi phai dung ma hoa UTF-8.";
        return false;
    }

    string cot[8];
    if (!TachChuoi(dong, '|', cot, 8)) {
        loi = "Moi dong lop tin chi phai co dung 8 cot.";
        return false;
    }

    int huyLop = 0;
    if (!ChuyenSangSoNguyen(cot[0], lopTinChi.MALOPTC)
        || !ChuyenSangSoNguyen(cot[3], lopTinChi.HOCKY)
        || !ChuyenSangSoNguyen(cot[4], lopTinChi.NHOM)
        || !ChuyenSangSoNguyen(cot[5], lopTinChi.SOSVMIN)
        || !ChuyenSangSoNguyen(cot[6], lopTinChi.SOSVMAX)
        || !ChuyenSangSoNguyen(cot[7], huyLop)) {
        loi = "Ma lop, hoc ky, nhom, si so va trang thai phai la so nguyen.";
        return false;
    }

    lopTinChi.MAMH = ChuanHoaMa(cot[1]);
    lopTinChi.NIENKHOA = XoaKhoangTrangDauCuoi(cot[2]);
    lopTinChi.HUYLOP = huyLop == 1;
    lopTinChi.dssvdk = nullptr;

    if (lopTinChi.MALOPTC <= 0) {
        loi = "Ma lop tin chi phai lon hon 0.";
        return false;
    }
    if (lopTinChi.MAMH.empty()) {
        loi = "Ma mon hoc khong duoc de trong.";
        return false;
    }
    if (!NienKhoaHopLe(lopTinChi.NIENKHOA)) {
        loi = "Nien khoa phai co dang YYYY-YYYY va hai nam lien tiep.";
        return false;
    }
    if (!HocKyHopLe(lopTinChi.HOCKY)
        || !NhomHopLe(lopTinChi.NHOM)) {
        loi = "Hoc ky phai tu 1 den 3 va nhom phai lon hon 0.";
        return false;
    }
    if (!SiSoHopLe(lopTinChi.SOSVMIN, lopTinChi.SOSVMAX)) {
        loi = "Si so phai thoa man 0 < toi thieu <= toi da.";
        return false;
    }
    if (huyLop != 0 && huyLop != 1) {
        loi = "Trang thai huy lop chi duoc la 0 hoac 1.";
        return false;
    }
    return true;
}

bool TrungLopTinChiTrongDanhSach(
    const DS_LTC& dsLTC,
    const Loptinchi& lopTinChi,
    string& loi
) {
    for (int i = 0; i < dsLTC.n; ++i) {
        const Loptinchi& lopHienTai = *dsLTC.nodes[i];
        if (lopHienTai.MALOPTC == lopTinChi.MALOPTC) {
            loi = "Ma lop tin chi bi trung.";
            return true;
        }
        if (lopHienTai.MAMH == lopTinChi.MAMH
            && lopHienTai.NIENKHOA == lopTinChi.NIENKHOA
            && lopHienTai.HOCKY == lopTinChi.HOCKY
            && lopHienTai.NHOM == lopTinChi.NHOM) {
            loi = "Lop tin chi bi trung mon, nien khoa, hoc ky va nhom.";
            return true;
        }
    }
    return false;
}

bool DocDongDangKy(const string& dong, Loptinchi& lop, string& loi) {
    string cot[4];
    if (!TachChuoi(dong, '|', cot, 4)) {
        loi = "Dong dang ky phai co 4 cot: ma SV, diem, huy dang ky, da co diem.";
        return false;
    }
    const string maSV = ChuanHoaMa(cot[0]);
    int huy = 0, daDiem = 0;
    float diem = 0;
    if (!MaSinhVienHopLe(maSV)) {
        loi = "Ma sinh vien dang ky khong hop le.";
        return false;
    }
    if (!ChuyenSangSoNguyen(cot[2], huy)
        || !ChuyenSangSoNguyen(cot[3], daDiem)
        || (huy != 0 && huy != 1) || (daDiem != 0 && daDiem != 1)) {
        loi = "Trang thai dang ky va diem chi duoc la 0 hoac 1.";
        return false;
    }
    try {
        const string chuoi = XoaKhoangTrangDauCuoi(cot[1]);
        size_t cuoi = 0;
        diem = std::stof(chuoi, &cuoi);
        if (cuoi != chuoi.size() || !std::isfinite(diem) || !DiemHopLe(diem)) {
            loi = "Diem phai la so tu 0 den 10.";
            return false;
        }
    } catch (const std::exception&) {
        loi = "Diem phai la so tu 0 den 10.";
        return false;
    }
    PTRDK* viTri = &lop.dssvdk;
    while (*viTri != nullptr) {
        if ((*viTri)->dk.MASV == maSV) {
            loi = "Sinh vien bi trung trong lop tin chi.";
            return false;
        }
        viTri = &((*viTri)->next);
    }
    *viTri = new nodeDK{{maSV, diem, huy == 1, daDiem == 1}, nullptr};
    return true;
}

}  // namespace

bool DocDanhSachMonHoc(
    const string& tenFile,
    treeMH& dsMonHoc,
    string& loi
) {
    loi.clear();
    ifstream tep(filesystem::u8path(tenFile));
    if (!tep.is_open()) {
        loi = "Khong the mo file mon hoc de doc: " + tenFile;
        return false;
    }

    treeMH danhSachMoi = nullptr;
    string dong;
    int soDong = 0;
    while (getline(tep, dong)) {
        ++soDong;
        ChuanHoaDong(dong, soDong);
        if (XoaKhoangTrangDauCuoi(dong).empty()) {
            continue;
        }

        Monhoc monHoc{};
        string loiDong;
        if (!DocMotDongMonHoc(dong, monHoc, loiDong)
            || !ThemMonHoc(danhSachMoi, monHoc, loiDong)) {
            GiaiPhongCayMonHoc(danhSachMoi);
            loi = "Loi tai dong " + to_string(soDong) + ": " + loiDong;
            return false;
        }
    }

    if (tep.bad()) {
        GiaiPhongCayMonHoc(danhSachMoi);
        loi = "Khong the doc het file mon hoc: " + tenFile;
        return false;
    }

    GiaiPhongCayMonHoc(dsMonHoc);
    dsMonHoc = danhSachMoi;
    return true;
}

bool GhiDanhSachMonHoc(const string& tenFile, treeMH dsMonHoc, string& loi) {
    return GhiAnToan(tenFile, [dsMonHoc](ofstream& tep) {
        return GhiCayMonHoc(tep, dsMonHoc);
    }, loi);
}

bool DocDanhSachLopSinhVien(const string& tenFile, DS_LOP& dsLop, string& loi) {
    loi.clear();
    ifstream tep(filesystem::u8path(tenFile));
    if (!tep.is_open()) {
        loi = "Khong the mo file lop sinh vien: " + tenFile;
        return false;
    }
    // Read into separate ownership so invalid input cannot damage live data.
    auto moi = std::make_unique<AppData>();
    string dong, maLop;
    int soDong = 0;
    while (getline(tep, dong)) {
        ChuanHoaDong(dong, ++soDong);
        if (XoaKhoangTrangDauCuoi(dong).empty()) continue;
        string loiDong;
        if (!LaChuoiUtf8HopLe(dong)) {
            loiDong = "Du lieu phai dung ma hoa UTF-8.";
        } else if (dong == "#") {
            if (maLop.empty()) loiDong = "Dau # khong co lop tuong ung.";
            else maLop.clear();
        } else if (maLop.empty()) {
            string cot[2];
            if (!TachChuoi(dong, '|', cot, 2)) {
                loiDong = "Dong lop phai co 2 cot: ma lop, ten lop.";
            } else if (ThemLop(moi->dsLop(), Lop{cot[0], cot[1], nullptr}, loiDong)) {
                maLop = ChuanHoaMa(cot[0]);
            }
        } else {
            string cot[5];
            if (!TachChuoi(dong, '|', cot, 5)) {
                loiDong = "Dong sinh vien phai co 5 cot; ket thuc lop bang #.";
            } else {
                ThemSinhVien(moi->dsLop(), maLop,
                    Sinhvien{cot[0], cot[1], cot[2], cot[3], cot[4]}, loiDong);
            }
        }
        if (!loiDong.empty()) {
            loi = "Loi tai dong " + to_string(soDong) + ": " + loiDong;
            return false;
        }
    }
    if (tep.bad() || !maLop.empty()) {
        loi = tep.bad() ? "Khong the doc het file lop sinh vien."
                       : "Thieu dau # ket thuc lop " + maLop + ".";
        return false;
    }
    for (int i = 0; i < dsLop.n; ++i) {
        GiaiPhongDanhSachSinhVien(dsLop.nodes[i].dssv);
    }
    dsLop = moi->dsLop();
    moi->dsLop().n = 0;  // Transfer ownership of student lists.
    return true;
}

bool GhiDanhSachLopSinhVien(const string& tenFile, const DS_LOP& dsLop, string& loi) {
    return GhiAnToan(tenFile, [&dsLop](ofstream& tep) {
        for (int i = 0; i < dsLop.n; ++i) {
            const Lop& lop = dsLop.nodes[i];
            tep << lop.MALOP << '|' << lop.TENLOP << '\n';
            for (PTRSV node = lop.dssv; node != nullptr; node = node->next) {
                const Sinhvien& sv = node->sv;
                tep << sv.MASV << '|' << sv.HO << '|' << sv.TEN << '|'
                    << sv.PHAI << '|' << sv.SODT << '\n';
            }
            tep << "#\n";
        }
        return tep.good();
    }, loi);
}

bool DocDanhSachLopTinChi(const string& tenFile, DS_LTC& dsLTC, string& loi) {
    loi.clear();
    ifstream tep(filesystem::u8path(tenFile));
    if (!tep.is_open()) {
        loi = "Khong the mo file lop tin chi: " + tenFile;
        return false;
    }
    auto moi = std::make_unique<AppData>();
    DS_LTC& dsMoi = moi->dsLopTinChi();
    Loptinchi* lop = nullptr;
    string dong;
    int soDong = 0;
    while (getline(tep, dong)) {
        ChuanHoaDong(dong, ++soDong);
        if (XoaKhoangTrangDauCuoi(dong).empty()) continue;
        string loiDong;
        if (!LaChuoiUtf8HopLe(dong)) {
            loiDong = "Du lieu phai dung ma hoa UTF-8.";
        } else if (dong == "#") {
            if (lop == nullptr) loiDong = "Dau # khong co lop tin chi tuong ung.";
            else lop = nullptr;
        } else if (lop == nullptr) {
            Loptinchi thongTin{};
            if (dsMoi.n >= MAXLTC) {
                loiDong = "Danh sach lop tin chi vuot qua kich thuoc toi da.";
            } else if (DocMotDongLopTinChi(dong, thongTin, loiDong)
                       && !TrungLopTinChiTrongDanhSach(dsMoi, thongTin, loiDong)) {
                if (thongTin.MALOPTC == numeric_limits<int>::max()) {
                    loiDong = "Ma lop tin chi da dat gioi han.";
                } else {
                    lop = new Loptinchi(thongTin);
                    dsMoi.nodes[dsMoi.n++] = lop;
                    dsMoi.maTiepTheo = max(dsMoi.maTiepTheo, lop->MALOPTC + 1);
                }
            }
        } else {
            DocDongDangKy(dong, *lop, loiDong);
        }
        if (!loiDong.empty()) {
            loi = "Loi tai dong " + to_string(soDong) + ": " + loiDong;
            return false;
        }
    }
    if (tep.bad() || lop != nullptr) {
        loi = tep.bad() ? "Khong the doc het file lop tin chi."
                       : "Thieu dau # ket thuc lop tin chi.";
        return false;
    }
    GiaiPhongDanhSachLopTinChiNoiBo(dsLTC);
    dsLTC = dsMoi;
    dsMoi.n = 0;  // Transfer ownership of credit classes and registrations.
    return true;
}

bool GhiDanhSachLopTinChi(const string& tenFile, const DS_LTC& dsLTC, string& loi) {
    return GhiAnToan(tenFile, [&dsLTC](ofstream& tep) {
        for (int i = 0; i < dsLTC.n; ++i) {
            const Loptinchi* lop = dsLTC.nodes[i];
            if (lop == nullptr) return false;
            tep << lop->MALOPTC << '|' << lop->MAMH << '|'
                << lop->NIENKHOA << '|' << lop->HOCKY << '|' << lop->NHOM << '|'
                << lop->SOSVMIN << '|' << lop->SOSVMAX << '|'
                << (lop->HUYLOP ? 1 : 0) << '\n';
            for (PTRDK node = lop->dssvdk; node != nullptr; node = node->next) {
                const Dangky& dk = node->dk;
                tep << dk.MASV << '|' << dk.DIEM << '|'
                    << (dk.HUYDK ? 1 : 0) << '|' << (dk.DADIEM ? 1 : 0) << '\n';
            }
            tep << "#\n";
        }
        return tep.good();
    }, loi);
}
