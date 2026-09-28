#include "../../include/model/AppData.h"

#include "../../include/functions/HamMonHoc.h"

namespace {

void GiaiPhongDanhSachDangKyNoiBo(PTRDK& danhSach) {
    while (danhSach != nullptr) {
        PTRDK nodeCanXoa = danhSach;
        danhSach = danhSach->next;
        delete nodeCanXoa;
    }
}

void GiaiPhongDanhSachSinhVienNoiBo(PTRSV& danhSach) {
    while (danhSach != nullptr) {
        PTRSV nodeCanXoa = danhSach;
        danhSach = danhSach->next;
        delete nodeCanXoa;
    }
}

}  // namespace

AppData::~AppData() {
    clear();
}

treeMH& AppData::dsMonHoc() {
    return dsMonHoc_;
}

const treeMH& AppData::dsMonHoc() const {
    return dsMonHoc_;
}

DS_LTC& AppData::dsLopTinChi() {
    return dsLopTinChi_;
}

const DS_LTC& AppData::dsLopTinChi() const {
    return dsLopTinChi_;
}

DS_LOP& AppData::dsLop() {
    return dsLop_;
}

const DS_LOP& AppData::dsLop() const {
    return dsLop_;
}

std::string& AppData::tenFileLopTinChi() { return tenFileLopTinChi_; }
const std::string& AppData::tenFileLopTinChi() const { return tenFileLopTinChi_; }

void AppData::clear() {
    tenFileLopTinChi_.clear();
    GiaiPhongCayMonHoc(dsMonHoc_);

    for (int i = 0; i < dsLopTinChi_.n; ++i) {
        if (dsLopTinChi_.nodes[i] == nullptr) {
            continue;
        }
        GiaiPhongDanhSachDangKyNoiBo(dsLopTinChi_.nodes[i]->dssvdk);
        delete dsLopTinChi_.nodes[i];
        dsLopTinChi_.nodes[i] = nullptr;
    }
    dsLopTinChi_.n = 0;
    dsLopTinChi_.maTiepTheo = 1;

    for (int i = 0; i < dsLop_.n; ++i) {
        GiaiPhongDanhSachSinhVienNoiBo(dsLop_.nodes[i].dssv);
        dsLop_.nodes[i] = Lop{};
    }
    dsLop_.n = 0;
}
