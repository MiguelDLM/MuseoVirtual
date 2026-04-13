#!/usr/bin/env python3
"""
convert_mesh.py — Conversor de mallas 3D para paleontología
============================================================
Convierte archivos de malla entre STL, OBJ, PLY, VTK y otros formatos.
Usa meshio como motor principal y trimesh como respaldo.

Uso:
    python convert_mesh.py archivo.ply -f obj
    python convert_mesh.py *.stl -f ply
    python convert_mesh.py --list-formats

Ver README.md para instrucciones de instalación y uso completo.
"""

import argparse
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Formatos soportados y sus descripciones
# ---------------------------------------------------------------------------
FORMATS = {
    "stl":  "Stereolithography — universal, ideal para impresión 3D",
    "obj":  "Wavefront OBJ — con textura y materiales (.mtl)",
    "ply":  "Polygon File Format — color por vértice, datos científicos",
    "vtk":  "VTK Legacy — mallas volumétricas y datos FEA/CFD",
    "vtu":  "VTK XML — volumétrico comprimible",
    "off":  "Object File Format — simple, usado en investigación",
    "msh":  "Gmsh — mallas volumétricas para FEA",
    "gltf": "GL Transmission Format — web y visualización",
    "glb":  "GLTF binario — web y visualización",
    "dae":  "COLLADA — intercambio con animación",
    "xdmf": "XDMF — datos científicos HPC con HDF5",
}

SURFACE_LIBS_ORDER = ["trimesh", "meshio"]   # trimesh primero: más robusto con PLY/color


# ---------------------------------------------------------------------------
# Conversión
# ---------------------------------------------------------------------------

def convert(src: Path, target_ext: str) -> tuple[bool, str]:
    """Convierte src al formato target_ext. Devuelve (éxito, mensaje)."""
    dst = src.with_suffix("." + target_ext.lstrip("."))

    if dst == src:
        return False, f"El archivo ya tiene el formato .{target_ext}"

    errors = []

    # Intentar con trimesh primero (mejor soporte de color y PLY)
    try:
        import trimesh
        mesh = trimesh.load(str(src), process=False)
        mesh.export(str(dst))
        return True, f"trimesh  ✓  {src.name}  →  {dst.name}"
    except Exception as e:
        errors.append(f"trimesh: {e}")

    # Intentar con meshio como respaldo
    try:
        import meshio
        mesh = meshio.read(str(src))
        meshio.write(str(dst), mesh)
        return True, f"meshio   ✓  {src.name}  →  {dst.name}"
    except Exception as e:
        errors.append(f"meshio: {e}")

    return False, "Conversión fallida:\n  " + "\n  ".join(errors)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Conversor de mallas 3D (STL, OBJ, PLY, VTK, …)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python convert_mesh.py fosil.ply -f obj
  python convert_mesh.py *.stl -f ply
  python convert_mesh.py scan1.ply scan2.ply -f stl
  python convert_mesh.py --list-formats
        """,
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Archivos de entrada (glob expandido por el shell)",
    )
    parser.add_argument(
        "-f", "--format",
        dest="target",
        help="Formato de salida (stl, obj, ply, vtk, …)",
    )
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="Muestra los formatos soportados y sale",
    )
    return parser.parse_args()


def check_dependencies():
    missing = []
    for lib in ("meshio", "trimesh"):
        try:
            __import__(lib)
        except ImportError:
            missing.append(lib)
    if missing:
        print("Faltan dependencias:", ", ".join(missing))
        print("Instálalas con:  pip install", " ".join(missing))
        sys.exit(1)


def main():
    args = parse_args()

    if args.list_formats:
        print("\nFormatos soportados:\n")
        for ext, desc in FORMATS.items():
            print(f"  {ext:<6}  {desc}")
        print()
        return

    if not args.files:
        print("Error: proporciona al menos un archivo de entrada.")
        print("Usa --help para ver la ayuda.")
        sys.exit(1)

    if not args.target:
        print("Error: indica el formato de salida con -f <formato>")
        print("Formatos disponibles:", ", ".join(FORMATS))
        sys.exit(1)

    target = args.target.lower().lstrip(".")
    if target not in FORMATS:
        print(f"Formato '{target}' no reconocido.")
        print("Formatos disponibles:", ", ".join(FORMATS))
        sys.exit(1)

    check_dependencies()

    ok, failed = 0, 0
    for pattern in args.files:
        paths = list(Path(".").glob(pattern)) if "*" in pattern else [Path(pattern)]
        for path in paths:
            if not path.exists():
                print(f"  ✗  No encontrado: {path}")
                failed += 1
                continue
            success, msg = convert(path, target)
            print((" " if success else "  ✗  ") + msg)
            if success:
                ok += 1
            else:
                failed += 1

    print(f"\nResultado: {ok} convertido(s), {failed} error(es).")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
