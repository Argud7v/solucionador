@echo off
rem Pide en la consola el estado del solucionador (ON u OFF)
rem El horario de horario.txt fuerza ON igualmente
set "archivo_estado=%~dp0estado.txt"
set "estado_actual="
set /p estado_actual=<"%archivo_estado%"
echo Estado actual: %estado_actual%
echo.
echo Horario que fuerza ON:
findstr /v /b "#" "%~dp0horario.txt"
echo.
:pedir
set "estado_nuevo="
set /p "estado_nuevo=Escribe ON u OFF (Enter vacio = salir sin cambios): "
if "%estado_nuevo%"=="" goto fin
if /i "%estado_nuevo%"=="ON" (
    >"%archivo_estado%" echo(ON
    echo Solucionador ON
    goto fin
)
if /i "%estado_nuevo%"=="OFF" (
    >"%archivo_estado%" echo(OFF
    echo Solucionador OFF ^(dentro del horario se enciende igual^)
    goto fin
)
echo Valor no valido.
goto pedir
:fin
timeout /t 2 >nul
