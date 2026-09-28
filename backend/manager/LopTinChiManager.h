#ifndef LOP_TIN_CHI_MANAGER_H
#define LOP_TIN_CHI_MANAGER_H

#include <string>

#include "model/AppData.h"

class LopTinChiManager {
public:
    explicit LopTinChiManager(AppData& appData);

    bool docDanhSachLopTinChi(const std::string& tenFile, std::string& loi);
    bool themLopTinChi(const Loptinchi& lopTinChi, std::string& loi);
    bool capNhatLopTinChi(
        int maLopTC,
        const Loptinchi& duLieuMoi,
        std::string& loi
    );
    bool xoaLopTinChi(int maLopTC, std::string& loi);
    bool timLopTinChi(int maLopTC, Loptinchi& ketQua) const;
    int layDanhSachLopTinChi(
        Loptinchi dsKetQua[],
        int kichThuocToiDa
    ) const;
    int tongSoLopTinChi() const;

private:
    bool luu(std::string& loi) const;

    AppData& appData_;
};

#endif
