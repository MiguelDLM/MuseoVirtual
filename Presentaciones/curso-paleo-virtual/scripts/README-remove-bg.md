# 📸 Guía para Eliminar Fondos Automáticamente (rembg)

Esta herramienta está diseñada para personas que trabajan en digitalización de fósiles y necesitan quitar el fondo de cientos de fotos de forma automática, sin necesidad de saber programar.

---

## 1. Preparación (Solo se hace la primera vez)

Antes de poder usar el script, necesitas tener instalado **Python** en tu computadora.

### 📥 Cómo instalar Python (Windows)
1. Ve a la página oficial: [python.org/downloads](https://www.python.org/downloads/).
2. Haz clic en el botón amarillo **Download Python 3.xx**.
3. **CRÍTICO:** Al abrir el instalador, marca la casilla que dice **"Add Python to PATH"** (esta es la parte más importante).
4. Haz clic en "Install Now".

### 📥 Cómo instalar Python (macOS)
1. Ve a la página oficial [python.org](https://www.python.org/downloads/macos/) e instala la versión más reciente.
2. O abre tu terminal y escribe: `brew install python` (si usas Homebrew).

---

## 2. Configuración de la Herramienta

Una vez que tengas Python, sigue estos pasos para preparar la herramienta:

1. **Descarga los archivos:** Asegúrate de tener en una carpeta los archivos `remove_bg.py` y `requirements.txt`.
2. **Abre la consola (Terminal):**
   - En Windows: Presiona la tecla `Inicio`, escribe `cmd` y dale a Enter.
   - Navega hasta la carpeta del proyecto usando el comando `cd`. (Ejemplo: `cd Documents\scripts`).
3. **Crea el entorno (Caja de herramientas aislada):**
   Escribe esto y presiona Enter:
   ```bash
   python -m venv venv
   ```
4. **Instala las librerías necesarias:**
   Copia y pega esto:
   ```bash
   # En Windows:
   venv\Scripts\pip install -r requirements.txt

   # En Mac/Linux:
   ./venv/bin/pip install -r requirements.txt
   ```

---

## 3. Cómo Usar el Script (Día a día)

Cuando ya tienes todo instalado, procesar tus fotos es muy sencillo:

1. **Coloca tus fotos:** Pon la carpeta con tus fotografías originales dentro de la misma carpeta donde está el script. (Ejemplo: una carpeta llamada `hueso_molar`).
2. **Abre la consola** en esa carpeta.
3. **Ejecuta el script:**
   
   **Si estás en Windows:**
   ```cmd
   venv\Scripts\python remove_bg.py hueso_molar
   ```

   **Si estás en Linux/Mac:**
   ```bash
   source venv/bin/activate
   python3 remove_bg.py hueso_molar
   ```

### 🌟 ¿Qué pasará al ejecutarlo?
- El script buscará todas las fotos (`.jpg`, `.jpeg`, `.png`).
- Creará automáticamente una carpeta nueva llamada `hueso_molar_nobg`.
- Guardará allí las fotos sin fondo y con transparencia (formato PNG).
- **Si el proceso se corta**, puedes volver a ejecutarlo; el script detectará qué fotos ya están listas y solo procesará las faltantes.

---

## ❓ Preguntas Frecuentes y Errores

### "El comando python no se reconoce"
Significa que no marcaste la casilla **"Add Python to PATH"** durante la instalación. Desinstala Python y vuelve a instalarlo marcando esa opción.

### "Tarda mucho la primera vez"
La primera vez que el script quita un fondo, tiene que descargar el "modelo de inteligencia artificial" (`u2net`) de internet. Esto mide unos 170MB y solo ocurre una vez.

### "¿Funciona con texturas complejas?"
Sí, el algoritmo es muy robusto. Sin embargo, intenta que el objeto no sea del mismo color exacto que el fondo para una precisión del 100%.

---
*Manual creado para el curso de Paleontología Virtual - Museo Virtual Nacional.*
