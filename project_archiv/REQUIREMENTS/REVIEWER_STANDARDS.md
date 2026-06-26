---
name: Reviewer Técnico de Componentes
description: Checklist de validación post-generación para asegurar calidad y arquitectura
---

# Checklist de Reviewer: Estándares de Calidad

## 1. Limpieza de Estilos (Anti-Bloat)
- **Selectores Huérfanos:** Verificar que no existan clases en el `<style>` que no se estén usando en el `<template>`.
- **Selectores de Etiqueta:** Confirmar que NO se están estilizando etiquetas directamente (ej. `button { ... }`). Todo debe usar clases BEM.
- **Variables CSS:** Validar que los colores y tamaños usen variables (`var(--base-...)`) y no valores hardcodeados (ej. `#000`).

## 2. Programación Defensiva (Anti-Crash)
- **Null Safety:** Verificar el uso de `optional chaining` (`?.`) en todas las llamadas a servicios inyectados y sus estados.
- **DOM Refs:** Comprobar que antes de acceder a una `.value` de una `ref` de elemento (como `videoElement.value`), exista una validación `if (elemento.value)`.
- **Injection Check:** Asegurar que el código maneja el caso de que un servicio no esté disponible en el `inject`.

## 3. Integridad de Reactividad (Vue 3 Setup)
- **Watchers:** Validar que los watchers de objetos reactivos o propiedades de servicios usen una función getter: `watch(() => objeto.prop, ...)`.
- **Ref vs Reactive:** Confirmar que no hay desestructuración de objetos reactivos que rompa la reactividad (usar `computed` o acceder vía `objeto.prop`).

## 4. Consistencia de la Feature
- **Eventos:** Verificar que todos los eventos nativos necesarios (ej. `@loadedmetadata`, `@change`) están implementados y conectados al servicio.
- **Sincronización:** Comprobar que no existen "estados duplicados" (el componente no debe tener su propia variable `isPlaying` si ya existe en el servicio).

## 5. Higiene de Código
- **Comentarios:** Confirmar la ausencia total de comentarios, especialmente en español o explicativos.
- **Tipado:** Asegurar que NO se ha colado ningún rastro de TypeScript (`lang="ts"`, interfaces, tipos).
- **Imports:** Verificar que los imports usan el alias `@/` y que las keys de inyección están correctamente importadas.
- 
## 7. Contrato de Responsabilidad (DOM vs Servicio)
- **Desacoplamiento:** Los métodos del servicio NO deben manipular directamente elementos del DOM (prohibido pasar `videoElement` como argumento a métodos de lógica).
- **Flujo Único:** El servicio actualiza el `state`, y el componente reacciona a ese `state` mediante `watch` para manipular el tag `<video>`.
- **Limpieza de Métodos:** Si el servicio pide un elemento DOM, el componente debe ser el encargado de mantener la referencia, no de enviarla en cada función.