from playwright.sync_api import sync_playwright
import time

SIMIT_URL = "https://www.fcm.org.co/simit/#/home-public"

def bot_buscar_simit(placa: str, *, headless: bool = False, slow_mo_ms: int = 200):
    """
    1. Verifica y cierra modal por XPath //*[@id="modalInformation"]/div/div
    2. Llena la placa y hace clic en #consultar
    3. Verifica si existe un elemento en la siguiente vista:
       - si existe -> no hace nada
       - si no existe -> guarda False en una variable
    """
    placa = (placa or "").strip().upper()
    if not placa:
        print("❌ Placa vacía.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=slow_mo_ms)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("🌐 Cargando página del SIMIT...")
            page.goto(SIMIT_URL, timeout=45000)
            time.sleep(2)

            # Paso 1: verificar y cerrar modal
            print("🔎 Buscando modal informativo (XPath)...")
            modal_xpath = 'xpath=//*[@id="modalInformation"]/div/div'
            modal = page.locator(modal_xpath)
            if modal.count() > 0 and modal.first.is_visible():
                print("📢 Modal detectado.")
                close_btn = modal.locator(
                    "xpath=.//button[contains(@class,'modal-info-close') or contains(@class,'close')]"
                )
                if close_btn.count() > 0 and close_btn.first.is_visible():
                    print("🖱️ Clic en botón de cierre del modal...")
                    close_btn.first.click()
                    time.sleep(1)
                    print("✅ Modal cerrado.")
                else:
                    print("⚠️ No se encontró botón de cierre visible.")
            else:
                print("✅ No hay modal activo. Continuando...")

            # Paso 2: escribir placa y buscar
            page.wait_for_selector("#txtBusqueda", timeout=20000)
            print(f"⌨️ Ingresando placa: {placa}")
            page.fill("#txtBusqueda", placa)
            print("🔍 Haciendo clic en 'Consultar'...")
            page.click("#consultar")

            # Esperar a que cargue la siguiente vista
            time.sleep(5)

            # Paso 3: verificar si existe un elemento esperado
            # 👉 reemplaza el selector por el que necesites verificar, ej: "div.resultado" o "table"
            elemento_objetivo = page.locator("div#contenedorResultado, div.tabla-resultados, table")
            print("🧭 Verificando si existe el elemento en la siguiente página...")

            variable_estado = None
            if elemento_objetivo.count() > 0 and elemento_objetivo.first.is_visible():
                variable_estado = True
                print("✅ Elemento encontrado. (Se deja vacío por ahora)")
            else:
                print("❌ Elemento no encontrado. Guardando False en variable.")
                variable_estado = False

            print(f"📦 Variable final: {variable_estado}")

        except Exception as e:
            print(f"❌ Error: {type(e).__name__} → {e}")
        finally:
            context.close()
            browser.close()
    return variable_estado

