#include <cassert>
#include <memory>
#include "../../backend/src/KhaiBao.h"

int main() {
    auto data = std::make_unique<AppData>();
    MonHocManager subjects(*data);
    LopSinhVienManager students(*data);
    LopTinChiManager credits(*data);
    int count = -1;
    assert(subjects.layDanhSachMonHoc(count) == nullptr && count == 0);
    assert(students.layDanhSachLop(count) == nullptr && count == 0);
    assert(credits.layDanhSachLopTinChi(count) == nullptr && count == 0);
    assert(students.layDanhSachSinhVien("missing", count) == nullptr && count == 0);
    string error;
    assert(subjects.themMonHoc(Monhoc{"MH2", "Mon hai", 3, 0}, error));
    assert(subjects.themMonHoc(Monhoc{"MH1", "Mon mot", 3, 0}, error));
    treeMH* mh = LayDanhSachMonHoc(data->dsMonHoc, data->n, count);
    assert(count == 2 && mh[0]->mh.MAMH == "MH1" && mh[1]->mh.MAMH == "MH2");
    assert(mh[0] == TimMonHoc(data->dsMonHoc, "MH1"));
    delete[] mh;
    Monhoc original;
    assert(subjects.timMonHoc("MH1", original) && original.TENMH == "Mon mot");
    assert(data->n == 2);
    assert(!subjects.themMonHoc(Monhoc{"MH1", "Duplicate", 3, 0}, error));
    assert(data->n == 2);
    assert(students.themLop(Lop{"L1", "Lop mot", nullptr}, error));
    assert(students.layDanhSachSinhVien("L1", count) == nullptr && count == 0);
    assert(students.themSinhVien("L1", Sinhvien{"SV2", "Le", "An", "Nam", "0901234567"}, error));
    assert(students.themSinhVien("L1", Sinhvien{"SV1", "Le", "Binh", "Nam", "0901234567"}, error));
    Lop* lop = LayDanhSachLop(data->dsLop, count);
    assert(count == 1 && lop[0].dssv != nullptr && lop[0].soSinhVien == 2);
    PTRSV* sv = LayDanhSachSinhVien(lop[0], count);
    assert(count == 2 && sv[0]->sv.MASV == "SV2" && sv[1]->sv.MASV == "SV1");
    assert(sv[0] == data->dsLop.nodes[0].dssv);
    delete[] sv;
    delete[] lop;
    assert(students.tongSoSinhVien() == 2);
    assert(students.capNhatSinhVien("SV1", Sinhvien{"SV1", "Le", "Zung", "Nam", "0912345678"}, error));
    assert(data->dsLop.nodes[0].soSinhVien == 2);
    assert(!students.themSinhVien("L1", Sinhvien{"SV1", "Le", "An", "Nam", "0901234567"}, error));
    assert(data->dsLop.nodes[0].soSinhVien == 2);
    assert(students.xoaSinhVien("SV1", error));
    assert(data->dsLop.nodes[0].soSinhVien == 1);
    assert(students.themSinhVien("L1", Sinhvien{"SV1", "Le", "Binh", "Nam", "0901234567"}, error));
    assert(credits.themLopTinChi(Loptinchi{0, "MH1", NienKhoaHienTai(), 1, 1, 1, 3, false, nullptr}, error));
    assert(DangKyLopTinChi(data->dsLopTinChi, data->dsLop, 1, "SV2", error));
    Loptinchi** ltc = LayDanhSachLopTinChi(data->dsLopTinChi, count);
    assert(count == 1 && ltc[0]->MALOPTC == 1 && ltc[0]->dssvdk != nullptr);
    assert(ltc == data->dsLopTinChi.nodes);  // Borrowed original array.
    assert(TimDangKy(data->dsLopTinChi.nodes[0]->dssvdk, "SV2") != nullptr);
    PTRDK* registrations = LayDanhSachDangKy(*data->dsLopTinChi.nodes[0], count);
    assert(count == 1 && registrations[0] == data->dsLopTinChi.nodes[0]->dssvdk);
    delete[] registrations;
    assert(!students.xoaSinhVien("SV2", error));
    assert(data->dsLop.nodes[0].soSinhVien == 2);
    GiaiPhongDanhSachDangKy(data->dsLopTinChi.nodes[0]->dssvdk);
    assert(data->dsLopTinChi.nodes[0]->dssvdk == nullptr);
    GiaiPhongDanhSachDangKy(data->dsLopTinChi.nodes[0]->dssvdk);
    assert(DangKyLopTinChi(data->dsLopTinChi, data->dsLop, 1, "SV1", error));
    data->tenFileMonHoc = "subjects.txt";
    data->tenFileLopSinhVien = "students.txt";
    data->tenFileLopTinChi = "credits.txt";
    AppData& sharedData = *data;
    assert(sharedData.tenFileMonHoc == "subjects.txt");
    assert(sharedData.tenFileLopSinhVien == "students.txt");
    assert(sharedData.tenFileLopTinChi == "credits.txt");
    data->clear();
    assert(data->tenFileMonHoc.empty());
    assert(data->tenFileLopSinhVien.empty());
    assert(data->tenFileLopTinChi.empty());
    assert(data->dsMonHoc == nullptr && data->n == 0);
    assert(data->dsLop.n == 0 && data->dsLop.nodes[0].dssv == nullptr && data->dsLop.nodes[0].soSinhVien == 0);
    assert(data->dsLopTinChi.n == 0 && data->dsLopTinChi.nodes[0] == nullptr);
    assert(data->dsLopTinChi.maTiepTheo == 1);
    data->clear();  // Repeated cleanup and destruction must remain safe.
    return 0;
}
