#include "../../include/utils/XuLyChuoi.h"

#include <algorithm>
#include <cctype>
#include <limits>

namespace {

bool LaKhoangTrangAscii(unsigned char kyTu) {
    return kyTu == ' '
        || kyTu == '\t'
        || kyTu == '\n'
        || kyTu == '\r'
        || kyTu == '\f'
        || kyTu == '\v';
}

char ChuyenThanhChuHoaAscii(unsigned char kyTu) {
    if (kyTu >= 'a' && kyTu <= 'z') {
        return static_cast<char>(kyTu - 'a' + 'A');
    }
    return static_cast<char>(kyTu);
}

char ChuyenThanhChuThuongAscii(unsigned char kyTu) {
    if (kyTu >= 'A' && kyTu <= 'Z') {
        return static_cast<char>(kyTu - 'A' + 'a');
    }
    return static_cast<char>(kyTu);
}

}  // namespace

string XoaKhoangTrangDauCuoi(const string& chuoi) {
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

string XoaKhoangTrangThua(const string& chuoi) {
    const string daCat = XoaKhoangTrangDauCuoi(chuoi);
    string ketQua;
    ketQua.reserve(daCat.size());
    bool kyTuTruocLaKhoangTrang = false;

    for (char kyTu : daCat) {
        const bool laKhoangTrang =
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

string ChuyenThanhChuHoa(const string& chuoi) {
    string ketQua = chuoi;
    std::transform(
        ketQua.begin(),
        ketQua.end(),
        ketQua.begin(),
        [](unsigned char kyTu) {
            return ChuyenThanhChuHoaAscii(kyTu);
        }
    );
    return ketQua;
}

string ChuyenThanhChuThuong(const string& chuoi) {
    string ketQua = chuoi;
    std::transform(
        ketQua.begin(),
        ketQua.end(),
        ketQua.begin(),
        [](unsigned char kyTu) {
            return ChuyenThanhChuThuongAscii(kyTu);
        }
    );
    return ketQua;
}

string ChuanHoaMa(const string& ma) {
    return ChuyenThanhChuHoa(XoaKhoangTrangDauCuoi(ma));
}

string ChuanHoaHoTen(const string& hoTen) {
    string ketQua = ChuyenThanhChuThuong(XoaKhoangTrangThua(hoTen));
    bool vietHoaKyTuTiepTheo = true;
    for (char& kyTu : ketQua) {
        if (kyTu == ' ') {
            vietHoaKyTuTiepTheo = true;
        } else if (vietHoaKyTuTiepTheo) {
            kyTu = ChuyenThanhChuHoaAscii(
                static_cast<unsigned char>(kyTu)
            );
            vietHoaKyTuTiepTheo = false;
        }
    }
    return ketQua;
}

bool ChuyenSangSoNguyen(const string& chuoi, int& ketQua) {
    try {
        const string daCat = XoaKhoangTrangDauCuoi(chuoi);
        size_t viTriCuoi = 0;
        const long long so = std::stoll(daCat, &viTriCuoi);
        if (viTriCuoi != daCat.size()
            || so < std::numeric_limits<int>::min()
            || so > std::numeric_limits<int>::max()) {
            return false;
        }
        ketQua = static_cast<int>(so);
        return true;
    } catch (const std::exception&) {
        return false;
    }
}

bool TachChuoi(
    const string& chuoi,
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

bool LaChuoiUtf8HopLe(const string& chuoi) {
    const auto* duLieu = reinterpret_cast<const unsigned char*>(chuoi.data());
    size_t viTri = 0;

    while (viTri < chuoi.size()) {
        const unsigned char byteDau = duLieu[viTri];
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

std::size_t DemSoKyTuUtf8(const string& chuoi) {
    std::size_t soKyTu = 0;
    for (unsigned char byte : chuoi) {
        if ((byte & 0xC0) != 0x80) {
            ++soKyTu;
        }
    }
    return soKyTu;
}

int SoSanhKhongPhanBietHoaThuong(
    const string& chuoi1,
    const string& chuoi2
) {
    const string chuoiThuong1 = ChuyenThanhChuThuong(chuoi1);
    const string chuoiThuong2 = ChuyenThanhChuThuong(chuoi2);
    if (chuoiThuong1 < chuoiThuong2) {
        return -1;
    }
    if (chuoiThuong1 > chuoiThuong2) {
        return 1;
    }
    return 0;
}
