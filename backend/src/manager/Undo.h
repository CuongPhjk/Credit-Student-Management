#pragma once

#include "../KhaiBao.h"

enum class DoiTuongUndo { MonHoc, Lop, SinhVien, LopTinChi };

// Chi sao chep gia tri; khong giu con tro den node co the da bi xoa.
struct BanGhiUndo {
    DoiTuongUndo doiTuong;
    string ma;
    int maLopTC = 0;
    bool tonTai = false;
    int viTri = -1;
    Monhoc monHoc{};
    Lop lop{};
    Sinhvien sinhVien{};
    Loptinchi lopTinChi{};
    vector<DangKy> dangKy;
};

struct UndoNode {
    char type = 'S'; // 'T': Them, 'X': Xoa, 'S': Sua
    string moTa;
    vector<BanGhiUndo> duLieuCu;
    int maTiepTheo = 1;
    UndoNode* next = nullptr;
};

void PushUndo(UndoStack& stack, unique_ptr<UndoNode> node);
bool PopUndo(UndoStack& stack);

// Chup truoc khi thay doi, chi PushUndo sau khi thao tac va luu file thanh cong.
class GiaoDichUndo {
public:
    GiaoDichUndo(AppData& data, DoiTuongUndo doiTuong, string ma, string moTa);
    GiaoDichUndo(AppData& data, int maLopTC, string moTa);
    GiaoDichUndo(AppData& data, const vector<int>& maLopTC, string moTa);
    void ghiNhan();

private:
    AppData& data_;
    unique_ptr<UndoNode> node_;
};
