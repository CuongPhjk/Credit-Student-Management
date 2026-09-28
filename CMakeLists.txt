cmake_minimum_required(VERSION 3.15)

project(credit_student_management LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

execute_process(
    COMMAND "${Python_EXECUTABLE}" -m pybind11 --cmakedir
    OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE PYBIND11_CMAKE_RESULT
)
if(NOT PYBIND11_CMAKE_RESULT EQUAL 0)
    message(FATAL_ERROR
        "Khong tim thay pybind11. Hay chay: pip install -r requirements.txt"
    )
endif()
list(APPEND CMAKE_PREFIX_PATH "${PYBIND11_CMAKE_DIR}")
find_package(pybind11 CONFIG REQUIRED)

add_library(credit_backend_core STATIC
    backend/src/model/AppData.cpp
    backend/src/functions/HamMonHoc.cpp
    backend/src/functions/HamLopTinChi.cpp
    backend/src/functions/HamLop.cpp
    backend/src/functions/HamSinhVien.cpp
    backend/src/functions/HamDangKy.cpp
    backend/src/functions/HamDiem.cpp
    backend/src/file/XuLyTep.cpp
    backend/src/manager/MonHocManager.cpp
    backend/src/manager/LopTinChiManager.cpp
    backend/src/manager/LopSinhVienManager.cpp
    backend/src/manager/DangKyManager.cpp
    backend/src/manager/DiemManager.cpp
    backend/src/utils/KiemTraDuLieu.cpp
    backend/src/utils/XuLyChuoi.cpp
)
set_target_properties(credit_backend_core PROPERTIES
    POSITION_INDEPENDENT_CODE ON
)
target_include_directories(credit_backend_core PUBLIC
    "${CMAKE_CURRENT_SOURCE_DIR}/backend/include"
    "${CMAKE_CURRENT_SOURCE_DIR}/backend/include/model"
    "${CMAKE_CURRENT_SOURCE_DIR}/backend/include/functions"
    "${CMAKE_CURRENT_SOURCE_DIR}/backend/manager"
)

pybind11_add_module(_credit_backend bridge/Bindings.cpp)
target_link_libraries(_credit_backend PRIVATE credit_backend_core)
set_target_properties(_credit_backend PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bridge"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bridge"
)
foreach(CONFIG Debug Release RelWithDebInfo MinSizeRel)
    string(TOUPPER "${CONFIG}" CONFIG_UPPER)
    set_target_properties(_credit_backend PROPERTIES
        "LIBRARY_OUTPUT_DIRECTORY_${CONFIG_UPPER}" "${CMAKE_CURRENT_SOURCE_DIR}/bridge"
        "RUNTIME_OUTPUT_DIRECTORY_${CONFIG_UPPER}" "${CMAKE_CURRENT_SOURCE_DIR}/bridge"
    )
endforeach()

if(MSVC)
    target_compile_options(credit_backend_core PRIVATE /W4 /utf-8)
    target_compile_options(_credit_backend PRIVATE /W4 /utf-8)
else()
    target_compile_options(credit_backend_core PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(_credit_backend PRIVATE -Wall -Wextra -Wpedantic)
endif()

include(CTest)
if(BUILD_TESTING)
    add_executable(test_mon_hoc tests/cpp/test_subject.cpp)
    target_link_libraries(test_mon_hoc PRIVATE credit_backend_core)
    add_test(NAME test_mon_hoc COMMAND test_mon_hoc)

    add_executable(test_lop_tin_chi tests/cpp/test_credit_class.cpp)
    target_link_libraries(test_lop_tin_chi PRIVATE credit_backend_core)
    add_test(NAME test_lop_tin_chi COMMAND test_lop_tin_chi)

    add_executable(test_lop_sinh_vien tests/cpp/test_student.cpp)
    target_link_libraries(test_lop_sinh_vien PRIVATE credit_backend_core)
    add_test(NAME test_lop_sinh_vien COMMAND test_lop_sinh_vien)

    add_executable(test_dang_ky tests/cpp/test_registration.cpp)
    target_link_libraries(test_dang_ky PRIVATE credit_backend_core)
    add_test(NAME test_dang_ky COMMAND test_dang_ky)

    add_executable(test_diem tests/cpp/test_score.cpp)
    target_link_libraries(test_diem PRIVATE credit_backend_core)
    add_test(NAME test_diem COMMAND test_diem)

endif()
