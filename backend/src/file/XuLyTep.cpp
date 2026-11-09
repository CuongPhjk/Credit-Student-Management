#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#endif

#include "../KhaiBao.h"

#include <algorithm>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iomanip>
#include <limits>



void ChuanHoaDong(string& dong, int soDong) {
    if (!dong.empty() && dong.back() == '\r') dong.pop_back();
    if (soDong == 1 && dong.compare(0, 3, "\xEF\xBB\xBF") == 0) {
        dong.erase(0, 3);
    }
}


bool GhiAnToan(string tenFile,
               std::function<bool(ofstream&)> ghi, string& loi) {
    loi.clear();
    auto dich = filesystem::u8path(tenFile);
    auto tam = dich;
    tam += ".tmp";
    ofstream tep(tam, ios::out | ios::trunc);
    if (!tep.is_open()) {
        loi = "Không thể tạo tệp tạm: " + tam.u8string();
        return false;
    }
    tep << std::setprecision(std::numeric_limits<float>::max_digits10);
    bool daGhi = ghi(tep);
    tep.flush();
    bool dayDu = daGhi && tep.good();
    tep.close();
    error_code ec;
    if (!dayDu || tep.fail()) {
        filesystem::remove(tam, ec);
        loi = "Không thể ghi đầy đủ tệp tạm: " + tam.u8string();
        return false;
    }
#ifdef _WIN32
    bool daThay = MoveFileExW(tam.c_str(), dich.c_str(),
        MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH) != 0;
#else
    filesystem::rename(tam, dich, ec);
    bool daThay = !ec;
#endif
    if (!daThay) {
        filesystem::remove(tam, ec);
        loi = "Không thể thay thế tệp dữ liệu: " + tenFile;
        return false;
    }
    return true;
}

bool KiemTraSinhVienTrongTep(Sinhvien sinhVien, string& loi) {
    if (!MaSinhVienHopLe(sinhVien.MASV)) {
        loi = "Mã sinh viên chỉ được chứa chữ cái, chữ số và tối đa 15 ký tự.";
        return false;
    }
    if (sinhVien.HO.empty() || sinhVien.TEN.empty()
        || DemSoKyTuUtf8(sinhVien.HO) > 40
        || DemSoKyTuUtf8(sinhVien.TEN) > 15
        || sinhVien.HO.find('|') != string::npos
        || sinhVien.TEN.find('|') != string::npos) {
        loi = "Họ hoặc tên sinh viên không hợp lệ.";
        return false;
    }
    if (!PhaiHopLe(sinhVien.PHAI)) {
        loi = u8"Phái chỉ được là Nam hoặc Nữ.";
        return false;
    }
    if (!SoDienThoaiHopLe(sinhVien.SODT)) {
        loi = "Số điện thoại không được chứa chữ; chỉ được chứa chữ số, bắt đầu bằng 0 và dài từ 9 đến 11 số.";
        return false;
    }
    return true;
}

bool DocMotDongMonHoc(
    string dong,
    Monhoc& monHoc,
    string& loi
) {
    if (!LaChuoiUtf8HopLe(dong)) {
        loi = "Dữ liệu môn học phải dùng mã hóa UTF-8.";
        return false;
    }

    string cot[4];
    if (!TachChuoi(dong, '|', cot, 4)) {
        loi = "Mỗi dòng môn học phải có đúng 4 cột, ngăn cách bởi ký tự |.";
        return false;
    }

    monHoc.MAMH = ChuanHoaMa(cot[0]);
    monHoc.TENMH = XoaKhoangTrangThua(cot[1]);
    if (!ChuyenSangSoNguyen(cot[2], monHoc.STCLT)
        || !ChuyenSangSoNguyen(cot[3], monHoc.STCTH)) {
        loi = "Số tín chỉ lý thuyết và thực hành phải là số nguyên.";
        return false;
    }
    if (!MaSinhVienHopLe(monHoc.MAMH) || monHoc.MAMH.size() > 10) {
        loi = "Mã môn học trong tệp phải gồm chữ, số và tối đa 10 ký tự.";
        return false;
    }
    if (monHoc.TENMH.empty() || DemSoKyTuUtf8(monHoc.TENMH) > 50) {
        loi = "Tên môn học trong tệp phải có từ 1 đến 50 ký tự.";
        return false;
    }
    if (monHoc.STCLT < 1 || monHoc.STCLT > 20 || monHoc.STCTH < 0 || monHoc.STCTH > 20) {
        loi = "Số tín chỉ trong tệp không hợp lệ.";
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

bool DocMotDongLopTinChi(
    string dong,
    Loptinchi& lopTinChi,
    string& loi
) {
    if (!LaChuoiUtf8HopLe(dong)) {
        loi = "Dữ liệu lớp tín chỉ phải dùng mã hóa UTF-8.";
        return false;
    }

    string cot[8];
    if (!TachChuoi(dong, '|', cot, 8)) {
        loi = "Mỗi dòng lớp tín chỉ phải có đúng 8 cột.";
        return false;
    }

    int huyLop = 0;
    if (!ChuyenSangSoNguyen(cot[0], lopTinChi.MALOPTC)
        || !ChuyenSangSoNguyen(cot[3], lopTinChi.HOCKY)
        || !ChuyenSangSoNguyen(cot[4], lopTinChi.NHOM)
        || !ChuyenSangSoNguyen(cot[5], lopTinChi.SOSVMIN)
        || !ChuyenSangSoNguyen(cot[6], lopTinChi.SOSVMAX)
        || !ChuyenSangSoNguyen(cot[7], huyLop)) {
        loi = "Mã lớp, học kỳ, nhóm, sĩ số và trạng thái phải là số nguyên.";
        return false;
    }

    lopTinChi.MAMH = ChuanHoaMa(cot[1]);
    lopTinChi.NIENKHOA = XoaKhoangTrangDauCuoi(cot[2]);
    lopTinChi.HUYLOP = huyLop == 1;
    lopTinChi.dssvdk = nullptr;

    if (lopTinChi.MALOPTC <= 0) {
        loi = "Mã lớp tín chỉ phải lớn hơn 0.";
        return false;
    }
    if (lopTinChi.MAMH.empty()) {
        loi = "Mã môn học không được để trống.";
        return false;
    }
    if (!NienKhoaHopLe(lopTinChi.NIENKHOA)) {
        loi = "Niên khóa phải có dạng YYYY-YYYY và hai năm liên tiếp.";
        return false;
    }
    if (!HocKyHopLe(lopTinChi.HOCKY)
        || !NhomHopLe(lopTinChi.NHOM)) {
        loi = "Học kỳ phải từ 1 đến 3 và nhóm phải lớn hơn 0.";
        return false;
    }
    if (!SiSoHopLe(lopTinChi.SOSVMIN, lopTinChi.SOSVMAX)) {
        loi = "Sĩ số phải thỏa mãn 0 < tối thiểu <= tối đa.";
        return false;
    }
    if (huyLop != 0 && huyLop != 1) {
        loi = "Trạng thái hủy lớp chỉ được là 0 hoặc 1.";
        return false;
    }
    return true;
}

bool TrungLopTinChiTrongDanhSach(
    DS_LTC& dsLTC,
    Loptinchi lopTinChi,
    string& loi
) {
    for (int i = 0; i < dsLTC.n; ++i) {
        Loptinchi& lopHienTai = *dsLTC.nodes[i];
        if (lopHienTai.MALOPTC == lopTinChi.MALOPTC) {
            loi = "Mã lớp tín chỉ bị trùng.";
            return true;
        }
        if (lopHienTai.MAMH == lopTinChi.MAMH
            && lopHienTai.NIENKHOA == lopTinChi.NIENKHOA
            && lopHienTai.HOCKY == lopTinChi.HOCKY
            && lopHienTai.NHOM == lopTinChi.NHOM) {
            loi = "Lớp tín chỉ bị trùng môn, niên khóa, học kỳ và nhóm.";
            return true;
        }
    }
    return false;
}

bool DocDongDangKy(string dong, Loptinchi& lop, string& loi) {
    string cot[4];
    bool cuBonCot = TachChuoi(dong, '|', cot, 4);
    if (!cuBonCot && !TachChuoi(dong, '|', cot, 3)) {
        loi = "Dòng đăng ký phải có 3 cột: mã SV, điểm, hủy đăng ký.";
        return false;
    }
    string maSV = ChuanHoaMa(cot[0]);
    int huy = 0, daDiem = 0;
    float diem = 0;
    if (!MaSinhVienHopLe(maSV)) {
        loi = "Mã sinh viên đăng ký không hợp lệ.";
        return false;
    }
    if (!ChuyenSangSoNguyen(cot[2], huy)
        || (cuBonCot && !ChuyenSangSoNguyen(cot[3], daDiem))
        || (huy != 0 && huy != 1) || (daDiem != 0 && daDiem != 1)) {
        loi = "Trạng thái đăng ký và điểm chỉ được là 0 hoặc 1.";
        return false;
    }
    try {
        string chuoi = XoaKhoangTrangDauCuoi(cot[1]);
        size_t cuoi = 0;
        diem = std::stof(chuoi, &cuoi);
        if (cuoi != chuoi.size() || !std::isfinite(diem) || (diem != -1.0F && !DiemHopLe(diem))) {
            loi = "Điểm phải từ 0 đến 10 hoặc -1 nếu chưa nhập.";
            return false;
        }
    } catch (std::exception&) {
        loi = "Điểm phải từ 0 đến 10 hoặc -1 nếu chưa nhập.";
        return false;
    }
    if (cuBonCot && !daDiem) diem = -1.0F;
    PTRDK cuoi = nullptr;
    for (PTRDK node = lop.dssvdk; node != nullptr; node = node->next) {
        if (node->dk.MASV == maSV) {
            loi = "Sinh viên bị trùng trong lớp tín chỉ.";
            return false;
        }
        cuoi = node;
    }
    PTRDK moi = new nodeDK{{maSV, diem, huy == 1}, nullptr};
    if (cuoi == nullptr) lop.dssvdk = moi;
    else cuoi->next = moi;
    return true;
}


bool DocDanhSachMonHoc(
    string tenFile,
    treeMH& dsMonHoc,
    int& n,
    string& loi
) {
    loi.clear();
    ifstream tep(filesystem::u8path(tenFile));
    if (!tep.is_open()) {
        loi = "Không thể mở tệp môn học để đọc: " + tenFile;
        return false;
    }

    GiaiPhongCayMonHoc(dsMonHoc);
    n = 0;
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
            || !ThemMonHoc(dsMonHoc, n, monHoc, loiDong)) {
            GiaiPhongCayMonHoc(dsMonHoc);
            n = 0;
            loi = "Lỗi tại dòng " + to_string(soDong) + ": " + loiDong;
            return false;
        }
    }

    if (tep.bad()) {
        GiaiPhongCayMonHoc(dsMonHoc);
        n = 0;
        loi = "Không thể đọc hết tệp môn học: " + tenFile;
        return false;
    }

    return true;
}

bool GhiDanhSachMonHoc(string tenFile, treeMH dsMonHoc, string& loi) {
    return GhiAnToan(tenFile, [dsMonHoc](ofstream& tep) {
        return GhiCayMonHoc(tep, dsMonHoc);
    }, loi);
}

bool DocDanhSachLopSinhVien(string tenFile, DS_LOP& dsLop, string& loi) {
    loi.clear();
    ifstream tep(filesystem::u8path(tenFile));
    if (!tep.is_open()) {
        loi = "Không thể mở tệp lớp sinh viên: " + tenFile;
        return false;
    }
    GiaiPhongDanhSachLop(dsLop);
    string dong, maLop;
    int soDong = 0;
    while (getline(tep, dong)) {
        ChuanHoaDong(dong, ++soDong);
        if (XoaKhoangTrangDauCuoi(dong).empty()) continue;
        string loiDong;
        if (!LaChuoiUtf8HopLe(dong)) {
            loiDong = "Dữ liệu phải dùng mã hóa UTF-8.";
        } else if (dong == "#") {
            if (maLop.empty()) loiDong = "Dấu # không có lớp tương ứng.";
            else maLop.clear();
        } else if (maLop.empty()) {
            string cot[2];
            if (!TachChuoi(dong, '|', cot, 2)) {
                loiDong = "Dòng lớp phải có 2 cột: mã lớp, tên lớp.";
            } else {
                string ma = ChuanHoaMa(cot[0]);
                string ten = XoaKhoangTrangThua(cot[1]);
                if (!MaHopLe(ma, 15)) {
                    loiDong = "Mã lớp trong tệp không hợp lệ, tối đa 15 ký tự.";
                } else if (TenLopHopLe(ten, loiDong)
                           && ThemLop(dsLop, Lop{ma, ten, nullptr}, loiDong)) {
                    maLop = ma;
                }
            }
        } else {
            string cot[5];
            if (!TachChuoi(dong, '|', cot, 5)) {
                loiDong = "Dòng sinh viên phải có 5 cột; kết thúc lớp bằng #.";
            } else {
                Sinhvien sv{ChuanHoaMa(cot[0]), ChuanHoaHoTen(cot[1]),
                    ChuanHoaHoTen(cot[2]), ChuanHoaHoTen(cot[3]), XoaKhoangTrangDauCuoi(cot[4])};
                if (KiemTraSinhVienTrongTep(sv, loiDong))
                    ThemSinhVien(dsLop, maLop, sv, loiDong);
            }
        }
        if (!loiDong.empty()) {
            GiaiPhongDanhSachLop(dsLop);
            loi = "Lỗi tại dòng " + to_string(soDong) + ": " + loiDong;
            return false;
        }
    }
    if (tep.bad() || !maLop.empty()) {
        GiaiPhongDanhSachLop(dsLop);
        loi = tep.bad() ? "Không thể đọc hết tệp lớp sinh viên."
                       : "Thiếu dấu # kết thúc lớp " + maLop + ".";
        return false;
    }
    return true;
}

bool GhiDanhSachLopSinhVien(string tenFile, DS_LOP& dsLop, string& loi) {
    return GhiAnToan(tenFile, [&dsLop](ofstream& tep) {
        for (int i = 0; i < dsLop.n; ++i) {
            Lop& lop = dsLop.nodes[i];
            tep << lop.MALOP << '|' << lop.TENLOP << '\n';
            for (PTRSV node = lop.dssv; node != nullptr; node = node->next) {
                Sinhvien& sv = node->sv;
                tep << sv.MASV << '|' << sv.HO << '|' << sv.TEN << '|'
                    << sv.PHAI << '|' << sv.SODT << '\n';
            }
            tep << "#\n";
        }
        return tep.good();
    }, loi);
}

bool DocDanhSachLopTinChi(string tenFile, DS_LTC& dsLTC, string& loi) {
    loi.clear();
    ifstream tep(filesystem::u8path(tenFile));
    if (!tep.is_open()) {
        loi = "Không thể mở tệp lớp tín chỉ: " + tenFile;
        return false;
    }
    GiaiPhongDanhSachLopTinChi(dsLTC);
    Loptinchi* lop = nullptr;
    string dong;
    int soDong = 0;
    while (getline(tep, dong)) {
        ChuanHoaDong(dong, ++soDong);
        if (XoaKhoangTrangDauCuoi(dong).empty()) continue;
        string loiDong;
        if (!LaChuoiUtf8HopLe(dong)) {
            loiDong = "Dữ liệu phải dùng mã hóa UTF-8.";
        } else if (dong == "#") {
            if (lop == nullptr) loiDong = "Dấu # không có lớp tín chỉ tương ứng.";
            else lop = nullptr;
        } else if (lop == nullptr) {
            Loptinchi thongTin{};
            if (dsLTC.n >= MAXLTC) {
                loiDong = "Danh sách lớp tín chỉ vượt quá kích thước tối đa.";
            } else if (DocMotDongLopTinChi(dong, thongTin, loiDong)
                       && !TrungLopTinChiTrongDanhSach(dsLTC, thongTin, loiDong)) {
                if (thongTin.MALOPTC == numeric_limits<int>::max()) {
                    loiDong = "Mã lớp tín chỉ đã đạt giới hạn.";
                } else {
                    lop = new Loptinchi(thongTin);
                    dsLTC.nodes[dsLTC.n++] = lop;
                    dsLTC.maTiepTheo = max(dsLTC.maTiepTheo, lop->MALOPTC + 1);
                }
            }
        } else {
            DocDongDangKy(dong, *lop, loiDong);
        }
        if (!loiDong.empty()) {
            GiaiPhongDanhSachLopTinChi(dsLTC);
            loi = "Lỗi tại dòng " + to_string(soDong) + ": " + loiDong;
            return false;
        }
    }
    if (tep.bad() || lop != nullptr) {
        GiaiPhongDanhSachLopTinChi(dsLTC);
        loi = tep.bad() ? "Không thể đọc hết tệp lớp tín chỉ."
                       : "Thiếu dấu # kết thúc lớp tín chỉ.";
        return false;
    }
    return true;
}

bool GhiDanhSachLopTinChi(string tenFile, DS_LTC& dsLTC, string& loi) {
    return GhiAnToan(tenFile, [&dsLTC](ofstream& tep) {
        for (int i = 0; i < dsLTC.n; ++i) {
            Loptinchi* lop = dsLTC.nodes[i];
            tep << lop->MALOPTC << '|' << lop->MAMH << '|'
                << lop->NIENKHOA << '|' << lop->HOCKY << '|' << lop->NHOM << '|'
                << lop->SOSVMIN << '|' << lop->SOSVMAX << '|'
                << (lop->HUYLOP ? 1 : 0) << '\n';
            for (PTRDK node = lop->dssvdk; node != nullptr; node = node->next) {
                DangKy& dk = node->dk;
                tep << dk.MASV << '|' << dk.DIEM << '|'
                    << (dk.HUYDK ? 1 : 0) << '\n';
            }
            tep << "#\n";
        }
        return tep.good();
    }, loi);
}
