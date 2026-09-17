#ifndef KHAI_BAO_H
#define KHAI_BAO_H

#include <iostream>
#include <string>
using namespace std;
const int MAXLOP = 10000;
const int MAXLTC = 10000;

struct Monhoc {
    string MAMH, TENMH;
    int STCLT, STCTH;
};

struct nodeMH{
    Monhoc mh;
    nodeMH *left;
    nodeMH *right;
};
typedef nodeMH *treeMH;

// DANG KY
struct Dangky{
    string MASV;
    float DIEM;
    bool HUYDK = false;
};

struct nodeDK{
    Dangky dk;
    nodeDK *next;
};

typedef nodeDK *PTRDK;

// DSLTC

struct Loptinchi{
    int MALOPTC;
    string MAMH, NIENKHOA;
    int HOCKY, NHOM, SOSVMIN, SOSVMAX;
    bool HUYLOP = false;
    PTRDK dssvdk = NULL;
};

struct DS_LTC{
    Loptinchi *nodes[MAXLTC];
    int n =0;
};

// DSSV
struct Sinhvien{
    string MASV, HO, TEN, PHAI, SODT;
};
struct nodeSV{
    Sinhvien sv;
    nodeSV *next;
};
typedef nodeSV *PTRSV;

// DSLOP
struct Lop{
    string MALOP, TENLOP;
    PTRSV dssv = NULL;
};

struct DS_LOP{
    Lop nodes[MAXLOP];
    int n = 0;
};

#endif
