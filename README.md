# Solucionador

Resuelve automaticamente fotos de ejercicios de la universidad con Claude Code:

- **Fisica**: formulas y proceso en el chat (notacion Sears-Zemansky).
- **Programacion**: solucion en C guardada en `codigo_salida/` y enviada por WhatsApp.

## Archivos

- `buscar_nuevas.ps1`: lista las fotos nuevas si el solucionador esta encendido.
- `horario.txt`: intervalos (`dia HH:MM-HH:MM`) en los que se enciende siempre.
- `activar_desactivar.bat`: pide en la consola `ON` u `OFF` y lo guarda en `estado.txt`.
- `enviar_whatsapp.py`: envia los `.c` de `codigo_salida/` por WhatsApp Web (Selenium + Brave).

## Encendido

Esta encendido si `estado.txt` dice `ON`, o si la hora actual esta dentro de `horario.txt`.

## Uso

1. En Claude Code, crear una tarea programada cada minuto que ejecute `buscar_nuevas.ps1` y resuelva cada foto.
2. Ejecutar `python enviar_whatsapp.py` para el envio por WhatsApp.
3. Encender o apagar con `activar_desactivar.bat`.
