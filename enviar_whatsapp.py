# enviar_whatsapp.py
# Vigila la carpeta codigo_salida y envia cada archivo .c como adjunto
# por WhatsApp Web al chat configurado. Luego lo mueve a "enviados".
#
# Uso:
#   pip install selenium
#   python enviar_whatsapp.py
# La primera vez se abre Chrome: escanea el QR de WhatsApp Web.
# La sesion queda guardada en la carpeta perfil_chrome.

import os
import shutil
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as condicion
from selenium.webdriver.support.ui import WebDriverWait

# ---- Configuracion ----
# Nombre exacto del chat como aparece en WhatsApp (tu propio chat suele
# llamarse "Tu" con tilde o tu nombre; tambien sirve tu numero).
NOMBRE_CHAT = "argus"
SEGUNDOS_ENTRE_REVISIONES = 10
# Poner True para guardar capturas de cada paso en la carpeta diagnostico
DEPURAR = False
RUTA_BRAVE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

carpeta_base = os.path.dirname(os.path.abspath(__file__))
carpeta_salida = os.path.join(carpeta_base, "codigo_salida")
carpeta_enviados = os.path.join(carpeta_salida, "enviados")
carpeta_perfil = os.path.join(carpeta_base, "perfil_chrome")


def buscar_primero(navegador, selectores, espera=20):
    # Prueba varios selectores CSS porque WhatsApp cambia su pagina a menudo
    fin = time.time() + espera
    while time.time() < fin:
        for selector in selectores:
            elementos = navegador.find_elements(By.CSS_SELECTOR, selector)
            if elementos:
                return elementos[0]
        time.sleep(0.5)
    raise RuntimeError("No se encontro ningun elemento: " + str(selectores))


def guardar_diagnostico(navegador, nombre_paso):
    # Captura de pantalla y lista de inputs de archivo para depurar
    if not DEPURAR:
        return
    carpeta_diagnostico = os.path.join(carpeta_base, "diagnostico")
    os.makedirs(carpeta_diagnostico, exist_ok=True)
    navegador.save_screenshot(os.path.join(carpeta_diagnostico, nombre_paso + ".png"))
    inputs = navegador.execute_script(
        "return Array.from(document.querySelectorAll('input[type=file]'))"
        ".map(e => e.outerHTML);")
    with open(os.path.join(carpeta_diagnostico, nombre_paso + ".txt"), "w",
              encoding="utf-8") as archivo:
        archivo.write("\n".join(inputs))


def abrir_chat(navegador):
    caja_busqueda = buscar_primero(navegador, [
        "div[contenteditable='true'][data-tab='3']",
        "#side input[type='text']",
        "#side input",
        "#side div[contenteditable='true']",
    ], espera=120)
    caja_busqueda.click()
    caja_busqueda.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
    caja_busqueda.send_keys(NOMBRE_CHAT)
    time.sleep(2)
    caja_busqueda.send_keys(Keys.ENTER)
    # Confirmar que el chat se abrio (aparece la barra de escribir abajo)
    try:
        buscar_primero(navegador, ["#main footer"], espera=15)
    except RuntimeError:
        raise RuntimeError("No se abrio el chat '" + NOMBRE_CHAT + "'")
    time.sleep(1)


def enviar_archivo(navegador, ruta_archivo):
    try:
        abrir_chat(navegador)
        boton_adjuntar = buscar_primero(navegador, [
            "#main footer [data-icon*='plus']",
            "#main footer [data-icon*='attach']",
            "#main footer button[aria-label*='djunt']",
            "#main footer button[title*='djunt']",
            "#main footer div[aria-label*='djunt']",
            "#main footer button[aria-label*='ttach']",
            "#main footer div[title*='djunt']",
        ])
        boton_adjuntar.click()
        time.sleep(1.5)
        # Evitar que se abra la ventana de archivos de Windows al pulsar
        # "Documento": se anula el click sobre los input de tipo archivo
        navegador.execute_script(
            "if (!window.clickOriginal) {"
            "  window.clickOriginal = HTMLInputElement.prototype.click;"
            "  HTMLInputElement.prototype.click = function () {"
            "    if (this.type === 'file') { document.body.appendChild(this); return; }"
            "    return window.clickOriginal.call(this);"
            "  };"
            "}")
        opcion_documento = navegador.find_element(
            By.XPATH, "//*[normalize-space(text())='Documento' or "
                      "normalize-space(text())='Document']")
        opcion_documento.click()
        time.sleep(1.5)
        guardar_diagnostico(navegador, "1_menu_adjuntar")
        # Solo el input de "Documento" acepta cualquier tipo (accept='*')
        entradas = navegador.find_elements(By.CSS_SELECTOR, "input[type='file']")
        entrada_archivo = None
        for entrada in entradas:
            if entrada.get_attribute("accept") in ("*", None, ""):
                entrada_archivo = entrada
                break
        if entrada_archivo is None:
            raise RuntimeError("No hay input de documento. Inputs: " + str(
                [e.get_attribute("accept") for e in entradas]))
        entrada_archivo.send_keys(ruta_archivo)
        # Esperar a que cargue la vista previa del documento
        time.sleep(4)
        guardar_diagnostico(navegador, "2_vista_previa")
        # En la vista previa, Enter envia el archivo
        ActionChains(navegador).send_keys(Keys.ENTER).perform()
        time.sleep(5)
        guardar_diagnostico(navegador, "3_despues_enviar")
    except Exception:
        # Guardar captura para poder ver que fallo
        navegador.save_screenshot(os.path.join(carpeta_base, "error_whatsapp.png"))
        raise


def main():
    os.makedirs(carpeta_enviados, exist_ok=True)
    opciones = webdriver.ChromeOptions()
    # Usar Brave en lugar de Chrome (Brave esta basado en Chromium)
    opciones.binary_location = RUTA_BRAVE
    opciones.add_argument("--user-data-dir=" + carpeta_perfil)
    navegador = webdriver.Chrome(options=opciones)
    navegador.get("https://web.whatsapp.com")
    print("Esperando a que cargue WhatsApp Web (escanea el QR si aparece)...")
    # La lista de chats (#pane-side) aparece cuando la sesion ya cargo
    WebDriverWait(navegador, 300).until(condicion.presence_of_element_located(
        (By.CSS_SELECTOR, "#pane-side")))
    print("Listo. Vigilando", carpeta_salida)

    while True:
        for nombre in sorted(os.listdir(carpeta_salida)):
            ruta = os.path.join(carpeta_salida, nombre)
            if not (os.path.isfile(ruta) and nombre.lower().endswith(".c")):
                continue
            try:
                enviar_archivo(navegador, ruta)
                shutil.move(ruta, os.path.join(carpeta_enviados, nombre))
                print("Enviado:", nombre)
            except Exception as error:
                print("Error enviando", nombre, "->", error)
        time.sleep(SEGUNDOS_ENTRE_REVISIONES)


if __name__ == "__main__":
    main()
