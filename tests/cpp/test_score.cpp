#include <cassert>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <string>

#include "AppData.h"
#include "DiemManager.h"
#include "HamDangKy.h"
#include "HamDiem.h"
#include "HamLop.h"
#include "HamLopTinChi.h"
#include "HamMonHoc.h"
#include "HamSinhVien.h"
#include "file/XuLyTep.h"
#include "utils/KiemTraDuLieu.h"

namespace {

void TaoDuLieu(AppData& duLieu, std::string& loi) {
    const std::string nienKhoa = NienKhoaHienTai();
    assert(ThemMonHoc(
        duLieu.dsMonHoc(), Monhoc{"INT100", "Lap trinh", 3, 1}, loi
    ));
    assert(ThemLop(
        duLieu.dsLop(), Lop{"D21CQCN01", "Cong nghe thong tin", nullptr}, loi
    ));
    assert(ThemSinhVien(
        duLieu.dsLop(), "D21CQCN01",
        Sinhvien{"N21DCCN001", "Nguyen Van", "An", "Nam", "0901234567"},
        loi
    ));
    assert(ThemSinhVien(
        duLieu.dsLop(), "D21CQCN01",
        Sinhvien{"N21DCCN002", "Tran Thi", "Binh", u8"Nữ", "0987654321"},
        loi
    ));
    assert(ThemSinhVien(
        duLieu.dsLop(), "D21CQCN01",
        Sinhvien{"N21DCCN003", "Le Van", "Cuong", "Nam", "0912345678"},
        loi
    ));
    assert(ThemLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(),
        Loptinchi{0, "INT100", nienKhoa, 1, 1, 1, 3, false, nullptr},
        loi
    ));
    assert(ThemLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsMonHoc(),
        Loptinchi{0, "INT100", nienKhoa, 1, 2, 1, 3, false, nullptr},
        loi
    ));
    assert(HuyLopTinChi(duLieu.dsLopTinChi(), 2, loi));
    assert(DangKyLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsLop(), 1, "N21DCCN001", loi
    ));
    assert(DangKyLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsLop(), 1, "N21DCCN002", loi
    ));
    assert(DangKyLopTinChi(
        duLieu.dsLopTinChi(), duLieu.dsLop(), 1, "N21DCCN003", loi
    ));
    assert(HuyDangKy(duLieu.dsLopTinChi(), 1, "N21DCCN003", loi));
}

}  // namespace

int main() {
    AppData duLieu;
    std::string loi;
    const std::string nienKhoa = NienKhoaHienTai();
    TaoDuLieu(duLieu, loi);

    assert(KiemTraDiemHopLe(0.0F));
    assert(KiemTraDiemHopLe(10.0F));
    assert(!KiemTraDiemHopLe(-0.1F));
    assert(!KiemTraDiemHopLe(10.1F));
    assert(!KiemTraDiemHopLe(std::nanf("")));
    assert(DemSinhVienNhapDiem(
        duLieu.dsLopTinChi(), nienKhoa, 1, "INT100", 1, loi
    ) == 2);
    assert(DemSinhVienNhapDiem(
        duLieu.dsLopTinChi(), nienKhoa, 1, "INT100", 2, loi
    ) == -1);
    assert(!loi.empty());

    Diemsinhvien danhSach[2];
    assert(LayDanhSachSinhVienNhapDiem(
        duLieu.dsLopTinChi(), duLieu.dsLop(),
        nienKhoa, 1, "INT100", 1, danhSach, 2, loi
    ) == 2);
    assert(danhSach[0].MASV == "N21DCCN001");
    assert(danhSach[0].HO == "Nguyen Van");
    assert(danhSach[1].MASV == "N21DCCN002");

    assert(NhapDiem(
        duLieu.dsLopTinChi(), nienKhoa, 1, "INT100", 1,
        "N21DCCN001", 8.5F, loi
    ));
    assert(!NhapDiem(
        duLieu.dsLopTinChi(), nienKhoa, 1, "INT100", 1,
        "N21DCCN003", 7.0F, loi
    ));
    assert(!NhapDiem(
        duLieu.dsLopTinChi(), nienKhoa, 1, "INT100", 1,
        "N21DCCN001", 11.0F, loi
    ));

    const std::filesystem::path fileDangKy =
        std::filesystem::current_path() / "score_test.txt";
    assert(GhiDanhSachLopTinChi(
        fileDangKy.string(), duLieu.dsLopTinChi(), loi
    ));
    DiemManager manager(duLieu);
    duLieu.tenFileLopTinChi() = fileDangKy.string();

    const Diemcapnhat diemMoi[2] = {
        {"N21DCCN001", 9.25F},
        {"N21DCCN002", 7.5F},
    };
    assert(manager.capNhatDanhSachDiem(
        nienKhoa, 1, "INT100", 1, diemMoi, 2, loi
    ));
    const Loptinchi* lop = TimLopTinChiTheoMa(duLieu.dsLopTinChi(), 1);
    assert(lop != nullptr);
    assert(TimDangKy(lop->dssvdk, "N21DCCN001")->dk.DIEM == 9.25F);
    assert(TimDangKy(lop->dssvdk, "N21DCCN002")->dk.DIEM == 7.5F);

    const Diemcapnhat biTrung[2] = {
        {"N21DCCN001", 5.0F},
        {"n21dccn001", 6.0F},
    };
    assert(!manager.capNhatDanhSachDiem(
        nienKhoa, 1, "INT100", 1, biTrung, 2, loi
    ));
    assert(TimDangKy(lop->dssvdk, "N21DCCN001")->dk.DIEM == 9.25F);

    AppData docLai;
    TaoDuLieu(docLai, loi);
    assert(DocDanhSachLopTinChi(
        fileDangKy.string(), docLai.dsLopTinChi(), loi
    ));
    const Loptinchi* lopDocLai = TimLopTinChiTheoMa(docLai.dsLopTinChi(), 1);
    assert(lopDocLai != nullptr);
    assert(TimDangKy(lopDocLai->dssvdk, "N21DCCN001")->dk.DIEM == 9.25F);
    assert(TimDangKy(lopDocLai->dssvdk, "N21DCCN002")->dk.DIEM == 7.5F);

    // Zero is a valid grade, distinct from the ungraded default.
    assert(manager.capNhatDiem(nienKhoa, 1, "INT100", 1, "N21DCCN001", 0.0F, loi));
    assert(DocDanhSachLopTinChi(fileDangKy.string(), docLai.dsLopTinChi(), loi));
    lopDocLai = TimLopTinChiTheoMa(docLai.dsLopTinChi(), 1);
    const PTRDK dangKyCu = TimDangKy(lopDocLai->dssvdk, "N21DCCN001");
    assert(dangKyCu != nullptr);
    assert(dangKyCu->dk.DIEM == 0.0F && dangKyCu->dk.DADIEM);

    std::filesystem::remove(fileDangKy);
    std::filesystem::remove("score_test_temp.txt");
    std::filesystem::remove("score_test_backup.txt");
    return 0;
}
