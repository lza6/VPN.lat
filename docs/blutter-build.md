# blutter 构建（Flutter AOT 反编译）Windows 全坑记录

目标: 反编译 `libapp.so`（Dart 3.10.8 snapshot, android arm64）。

## 环境要求
- Visual Studio 2022/2026 + C++ 桌面开发 + CMake
- Python 3 + pip（pyelftools, requests）
- CMake（VS 自带或独立版）、Ninja（`pip install ninja`）

## 坑 1: git clone dart-sdk 失败
`git clone https://github.com/dart-lang/sdk.git` 需代理:
```bash
git config --global http.proxy http://127.0.0.1:10808
```

## 坑 2: cmake 找不到编译器 / LNK1104 kernel32.lib
必须先进入 VS 开发者环境再跑 blutter.py:
```cmd
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
python blutter\blutter.py <lib目录> <输出目录>
```

## 坑 3: ICU 找不到
先跑 `python scripts\init_env_win.py`（下载 ICU 73 + Capstone 到 external/）。
blutter 的 CMakeLists 在 MSVC 下只设 `ICU_ROOT`，但 `FindICU` 会命中 **Windows SDK 的 icuuc.lib**（C API 导出不全，缺 `u_getPropertyName_73` 等 19 个符号）→ LNK2001。

修复（双保险）:
1. blutter.py 的 cmake 调用追加:
   `-DICU_ROOT=<...>/external/icu-windows -DICU_UC_LIBRARY_RELEASE=<...>/external/icu-windows/lib64/icuuc.lib -DICU_INCLUDE_DIR=<...>/external/icu-windows/include`
2. `blutter/blutter/CMakeLists.txt` 的 `target_link_libraries` 追加 `${ICU_LIBRARIES}`。

## 坑 4: 'vswhere.exe' 不是内部或外部命令
vcvars64.bat 已解决（它会设置 vswhere 路径）。

## 版本识别
snapshot hash 在 libflutter.so 中，Dart SDK 版本字符串格式 `3.10.8 (stable)`。
blutter 输出 `pp.txt`（对象池）、`asm/`（逐函数 ARM64 反汇编+符号）、`objs.txt`。

## 提示
- 搜索字符串直接在 `pp.txt` grep，定位到函数后看 `asm/<lib>/<file>.dart`。
- Flutter AOT 字符串是长度前缀+分离存储，`strings` 直读 libapp.so 会碎片化，建议 python 正则 `[ -~]{4,}` 全量提。
