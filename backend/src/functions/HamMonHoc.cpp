#include "HamMonHoc.h"

#include "../../include/utils/XuLyChuoi.h"

using namespace std;

namespace {

bool dungTruocTheoTen(const Monhoc& left, const Monhoc& right)
{
    const int soSanhTen = SoSanhKhongPhanBietHoaThuong(
        left.TENMH, right.TENMH
    );
    if (soSanhTen != 0)
        return soSanhTen < 0;

    return left.MAMH < right.MAMH;
}

treeMH TimNodeTheMang(treeMH root)
{
    while (root->left != nullptr)
    {
        root = root->left;
    }

    return root;
}

bool XoaNodeMonHoc(treeMH& root, const string& maMH)
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
    const string maSuccessor = successor->mh.MAMH;
    root->mh = successor->mh;
    XoaNodeMonHoc(root->right, maSuccessor);
    return true;
}

bool ThemNodeMonHoc(treeMH& root, const Monhoc& monHoc)
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

}  // namespace

void SapXepMonHocTheoTen(Monhoc dsMonHoc[], int soLuong)
{
    if (dsMonHoc == nullptr || soLuong <= 1)
        return;

    for (int i = 1; i < soLuong; ++i)
    {
        Monhoc current = dsMonHoc[i];
        int j = i - 1;
        while (j >= 0 && dungTruocTheoTen(current, dsMonHoc[j]))
        {
            dsMonHoc[j + 1] = dsMonHoc[j];
            --j;
        }
        dsMonHoc[j + 1] = current;
    }
}

int TongSoTinChi(const Monhoc& monHoc)
{
    return monHoc.STCLT + monHoc.STCTH;
}

void GiaiPhongCayMonHoc(treeMH& root)
{
    if (root == nullptr)
        return;

    GiaiPhongCayMonHoc(root->left);
    GiaiPhongCayMonHoc(root->right);
    delete root;
    root = nullptr;
}

int DemMonHoc(treeMH root)
{
    if (root == nullptr)
        return 0;

    return 1 + DemMonHoc(root->left) + DemMonHoc(root->right);
}

void ChuyenCayMonHocSangMang(
    treeMH root,
    Monhoc dsMonHoc[],
    int& soLuong
)
{
    if (root == nullptr || dsMonHoc == nullptr)
        return;

    ChuyenCayMonHocSangMang(root->left, dsMonHoc, soLuong);
    dsMonHoc[soLuong++] = root->mh;
    ChuyenCayMonHocSangMang(root->right, dsMonHoc, soLuong);
}

treeMH TimMonHoc(treeMH root, const string& maMH)
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

bool KiemTraTrungMaMonHoc(treeMH root, const string& maMH)
{
    return TimMonHoc(root, maMH) != nullptr;
}

bool MonHocDaMoLopTinChi(
    const DS_LTC& dsLTC,
    const string& maMH
)
{
    for (int i = 0; i < dsLTC.n; i++)
    {
        if (dsLTC.nodes[i] == NULL)
            continue;

        if (dsLTC.nodes[i]->MAMH == maMH)
            return true;
    }

    return false;
}

bool ThemMonHoc(treeMH& root, const Monhoc& monHoc, string& loi) {
    loi.clear();

    if (monHoc.MAMH.empty()) {
        loi = "Ma mon hoc khong duoc de trong!";
        return false;
    }

    if (monHoc.MAMH.length() > 10) {
        loi = "Ma mon hoc toi da 10 ky tu!";
        return false;
    }

    if (monHoc.TENMH.empty()) {
        loi = "Ten mon hoc khong duoc de trong!";
        return false;
    }

    if (DemSoKyTuUtf8(monHoc.TENMH) > 50) {
        loi = "Ten mon hoc toi da 50 ky tu!";
        return false;
    }

    if (monHoc.STCLT <= 0) {
        loi = "So tin chi ly thuyet phai lon hon 0!";
        return false;
    }

    if (monHoc.STCTH < 0) {
        loi = "So tin chi thuc hanh khong duoc am!";
        return false;
    }

    if (!ThemNodeMonHoc(root, monHoc))
    {
        loi = "Ma mon hoc da ton tai!";
        return false;
    }

    return true;
}

bool XoaMonHoc(
    treeMH& root,
    const DS_LTC& dsLTC,
    const string& maMH,
    string& loi
)
{
    loi.clear();

    if (maMH.empty())
    {
        loi = "Ma mon hoc khong duoc de trong.";
        return false;
    }

    if (root == nullptr)
    {
        loi = "Danh sach mon hoc dang rong.";
        return false;
    }

    if (MonHocDaMoLopTinChi(dsLTC, maMH))
    {
        loi = "Mon hoc dang duoc su dung trong lop tin chi.";
        return false;
    }

    if (!XoaNodeMonHoc(root, maMH))
    {
        loi = "Khong tim thay mon hoc.";
        return false;
    }
    return true;
}

bool HieuChinhMonHoc(
    treeMH& root,
    const string& maMH,
    const Monhoc& duLieuMoi,
    string& loi
)
{
    loi.clear();

    if (maMH.empty())
    {
        loi = "Ma mon hoc khong duoc de trong!";
        return false;
    }

    if (root == nullptr)
    {
        loi = "Danh sach mon hoc dang rong!";
        return false;
    }

    treeMH monHocCanSua = TimMonHoc(root, maMH);

    if (monHocCanSua == nullptr)
    {
        loi = "Khong tim thay mon hoc!";
        return false;
    }

    if (duLieuMoi.TENMH.empty())
    {
        loi = "Ten mon hoc khong duoc de trong!";
        return false;
    }

    if (DemSoKyTuUtf8(duLieuMoi.TENMH) > 50)
    {
        loi = "Ten mon hoc toi da 50 ky tu!";
        return false;
    }

    if (duLieuMoi.STCLT <= 0)
    {
        loi = "So tin chi ly thuyet phai lon hon 0!";
        return false;
    }

    if (duLieuMoi.STCTH < 0)
    {
        loi = "So tin chi thuc hanh khong duoc am!";
        return false;
    }

    monHocCanSua->mh.TENMH = duLieuMoi.TENMH;
    monHocCanSua->mh.STCLT = duLieuMoi.STCLT;
    monHocCanSua->mh.STCTH = duLieuMoi.STCTH;

    return true;
}
