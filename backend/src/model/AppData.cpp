#include "../KhaiBao.h"

void GiaiPhongCayMonHoc(treeMH& root)
{
    if (root == nullptr)
        return;

    GiaiPhongCayMonHoc(root->left);
    GiaiPhongCayMonHoc(root->right);
    delete root;
    root = nullptr;
}

void GiaiPhongDanhSachSinhVien(PTRSV& dsSV) {
    while (dsSV != nullptr) {
        PTRSV nodeCanXoa = dsSV;
        dsSV = dsSV->next;
        delete nodeCanXoa;
    }
}

void GiaiPhongDanhSachLop(DS_LOP& dsLop) {
    ++dsLop.phienBan;
    for (int i = 0; i < dsLop.n; ++i) {
        GiaiPhongDanhSachSinhVien(dsLop.nodes[i].dssv);
        dsLop.nodes[i] = Lop{};
    }
    dsLop.n = 0;
}

void GiaiPhongDanhSachDangKy(PTRDK& danhSach) {
    while (danhSach != nullptr) {
        PTRDK nodeCanXoa = danhSach;
        danhSach = danhSach->next;
        delete nodeCanXoa;
    }
}

void GiaiPhongDanhSachLopTinChi(DS_LTC& dsLTC) {
    for (int i = 0; i < dsLTC.n; ++i) {
        GiaiPhongDanhSachDangKy(dsLTC.nodes[i]->dssvdk);
        delete dsLTC.nodes[i];
        dsLTC.nodes[i] = nullptr;
    }
    dsLTC.n = 0;
    dsLTC.maTiepTheo = 1;
}

AppData::~AppData() {
    clear();
}

void AppData::clear() {
    tenFileMonHoc.clear();
    tenFileLopSinhVien.clear();
    tenFileLopTinChi.clear();
    ++phienBanMonHoc;
    GiaiPhongCayMonHoc(dsMonHoc);
    n = 0;
    GiaiPhongDanhSachLopTinChi(dsLopTinChi);
    GiaiPhongDanhSachLop(dsLop);
}
