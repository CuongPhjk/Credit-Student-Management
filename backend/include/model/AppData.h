#ifndef APP_DATA_H
#define APP_DATA_H

#include "KhaiBao.h"

class AppData {
public:
    AppData() = default;
    ~AppData();

    AppData(const AppData&) = delete;
    AppData& operator=(const AppData&) = delete;

    treeMH& dsMonHoc();
    const treeMH& dsMonHoc() const;

    DS_LTC& dsLopTinChi();
    const DS_LTC& dsLopTinChi() const;

    DS_LOP& dsLop();
    const DS_LOP& dsLop() const;

    std::string& tenFileLopTinChi();
    const std::string& tenFileLopTinChi() const;

    void clear();

private:
    std::string tenFileLopTinChi_;
    treeMH dsMonHoc_ = nullptr;
    DS_LTC dsLopTinChi_{};
    DS_LOP dsLop_{};
};

#endif
