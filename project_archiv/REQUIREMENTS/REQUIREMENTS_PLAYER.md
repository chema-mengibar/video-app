---
name: Crear Componente Player
description: Genera el componente VideoPlayer.vue en JS puro sincronizado con VideoService
---

# Requerimientos: VideoPlayer Component

## 1. Estructura y UI (Layout BEM)
- **Contenedor:** `.video-player` con `display: grid` (3 filas: `40px 1fr 50px`) y `height: 100%`.
- **Fila Superior (`__top-row`)**:
    - Debe incluir un `<input type="file" ref="fileInput" hidden accept="video/*" />`.
    - Botón "Cargar Video" que ejecute obligatoriamente `fileInput.value.click()`.
- **Fila Central (`__screen-row`)**: Fondo negro (`#000`) para el área de visualización.
- **Video Element (`__video`)**:
    - Tag `<video>` con clase `.video-player__video`.
    - **PROHIBIDO** usar el atributo `controls` nativo del navegador.
    - Estilo `object-fit: contain` para no deformar el video.
- **Fila Inferior (`__controls-row`)**: Controles personalizados (Botones Play/Pause con texto dinámico y botón Stop).

## 2. Sincronización Servicio-DOM (Lógica Crítica)
- **Referencias:** Uso obligatorio de `ref(null)` para `videoElement` y `fileInput`.
- **Vincular SRC**: El atributo `:src` del video debe reaccionar a `videoService.state.videoPath`.
- **Watch isPlaying**: Escuchar `videoService.state.isPlaying` para ejecutar los métodos `.play()` o `.pause()` del elemento de video (validando que la ref exista).
- **Watch currentTime**: Escuchar cambios en el estado del servicio para actualizar el video solo si la diferencia es significativa (> 0.1s) para evitar bucles.
- **Eventos de Video**:
    - `@loadedmetadata`: Sincronizar la duración real del video con `videoService.state.duration`.
    - `@timeupdate`: Actualizar `videoService.state.currentTime` en el servicio mientras el video se reproduce.

## 3. Lógica de Métodos
- **Carga de Archivo**: Al detectar un `change` en el input, generar `URL.createObjectURL(file)` y enviarlo a `videoService.loadVideo(url)`.
- **Playback**: Los métodos `togglePlay` y `stopVideo` del componente deben invocar exclusivamente los métodos homónimos del `videoService`.

## 4. Estilos Específicos (SCSS)
- **Metodología BEM**: Uso de selectores anidados (`&__`).
- **Selectores**: PROHIBIDO estilizar etiquetas HTML directamente (ej. `video { ... }`). Usar siempre clases.
- **Variables CSS**: Aplicar variables del sistema: `--base-dark-1`, `--base-dark-3`, `--accent-primary` y `--fs-ui-small`.
- **Botones**: Estética de software (bordes rectos, hover sutil, estado `:disabled` con opacidad reducida al 30%).