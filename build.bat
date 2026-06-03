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
REM 步骤: 编译知识包 (YAML → JSON)
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
echo.

REM 安装依赖
echo.
echo 📦 安装依赖...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

REM 清理旧的构建
echo.
echo 🧹 清理旧构建...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo ✅ 清理完成

REM 打包
echo.
echo 🔨 开始打包为单文件EXE...
echo 注意: 首次打包可能需要3-5分钟，请耐心等待
echo.

REM TODO Phase 8: --add-data "prompt_tool/knowledge_packs_compiled/*.json;prompt_tool/knowledge_packs_compiled"
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "智能提示词工坊" ^
    --icon NONE ^
    --add-data "prompt_tool;prompt_tool" ^
    --hidden-import "customtkinter" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "prompt_tool" ^
    --hidden-import "prompt_tool.knowledge" ^
    --hidden-import "prompt_tool.engine" ^
    --hidden-import "prompt_tool.generator" ^
    --hidden-import "prompt_tool.app" ^
    --collect-data "customtkinter" ^
    run.py

if %errorlevel% neq 0 (
    echo ❌ 打包失败！请查看上方错误信息
    pause
    exit /b 1
)

echo.
echo ✅ 打包成功！
echo.
echo 📁 输出文件：dist\智能提示词工坊.exe
echo 大小：
dir "dist\智能提示词工坊.exe" /-c 2>nul || dir "dist\智能提示词工坊.exe"

echo.
echo ============================================
echo   🎉 打包完成！请将 dist\智能提示词工坊.exe
echo      发送给他人使用，无需安装Python
echo ============================================

pause
