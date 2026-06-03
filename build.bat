@echo off
chcp 65001 >nul
title 智能提示词工坊 - 打包构建

echo ============================================
echo   🧠 智能提示词工坊 - 打包构建工具
echo ============================================
echo.

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python 已安装

REM ============================================
REM 步骤 1: 编译知识包 (YAML → JSON)
REM ============================================
echo.
echo 📦 编译知识包...
python build_packs.py
if %errorlevel% neq 0 (
    echo ❌ 知识包编译失败！请修复上方错误
    pause
    exit /b 1
)
echo ✅ 知识包编译完成

REM ============================================
REM 步骤 2: Gzip 压缩知识包 (PKG-02)
REM ============================================
echo.
echo 📦 压缩知识包...
python -c "import gzip,json,os; src='prompt_tool/knowledge_packs_compiled'; [gzip.open(os.path.join(src,f).replace('.json','.json.gz'),'wb').write(open(os.path.join(src,f),'rb').read()) for f in os.listdir(src) if f.endswith('.json') and not f.endswith('.gz')]; print('✅ 压缩完成')"
echo ✅ 知识包压缩完成

REM ============================================
REM 步骤 3: 安装依赖
REM ============================================
echo.
echo 📦 安装依赖...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

REM ============================================
REM 步骤 4: 清理旧构建
REM ============================================
echo.
echo 🧹 清理旧构建...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo ✅ 清理完成

REM ============================================
REM 步骤 5: 打包 (PKG-01: --onedir 模式)
REM ============================================
echo.
echo 🔨 开始打包为目录EXE (onedir)...
echo 注意: 首次打包可能需要3-5分钟

pyinstaller ^
    --onedir ^
    --windowed ^
    --name "智能提示词工坊" ^
    --icon NONE ^
    --add-data "prompt_tool;prompt_tool" ^
    --hidden-import "customtkinter" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "yaml" ^
    --hidden-import "pydantic" ^
    run.py

if %errorlevel% neq 0 (
    echo ❌ 打包失败！请查看上方错误信息
    pause
    exit /b 1
)

echo.
echo ✅ 打包成功！
echo.
echo 📁 输出目录：dist\智能提示词工坊\
dir "dist\智能提示词工坊\智能提示词工坊.exe" /-c 2>nul
echo.

REM ============================================
REM 步骤 6: 检查体积 (PKG-03)
REM ============================================
for /f "usebackq tokens=3" %%i in (`dir "dist\智能提示词工坊" /s /-c 2^>nul ^| findstr "个文件"`) do (
    set SIZE=%%i
)
echo 📊 输出目录总大小: %SIZE% 字节
echo.
echo ============================================
echo   🎉 打包完成！
echo   目标: ^<50MB
echo   双击 "dist\智能提示词工坊\智能提示词工坊.exe" 运行
echo ============================================

pause
