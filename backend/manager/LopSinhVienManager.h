#ifndef LOP_SINH_VIEN_MANAGER_H
#define LOP_SINH_VIEN_MANAGER_H

#include <string>

#include "model/AppData.h"

class LopSinhVienManager {
public:
    explicit LopSinhVienManager(AppData& appData);

    bool docDanhSachLopSinhVien(const std::string& tenFile, std::string& loi);

    bool themLop(const Lop& lop, std::string& loi);
    bool capNhatLop(
        const std::string& maLop,
        const std::string& tenLopMoi,
        std::string& loi
    );
    bool xoaLop(const std::string& maLop, std::string& loi);
    bool timLop(const std::string& maLop, Lop& ketQua) const;
    int layDanhSachLop(Lop dsKetQua[], int kichThuocToiDa) const;
    int tongSoLop() const;

    bool themSinhVien(
        const std::string& maLop,
        const Sinhvien& sinhVien,
        std::string& loi
    );
    bool capNhatSinhVien(
        const std::string& maSV,
        const Sinhvien& duLieuMoi,
        std::string& loi
    );
    bool xoaSinhVien(const std::string& maSV, std::string& loi);
    bool timSinhVien(
        const std::string& maSV,
        Sinhvien& ketQua,
        std::string& maLop
    ) const;
    int layDanhSachSinhVien(
        const std::string& maLop,
        Sinhvien dsKetQua[],
        int kichThuocToiDa
    ) const;
    int tongSoSinhVienTrongLop(const std::string& maLop) const;
    int tongSoSinhVien() const;

private:
    bool luu(std::string& loi) const;

    AppData& appData_;
    std::string tenFileLopSinhVien_;
};

#endif
