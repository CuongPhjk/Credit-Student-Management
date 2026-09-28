#ifndef DANG_KY_MANAGER_H
#define DANG_KY_MANAGER_H

#include <string>

#include "model/AppData.h"

class DangKyManager {
public:
    explicit DangKyManager(AppData& appData);

    bool dangKy(int maLopTC, const std::string& maSV, std::string& loi);
    bool huyDangKy(int maLopTC, const std::string& maSV, std::string& loi);
    bool daDangKy(int maLopTC, const std::string& maSV) const;

private:
    bool luu(std::string& loi) const;

    AppData& appData_;
};

#endif
