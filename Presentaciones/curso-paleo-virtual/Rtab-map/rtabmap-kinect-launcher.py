#!/usr/bin/env python3
"""
RTAB-Map Kinect v1 Launcher
Control de motor + lanzador de scanner 3D
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import ctypes.util
import subprocess
import os
import sys
import threading

# ── Carga de libfreenect via ctypes ──────────────────────────────────────────

class FreenectMotor:
    def __init__(self):
        self.ctx = ctypes.c_void_p()
        self.dev = ctypes.c_void_p()
        self.connected = False
        try:
            self.lib = ctypes.CDLL("libfreenect.so.0.5")
            self._setup_prototypes()
            if self.lib.freenect_init(ctypes.byref(self.ctx), None) < 0:
                return
            self.lib.freenect_select_subdevices(self.ctx, 1)  # MOTOR only
            if self.lib.freenect_open_device(self.ctx, ctypes.byref(self.dev), 0) < 0:
                self.lib.freenect_shutdown(self.ctx)
                return
            self.connected = True
        except Exception:
            self.connected = False

    def _setup_prototypes(self):
        self.lib.freenect_init.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
        self.lib.freenect_init.restype = ctypes.c_int
        self.lib.freenect_select_subdevices.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.lib.freenect_open_device.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.c_int]
        self.lib.freenect_open_device.restype = ctypes.c_int
        self.lib.freenect_set_tilt_degs.argtypes = [ctypes.c_void_p, ctypes.c_double]
        self.lib.freenect_set_tilt_degs.restype = ctypes.c_int
        self.lib.freenect_close_device.argtypes = [ctypes.c_void_p]
        self.lib.freenect_shutdown.argtypes = [ctypes.c_void_p]

    def set_tilt(self, angle):
        if not self.connected:
            return False
        angle = max(-30.0, min(30.0, float(angle)))
        self.lib.freenect_set_tilt_degs(self.dev, angle)
        return True

    def close(self):
        if self.connected:
            self.lib.freenect_close_device(self.dev)
            self.lib.freenect_shutdown(self.ctx)
            self.connected = False


# ── UI ───────────────────────────────────────────────────────────────────────

class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RTAB-Map Kinect Scanner")
        self.resizable(False, False)
        self.configure(bg="#2b2b2b")

        self.motor = FreenectMotor()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        PAD = dict(padx=16, pady=8)
        BG = "#2b2b2b"
        FG = "#eeeeee"
        ACCENT = "#4a9eff"

        # Título
        tk.Label(self, text="RTAB-Map  Kinect Scanner",
                 font=("Sans", 14, "bold"), bg=BG, fg=FG).pack(pady=(18, 4))
        tk.Label(self, text="Scanner 3D con Kinect v1",
                 font=("Sans", 9), bg=BG, fg="#888888").pack()

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=16, pady=12)

        # Motor
        motor_frame = tk.LabelFrame(self, text="  Motor  ", bg=BG, fg=FG,
                                    font=("Sans", 10, "bold"),
                                    bd=1, relief="groove")
        motor_frame.pack(fill="x", padx=16, pady=(0, 8))

        if not self.motor.connected:
            tk.Label(motor_frame, text="⚠ Motor no disponible\n(cierra rtabmap si está abierto)",
                     bg=BG, fg="#ffaa44", font=("Sans", 9), justify="center").pack(pady=10)
        else:
            tk.Label(motor_frame, text="Ángulo de inclinación",
                     bg=BG, fg=FG, font=("Sans", 9)).pack(pady=(10, 0))

            self.angle_var = tk.DoubleVar(value=0.0)
            self.angle_label = tk.Label(motor_frame, text="0°",
                                        bg=BG, fg=ACCENT, font=("Sans", 18, "bold"))
            self.angle_label.pack()

            slider = tk.Scale(motor_frame, from_=30, to=-30, resolution=1,
                              orient="vertical", variable=self.angle_var,
                              bg=BG, fg=FG, troughcolor="#444", activebackground=ACCENT,
                              highlightthickness=0, bd=0, length=140, showvalue=False,
                              command=self._on_slider)
            slider.pack(pady=4)

            btn_frame = tk.Frame(motor_frame, bg=BG)
            btn_frame.pack(pady=(0, 10))

            for label, angle in [("▲ Arriba (+30°)", 30), ("Centro (0°)", 0), ("▼ Abajo (-30°)", -30)]:
                tk.Button(btn_frame, text=label, bg="#3c3c3c", fg=FG,
                          activebackground="#555", activeforeground=FG,
                          relief="flat", padx=10, pady=4,
                          command=lambda a=angle: self._set_angle(a)).pack(fill="x", pady=2)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=16, pady=8)

        # Botón principal
        tk.Button(self, text="▶  Iniciar Scanner 3D",
                  font=("Sans", 12, "bold"),
                  bg=ACCENT, fg="white",
                  activebackground="#2a7de0", activeforeground="white",
                  relief="flat", padx=20, pady=12,
                  command=self.launch_rtabmap).pack(padx=16, pady=(0, 16), fill="x")

    def _on_slider(self, val):
        angle = int(float(val))
        self.angle_label.config(text=f"{angle:+d}°")
        self.motor.set_tilt(angle)

    def _set_angle(self, angle):
        self.angle_var.set(angle)
        self.angle_label.config(text=f"{angle:+d}°")
        self.motor.set_tilt(angle)

    def launch_rtabmap(self):
        self.motor.close()
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = "/usr/local/lib:/opt/ros/jazzy/lib/x86_64-linux-gnu:" + env.get("LD_LIBRARY_PATH", "")

        # Parámetros optimizados para Kinect v1
        # Fuente: rtabmap wiki + Parameters.h defaults + foros
        params = [
            # ── Rango de profundidad ────────────────────────────────────────
            # Kinect v1: fiable entre 0.5m y 3.5m. Más allá hay mucho ruido.
            "--Kp/MaxDepth",        "3.5",
            "--Kp/MinDepth",        "0.5",
            "--Vis/MaxDepth",       "3.5",
            "--Vis/MinDepth",       "0.5",

            # ── Detección de características visuales ───────────────────────
            # GFTT/BRIEF (6): más estable que el default ORB para superficies
            # con textura moderada como las del Kinect v1.
            "--Kp/DetectorStrategy","6",    # GFTT/BRIEF
            "--Kp/MaxFeatures",     "1000", # default 500, más = mejor tracking
            "--Kp/GridRows",        "4",    # distribuir features en grid 4x4
            "--Kp/GridCols",        "4",    # evita concentración en zonas ricas
            "--Kp/SubPixIterations","3",    # sub-pixel refinement para precisión

            # ── Odometría F2M ───────────────────────────────────────────────
            # Mapa local más grande = menos deriva acumulada
            "--OdomF2M/MaxSize",           "3000",  # default 2000
            "--OdomF2M/BundleAdjustment",  "1",     # bundle adjustment con g2o

            # ── Frecuencia de captura ───────────────────────────────────────
            # Default 0.1m/0.1rad: salta muchos frames.
            # 0.01 = captura casi cada frame → mapa más denso y preciso.
            "--RGBD/LinearUpdate",  "0.01",
            "--RGBD/AngularUpdate", "0.01",

            # ── Loop closure ────────────────────────────────────────────────
            # Re-extraer features en loop closure mejora la calidad del grafo
            "--RGBD/LoopClosureReextractFeatures", "true",

            # ── Nube de puntos / vóxeles ────────────────────────────────────
            # Voxel 1cm = máximo detalle para objetos pequeños/medianos.
            # Aumentar a 0.02 si el PC va lento.
            "--Grid/CellSize",      "0.01",
            "--Grid/RangeMax",      "3.5",
            "--Grid/RangeMin",      "0.5",
        ]

        subprocess.Popen(["/usr/local/bin/rtabmap", "--freenect"] + params, env=env)
        self.destroy()

    def on_close(self):
        self.motor.close()
        self.destroy()


if __name__ == "__main__":
    app = Launcher()
    app.mainloop()
