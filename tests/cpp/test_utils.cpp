#include <cassert>
#include "../../backend/src/KhaiBao.h"

int main() {
    assert(SoSanhKhongPhanBietHoaThuong(u8"Bảo", u8"Bình") < 0);
    assert(SoSanhKhongPhanBietHoaThuong(u8"Bình", u8"Bảo") > 0);
    assert(SoSanhKhongPhanBietHoaThuong("Ban", u8"Bào") < 0);
    assert(SoSanhKhongPhanBietHoaThuong(u8"Bà", "Ban") < 0);
    assert(SoSanhKhongPhanBietHoaThuong("", "A") < 0);
    assert(SoSanhKhongPhanBietHoaThuong("A", "") > 0);
    assert(SoSanhKhongPhanBietHoaThuong("", "") == 0);
    string bangChu[] = {"a", u8"ă", u8"â", "b", "c", "d", u8"đ",
        "e", u8"ê", "f", "g", "h", "i", "j", "k", "l", "m", "n",
        "o", u8"ô", u8"ơ", "p", "q", "r", "s", "t", "u", u8"ư", "v", "w", "x", "y", "z"};
    for (int i = 0; i < 33; ++i) {
        assert(SoSanhKhongPhanBietHoaThuong(bangChu[i], ChuyenThanhChuHoa(bangChu[i])) == 0);
        for (int j = i + 1; j < 33; ++j)
            assert(SoSanhKhongPhanBietHoaThuong(bangChu[i], bangChu[j]) < 0);
    }
    string dau[] = {"a", u8"à", u8"ả", u8"ã", u8"á", u8"ạ"};
    for (int i = 0; i < 6; ++i) {
        assert(ChuyenThanhChuThuong(ChuyenThanhChuHoa(dau[i])) == dau[i]);
        for (int j = i + 1; j < 6; ++j)
            assert(SoSanhKhongPhanBietHoaThuong(dau[i], dau[j]) < 0);
    }
    assert(SoSanhKhongPhanBietHoaThuong(u8"BA\u0309O", u8"Bảo") == 0);
    assert(SoSanhKhongPhanBietHoaThuong(u8"BI\u0300NH", u8"Bình") == 0);
    assert(SoSanhKhongPhanBietHoaThuong(u8"a\u0323\u0302", u8"ậ") == 0);
    assert(SoSanhKhongPhanBietHoaThuong(u8"a\u0302\u0323", u8"ậ") == 0);
    assert(SoSanhKhongPhanBietHoaThuong(u8"ĐẶNG", u8"đặng") == 0);
    assert(ChuyenThanhChuHoa(u8"đặng bảo bình ươ") == u8"ĐẶNG BẢO BÌNH ƯƠ");
    assert(ChuyenThanhChuThuong(u8"ĐẶNG BẢO BÌNH ƯƠ") == u8"đặng bảo bình ươ");
    assert(ChuanHoaHoTen(u8"  đẶNG   bẢo   BÌNH ") == u8"Đặng Bảo Bình");
    assert(ChuanHoaHoTen(u8"  đA\u0323\u0306NG  ba\u0309o ") == u8"Đặng Bảo");
    assert(PhaiHopLe(u8"NỮ") && PhaiHopLe(u8"nữ"));
    assert(SoSanhKhongPhanBietHoaThuong("SV002", "SV010") < 0);
    return 0;
}
