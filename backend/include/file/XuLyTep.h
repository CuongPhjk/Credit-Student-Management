#ifndef XU_LY_TEP_H
#define XU_LY_TEP_H

#include "../model/KhaiBao.h"

bool DocDanhSachMonHoc(const string& tenFile, treeMH& dsMonHoc, string& loi);
bool GhiDanhSachMonHoc(const string& tenFile, treeMH dsMonHoc, string& loi);

// Each class header is followed by its students and a standalone # terminator.
bool DocDanhSachLopSinhVien(const string& tenFile, DS_LOP& dsLop, string& loi);
bool GhiDanhSachLopSinhVien(const string& tenFile, const DS_LOP& dsLop, string& loi);

// Each credit class header is followed by registrations and a # terminator.
bool DocDanhSachLopTinChi(const string& tenFile, DS_LTC& dsLTC, string& loi);
bool GhiDanhSachLopTinChi(const string& tenFile, const DS_LTC& dsLTC, string& loi);

#endif
