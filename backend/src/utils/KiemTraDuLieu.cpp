#include "../../include/utils/KiemTraDuLieu.h"

#include <ctime>

#include "../../include/utils/XuLyChuoi.h"

namespace {

constexpr int THANG_BAT_DAU_NIEN_KHOA = 8;

bool TachNienKhoa(
    const string& nienKhoa,
    int& namBatDau,
    int& namKetThuc
) {
    if (nienKhoa.size() != 9 || nienKhoa[4] != '-') {
        return false;
    }

    namBatDau = 0;
    namKetThuc = 0;
    for (int i = 0; i < 4; ++i) {
        const char kyTuNamDau = nienKhoa[i];
        const char kyTuNamCuoi = nienKhoa[i + 5];
        if (kyTuNamDau < '0' || kyTuNamDau > '9'
            || kyTuNamCuoi < '0' || kyTuNamCuoi > '9') {
            return false;
        }
        namBatDau = namBatDau * 10 + (kyTuNamDau - '0');
        namKetThuc = namKetThuc * 10 + (kyTuNamCuoi - '0');
    }
    return true;
}

int LayNamBatDauNienKhoaHienTai() {
    const std::time_t bayGio = std::time(nullptr);
    std::tm thoiGianDiaPhuong{};
#ifdef _WIN32
    localtime_s(&thoiGianDiaPhuong, &bayGio);
#else
    localtime_r(&bayGio, &thoiGianDiaPhuong);
#endif
    const int namHienTai = thoiGianDiaPhuong.tm_year + 1900;
    const int thangHienTai = thoiGianDiaPhuong.tm_mon + 1;
    return thangHienTai >= THANG_BAT_DAU_NIEN_KHOA
        ? namHienTai : namHienTai - 1;
}

}  // namespace

bool LaChuoiRong(const string& chuoi) {
    return XoaKhoangTrangDauCuoi(chuoi).empty();
}

bool MaHopLe(const string& ma, int doDaiToiDa) {
    const string daCat = XoaKhoangTrangDauCuoi(ma);
    if (daCat.empty() || doDaiToiDa <= 0
        || static_cast<int>(daCat.size()) > doDaiToiDa) {
        return false;
    }
    for (char kyTu : daCat) {
        const bool laChu = (kyTu >= 'A' && kyTu <= 'Z')
            || (kyTu >= 'a' && kyTu <= 'z');
        const bool laSo = kyTu >= '0' && kyTu <= '9';
        if (!laChu && !laSo && kyTu != '-' && kyTu != '_') {
            return false;
        }
    }
    return true;
}

bool MaSinhVienHopLe(const string& maSV) {
    return MaHopLe(maSV, 15);
}

bool SoDienThoaiHopLe(const string& soDienThoai) {
    const string daCat = XoaKhoangTrangDauCuoi(soDienThoai);
    if (daCat.size() < 9 || daCat.size() > 11) {
        return false;
    }
    for (char kyTu : daCat) {
        if (kyTu < '0' || kyTu > '9') {
            return false;
        }
    }
    return true;
}

bool PhaiHopLe(const string& phai) {
    const string daChuanHoa = ChuanHoaHoTen(phai);
    return daChuanHoa == "Nam" || daChuanHoa == u8"Nữ";
}

bool NienKhoaHopLe(const string& nienKhoa) {
    int namBatDau = 0;
    int namKetThuc = 0;
    return TachNienKhoa(nienKhoa, namBatDau, namKetThuc)
        && namBatDau > 0 && namKetThuc == namBatDau + 1;
}

string NienKhoaHienTai() {
    const int namBatDau = LayNamBatDauNienKhoaHienTai();
    return std::to_string(namBatDau) + "-" + std::to_string(namBatDau + 1);
}

bool NienKhoaKhongCuHonHienTai(const string& nienKhoa) {
    int namBatDau = 0;
    int namKetThuc = 0;
    return TachNienKhoa(nienKhoa, namBatDau, namKetThuc)
        && namBatDau > 0 && namKetThuc == namBatDau + 1
        && namBatDau >= LayNamBatDauNienKhoaHienTai();
}

bool HocKyHopLe(int hocKy) {
    return hocKy >= 1 && hocKy <= 3;
}

bool NhomHopLe(int nhom) {
    return nhom > 0;
}

bool SiSoHopLe(int soSVMin, int soSVMax) {
    return soSVMin > 0 && soSVMin <= soSVMax;
}

bool DiemHopLe(float diem) {
    return diem >= 0.0F && diem <= 10.0F;
}
