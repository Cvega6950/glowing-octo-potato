cmake_minimum_required(VERSION 3.16)
project(dsrun CXX C)

# MELONDS_DIR: a checkout of rileytestut/melonDS at a53f9ba, the melonDS core inside Delta.
if(NOT MELONDS_DIR)
    message(FATAL_ERROR "Set MELONDS_DIR to a rileytestut/melonDS checkout at a53f9ba")
endif()

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
# What melonDS's own top-level CMakeLists.txt sets before src/ (version 0.9.5).
set(CMAKE_MODULE_PATH "${MELONDS_DIR}/cmake" ${CMAKE_MODULE_PATH})
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_compile_definitions(MELONDS_VERSION="0.9.5")
if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
    add_definitions(-DARCHITECTURE_x86_64=1)
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
    add_definitions(-DARCHITECTURE_ARM64=1)
endif()
string(REPLACE "-O2" "-O3" CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE}")
string(REPLACE "-O2" "-O3" CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")
# As in Delta: no JIT (interpreter only), software renderer only, no Qt/SDL frontend.
set(ENABLE_JIT OFF CACHE BOOL "" FORCE)
set(ENABLE_OGLRENDERER OFF CACHE BOOL "" FORCE)
set(BUILD_QT_SDL OFF CACHE BOOL "" FORCE)
set(ENABLE_LTO_RELEASE OFF CACHE BOOL "" FORCE)

add_subdirectory(${MELONDS_DIR}/src melonds-core)

find_package(PNG REQUIRED)
add_library(dsrun SHARED dsrun.cpp)
target_include_directories(dsrun PRIVATE ${MELONDS_DIR}/src)
target_link_libraries(dsrun PRIVATE core PNG::PNG pthread)
# Bind the core's calls to time() to dsrun's fake clock.
target_link_options(dsrun PRIVATE -Wl,-Bsymbolic)
