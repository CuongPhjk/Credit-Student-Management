#include <cassert>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <string>

#include "AppData.h"
#include "MonHocManager.h"

namespace {

std::string docNoiDungFile(const std::filesystem::path& duongDan) {
    std::ifstream tep(duongDan);
    std::ostringstream noiDung;
    noiDung << tep.rdbuf();
    return noiDung.str();
}

}  // namespace

int main() {
    AppData appData;
    MonHocManager manager(appData);
    std::string loi;

    Monhoc lapTrinh{"  int101  ", "  Lap   trinh C++  ", 3, 1};
    assert(manager.themMonHoc(lapTrinh, loi));

    Monhoc coSoDuLieu{"DB101", "Co so du lieu", 3, 0};
    assert(manager.themMonHoc(coSoDuLieu, loi));

    Monhoc khongHopLe{"BAD101", "Mon khong hop le", 0, 1};
    assert(!manager.themMonHoc(khongHopLe, loi));
    assert(!loi.empty());

    Monhoc trungMa{"INT101", "Mon trung ma", 2, 0};
    assert(!manager.themMonHoc(trungMa, loi));

    Monhoc timThay{"", "", 0, 0};
    assert(manager.timMonHoc(" int101 ", timThay));
    assert(timThay.MAMH == "INT101");
    assert(timThay.TENMH == "Lap trinh C++");

    Monhoc danhSach[2];
    const int soLuong = manager.layDanhSachMonHoc(danhSach, 2);
    assert(soLuong == 2);
    assert(danhSach[0].TENMH == "Co so du lieu");
    assert(danhSach[1].TENMH == "Lap trinh C++");

    Monhoc duLieuMoi{"MA_KHONG_DUOC_DOI", "Lap trinh hien dai", 4, 0};
    assert(manager.capNhatMonHoc("int101", duLieuMoi, loi));
    assert(manager.timMonHoc("INT101", timThay));
    assert(timThay.MAMH == "INT101");
    assert(timThay.TENMH == "Lap trinh hien dai");

    Loptinchi* lopTinChi = new Loptinchi{};
    lopTinChi->MALOPTC = 1;
    lopTinChi->MAMH = "INT101";
    appData.dsLopTinChi().nodes[0] = lopTinChi;
    appData.dsLopTinChi().n = 1;
    assert(!manager.xoaMonHoc("INT101", loi));

    assert(manager.xoaMonHoc("DB101", loi));
    assert(manager.tongSoMonHoc() == 1);

    appData.clear();
    assert(manager.tongSoMonHoc() == 0);

    const std::filesystem::path fileMonHoc =
        std::filesystem::current_path() / "monhoc_test.txt";
    {
        std::ofstream tep(fileMonHoc);
        tep << u8"CS102|Hệ điều hành|3|1\n";
    }

    AppData duLieuTuFile;
    MonHocManager managerFile(duLieuTuFile);
    assert(managerFile.docDanhSachMonHoc(fileMonHoc.string(), loi));
    assert(managerFile.tongSoMonHoc() == 1);
    Monhoc monHocUnicode{"", "", 0, 0};
    assert(managerFile.timMonHoc("CS102", monHocUnicode));
    assert(monHocUnicode.TENMH == u8"Hệ điều hành");
    Monhoc danhSachUnicode[1];
    assert(managerFile.layDanhSachMonHoc(danhSachUnicode, 1) == 1);
    assert(danhSachUnicode[0].TENMH == u8"Hệ điều hành");

    Monhoc monThem{"INT101", "Lap trinh Python", 3, 1};
    assert(managerFile.themMonHoc(monThem, loi));
    assert(docNoiDungFile(fileMonHoc)
           == u8"CS102|Hệ điều hành|3|1\n"
              "INT101|Lap trinh Python|3|1\n");

    Monhoc monSua{"CS102", "Cau truc du lieu va giai thuat", 4, 0};
    assert(managerFile.capNhatMonHoc("CS102", monSua, loi));
    assert(docNoiDungFile(fileMonHoc)
           == "CS102|Cau truc du lieu va giai thuat|4|0\n"
              "INT101|Lap trinh Python|3|1\n");

    assert(managerFile.xoaMonHoc("CS102", loi));
    assert(docNoiDungFile(fileMonHoc)
           == "INT101|Lap trinh Python|3|1\n");
    assert(!std::filesystem::exists("monhoc_test_temp.txt"));
    assert(!std::filesystem::exists("monhoc_test_backup.txt"));
    std::filesystem::remove(fileMonHoc);
    return 0;
}
