#pragma once

#include <iostream>
#include <string>
#include <cstddef>
#include <memory>

using namespace std;

const int MAXLOP = 10000;
const int MAXLTC = 10000;



struct Monhoc {
    string MAMH, TENMH;
    int STCLT, STCTH;
};

struct nodeMH {
    Monhoc mh;
    nodeMH *left;
    nodeMH *right;
};
typedef nodeMH *treeMH;

struct DangKy {
    string MASV;
    float DIEM = -1.0F;
    bool HUYDK = false;
};

struct nodeDK {
    DangKy dk;
    nodeDK *next;
};
typedef nodeDK *PTRDK;

struct Loptinchi {
    int MALOPTC;
    string MAMH, NIENKHOA;
    int HOCKY, NHOM, SOSVMIN, SOSVMAX;
    bool HUYLOP = false;
    PTRDK dssvdk = nullptr;
};

struct DS_LTC {
    Loptinchi *nodes[MAXLTC];
    int n = 0;
    int maTiepTheo = 1;
};

struct Sinhvien {
    string MASV, HO, TEN, PHAI, SODT;
};

struct nodeSV {
    Sinhvien sv;
    nodeSV *next;
};
typedef nodeSV *PTRSV;

struct Lop {
    string MALOP, TENLOP;
    PTRSV dssv = nullptr;
    int soSinhVien = 0;
};

struct DS_LOP {
    Lop nodes[MAXLOP];
    int n = 0;
    // Changes whenever node membership or the owning class array is rebuilt.
    unsigned long long phienBan = 0;
};

// ==========================================
// APP DATA (IN-MEMORY CENTRAL STORE)
// ==========================================

struct AppData {
    treeMH dsMonHoc = nullptr;
    unsigned long long phienBanMonHoc = 0;
    int n = 0;
    DS_LTC dsLopTinChi{};
    DS_LOP dsLop{};
    string tenFileMonHoc;
    string tenFileLopSinhVien;
    string tenFileLopTinChi;

    AppData() = default;
    ~AppData();
    AppData(const AppData&) = delete;
    AppData& operator=(const AppData&) = delete;
    void clear();
};

// ==========================================
// UTILS
// ==========================================

string XoaKhoangTrangDauCuoi(string chuoi);
string XoaKhoangTrangThua(string chuoi);
string ChuyenThanhChuHoa(string chuoi);
string ChuyenThanhChuThuong(string chuoi);
string ChuanHoaMa(string ma);
string ChuanHoaHoTen(string hoTen);
bool ChuyenSangSoNguyen(string chuoi, int& ketQua);
bool TachChuoi(
    string chuoi,
    char kyTuPhanCach,
    string dsKetQua[],
    int soPhanTu
);
bool LaChuoiUtf8HopLe(string chuoi);
std::size_t DemSoKyTuUtf8(string chuoi);
int SoSanhKhongPhanBietHoaThuong(
    string chuoi1,
    string chuoi2
);

bool MaHopLe(string ma, int doDaiToiDa);
bool MaSinhVienHopLe(string maSV);
bool TenLopHopLe(string tenLop, string& loi);
bool SoDienThoaiHopLe(string soDienThoai);
bool PhaiHopLe(string phai);
bool NienKhoaHopLe(string nienKhoa);
string NienKhoaHienTai();
bool HocKyHopLe(int hocKy);
bool NhomHopLe(int nhom);
bool SiSoHopLe(int soSVMin, int soSVMax);
bool DiemHopLe(float diem);

// ==========================================
// CORE FUNCTIONS
// ==========================================

// Subject, student and registration exports allocate arrays of borrowed node pointers.
// Delete only those arrays, never the nodes. Credit-class export borrows the original array.
// Class export remains an allocated value array. Empty exports return nullptr and count 0.
treeMH* LayDanhSachMonHoc(treeMH root, int n, int& soLuong);
void SapXepConTroMonHocTheoTen(treeMH danhSach[], int soLuong);
Lop* LayDanhSachLop(DS_LOP& dsLop, int& soLuong);
Loptinchi** LayDanhSachLopTinChi(DS_LTC& dsLTC, int& soLuong);
PTRSV* LayDanhSachSinhVien(Lop& lop, int& soLuong);
void SapXepConTroSinhVienTheoMa(PTRSV danhSach[], int soLuong);

// Mon hoc
Monhoc ChuanHoaMonHoc(Monhoc monHoc);
void GiaiPhongCayMonHoc(treeMH& root);
treeMH TimMonHoc(treeMH root, string maMH);
bool MonHocDaMoLopTinChi(DS_LTC& dsLTC, string maMH);
bool ThemMonHoc(treeMH& root, int& n, Monhoc monHoc, string& loi);
bool HieuChinhMonHoc(
    treeMH& root,
    string maMH,
    Monhoc duLieuMoi,
    string& loi
);
bool XoaMonHoc(
    treeMH& root,
    int& n,
    DS_LTC& dsLTC,
    string maMH,
    string& loi
);

// Lop
void GiaiPhongDanhSachLop(DS_LOP& dsLop);
int TimViTriLop(DS_LOP& dsLop, string maLop);
Lop* TimLop(DS_LOP& dsLop, string maLop);
bool KiemTraTrungMaLop(DS_LOP& dsLop, string maLop);
bool ThemLop(DS_LOP& dsLop, Lop lop, string& loi);
bool HieuChinhLop(
    DS_LOP& dsLop,
    string maLop,
    string tenLopMoi,
    string& loi
);
bool XoaLop(DS_LOP& dsLop, string maLop, string& loi);

// Sinh vien
PTRSV TimSinhVienTrongLop(PTRSV dsSV, string maSV);
PTRSV TimSinhVienToanTruong(
    DS_LOP& dsLop,
    string maSV,
    int& viTriLop
);
int SoSanhSinhVienTheoTen(Sinhvien sv1, Sinhvien sv2);
void ChenSinhVienTheoTen(Lop& lop, Sinhvien sinhVien);
bool ThemSinhVien(
    DS_LOP& dsLop,
    string maLop,
    Sinhvien sinhVien,
    string& loi
);
bool HieuChinhSinhVien(
    DS_LOP& dsLop,
    string maSV,
    Sinhvien duLieuMoi,
    string& loi
);
bool SinhVienDaDangKy(DS_LTC& dsLTC, string maSV);
bool XoaSinhVien(
    DS_LOP& dsLop,
    DS_LTC& dsLTC,
    string maSV,
    string& loi
);
void GiaiPhongDanhSachSinhVien(PTRSV& dsSV);

// Lop tin chi
void GiaiPhongDanhSachLopTinChi(DS_LTC& dsLTC);
Loptinchi* TimLopTinChiTheoMa(DS_LTC& dsLTC, int maLopTC);
Loptinchi* TimLopTinChi(
    DS_LTC& dsLTC,
    string nienKhoa,
    int hocKy,
    string maMH,
    int nhom
);
bool ThemLopTinChi(
    DS_LTC& dsLTC,
    treeMH dsMonHoc,
    Loptinchi lopTinChi,
    string& loi
);
bool HieuChinhLopTinChi(
    DS_LTC& dsLTC,
    treeMH dsMonHoc,
    int maLopTC,
    Loptinchi duLieuMoi,
    string& loi
);
bool XoaLopTinChi(DS_LTC& dsLTC, int maLopTC, string& loi);
int DemSoSinhVienDangKy(Loptinchi lopTinChi);
int TinhSoChoTrong(Loptinchi lopTinChi);
bool HuyLopTinChi(DS_LTC& dsLTC, int maLopTC, string& loi);

// Dang ky
void GiaiPhongDanhSachDangKy(PTRDK& danhSach);
PTRDK TimDangKy(PTRDK dsDangKy, string maSV);
bool SinhVienDangKyLopTinChi(
    Loptinchi lopTinChi,
    string maSV
);
bool SinhVienDaDangKyMonTrongHocKy(
    DS_LTC& dsLTC,
    string maSV,
    string maMH,
    string nienKhoa,
    int hocKy,
    int maLopTCBoQua = -1
);
bool LopTinChiConCho(Loptinchi lopTinChi);
bool DangKyLopTinChi(
    DS_LTC& dsLTC,
    DS_LOP& dsLop,
    int maLopTC,
    string maSV,
    string& loi
);
bool HuyDangKy(
    DS_LTC& dsLTC,
    int maLopTC,
    string maSV,
    string& loi
);
PTRDK* LayDanhSachDangKy(
    Loptinchi& lopTinChi, int& soLuong
);

// ==========================================
// FILE PROCESSING
// ==========================================

bool DocDanhSachMonHoc(string tenFile, treeMH& dsMonHoc, int& n, string& loi);
bool GhiDanhSachMonHoc(string tenFile, treeMH dsMonHoc, string& loi);
bool DocDanhSachLopSinhVien(string tenFile, DS_LOP& dsLop, string& loi);
bool GhiDanhSachLopSinhVien(string tenFile, DS_LOP& dsLop, string& loi);
bool DocDanhSachLopTinChi(string tenFile, DS_LTC& dsLTC, string& loi);
bool GhiDanhSachLopTinChi(string tenFile, DS_LTC& dsLTC, string& loi);

// ==========================================
// MANAGERS
// ==========================================

class MonHocManager {
public:
    explicit MonHocManager(AppData& appData);

    bool docDanhSachMonHoc(std::string tenFile, std::string& loi);
    bool themMonHoc(Monhoc monHoc, std::string& loi);
    bool capNhatMonHoc(
        std::string maMH,
        Monhoc duLieuMoi,
        std::string& loi
    );
    bool xoaMonHoc(std::string maMH, std::string& loi);
    bool timMonHoc(std::string maMH, Monhoc& ketQua) ;
    treeMH* layDanhSachMonHoc(int& soLuong);
    // Borrowed array sorted by name. The manager owns the array.
    treeMH* layMonHocTheoTen(int& soLuong);
    int tongSoMonHoc();

private:
    void boThuTuTheoTen();
    AppData& appData_;
    std::unique_ptr<treeMH[]> dsTheoTen_;
    unsigned long long phienBanDangGiu_ = 0;
};

class LopSinhVienManager {
public:
    explicit LopSinhVienManager(AppData& appData);
    ~LopSinhVienManager();
    LopSinhVienManager(const LopSinhVienManager&) = delete;
    LopSinhVienManager& operator=(const LopSinhVienManager&) = delete;
    // Borrowed cached array sorted ascending; caller must not delete[].
    PTRSV* laySinhVienTheoMa(string maLop, int& soLuong);
    void giaiPhongThuTuSinhVien();

    bool docDanhSachLopSinhVien(std::string tenFile, std::string& loi);
    bool themLop(Lop lop, std::string& loi);
    bool capNhatLop(
        std::string maLop,
        std::string tenLopMoi,
        std::string& loi
    );
    bool xoaLop(std::string maLop, std::string& loi);
    bool timLop(std::string maLop, Lop& ketQua) ;
    Lop* layDanhSachLop(int& soLuong) ;
    int tongSoLop() ;

    bool themSinhVien(
        std::string maLop,
        Sinhvien sinhVien,
        std::string& loi
    );
    bool capNhatSinhVien(
        std::string maSV,
        Sinhvien duLieuMoi,
        std::string& loi
    );
    bool xoaSinhVien(std::string maSV, std::string& loi);
    bool timSinhVien(
        std::string maSV,
        Sinhvien& ketQua,
        std::string& maLop
    ) ;
    PTRSV* layDanhSachSinhVien(string maLop, int& soLuong) ;
    int tongSoSinhVienTrongLop(std::string maLop) ;
    int tongSoSinhVien() ;

private:
    bool luu(std::string& loi) ;

    AppData& appData_;
    PTRSV* dsTheoMa_ = nullptr;
    int soLuongTheoMa_ = 0;
    string maLopDangGiu_;
    unsigned long long phienBanDangGiu_ = 0;
};

class LopTinChiManager {
public:
    explicit LopTinChiManager(AppData& appData);

    bool docDanhSachLopTinChi(std::string tenFile, std::string& loi);
    bool themLopTinChi(Loptinchi lopTinChi, std::string& loi);
    bool capNhatLopTinChi(
        int maLopTC,
        Loptinchi duLieuMoi,
        std::string& loi
    );
    bool xoaLopTinChi(int maLopTC, std::string& loi);
    bool timLopTinChi(int maLopTC, Loptinchi& ketQua) ;
    Loptinchi** layDanhSachLopTinChi(int& soLuong) ;
    int tongSoLopTinChi() ;

private:
    bool luu(std::string& loi) ;

    AppData& appData_;
};

class DangKyManager {
public:
    explicit DangKyManager(AppData& appData);

    bool dangKy(int maLopTC, std::string maSV, std::string& loi);
    bool huyDangKy(int maLopTC, std::string maSV, std::string& loi);
    bool daDangKy(int maLopTC, std::string maSV) ;
    PTRDK* layDanhSach(int maLopTC, int& soLuong, std::string& loi) ;
    bool timSinhVien(string maSV, Sinhvien& ketQua) ;

private:
    bool luu(std::string& loi) ;

    AppData& appData_;
};
