#ifndef MON_HOC_MANAGER_H
#define MON_HOC_MANAGER_H

#include <string>

#include "model/AppData.h"

class MonHocManager {
public:
    explicit MonHocManager(AppData& appData);

    bool docDanhSachMonHoc(const std::string& tenFile, std::string& loi);

    bool themMonHoc(const Monhoc& monHoc, std::string& loi);

    bool capNhatMonHoc(
        const std::string& maMH,
        const Monhoc& duLieuMoi,
        std::string& loi
    );

    bool xoaMonHoc(const std::string& maMH, std::string& loi);

    bool timMonHoc(const std::string& maMH, Monhoc& ketQua) const;

    int layDanhSachMonHoc(
        Monhoc dsKetQua[],
        int kichThuocToiDa
    ) const;

    int tongSoMonHoc() const;

private:
    AppData& appData_;
    std::string tenFileMonHoc_;
};

#endif
