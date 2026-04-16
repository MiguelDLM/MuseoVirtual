import os
import glob
import argparse
from rembg import remove
from PIL import Image

def process_images(input_dir):
    # Validar que el directorio de entrada existe
    if not os.path.exists(input_dir):
        print(f"Error: El directorio '{input_dir}' no existe.")
        return

    # El directorio de salida será el nombre del de entrada más el sufijo "_nobg"
    # Quitamos posibles barras al final para que os.path.basename funcione bien
    input_dir = input_dir.rstrip(os.sep)
    output_dir = f"{input_dir}_nobg"
    
    # Crear el directorio de salida si no existe
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Directorio de salida creado: {output_dir}")
        
    # Buscar todas las imágenes JPG y PNG en el directorio
    image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(input_dir, ext)))
    
    image_files.sort()
    
    if not image_files:
        print(f"No se encontraron imágenes en '{input_dir}'.")
        return
        
    print(f"Se encontraron {len(image_files)} imágenes en '{input_dir}' para procesar.")
    print(f"Los resultados se guardarán en: {output_dir}")
    
    for idx, img_path in enumerate(image_files):
        filename = os.path.basename(img_path)
        name, _ = os.path.splitext(filename)
        
        # El archivo de salida será PNG para conservar la transparencia
        out_path = os.path.join(output_dir, f"{name}_nobg.png")
        
        if os.path.exists(out_path):
            print(f"[{idx+1}/{len(image_files)}] Saltando {filename}, ya fue procesado.")
            continue
            
        print(f"[{idx+1}/{len(image_files)}] Procesando {filename}...")
        try:
            input_image = Image.open(img_path)
            
            # Remover el fondo usando rembg
            output_image = remove(input_image)
            
            # Guardar la imagen procesada
            output_image.save(out_path, format="PNG")
        except Exception as e:
            print(f"Error al procesar {filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remueve el fondo de imágenes en una carpeta usando rembg.")
    parser.add_argument("input_dir", help="Directorio que contiene las imágenes a procesar.")
    
    args = parser.parse_args()
    
    print("Iniciando removedor de fondos...")
    process_images(args.input_dir)
    print("¡Proceso completado!")
