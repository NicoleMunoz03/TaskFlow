# Documento Maestro: Sistema de Diseño para Gestión de Tareas de Alta Gama

## 1. Visión General y Norte Creativo: "El Santuario Productivo"

Este sistema de diseño no es simplemente una herramienta de organización; es un **Santuario Productivo**. En un mundo saturado de notificaciones y ruido visual, nuestra misión es devolver la claridad mental al usuario a través de una interfaz que respira. 

El diseño rompe con la rigidez del software empresarial tradicional mediante el uso de **Minimalismo Atmosférico**. En lugar de rejillas densas y líneas divisorias agresivas, utilizamos la profundidad tonal y la tipografía editorial para guiar el ojo. La experiencia debe sentirse como trabajar sobre un escritorio de roble claro perfectamente despejado bajo una luz natural suave.

**Norte Creativo:** *Intencionalidad sobre Densidad.* Cada elemento en pantalla debe justificar su existencia. Si no ayuda a la concentración, es ruido.

---

## 2. Paleta de Colores y Teoría de Superficies

La paleta se aleja de los grises industriales para abrazar tonos más orgánicos y "aireados".

### Definición de Tonos (Material Design Tokens)
*   **Fondo (Background):** `#f7f9fb` (Un gris azulado extremadamente ligero que reduce la fatiga visual).
*   **Primario (Primary):** `#0053dc` (Un azul vibrante pero autoritario para acciones críticas).
*   **Superficies de Capas:** 
    *   `surface_container_lowest`: `#ffffff` (Blanco puro, reservado exclusivamente para las tarjetas de tareas).
    *   `surface_container_low`: `#f0f4f7` (Para secciones secundarias o carriles del Kanban).
*   **Prioridades (Semántica Suave):**
    *   **Alta:** `error_container` (`#fa746f`) con texto `on_error_container`.
    *   **Media:** `secondary_container` (`#d3e4fe`) con texto `on_secondary_container`.
    *   **Baja:** `tertiary_container` (`#91feef`) con texto `on_tertiary_container`.

### Las Reglas de Oro de la Superficie:
1.  **Regla de "No-Línea":** Queda estrictamente prohibido el uso de bordes sólidos de 1px para separar secciones. La arquitectura se define por el cambio de tono (ej. una tarjeta `surface_container_lowest` sobre un carril `surface_container_low`).
2.  **Jerarquía por Anidación:** Tratamos la UI como capas de papel fino. El fondo es la base; los carriles del Kanban son hendiduras sutiles (`surface_container_low`); las tareas son hojas que flotan encima (`surface_container_lowest`).
3.  **El Toque de Cristal (Glassmorphism):** Para menús contextuales o diálogos flotantes, utilizar el color de superficie con una opacidad del 80% y un `backdrop-blur` de 12px. Esto mantiene la conexión visual con el contexto inferior.

---

## 3. Tipografía: Autoridad Editorial

Utilizamos una escala tipográfica que prioriza la legibilidad y el ritmo. La combinación de **Manrope** (para estructura y títulos) e **Inter** (para datos técnicos) crea un contraste profesional y moderno.

*   **Display & Headlines (Manrope):** Usar pesos semibold (600) para los nombres de los proyectos. El espaciado entre letras (letter-spacing) debe ser ligeramente negativo (-0.02em) para un look premium.
*   **Title SM/MD (Manrope):** Utilizado para los títulos de las tarjetas de tareas. Máxima claridad.
*   **Labels (Inter):** La fuente Inter se reserva para metadatos (fechas, etiquetas de prioridad, contadores). Su diseño optimizado para pantallas pequeñas garantiza que los datos sean legibles incluso a 11px (`label-sm`).

---

## 4. Elevación, Profundidad y Sombras Ambientales

En este sistema de diseño, la profundidad no es un efecto cosmético, es información.

*   **Principio de Capas Tonales:** Antes de aplicar una sombra, intenta diferenciar el elemento cambiando el token de superficie. Una tarjeta blanca sobre un fondo gris claro ya comunica elevación sin necesidad de efectos adicionales.
*   **Sombras Ambientales:** Cuando una tarea es "arrastrada" (drag & drop), aplicamos una sombra extra-difundida:
    *   *Offset:* 0px 8px | *Blur:* 24px | *Color:* `on_surface` al 6% de opacidad.
    *   El color de la sombra debe ser una versión teñida de la superficie, nunca un gris neutro o negro puro, para imitar la dispersión de la luz real.
*   **Bordes Fantasma (Ghost Borders):** Si la accesibilidad requiere un límite (ej. en estados de foco), usar `outline_variant` con una opacidad del 15%. Nunca usar negros puros ni contrastes altos en bordes.

---

## 5. Componentes Clave

### Tarjetas de Tarea (Cards)
*   **Contenedor:** `surface_container_lowest` (#ffffff).
*   **Radio:** `md` (0.75rem) para un equilibrio entre suavidad y estructura.
*   **Interacción:** Al hacer hover, la tarjeta debe elevarse sutilmente mediante un cambio a una sombra de 4% de opacidad, no mediante un borde.
*   **Prohibición:** No usar líneas divisorias internas. Separar el título de la descripción mediante el uso de la escala de espaciado (v-space).

### Botones de Acción Primaria
*   **Estilo:** Fondo `primary` con texto `on_primary`.
*   **Refinamiento:** Aplicar un degradado lineal sutil (10%) desde `primary` hasta `primary_container` para evitar la apariencia de "color plano de plantilla".
*   **Radio:** `full` (píldora) para acciones globales; `md` para acciones contextuales dentro de tarjetas.

### Chips de Prioridad
*   No usar colores saturados. Utilizar las versiones "dim" o "container" de la paleta.
*   El texto debe mantener un contraste de 4.5:1 pero sin ser negro puro; usar los tokens `on_primary_container`, `on_error_container`, etc.

### Campos de Entrada (Inputs)
*   **Fondo:** `surface_container_low`.
*   **Estado Activo:** El borde no debe ser el protagonista; en su lugar, utilizar un resplandor suave del color `primary` al 10% de opacidad alrededor de todo el componente.

---

## 6. Do's and Don'ts (Prácticas Recomendadas)

### ✅ Do's
*   **Abrazar el Espacio en Blanco:** Si sientes que dos elementos están muy cerca, duplica el espacio. El lujo en el diseño digital es el aire.
*   **Asimetría Intencional:** En los dashboards, permite que los encabezados tengan márgenes izquierdos más amplios que el contenido para crear un ritmo editorial.
*   **Micro-interacciones Suaves:** Las transiciones de estado (ej. completar una tarea) deben durar entre 200ms y 300ms con una curva *cubic-bezier(0.4, 0, 0.2, 1)*.

### ❌ Don'ts
*   **No usar divisores:** Nunca uses `<hr>` o bordes de 1px para separar tareas en una lista. Usa 8px o 12px de espacio vertical puro.
*   **No usar sombras pesadas:** Si la sombra es visible a primera vista, es demasiado oscura. Debe sentirse, no verse.
*   **No saturar de iconos:** Usa iconos solo donde la acción no sea clara. Preferimos etiquetas de texto claras en `label-md` para mantener el tono profesional.