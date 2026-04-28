@echo off
setlocal EnableDelayedExpansion

set EXE_NAME=Organizacion_CV
set VENV_DIR=.venv_build

echo ==============================
echo   BUILD AUTOMATICO DEL EXE
echo ==============================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: No se encontro Python en el sistema.
    echo.
    echo Instala Python y marca la opcion:
    echo Add Python to PATH
    echo.
    pause
    exit /b 1
)

echo [0/7] Limpiando variables conflictivas de Conda/Qt...
set PYTHONHOME=
set PYTHONPATH=
set QT_PLUGIN_PATH=
set QML2_IMPORT_PATH=
set CONDA_PREFIX=
set CONDA_DEFAULT_ENV=
set CONDA_PROMPT_MODIFIER=
set CONDA_EXE=
set CONDA_PYTHON_EXE=
set CONDA_SHLVL=

echo [1/7] Borrando entorno virtual anterior...
if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"

echo [2/7] Creando entorno virtual...
python -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual.
    pause
    exit /b 1
)

echo [3/7] Actualizando pip...
call "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: No se pudo actualizar pip.
    pause
    exit /b 1
)

echo [4/7] Instalando dependencias...
call "%VENV_DIR%\Scripts\python.exe" -m pip install -r Requirements.txt
if errorlevel 1 (
    echo ERROR: Fallo instalando Requirements.txt
    pause
    exit /b 1
)

echo [5/7] Limpiando compilaciones anteriores...
if exist "%EXE_NAME%" rmdir /s /q "%EXE_NAME%"
if exist "build" rmdir /s /q "build"
if exist "build_tmp" rmdir /s /q "build_tmp"
if exist "%EXE_NAME%.spec" del /q "%EXE_NAME%.spec"

echo [6/7] Compilando ejecutable...
call "%VENV_DIR%\Scripts\python.exe" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onedir ^
  --windowed ^
  --log-level=WARN ^
  --name "%EXE_NAME%" ^
  --distpath "." ^
  --workpath "build_tmp" ^
  --specpath "." ^
  --add-data "logo.jpg;." ^
  --add-data "assets;assets" ^
  --add-data "cv_sorter\config.yaml;cv_sorter" ^
  --add-data "cv_sorter\ui\styles.qss;cv_sorter/ui" ^
  --add-data "cv_sorter\ocr_bin\tessdata;ocr_bin\tessdata" ^
  --add-binary "cv_sorter\ocr_bin\*.dll;ocr_bin" ^
  --add-binary "cv_sorter\ocr_bin\*.exe;ocr_bin" ^
  --hidden-import fitz ^
  --hidden-import PySide6.QtCore ^
  --hidden-import PySide6.QtGui ^
  --hidden-import PySide6.QtWidgets ^
  --collect-all PySide6 ^
  --collect-all shiboken6 ^
  --collect-submodules fitz ^
  --collect-binaries fitz ^
  cv_sorter\main.py

if errorlevel 1 (
    echo ERROR: Fallo al compilar con PyInstaller.
    pause
    exit /b 1
)

echo [7/7] Limpieza final...
if exist "build" rmdir /s /q "build"
if exist "build_tmp" rmdir /s /q "build_tmp"
if exist "%EXE_NAME%.spec" del /q "%EXE_NAME%.spec"

echo.
echo =====================================
echo EXE CREADO CORRECTAMENTE
echo =====================================
echo Carpeta generada: %EXE_NAME%
echo Ejecutable: %EXE_NAME%\%EXE_NAME%.exe
echo.
pause
exit /b 0