# Guía de escaneo 3D con Kinect v1 + rtabmap

## Lanzar el scanner
Doble clic en el icono del escritorio **RTAB-Map Kinect Scanner**,
o desde terminal:
```bash
python3 ~/Desktop/rtabmap-kinect-launcher.py
```

---

## Parámetros optimizados (ya aplicados en el launcher)

| Parámetro | Valor | Por qué |
|-----------|-------|---------|
| Kp/MaxDepth | 3.5m | Kinect v1 es ruidoso más allá de 3.5m |
| Kp/MinDepth | 0.5m | Zona ciega del Kinect |
| Kp/MaxFeatures | 1000 | Más features = mejor tracking |
| Kp/DetectorStrategy | 6 (GFTT/BRIEF) | Más estable que ORB para Kinect |
| Kp/GridRows/Cols | 4x4 | Features distribuidas uniformemente |
| OdomF2M/MaxSize | 3000 | Mapa local más grande = menos deriva |
| OdomF2M/BundleAdjustment | 1 (g2o) | Optimización geométrica de poses |
| RGBD/LinearUpdate | 0.01m | Captura casi cada frame |
| RGBD/AngularUpdate | 0.01rad | Idem para rotación |
| Grid/CellSize | 0.01m (1cm) | Máxima resolución |

---

## Técnica de escaneo

### Preparación
- Ilumina bien el objeto (sin luz solar directa que sature el IR)
- El objeto debe tener **textura visible** (evitar superficies blancas lisas)
- Mantén el Kinect entre **0.5m y 2m** del objeto
- Usa el control de motor para ajustar la inclinación antes de empezar

### Durante el escaneo
1. Pulsa **Start** (▶) y espera a ver puntos verdes sobre la imagen (features)
2. Mueve el Kinect **muy lentamente** (~5 cm/segundo)
3. Solapa cada posición con la anterior (mínimo 50% de overlap)
4. Haz círculos completos alrededor del objeto
5. Si aparece pantalla roja (odometría perdida): **para, vuelve a una zona ya escaneada**

### Señales de calidad
- ✅ Barra de odometría en verde = tracking correcto
- ✅ Números altos en "Inliers" (>50 = excelente)
- ⚠️ Barra amarilla = tracking inestable, ve más despacio
- ❌ Pantalla roja = tracking perdido, reposiciona

---

## Exportar el modelo 3D

### Generar la malla (en rtabmap)
1. **Edit → Optimize graph** (o Ctrl+G) — optimiza el mapa completo
2. **File → Export 3D clouds** con estos ajustes:

   **Filtrado de la nube:**
   - Voxel size: `0.005` (5mm, máximo detalle)
   - Noise filter radius: `0.05`, min neighbors: `5`

   **Reconstrucción de superficie:**
   - Método: **Poisson** (mejor para objetos cerrados)
   - Depth: `8` (más detalle, más lento)
   - ó **Greedy Triangulation** si Poisson falla

   **Textura:**
   - Activar "Generate texture" para modelo con color

3. Exporta en **.obj** (con textura) o **.ply** (nube de puntos)

### Post-proceso en MeshLab (recomendado)
```
Filters → Cleaning → Remove Isolated pieces
Filters → Smoothing → Laplacian Smooth (2-3 iteraciones)
Filters → Reconstruction → Screened Poisson (si no lo hiciste en rtabmap)
```

---

## Solución de problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| Tracking perdido constantemente | Superficie sin textura | Poner objetos con textura en la escena |
| Nube muy dispersa/ruidosa | Movimiento demasiado rápido | Ve más despacio, más overlap |
| Malla con agujeros | Zonas no escaneadas | Haz otra pasada enfocando esas zonas |
| `fromImageEmpty=1` en logs | RGB no recibe datos | Reconecta el Kinect |
| Motor no responde en launcher | rtabmap tiene el Kinect ocupado | Cierra rtabmap, ajusta motor, reinicia |
