#include <cassert>
#include <filesystem>
#include <fstream>
#include <memory>
#include <string>

#include "AppData.h"
#include "DangKyManager.h"
#include "HamDangKy.h"
#include "HamLop.h"
#include "HamLopTinChi.h"
#include "HamMonHoc.h"
#include "HamSinhVien.h"
#include "file/XuLyTep.h"
#include "utils/KiemTraDuLieu.h"

namespace {

void TaoDuLieuCoBan(AppData& duLieu, std::string& loi) {
    const std::string nienKhoa = NienKhoaHienTai();
    assert(ThemMonHoc(
        duLieu.dsMonHoc(), Monhoc{"INT100", "Mang may tinh", 3, 0}, loi
    ));
    assert(ThemMonHoc(
        duLieu.dsMonHoc(), Monhoc{"INT101", "Co so du lieu", 3, 1}, loi
    ));
    assert(ThemLop(
        duLieu.dsLop(), Lop{"D21CQCN01", "Cong nghe thong tin", nullptr}, loi
    ));
    assert(ThemSinhVien(
        duLieu.dsLop(), "D21CQCN01",
        Sinhvien{"N21DCCN002", "Tran Thi", "Binh", u8"Nữ", "0987654321"},
        loi
    ));
    assert(ThemSinhVien(
        duLieu.dsLop(), "D21CQCN01",
        Sinhvien{"N21DCCN001", "Nguyen Van", "An", "Nam", "0901234567"},
        loi
    ));

    assert(ThemLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(),
        Loptinchi{0, "INT100", nienKhoa, 1, 1, 1, 2, false, nullptr},
        loi
    ));
    assert(ThemLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(),
        Loptinchi{0, "INT100", nienKhoa, 1, 2, 1, 2, false, nullptr},
        loi
    ));
    assert(ThemLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(),
        Loptinchi{0, "INT101", nienKhoa, 1, 1, 1, 1, false, nullptr},
        loi
    ));
    assert(ThemLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(),
        Loptinchi{0, "INT101", nienKhoa, 2, 1, 1, 2, false, nullptr},
        loi
    ));
    assert(HuyLopTinChi(duLieu.dsLopTinChi(), 4, loi));
}

}  // namespace

int main() {
    AppData duLieu;
    std::string loi;
    TaoDuLieuCoBan(duLieu, loi);

    assert(!DangKyLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsLop(), 1, "KHONGTONTAI", loi
    ));
    assert(DangKyLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsLop(), 1, "N21DCCN002", loi
    ));
    assert(DangKyLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsLop(), 1, "N21DCCN001", loi
    ));
    const Loptinchi* lopMot = TimLopTinChiTheoMa(duLieu.dsLopTinChi(), 1);
    assert(lopMot != nullptr);
    assert(lopMot->dssvdk->dk.MASV == "N21DCCN001");
    assert(lopMot->dssvdk->next->dk.MASV == "N21DCCN002");
    assert(DemSoSinhVienDangKy(*lopMot) == 2);

    assert(!DangKyLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsLop(), 1, "N21DCCN001", loi
    ));
    assert(!DangKyLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsLop(), 2, "N21DCCN001", loi
    ));
    assert(DangKyLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsLop(), 3, "N21DCCN001", loi
    ));
    assert(!DangKyLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsLop(), 3, "N21DCCN002", loi
    ));
    assert(!DangKyLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsLop(), 4, "N21DCCN001", loi
    ));

    assert(HuyDangKy(duLieu.dsLopTinChi(), 1, "N21DCCN001", loi));
    assert(!SinhVienDangKyLopTinChi(*lopMot, "N21DCCN001"));
    assert(DangKyLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsLop(), 2, "N21DCCN001", loi
    ));

    Dangky danhSach[3];
    assert(LayDanhSachDangKy(*lopMot, danhSach, 3, true) == 2);
    assert(LayDanhSachDangKy(*lopMot, danhSach, 3, false) == 1);

    const std::filesystem::path fileDangKy =
        std::filesystem::current_path() / "registration_test.txt";
    {
        std::ofstream tep(fileDangKy);
    }
    std::unique_ptr<AppData> duLieuQuaManager(new AppData());
    TaoDuLieuCoBan(*duLieuQuaManager, loi);
    DangKyManager manager(*duLieuQuaManager);
    duLieuQuaManager->tenFileLopTinChi() = fileDangKy.string();
    assert(manager.dangKy(1, "N21DCCN001", loi));
    assert(manager.daDangKy(1, "N21DCCN001"));

    std::unique_ptr<AppData> duLieuDocLai(new AppData());
    TaoDuLieuCoBan(*duLieuDocLai, loi);
    assert(DocDanhSachLopTinChi(
        fileDangKy.string(), duLieuDocLai->dsLopTinChi(), loi
    ));
    assert(SinhVienDangKyLopTinChi(
        *TimLopTinChiTheoMa(duLieuDocLai->dsLopTinChi(), 1), "N21DCCN001"
    ));
    assert(manager.huyDangKy(1, "N21DCCN001", loi));
    assert(!manager.daDangKy(1, "N21DCCN001"));

    std::filesystem::remove(fileDangKy);
    std::filesystem::remove("registration_test_temp.txt");
    std::filesystem::remove("registration_test_backup.txt");
    return 0;
}
