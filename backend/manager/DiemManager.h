#ifndef DIEM_MANAGER_H
#define DIEM_MANAGER_H

#include <string>

#include "model/AppData.h"

class DiemManager {
public:
    explicit DiemManager(AppData& appData);

    int demSinhVien(
        const std::string& nienKhoa,
        int hocKy,
        const std::string& maMH,
        int nhom,
        std::string& loi
    ) const;
    int layDanhSachSinhVien(
        const std::string& nienKhoa,
        int hocKy,
        const std::string& maMH,
        int nhom,
        Diemsinhvien dsKetQua[],
        int kichThuocToiDa,
        std::string& loi
    ) const;
    bool capNhatDiem(
        const std::string& nienKhoa,
        int hocKy,
        const std::string& maMH,
        int nhom,
        const std::string& maSV,
        float diemMoi,
        std::string& loi
    );
    bool capNhatDanhSachDiem(
        const std::string& nienKhoa,
        int hocKy,
        const std::string& maMH,
        int nhom,
        const Diemcapnhat dsDiemMoi[],
        int soLuong,
        std::string& loi
    );

private:
    bool luu(std::string& loi) const;

    AppData& appData_;
};

#endif
