#include "../KhaiBao.h"
#include "../utils/MergeSort.h"
using namespace std;

Monhoc ChuanHoaMonHoc(Monhoc monHoc) {
    Monhoc ketQua = monHoc;
    ketQua.MAMH = ChuanHoaMa(monHoc.MAMH);
    ketQua.TENMH = XoaKhoangTrangThua(monHoc.TENMH);
    return ketQua;
}

treeMH TimNodeTheMang(treeMH root)
{
    while (root->left != nullptr)
    {
        root = root->left;
    }
    return root;
}

bool XoaNodeMonHoc(treeMH& root, string maMH)
{
    if (root == nullptr)
        return false;

    if (maMH < root->mh.MAMH)
        return XoaNodeMonHoc(root->left, maMH);

    if (maMH > root->mh.MAMH)
        return XoaNodeMonHoc(root->right, maMH);

    if (root->left == nullptr)
    {
        treeMH temp = root;
        root = root->right;
        delete temp;
        return true;
    }

    if (root->right == nullptr)
    {
        treeMH temp = root;
        root = root->left;
        delete temp;
        return true;
    }

    treeMH successor = TimNodeTheMang(root->right);
    string maSuccessor = successor->mh.MAMH;
    root->mh = successor->mh;
    XoaNodeMonHoc(root->right, maSuccessor);
    return true;
}

bool ThemNodeMonHoc(treeMH& root, Monhoc monHoc)
{
    if (root == nullptr)
    {
        root = new nodeMH{monHoc, nullptr, nullptr};
        return true;
    }

    if (monHoc.MAMH < root->mh.MAMH)
        return ThemNodeMonHoc(root->left, monHoc);

    if (monHoc.MAMH > root->mh.MAMH)
        return ThemNodeMonHoc(root->right, monHoc);

    return false;
}


treeMH TimMonHoc(treeMH root, string maMH)
{
    while (root != nullptr)
    {
        if (maMH == root->mh.MAMH)
            return root;

        if (maMH < root->mh.MAMH)
            root = root->left;
        else
            root = root->right;
    }

    return nullptr;
}

bool MonHocDaMoLopTinChi(
    DS_LTC& dsLTC,
    string maMH
)
{
    for (int i = 0; i < dsLTC.n; i++)
    {
        if (dsLTC.nodes[i]->MAMH == maMH)
            return true;
    }

    return false;
}

bool ThemMonHoc(treeMH& root, int& n, Monhoc monHoc, string& loi) {
    loi.clear();
    Monhoc daChuanHoa = ChuanHoaMonHoc(monHoc);
    if (!ThemNodeMonHoc(root, daChuanHoa)) {
        loi = "Mã môn học đã tồn tại.";
        return false;
    }
    ++n;
    return true;
}

bool XoaMonHoc(
    treeMH& root,
    int& n,
    DS_LTC& dsLTC,
    string maMH,
    string& loi
)
{
    loi.clear();

    if (root == nullptr)
    {
        loi = "Danh sách môn học đang rỗng.";
        return false;
    }

    if (MonHocDaMoLopTinChi(dsLTC, maMH))
    {
        loi = "Môn học đang được sử dụng trong lớp tín chỉ.";
        return false;
    }

    if (!XoaNodeMonHoc(root, maMH))
    {
        loi = "Không tìm thấy môn học.";
        return false;
    }
    --n;
    return true;
}

bool HieuChinhMonHoc(
    treeMH& root,
    string maMH,
    Monhoc duLieuMoi,
    string& loi
) {
    loi.clear();
    Monhoc daChuanHoa = duLieuMoi;
    daChuanHoa.MAMH = maMH;
    daChuanHoa = ChuanHoaMonHoc(daChuanHoa);
    if (root == nullptr) {
        loi = "Danh sách môn học đang rỗng.";
        return false;
    }
    treeMH monHocCanSua = TimMonHoc(root, daChuanHoa.MAMH);
    if (monHocCanSua == nullptr) {
        loi = "Không tìm thấy môn học.";
        return false;
    }
    monHocCanSua->mh.TENMH = daChuanHoa.TENMH;
    monHocCanSua->mh.STCLT = daChuanHoa.STCLT;
    monHocCanSua->mh.STCTH = daChuanHoa.STCTH;
    return true;
}

void ChepMonHocTheoMa(treeMH root, treeMH ketQua[], int& viTri) {
    if (root == nullptr) return;
    ChepMonHocTheoMa(root->left, ketQua, viTri);
    ketQua[viTri++] = root;
    ChepMonHocTheoMa(root->right, ketQua, viTri);
}

treeMH* LayDanhSachMonHoc(treeMH root, int n, int& soLuong) {
    soLuong = n;
    if (soLuong == 0) return nullptr;
    treeMH* ketQua = new treeMH[soLuong];
    int viTri = 0;
    ChepMonHocTheoMa(root, ketQua, viTri);
    return ketQua;
}

bool MonHocDungTruoc(treeMH a, treeMH b) {
    int ketQua = SoSanhKhongPhanBietHoaThuong(a->mh.TENMH, b->mh.TENMH);
    if (ketQua != 0) return ketQua < 0;
    return a->mh.MAMH < b->mh.MAMH;
}

void SapXepConTroMonHocTheoTen(treeMH danhSach[], int soLuong) {
    MergeSort(danhSach, soLuong, MonHocDungTruoc);
}
