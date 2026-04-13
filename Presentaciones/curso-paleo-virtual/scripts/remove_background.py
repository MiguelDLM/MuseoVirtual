import sys
import os
from rembg import remove
from PIL import Image

def remove_background(image_path):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} does not exist.")
        return
    
    filename, ext = os.path.splitext(image_path)
    output_path = f"{filename}_nobg.png"
    
    try:
        with open(image_path, 'rb') as i:
            input_data = i.read()
            output_data = remove(input_data)
        
        with open(output_path, 'wb') as o:
            o.write(output_data)
        
        print(f"Background removed. Saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error removing background from {image_path}: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python remove_background.py <path_to_image>")
        sys.exit(1)
    
    remove_background(sys.argv[1])
