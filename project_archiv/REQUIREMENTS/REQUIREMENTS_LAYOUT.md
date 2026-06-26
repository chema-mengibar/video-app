# Requerimientos del Layout Base (Inspiración Blender)

## 1. Objetivo
Crear la estructura visual principal con paneles redimensionables y composición mediante slots.

## 2. Estructura Visual y Medidas
La aplicación se divide en las siguientes zonas obligatorias:

1.  **TopBar (Menú):** Altura fija (40px).
2.  **Workspace (Área central):** Contenedor flexible entre TopBar y BottomBar.
    -   **PanelLeft (Assets):** Ancho inicial 250px.
    -   **MainPanel (Editor):** Espacio flexible restante (1fr).
    -   **PanelRight (Properties):** Ancho inicial 300px.
3.  **BottomBar (Timeline):** Altura inicial 200px, mínima 40px.

## 3. Comportamiento de Redimensionado
- Entre cada panel debe existir un componente **ResizeHandler**.
- La lógica de resize debe actualizar variables reactivas (`leftWidth`, `rightWidth`, `bottomHeight`) en el componente padre.

## 4. Arquitectura de Componentes (Slots)
- Todos los paneles deben ser contenedores.
- Estructura interna requerida por panel:
    - `<div class="panel__header">` (Texto con el nombre del panel).
    - `<div class="panel__content">` -> Aquí va un `<slot />` para el contenido dinámico.