# Requerimientos del Theme (Inspiración Blender)

## 1. Objetivo
Crear el conjunto de variables css que definen la paleta de colores de la aplicacion

## 2. Variables
1. Anyade las variables en el cuerpo de :root { } en `./frontend/styles/_theme.scss`
2. Lista de variables
    - --base: grey
    - --base-dark-1, --base-dark-2, --base-dark-3: variaciones a oscuro de --base
    - --base-light-1 , --base-light-2, --base-light-3: variaciones a claro de --base
    - --accent-primary:  un naranja
    - --accent-primary_hover: variacion oscura de --accent-primary
    - --accent-primary_str :  el rgb de --acent-primary
            en texto para aplicar a rgba(--accent-primary), por ejemplo '123,65,23'
    - --text-color: algun tipo de blanco, que tenga buen contraste y legibilidad
    - --text-color-seconary: menos contraste que --text-color
3. a