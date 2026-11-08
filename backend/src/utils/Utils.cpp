#include "../KhaiBao.h"

#include <ctime>
#include <limits>
#include <string>

namespace {

// ==========================================
// VIETNAMESE COMPARISON TABLES & FUNCTIONS
// ==========================================

const int SO_CHU = 33;
const int SO_DAU = 6;

const string CHU_THUONG[SO_CHU][SO_DAU] = {
    {"a", "à", "ả", "ã", "á", "ạ"}, {"ă", "ằ", "ẳ", "ẵ", "ắ", "ặ"},
    {"â", "ầ", "ẩ", "ẫ", "ấ", "ậ"}, {"b"}, {"c"}, {"d"}, {"đ"},
    {"e", "è", "ẻ", "ẽ", "é", "ẹ"}, {"ê", "ề", "ể", "ễ", "ế", "ệ"},
    {"f"}, {"g"}, {"h"},
    {"i", "ì", "ỉ", "ĩ", "í", "ị"},
    {"j"}, {"k"}, {"l"}, {"m"}, {"n"},
    {"o", "ò", "ỏ", "õ", "ó", "ọ"}, {"ô", "ồ", "ổ", "ỗ", "ố", "ộ"},
    {"ơ", "ờ", "ở", "ỡ", "ớ", "ợ"},
    {"p"}, {"q"}, {"r"}, {"s"}, {"t"},
    {"u", "ù", "ủ", "ũ", "ú", "ụ"}, {"ư", "ừ", "ử", "ữ", "ứ", "ự"},
    {"v"}, {"w"}, {"x"},
    {"y", "ỳ", "ỷ", "ỹ", "ý", "ỵ"}, {"z"}};

const string CHU_HOA[SO_CHU][SO_DAU] = {
    {"A", "À", "Ả", "Ã", "Á", "Ạ"}, {"Ă", "Ằ", "Ẳ", "Ẵ", "Ắ", "Ặ"},
    {"Â", "Ầ", "Ẩ", "Ẫ", "Ấ", "Ậ"}, {"B"}, {"C"}, {"D"}, {"Đ"},
    {"E", "È", "Ẻ", "Ẽ", "É", "Ẹ"}, {"Ê", "Ề", "Ể", "Ễ", "Ế", "Ệ"},
    {"F"}, {"G"}, {"H"},
    {"I", "Ì", "Ỉ", "Ĩ", "Í", "Ị"},
    {"J"}, {"K"}, {"L"}, {"M"}, {"N"},
    {"O", "Ò", "Ỏ", "Õ", "Ó", "Ọ"}, {"Ô", "Ồ", "Ổ", "Ỗ", "Ố", "Ộ"},
    {"Ơ", "Ờ", "Ở", "Ỡ", "Ớ", "Ợ"},
    {"P"}, {"Q"}, {"R"}, {"S"}, {"T"},
    {"U", "Ù", "Ủ", "Ũ", "Ú", "Ụ"}, {"Ư", "Ừ", "Ử", "Ữ", "Ứ", "Ự"},
    {"V"}, {"W"}, {"X"},
    {"Y", "Ỳ", "Ỷ", "Ỹ", "Ý", "Ỵ"}, {"Z"}};

// Read one UTF-8 code point; consume invalid bytes separately for deterministic fallback.
unsigned int DocMaUtf8(string& chuoi, size_t& viTri) {
    unsigned char dau = static_cast<unsigned char>(chuoi[viTri++]);
    if (dau < 0x80) return dau;
    int them = 0;
    unsigned int ma = 0;
    if (dau >= 0xC2 && dau <= 0xDF) { them = 1; ma = dau & 0x1F; }
    else if (dau >= 0xE0 && dau <= 0xEF) { them = 2; ma = dau & 0x0F; }
    else if (dau >= 0xF0 && dau <= 0xF4) { them = 3; ma = dau & 0x07; }
    else return dau;
    if (viTri + them > chuoi.size()) return dau;
    for (int i = 0; i < them; ++i) {
        unsigned char byte = static_cast<unsigned char>(chuoi[viTri + i]);
        if ((byte & 0xC0) != 0x80) return dau;
        ma = (ma << 6) | (byte & 0x3F);
    }
    viTri += them;
    return ma;
}

bool timChuCai(string& tu, size_t i, int& chu, int& dau, size_t& doDai) {
    bool timThay = false;
    for (int r = 0; r < SO_CHU && !timThay; ++r) {
        for (int t = 0; t < SO_DAU; ++t) {
            string a = CHU_THUONG[r][t];
            string b = CHU_HOA[r][t];
            if ((!a.empty() && tu.compare(i, a.size(), a) == 0)
                || (!b.empty() && tu.compare(i, b.size(), b) == 0)) {
                chu = r; dau = t; doDai = a.size();
                timThay = true;
                break;
            }
        }
    }
    if (!timThay) return false;

    // Accept decomposed Vietnamese too, including dot-below before circumflex.
    size_t viTri = i + doDai;
    while (viTri < tu.size()) {
        size_t tiep = viTri;
        unsigned int ma = DocMaUtf8(tu, tiep);
        bool laNguyenAm = chu == 0 || chu == 1 || chu == 2 || chu == 7
            || chu == 8 || chu == 12 || chu == 18 || chu == 19 || chu == 20
            || chu == 26 || chu == 27 || chu == 31;
        if (laNguyenAm && ma == 0x300) dau = 1;
        else if (laNguyenAm && ma == 0x309) dau = 2;
        else if (laNguyenAm && ma == 0x303) dau = 3;
        else if (laNguyenAm && ma == 0x301) dau = 4;
        else if (laNguyenAm && ma == 0x323) dau = 5;
        else if (ma == 0x306 && chu == 0) chu = 1;
        else if (ma == 0x302 && chu == 0) chu = 2;
        else if (ma == 0x302 && chu == 7) chu = 8;
        else if (ma == 0x302 && chu == 18) chu = 19;
        else if (ma == 0x31B && chu == 18) chu = 20;
        else if (ma == 0x31B && chu == 26) chu = 27;
        else break;
        viTri = tiep;
    }
    doDai = viTri - i;
    return true;
}

unsigned int DocTrongSoChu(string& chuoi, size_t& viTri, int& dau) {
    int chu;
    size_t doDai;
    dau = 0;
    if (timChuCai(chuoi, viTri, chu, dau, doDai)) {
        viTri += doDai;
        return 0x100 + chu;
    }
    unsigned int ma = DocMaUtf8(chuoi, viTri);
    return ma < 0x80 ? ma : 0x10000 + ma;
}


constexpr int THANG_BAT_DAU_NIEN_KHOA = 8;

bool LaKhoangTrangAscii(unsigned char kyTu) {
    return kyTu == ' '
        || kyTu == '\t'
        || kyTu == '\n'
        || kyTu == '\r'
        || kyTu == '\f'
        || kyTu == '\v';
}

bool TachNienKhoa(
    string nienKhoa,
    int& namBatDau,
    int& namKetThuc
) {
    if (nienKhoa.size() != 9 || nienKhoa[4] != '-') {
        return false;
    }

    namBatDau = 0;
    namKetThuc = 0;
    for (int i = 0; i < 4; ++i) {
        char kyTuNamDau = nienKhoa[i];
        char kyTuNamCuoi = nienKhoa[i + 5];
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
    std::time_t bayGio = std::time(nullptr);
    std::tm thoiGianDiaPhuong{};
#ifdef _WIN32
    localtime_s(&thoiGianDiaPhuong, &bayGio);
#else
    localtime_r(&bayGio, &thoiGianDiaPhuong);
#endif
    int namHienTai = thoiGianDiaPhuong.tm_year + 1900;
    int thangHienTai = thoiGianDiaPhuong.tm_mon + 1;
    return thangHienTai >= THANG_BAT_DAU_NIEN_KHOA
        ? namHienTai : namHienTai - 1;
}

}  // namespace

// ==========================================
// STRING PROCESSING
// ==========================================

string XoaKhoangTrangDauCuoi(string chuoi) {
    size_t batDau = 0;
    while (batDau < chuoi.size()
           && LaKhoangTrangAscii(
               static_cast<unsigned char>(chuoi[batDau])
           )) {
        ++batDau;
    }

    size_t ketThuc = chuoi.size();
    while (ketThuc > batDau
           && LaKhoangTrangAscii(
               static_cast<unsigned char>(chuoi[ketThuc - 1])
           )) {
        --ketThuc;
    }
    return chuoi.substr(batDau, ketThuc - batDau);
}

string XoaKhoangTrangThua(string chuoi) {
    string daCat = XoaKhoangTrangDauCuoi(chuoi);
    string ketQua;
    ketQua.reserve(daCat.size());
    bool kyTuTruocLaKhoangTrang = false;

    for (char kyTu : daCat) {
        bool laKhoangTrang =
            LaKhoangTrangAscii(static_cast<unsigned char>(kyTu));
        if (!laKhoangTrang) {
            ketQua.push_back(kyTu);
        } else if (!kyTuTruocLaKhoangTrang) {
            ketQua.push_back(' ');
        }
        kyTuTruocLaKhoangTrang = laKhoangTrang;
    }
    return ketQua;
}

string ChuyenThanhChuHoa(string chuoi) {
    string ketQua;
    for (size_t i = 0; i < chuoi.size();) {
        int chu, dau;
        size_t doDai;
        if (timChuCai(chuoi, i, chu, dau, doDai)) {
            ketQua += CHU_HOA[chu][dau];
            i += doDai;
        } else {
            size_t batDau = i;
            DocMaUtf8(chuoi, i);
            ketQua.append(chuoi, batDau, i - batDau);
        }
    }
    return ketQua;
}

string ChuyenThanhChuThuong(string chuoi) {
    string ketQua;
    for (size_t i = 0; i < chuoi.size();) {
        int chu, dau;
        size_t doDai;
        if (timChuCai(chuoi, i, chu, dau, doDai)) {
            ketQua += CHU_THUONG[chu][dau];
            i += doDai;
        } else {
            size_t batDau = i;
            DocMaUtf8(chuoi, i);
            ketQua.append(chuoi, batDau, i - batDau);
        }
    }
    return ketQua;
}

string ChuanHoaMa(string ma) {
    return ChuyenThanhChuHoa(XoaKhoangTrangDauCuoi(ma));
}

string ChuanHoaHoTen(string hoTen) {
    string daCat = XoaKhoangTrangThua(hoTen);
    string ketQua;
    bool dauTu = true;
    for (size_t i = 0; i < daCat.size();) {
        int chu, dau;
        size_t doDai;
        if (timChuCai(daCat, i, chu, dau, doDai)) {
            ketQua += dauTu ? CHU_HOA[chu][dau] : CHU_THUONG[chu][dau];
            dauTu = false;
            i += doDai;
        } else {
            size_t batDau = i;
            unsigned int ma = DocMaUtf8(daCat, i);
            ketQua.append(daCat, batDau, i - batDau);
            dauTu = ma == ' ';
        }
    }
    return ketQua;
}

bool ChuyenSangSoNguyen(string chuoi, int& ketQua) {
    try {
        string daCat = XoaKhoangTrangDauCuoi(chuoi);
        size_t viTriCuoi = 0;
        long long so = std::stoll(daCat, &viTriCuoi);
        if (viTriCuoi != daCat.size()
            || so < std::numeric_limits<int>::min()
            || so > std::numeric_limits<int>::max()) {
            return false;
        }
        ketQua = static_cast<int>(so);
        return true;
    } catch (std::exception&) {
        return false;
    }
}

bool TachChuoi(
    string chuoi,
    char kyTuPhanCach,
    string dsKetQua[],
    int soPhanTu
) {
    if (dsKetQua == nullptr || soPhanTu <= 0) {
        return false;
    }

    int soPhanTuDaTach = 0;
    size_t viTriBatDau = 0;
    for (size_t i = 0; i <= chuoi.size(); ++i) {
        if (i < chuoi.size() && chuoi[i] != kyTuPhanCach) {
            continue;
        }
        if (soPhanTuDaTach >= soPhanTu) {
            return false;
        }
        dsKetQua[soPhanTuDaTach++] = chuoi.substr(
            viTriBatDau,
            i - viTriBatDau
        );
        viTriBatDau = i + 1;
    }
    return soPhanTuDaTach == soPhanTu;
}

bool LaChuoiUtf8HopLe(string chuoi) {
    auto* duLieu = reinterpret_cast<unsigned char*>(chuoi.data());
    size_t viTri = 0;

    while (viTri < chuoi.size()) {
        unsigned char byteDau = duLieu[viTri];
        if (byteDau <= 0x7F) {
            ++viTri;
            continue;
        }

        size_t soByte = 0;
        unsigned char byteHaiNhoNhat = 0x80;
        unsigned char byteHaiLonNhat = 0xBF;
        if (byteDau >= 0xC2 && byteDau <= 0xDF) {
            soByte = 2;
        } else if (byteDau == 0xE0) {
            soByte = 3;
            byteHaiNhoNhat = 0xA0;
        } else if (byteDau >= 0xE1 && byteDau <= 0xEC) {
            soByte = 3;
        } else if (byteDau == 0xED) {
            soByte = 3;
            byteHaiLonNhat = 0x9F;
        } else if (byteDau >= 0xEE && byteDau <= 0xEF) {
            soByte = 3;
        } else if (byteDau == 0xF0) {
            soByte = 4;
            byteHaiNhoNhat = 0x90;
        } else if (byteDau >= 0xF1 && byteDau <= 0xF3) {
            soByte = 4;
        } else if (byteDau == 0xF4) {
            soByte = 4;
            byteHaiLonNhat = 0x8F;
        } else {
            return false;
        }

        if (viTri + soByte > chuoi.size()
            || duLieu[viTri + 1] < byteHaiNhoNhat
            || duLieu[viTri + 1] > byteHaiLonNhat) {
            return false;
        }
        for (size_t i = 2; i < soByte; ++i) {
            if (duLieu[viTri + i] < 0x80 || duLieu[viTri + i] > 0xBF) {
                return false;
            }
        }
        viTri += soByte;
    }
    return true;
}

std::size_t DemSoKyTuUtf8(string chuoi) {
    std::size_t soKyTu = 0;
    for (unsigned char byte : chuoi) {
        if ((byte & 0xC0) != 0x80) {
            ++soKyTu;
        }
    }
    return soKyTu;
}

int SoSanhKhongPhanBietHoaThuong(string chuoi1, string chuoi2) {
    size_t i = 0, j = 0;
    int soSanhDau = 0;
    while (i < chuoi1.size() && j < chuoi2.size()) {
        int dau1, dau2;
        unsigned int chu1 = DocTrongSoChu(chuoi1, i, dau1);
        unsigned int chu2 = DocTrongSoChu(chuoi2, j, dau2);
        if (chu1 != chu2) return chu1 < chu2 ? -1 : 1;
        // Alphabet order has priority over tone differences throughout the string.
        if (soSanhDau == 0 && dau1 != dau2) soSanhDau = dau1 < dau2 ? -1 : 1;
    }
    if (i < chuoi1.size()) return 1;
    if (j < chuoi2.size()) return -1;
    return soSanhDau;
}

// ==========================================
// DATA VALIDATION
// ==========================================

bool MaHopLe(string ma, int doDaiToiDa) {
    string daCat = XoaKhoangTrangDauCuoi(ma);
    if (daCat.empty() || doDaiToiDa <= 0
        || static_cast<int>(daCat.size()) > doDaiToiDa) {
        return false;
    }
    for (char kyTu : daCat) {
        bool laChu = (kyTu >= 'A' && kyTu <= 'Z')
            || (kyTu >= 'a' && kyTu <= 'z');
        bool laSo = kyTu >= '0' && kyTu <= '9';
        if (!laChu && !laSo && kyTu != '-' && kyTu != '_') {
            return false;
        }
    }
    return true;
}

bool MaSinhVienHopLe(string maSV) {
    string maDaChuanHoa = ChuanHoaMa(maSV);
    if (maDaChuanHoa.empty() || maDaChuanHoa.size() > 15) {
        return false;
    }
    for (char kyTu : maDaChuanHoa) {
        if (!((kyTu >= 'A' && kyTu <= 'Z')
              || (kyTu >= '0' && kyTu <= '9'))) {
            return false;
        }
    }
    return true;
}

bool TenLopHopLe(string tenLop, string& loi) {
    if (tenLop.empty()
        || DemSoKyTuUtf8(tenLop) > 50
        || tenLop.find('|') != string::npos) {
        loi = "Tên lớp không hợp lệ, tối đa 50 ký tự và không chứa |.";
        return false;
    }
    return true;
}

bool SoDienThoaiHopLe(string soDienThoai) {
    string daCat = XoaKhoangTrangDauCuoi(soDienThoai);
    if (daCat.size() < 9 || daCat.size() > 11 || daCat.front() != '0') {
        return false;
    }
    for (char kyTu : daCat) {
        if (kyTu < '0' || kyTu > '9') {
            return false;
        }
    }
    return true;
}

bool PhaiHopLe(string phai) {
    string daChuanHoa = ChuanHoaHoTen(phai);
    return daChuanHoa == "Nam" || daChuanHoa == u8"Nữ";
}

bool NienKhoaHopLe(string nienKhoa) {
    int namBatDau = 0;
    int namKetThuc = 0;
    return TachNienKhoa(nienKhoa, namBatDau, namKetThuc)
        && namBatDau > 0 && namKetThuc == namBatDau + 1;
}

string NienKhoaHienTai() {
    int namBatDau = LayNamBatDauNienKhoaHienTai();
    return std::to_string(namBatDau) + "-" + std::to_string(namBatDau + 1);
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

