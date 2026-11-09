#include "Undo.h"

#include <algorithm>
#include <tuple>
#include <utility>

namespace {

BanGhiUndo chup(AppData& data, DoiTuongUndo loai, string ma, int maLopTC = 0) {
    BanGhiUndo banGhi{};
    banGhi.doiTuong = loai;
    banGhi.ma = ChuanHoaMa(ma);
    banGhi.maLopTC = maLopTC;
    switch (loai) {
    case DoiTuongUndo::MonHoc:
        if (treeMH node = TimMonHoc(data.dsMonHoc, banGhi.ma)) {
            banGhi.tonTai = true;
            banGhi.monHoc = node->mh;
        }
        break;
    case DoiTuongUndo::Lop:
        banGhi.viTri = TimViTriLop(data.dsLop, banGhi.ma);
        if (banGhi.viTri >= 0) {
            banGhi.tonTai = true;
            banGhi.lop = data.dsLop.nodes[banGhi.viTri];
            banGhi.lop.dssv = nullptr;
        }
        break;
    case DoiTuongUndo::SinhVien: {
        int viTriLop;
        if (PTRSV node = TimSinhVienToanTruong(data.dsLop, banGhi.ma, viTriLop)) {
            banGhi.tonTai = true;
            banGhi.sinhVien = node->sv;
            banGhi.lop.MALOP = data.dsLop.nodes[viTriLop].MALOP;
        }
        break;
    }
    case DoiTuongUndo::LopTinChi:
        for (int i = 0; i < data.dsLopTinChi.n; ++i) {
            const Loptinchi& lop = *data.dsLopTinChi.nodes[i];
            if (lop.MALOPTC != maLopTC) continue;
            banGhi.tonTai = true;
            banGhi.viTri = i;
            banGhi.lopTinChi = lop;
            banGhi.lopTinChi.dssvdk = nullptr;
            for (PTRDK node = lop.dssvdk; node; node = node->next)
                banGhi.dangKy.push_back(node->dk);
            break;
        }
        break;
    }
    return banGhi;
}

BanGhiUndo chupHienTai(AppData& data, const BanGhiUndo& cu) {
    return chup(data, cu.doiTuong, cu.ma, cu.maLopTC);
}

bool giongNhau(const BanGhiUndo& a, const BanGhiUndo& b) {
    if (a.tonTai != b.tonTai) return false;
    if (!a.tonTai) return true;
    switch (a.doiTuong) {
    case DoiTuongUndo::MonHoc:
        return tie(a.monHoc.MAMH, a.monHoc.TENMH, a.monHoc.STCLT, a.monHoc.STCTH)
            == tie(b.monHoc.MAMH, b.monHoc.TENMH, b.monHoc.STCLT, b.monHoc.STCTH);
    case DoiTuongUndo::Lop:
        return a.lop.MALOP == b.lop.MALOP && a.lop.TENLOP == b.lop.TENLOP;
    case DoiTuongUndo::SinhVien:
        return tie(a.sinhVien.MASV, a.sinhVien.HO, a.sinhVien.TEN,
                   a.sinhVien.PHAI, a.sinhVien.SODT, a.lop.MALOP)
            == tie(b.sinhVien.MASV, b.sinhVien.HO, b.sinhVien.TEN,
                   b.sinhVien.PHAI, b.sinhVien.SODT, b.lop.MALOP);
    case DoiTuongUndo::LopTinChi: {
        const auto& x = a.lopTinChi;
        const auto& y = b.lopTinChi;
        return tie(x.MALOPTC, x.MAMH, x.NIENKHOA, x.HOCKY, x.NHOM,
                   x.SOSVMIN, x.SOSVMAX, x.HUYLOP)
            == tie(y.MALOPTC, y.MAMH, y.NIENKHOA, y.HOCKY, y.NHOM,
                   y.SOSVMIN, y.SOSVMAX, y.HUYLOP)
            && a.dangKy.size() == b.dangKy.size()
            && equal(a.dangKy.begin(), a.dangKy.end(), b.dangKy.begin(),
                [](const DangKy& x, const DangKy& y) {
                    return tie(x.MASV, x.DIEM, x.HUYDK) == tie(y.MASV, y.DIEM, y.HUYDK);
                });
    }
    }
    return false;
}

bool khoiPhuc(AppData& data, const BanGhiUndo& cu, string& loi) {
    switch (cu.doiTuong) {
    case DoiTuongUndo::MonHoc: {
        treeMH node = TimMonHoc(data.dsMonHoc, cu.ma);
        ++data.phienBanMonHoc;
        if (!cu.tonTai)
            return !node || XoaMonHoc(data.dsMonHoc, data.n, data.dsLopTinChi, cu.ma, loi);
        if (node) { node->mh = cu.monHoc; return true; }
        return ThemMonHoc(data.dsMonHoc, data.n, cu.monHoc, loi);
    }
    case DoiTuongUndo::Lop: {
        Lop* lop = TimLop(data.dsLop, cu.ma);
        if (!cu.tonTai) return !lop || XoaLop(data.dsLop, cu.ma, loi);
        if (lop) { lop->TENLOP = cu.lop.TENLOP; return true; }
        if (!ThemLop(data.dsLop, cu.lop, loi)) return false;
        // ThemLop noi cuoi mang; dua lop vua phuc hoi ve dung vi tri cu.
        int viTri = min(max(cu.viTri, 0), data.dsLop.n - 1);
        Lop vuaThem = data.dsLop.nodes[data.dsLop.n - 1];
        for (int i = data.dsLop.n - 1; i > viTri; --i)
            data.dsLop.nodes[i] = data.dsLop.nodes[i - 1];
        data.dsLop.nodes[viTri] = vuaThem;
        return true;
    }
    case DoiTuongUndo::SinhVien: {
        int viTriLop;
        PTRSV node = TimSinhVienToanTruong(data.dsLop, cu.ma, viTriLop);
        if (!cu.tonTai)
            return !node || XoaSinhVien(data.dsLop, data.dsLopTinChi, cu.ma, loi);
        if (node) return HieuChinhSinhVien(data.dsLop, cu.ma, cu.sinhVien, loi);
        return ThemSinhVien(data.dsLop, cu.lop.MALOP, cu.sinhVien, loi);
    }
    case DoiTuongUndo::LopTinChi: {
        DS_LTC& ds = data.dsLopTinChi;
        Loptinchi* lop = TimLopTinChiTheoMa(ds, cu.maLopTC);
        if (!cu.tonTai) return !lop || XoaLopTinChi(ds, cu.maLopTC, loi);
        if (!lop && ds.n >= MAXLTC) {
            loi = "Danh sách lớp tín chỉ đã đầy.";
            return false;
        }
        // Dung danh sach moi truoc khi giai phong du lieu hien tai.
        PTRDK danhSach = nullptr;
        PTRDK* cuoi = &danhSach;
        try {
            for (const DangKy& dk : cu.dangKy) {
                *cuoi = new nodeDK{dk, nullptr};
                cuoi = &(*cuoi)->next;
            }
            if (!lop) {
                auto moi = make_unique<Loptinchi>(cu.lopTinChi);
                int viTri = min(max(cu.viTri, 0), ds.n);
                for (int i = ds.n; i > viTri; --i) ds.nodes[i] = ds.nodes[i - 1];
                lop = moi.release();
                ds.nodes[viTri] = lop;
                ++ds.n;
            }
        } catch (...) {
            GiaiPhongDanhSachDangKy(danhSach);
            throw;
        }
        GiaiPhongDanhSachDangKy(lop->dssvdk);
        *lop = cu.lopTinChi;
        lop->dssvdk = danhSach;
        return true;
    }
    }
    return false;
}

bool luu(AppData& data, DoiTuongUndo loai, string& loi) {
    switch (loai) {
    case DoiTuongUndo::MonHoc:
        return data.tenFileMonHoc.empty()
            || GhiDanhSachMonHoc(data.tenFileMonHoc, data.dsMonHoc, loi);
    case DoiTuongUndo::Lop:
    case DoiTuongUndo::SinhVien:
        return data.tenFileLopSinhVien.empty()
            || GhiDanhSachLopSinhVien(data.tenFileLopSinhVien, data.dsLop, loi);
    case DoiTuongUndo::LopTinChi:
        return data.tenFileLopTinChi.empty()
            || GhiDanhSachLopTinChi(data.tenFileLopTinChi, data.dsLopTinChi, loi);
    }
    return false;
}

} // namespace

UndoStack::~UndoStack() { ClearUndo(*this); }

void PushUndo(UndoStack& stack, unique_ptr<UndoNode> node) {
    node->next = stack.top;
    stack.top = node.release();
    ++stack.count;
}

bool PopUndo(UndoStack& stack) {
    if (!stack.top) return false;
    UndoNode* node = stack.top;
    stack.top = node->next;
    delete node;
    --stack.count;
    return true;
}

void ClearUndo(UndoStack& stack) {
    while (PopUndo(stack)) {}
}

string MoTaUndo(const AppData& data) {
    return data.undoStack.top ? data.undoStack.top->moTa : "";
}

GiaoDichUndo::GiaoDichUndo(AppData& data, DoiTuongUndo loai, string ma, string moTa)
    : data_(data), node_(make_unique<UndoNode>()) {
    node_->moTa = std::move(moTa);
    node_->duLieuCu.push_back(chup(data, loai, ma));
}

GiaoDichUndo::GiaoDichUndo(AppData& data, int maLopTC, string moTa)
    : GiaoDichUndo(data, vector<int>{maLopTC}, std::move(moTa)) {}

GiaoDichUndo::GiaoDichUndo(AppData& data, const vector<int>& maLopTC, string moTa)
    : data_(data), node_(make_unique<UndoNode>()) {
    node_->moTa = std::move(moTa);
    node_->maTiepTheo = data.dsLopTinChi.maTiepTheo;
    for (int ma : maLopTC)
        node_->duLieuCu.push_back(chup(data, DoiTuongUndo::LopTinChi, "", ma));
}

void GiaoDichUndo::ghiNhan() {
    bool thayDoi = false;
    for (const auto& cu : node_->duLieuCu) {
        auto moi = chupHienTai(data_, cu);
        if (!giongNhau(cu, moi)) {
            thayDoi = true;
            node_->type = !cu.tonTai ? 'T' : (!moi.tonTai ? 'X' : 'S');
        }
    }
    if (thayDoi) PushUndo(data_.undoStack, std::move(node_));
}

bool ThucHienUndo(AppData& data, string& loi) {
    loi.clear();
    UndoNode* node = data.undoStack.top;
    if (!node) {
        loi = "Không có thao tác nào để hoàn tác.";
        return false;
    }
    vector<BanGhiUndo> hienTai;
    for (const auto& cu : node->duLieuCu) hienTai.push_back(chupHienTai(data, cu));
    int maTiepTheo = data.dsLopTinChi.maTiepTheo;
    auto loai = node->duLieuCu.front().doiTuong;
    bool thanhCong = true;
    for (auto it = node->duLieuCu.rbegin(); it != node->duLieuCu.rend(); ++it) {
        if (!khoiPhuc(data, *it, loi)) { thanhCong = false; break; }
    }
    if (thanhCong) {
        if (loai == DoiTuongUndo::LopTinChi)
            data.dsLopTinChi.maTiepTheo = node->maTiepTheo;
        thanhCong = luu(data, loai, loi);
    }
    if (!thanhCong) {
        // Khong pop khi loi: giu du lieu hien tai va cho phep thu Undo lai.
        string loiKhoiPhuc;
        for (const auto& banGhi : hienTai) khoiPhuc(data, banGhi, loiKhoiPhuc);
        data.dsLopTinChi.maTiepTheo = maTiepTheo;
        return false;
    }
    PopUndo(data.undoStack);
    return true;
}
