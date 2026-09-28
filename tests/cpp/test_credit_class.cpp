#include <cassert>
#include <filesystem>
#include <string>

#include "AppData.h"
#include "file/XuLyTep.h"
#include "HamLopTinChi.h"
#include "HamMonHoc.h"
#include "utils/KiemTraDuLieu.h"

namespace {

std::string NienKhoaTheoDoLech(int doLech) {
    const int namBatDau = std::stoi(NienKhoaHienTai().substr(0, 4)) + doLech;
    return std::to_string(namBatDau) + "-" + std::to_string(namBatDau + 1);
}

}  // namespace

int main() {
    AppData duLieu;
    std::string loi;
    const std::string nienKhoaCu = NienKhoaTheoDoLech(-1);
    const std::string nienKhoaHienTai = NienKhoaTheoDoLech(0);
    const std::string nienKhoaTuongLai = NienKhoaTheoDoLech(1);

    assert(ThemMonHoc(
        duLieu.dsMonHoc(),
        Monhoc{"INT100", "Mang may tinh", 3, 0},
        loi
    ));
    assert(ThemMonHoc(
        duLieu.dsMonHoc(),
        Monhoc{"INT104", "Co so du lieu", 3, 1},
        loi
    ));

    const Loptinchi lopNienKhoaCu{
        0, "INT100", nienKhoaCu, 1, 1, 10, 50, false, nullptr
    };
    assert(!ThemLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(), lopNienKhoaCu, loi
    ));
    assert(loi.find(NienKhoaHienTai()) != std::string::npos);
    assert(duLieu.dsLopTinChi().n == 0);

    Loptinchi lopNhomMot{
        999, " int100 ", " " + nienKhoaHienTai + " ",
        1, 1, 10, 50, true, nullptr
    };
    assert(ThemLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(), lopNhomMot, loi
    ));
    assert(duLieu.dsLopTinChi().n == 1);
    assert(duLieu.dsLopTinChi().nodes[0]->MALOPTC == 1);
    assert(duLieu.dsLopTinChi().nodes[0]->MAMH == "INT100");
    assert(duLieu.dsLopTinChi().nodes[0]->NIENKHOA == nienKhoaHienTai);
    assert(!duLieu.dsLopTinChi().nodes[0]->HUYLOP);
    assert(duLieu.dsLopTinChi().nodes[0]->dssvdk == nullptr);
    assert(duLieu.dsLopTinChi().maTiepTheo == 2);

    assert(!ThemLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(), lopNhomMot, loi
    ));
    assert(!loi.empty());

    Loptinchi lopNhomHai{
        0, "INT100", nienKhoaHienTai, 1, 2, 10, 40, false, nullptr
    };
    assert(ThemLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(), lopNhomHai, loi
    ));
    assert(duLieu.dsLopTinChi().nodes[1]->MALOPTC == 2);
    assert(duLieu.dsLopTinChi().maTiepTheo == 3);

    Loptinchi duLieuSua{
        123, "INT104", nienKhoaHienTai, 2, 1, 5, 30, true, nullptr
    };
    assert(HieuChinhLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(), 1, duLieuSua, loi
    ));
    Loptinchi* lopDaSua = duLieu.dsLopTinChi().nodes[0];
    assert(lopDaSua->MALOPTC == 1);
    assert(lopDaSua->MAMH == "INT104");
    assert(lopDaSua->HOCKY == 2);
    assert(!lopDaSua->HUYLOP);

    Loptinchi suaThanhNienKhoaCu = *lopDaSua;
    suaThanhNienKhoaCu.NIENKHOA = nienKhoaCu;
    assert(!HieuChinhLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(), 1,
        suaThanhNienKhoaCu, loi
    ));
    assert(loi.find(NienKhoaHienTai()) != std::string::npos);
    assert(lopDaSua->NIENKHOA == nienKhoaHienTai);

    lopDaSua->dssvdk = new nodeDK{{"SV001", 0.0F, false}, nullptr};
    lopDaSua->dssvdk->next = new nodeDK{{"SV002", 0.0F, false}, nullptr};
    assert(DemSoSinhVienDangKy(*lopDaSua) == 2);
    assert(TinhSoChoTrong(*lopDaSua) == 28);

    Loptinchi suaSiSo = *lopDaSua;
    suaSiSo.SOSVMIN = 1;
    suaSiSo.SOSVMAX = 1;
    assert(!HieuChinhLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(), 1, suaSiSo, loi
    ));

    Loptinchi doiMonHoc = *lopDaSua;
    doiMonHoc.MAMH = "INT100";
    assert(!HieuChinhLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(), 1, doiMonHoc, loi
    ));
    assert(!XoaLopTinChi(duLieu.dsLopTinChi(), 1, loi));

    assert(XoaLopTinChi(duLieu.dsLopTinChi(), 2, loi));
    assert(duLieu.dsLopTinChi().n == 1);
    assert(duLieu.dsLopTinChi().nodes[0]->MALOPTC == 1);
    assert(duLieu.dsLopTinChi().nodes[1] == nullptr);

    Loptinchi lopSauKhiXoa{
        0, "INT100", nienKhoaTuongLai, 1, 1, 5, 35, false, nullptr
    };
    assert(ThemLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(), lopSauKhiXoa, loi
    ));
    assert(duLieu.dsLopTinChi().nodes[1]->MALOPTC == 3);
    assert(duLieu.dsLopTinChi().maTiepTheo == 4);

    const std::filesystem::path fileLopTinChi =
        std::filesystem::current_path() / "loptinchi_test.txt";
    assert(GhiDanhSachLopTinChi(
        fileLopTinChi.string(), duLieu.dsLopTinChi(), loi
    ));

    AppData duLieuDocLai;
    assert(DocDanhSachLopTinChi(
        fileLopTinChi.string(), duLieuDocLai.dsLopTinChi(), loi
    ));
    assert(duLieuDocLai.dsLopTinChi().n == 2);
    assert(duLieuDocLai.dsLopTinChi().maTiepTheo == 4);
    assert(duLieuDocLai.dsLopTinChi().nodes[0]->MALOPTC == 1);
    assert(duLieuDocLai.dsLopTinChi().nodes[0]->MAMH == "INT104");
    assert(duLieuDocLai.dsLopTinChi().nodes[0]->dssvdk != nullptr);
    assert(duLieuDocLai.dsLopTinChi().nodes[1]->MALOPTC == 3);
    assert(DemSoSinhVienDangKy(
        *duLieuDocLai.dsLopTinChi().nodes[0]
    ) == 2);
    assert(!std::filesystem::exists("loptinchi_test_temp.txt"));
    assert(!std::filesystem::exists("loptinchi_test_backup.txt"));
    std::filesystem::remove(fileLopTinChi);
    return 0;
}
