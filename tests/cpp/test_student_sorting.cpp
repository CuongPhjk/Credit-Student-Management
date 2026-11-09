#include <cassert>
#include <memory>
#include "../../backend/src/KhaiBao.h"

int main() {
    auto data = std::make_unique<AppData>();
    LopSinhVienManager manager(*data), other(*data);
    string error;
    assert(manager.themLop(Lop{"L1", "Lop mot"}, error));
    assert(manager.themLop(Lop{"L2", "Lop hai"}, error));
    assert(manager.themSinhVien("L1", Sinhvien{"SV3", "Le", "An", "Nam", "0901234567"}, error));
    assert(manager.themSinhVien("L1", Sinhvien{"SV1", "Le", "Cuong", "Nam", "0901234567"}, error));
    assert(manager.themSinhVien("L1", Sinhvien{"SV2", "Le", "Binh", "Nam", "0901234567"}, error));
    int count;
    PTRSV originalHead = data->dsLop.nodes[0].dssv;
    PTRSV originalNext = originalHead->next;
    PTRSV* sorted = manager.laySinhVienTheoMa(" l1 ", count);
    assert(count == 3);
    assert(sorted[0]->sv.MASV == "SV1" && sorted[1]->sv.MASV == "SV2" && sorted[2]->sv.MASV == "SV3");
    assert(data->dsLop.nodes[0].dssv == originalHead && originalHead->next == originalNext);
    assert(manager.laySinhVienTheoMa("L1", count) == sorted);
    // A name-order export must not discard this class's ID-order cache.
    PTRSV* byName = manager.layDanhSachSinhVien("L1", count);
    assert(byName[0]->sv.MASV == "SV3" && byName[1]->sv.MASV == "SV2");
    delete[] byName;
    assert(manager.laySinhVienTheoMa("L1", count) == sorted);
    // Editing fields, even moving a node in the linked list, preserves node addresses.
    assert(other.capNhatSinhVien("SV3", Sinhvien{"SV3", "Le", "Zung", "Nam", "0912345678"}, error));
    assert(manager.laySinhVienTheoMa("L1", count) == sorted);
    assert(sorted[2] == originalHead && sorted[2]->sv.TEN == "Zung");
    assert(data->dsLop.nodes[0].dssv->sv.MASV == "SV2");
    // Same count after delete + add must still invalidate pointers to deleted nodes.
    assert(other.xoaSinhVien("SV2", error));
    assert(other.themSinhVien("L1", Sinhvien{"SV4", "Le", "Dung", "Nam", "0901234567"}, error));
    sorted = manager.laySinhVienTheoMa("L1", count);
    assert(count == 3 && sorted[0]->sv.MASV == "SV1" && sorted[1]->sv.MASV == "SV3" && sorted[2]->sv.MASV == "SV4");
    assert(manager.laySinhVienTheoMa("L2", count) == nullptr && count == 0);
    assert(other.themSinhVien("L2", Sinhvien{"ONLY", "Le", "An", "Nam", "0901234567"}, error));
    sorted = manager.laySinhVienTheoMa("L2", count);
    assert(count == 1 && sorted[0]->sv.MASV == "ONLY");
    assert(manager.laySinhVienTheoMa("missing", count) == nullptr && count == 0);
    sorted = manager.laySinhVienTheoMa("L1", count);
    data->clear();
    assert(manager.laySinhVienTheoMa("L1", count) == nullptr && count == 0);
    assert(manager.themLop(Lop{"L1", "New class"}, error));
    for (int i = 30; i >= 0; --i) {
        assert(manager.themSinhVien("L1", Sinhvien{"CODE" + to_string(i), "Le", "An", "Nam", "0901234567"}, error));
    }
    sorted = manager.laySinhVienTheoMa("L1", count);
    assert(count == 31);
    for (int i = 1; i < count; ++i) assert(sorted[i-1]->sv.MASV < sorted[i]->sv.MASV);
    manager.giaiPhongThuTuSinhVien();
    manager.giaiPhongThuTuSinhVien();
    sorted = manager.laySinhVienTheoMa("L1", count);
    assert(count == 31);
    data->clear();  // Manager destruction only releases its array, not dead nodes.
    return 0;
}
