#include <cassert>
#include <filesystem>
#include <fstream>
#include <string>

#include "AppData.h"
#include "HamLop.h"
#include "HamSinhVien.h"
#include "LopSinhVienManager.h"

int main() {
    AppData duLieu;
    std::string loi;

    assert(ThemLop(
        duLieu.dsLop(), Lop{" d22cqcn01 ", " Cong nghe thong tin ", nullptr}, loi
    ));
    assert(ThemLop(
        duLieu.dsLop(), Lop{"D21CQCN01", "Ky thuat may tinh", nullptr}, loi
    ));
    assert(duLieu.dsLop().nodes[0].MALOP == "D21CQCN01");
    assert(duLieu.dsLop().nodes[1].MALOP == "D22CQCN01");
    assert(!ThemLop(
        duLieu.dsLop(), Lop{"D21CQCN01", "Trung ma", nullptr}, loi
    ));

    assert(ThemSinhVien(
        duLieu.dsLop(), "D21CQCN01",
        Sinhvien{" n21dccn003 ", " le ", " binh ", "Nam", "0912345678"},
        loi
    ));
    assert(ThemSinhVien(
        duLieu.dsLop(), "D21CQCN01",
        Sinhvien{"N21DCCN002", "Tran Thi", "An", u8"Nữ", "0987654321"},
        loi
    ));
    assert(ThemSinhVien(
        duLieu.dsLop(), "D21CQCN01",
        Sinhvien{"N21DCCN001", "Nguyen Van", "An", "Nam", "0901234567"},
        loi
    ));
    PTRSV danhSach = duLieu.dsLop().nodes[0].dssv;
    assert(danhSach->sv.MASV == "N21DCCN001");
    assert(danhSach->next->sv.MASV == "N21DCCN002");
    assert(danhSach->next->next->sv.MASV == "N21DCCN003");
    assert(!ThemSinhVien(
        duLieu.dsLop(), "D22CQCN01",
        Sinhvien{"N21DCCN001", "Nguoi", "Trung", "Nam", "0901234567"},
        loi
    ));

    Sinhvien duLieuMoi{
        "KHONG_DOI_MA", "Do", "A", "Nam", "0909999999"
    };
    assert(HieuChinhSinhVien(
        duLieu.dsLop(), "N21DCCN003", duLieuMoi, loi
    ));
    assert(duLieu.dsLop().nodes[0].dssv->sv.MASV == "N21DCCN003");
    assert(duLieu.dsLop().nodes[0].dssv->sv.TEN == "A");
    assert(!XoaLop(duLieu.dsLop(), "D21CQCN01", loi));

    Loptinchi* lopTinChi = new Loptinchi{};
    lopTinChi->MALOPTC = 1;
    lopTinChi->dssvdk = new nodeDK{{"N21DCCN001", 0.0F, false}, nullptr};
    duLieu.dsLopTinChi().nodes[0] = lopTinChi;
    duLieu.dsLopTinChi().n = 1;
    assert(!XoaSinhVien(
        duLieu.dsLop(), duLieu.dsLopTinChi(), "N21DCCN001", loi
    ));
    assert(XoaSinhVien(
        duLieu.dsLop(), duLieu.dsLopTinChi(), "N21DCCN002", loi
    ));

    const std::filesystem::path fileSinhVien =
        std::filesystem::current_path() / "lopsinhvien_test.txt";
    {
        std::ofstream tep(fileSinhVien);
        tep << "D21CQCN01|Cong nghe thong tin\n"
            << "N21DCCN002|Tran Thi|Binh|Nu|0987654321\n#\n";
    }
    AppData duLieuFile;
    LopSinhVienManager manager(duLieuFile);
    // A malformed student must not partially load its parent class.
    assert(!manager.docDanhSachLopSinhVien(fileSinhVien.string(), loi));
    assert(manager.tongSoLop() == 0);
    {
        std::ofstream tep(fileSinhVien, std::ios::trunc);
        tep << "D21CQCN01|Cong nghe thong tin\n"
            << u8"N21DCCN002|Trần Thị|Bình|Nữ|0987654321\n#\n";
    }
    assert(manager.docDanhSachLopSinhVien(fileSinhVien.string(), loi));
    assert(manager.tongSoLop() == 1);
    assert(manager.tongSoSinhVien() == 1);
    assert(manager.themSinhVien(
        "D21CQCN01",
        Sinhvien{"N21DCCN001", "Nguyen Van", "An", "Nam", "0901234567"},
        loi
    ));
    Sinhvien mangSinhVien[2];
    assert(manager.layDanhSachSinhVien("D21CQCN01", mangSinhVien, 2) == 2);
    assert(mangSinhVien[0].TEN == "An");
    assert(mangSinhVien[1].TEN == u8"Bình");
    assert(manager.xoaSinhVien("N21DCCN001", loi));

    std::filesystem::remove(fileSinhVien);
    std::filesystem::remove("lop_test_temp.txt");
    std::filesystem::remove("lop_test_backup.txt");
    std::filesystem::remove("sinhvien_test_temp.txt");
    std::filesystem::remove("sinhvien_test_backup.txt");
    return 0;
}
