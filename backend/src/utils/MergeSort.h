#pragma once

template <typename T, typename SoSanh>
void ChiaVaTron(T ds[], T tam[], int trai, int phai, SoSanh dungTruoc) {
    if (trai >= phai) return;
    int giua = trai + (phai - trai) / 2;
    ChiaVaTron(ds, tam, trai, giua, dungTruoc);
    ChiaVaTron(ds, tam, giua + 1, phai, dungTruoc);

    int i = trai;
    int j = giua + 1;
    int k = trai;
    while (i <= giua && j <= phai) {
        if (dungTruoc(ds[j], ds[i])) {
            tam[k++] = ds[j++];
        } else {
            tam[k++] = ds[i++];
        }
    }
    while (i <= giua) tam[k++] = ds[i++];
    while (j <= phai) tam[k++] = ds[j++];
    for (int viTri = trai; viTri <= phai; ++viTri) {
        ds[viTri] = tam[viTri];
    }
}

template <typename T, typename SoSanh>
void MergeSort(T ds[], int soLuong, SoSanh dungTruoc) {
    if (soLuong < 2) return;
    T* tam = new T[soLuong];
    ChiaVaTron(ds, tam, 0, soLuong - 1, dungTruoc);
    delete[] tam;
}
