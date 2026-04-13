import sys
import os
from PIL import Image

def convert_webp(image_path, output_format="PNG"):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} does not exist.")
        return
    
    filename, ext = os.path.splitext(image_path)
    if ext.lower() != ".webp":
        print(f"Warning: {image_path} is not a .webp file.")
    
    output_ext = ".png" if output_format.upper() == "PNG" else ".jpg"
    output_path = f"{filename}_converted{output_ext}"
    
    try:
        with Image.open(image_path) as img:
            img.convert("RGBA" if output_format.upper() == "PNG" else "RGB").save(output_path, output_format)
        print(f"Converted {image_path} to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error converting {image_path}: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_webp.py <path_to_webp> [PNG|JPEG]")
        sys.exit(1)
    
    fmt = sys.argv[2] if len(sys.argv) > 2 else "PNG"
    convert_webp(sys.argv[1], fmt)
