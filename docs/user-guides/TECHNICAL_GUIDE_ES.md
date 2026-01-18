# LocalMind
## Guía Técnica

---

**Transforme Audio en Inteligencia**

Transcripción de calidad profesional con análisis de calidad impulsado por IA.
100% offline. Costo cero. Privacidad completa.

---

## Contenido

- [Inicio Rápido](#inicio-rápido)
- [Su Primera Transcripción](#su-primera-transcripción)
- [Comprender la Puntuación de Calidad](#comprender-la-puntuación-de-calidad)
- [Elegir el Modelo Correcto](#elegir-el-modelo-correcto)
- [Configuración](#configuración)
- [Exportar y Compartir](#exportar-y-compartir)
- [Solución de Problemas](#solución-de-problemas)

---

## Inicio Rápido

### Lo que Necesita

- **macOS** 10.15 o posterior
- **4GB RAM** mínimo (8GB recomendado)
- **Archivo de audio** en formato MP3, WAV, M4A, FLAC, OGG o WEBM

### Primer Lanzamiento

1. Descargue LocalMind
2. Mueva a la carpeta Aplicaciones
3. Haga doble clic para abrir
4. Otorgue permisos si se solicita

Eso es todo. Sin cuenta. Sin suscripción. Sin internet requerido.

---

## Su Primera Transcripción

![Ventana Principal](screenshots/01-main-window-en.png)

### Paso 1: Agregue su Audio

Arrastre y suelte su archivo de audio en la ventana.

**Formatos compatibles:**
MP3 · WAV · M4A · FLAC · OGG · WEBM

**Tamaño del archivo:**
Hasta 2GB por archivo

### Paso 2: Configure el Procesamiento

Elija sus preferencias:

**Modo de Procesamiento:**
- **Offline** - Procesa localmente en su dispositivo
- **Online** - Usa IA en la nube (requiere claves API)

**Idioma:**
Detección automática o seleccione de más de 50 idiomas

**Modelo:**
Large V3 (Mejor Calidad) - Recomendado para el primer uso

**Preprocesamiento de Audio:**
Habilite la reducción de ruido para resultados más claros

### Paso 3: Procesar

Haga clic en **Procesar** y observe el pipeline:

1. **Transcripción** - Convirtiendo voz a texto
2. **Fusionar Canales** - Combinando flujos de audio
3. **Auditoría de Calidad** - Análisis impulsado por IA
4. **Generar Informe** - Creando salida completa

**Tiempo de procesamiento:**
Audio de 10 minutos ≈ 5-7 minutos en laptop promedio

---

## Comprender la Puntuación de Calidad

LocalMind no solo transcribe—evalúa sus conversaciones usando razonamiento avanzado de IA.

### Parámetros Predeterminados

**Cumplimiento** (peso 1.0x)
- Saludo e Introducción
- Escucha Activa
- Identificación del Problema
- Solución Proporcionada
- Conocimiento del Producto
- Claridad de Comunicación
- Empatía y Rapport
- Control de Llamada
- Cierre de Llamada
- Cumplimiento del Guión

### Personalizar Puntuaciones

Ajuste los pesos de los parámetros de 0.1x a 3.0x:

- **Mayor peso** = Más importante para la puntuación general
- **Menor peso** = Menor impacto en la calificación final

**Ejemplo:** Para llamadas de ventas, aumente "Conocimiento del Producto" a 2.5x

### Cómo Funciona la Puntuación

LocalMind usa **razonamiento de Cadena de Pensamiento (CoT)**:

1. Analiza el contexto completo de la transcripción
2. Identifica momentos y patrones clave
3. Evalúa contra cada parámetro
4. Proporciona explicaciones detalladas
5. Calcula puntuación final ponderada

**Resultado:** Comprenda no solo *qué* se dijo, sino *qué tan bien* se comunicó.

---

## Elegir el Modelo Correcto

### Modelos de Transcripción

#### Qwen 2.5 (7B) - Mejor para auditoría (Recomendado)

- **Tamaño:** 4GB
- **Velocidad:** Rápida
- **Calidad:** Excelente salida JSON
- **Mejor para:** Análisis de calidad, uso profesional

#### Qwen 2.7B (6.4GB) - Audio de alta calidad

- **Tamaño:** 6.4GB
- **Velocidad:** Moderada
- **Calidad:** Muy precisa para audio claro
- **Mejor para:** Transcripción estructurada

#### Mixtral 7b-v3 (4.6GB) - Excelente salida

- **Tamaño:** 4.6GB
- **Velocidad:** Equilibrada
- **Calidad:** Gran capacidad de razonamiento
- **Mejor para:** Buen rendimiento general

#### Qwen 2.5 (3.2GB) - Buen equilibrio

- **Tamaño:** 3.2GB
- **Velocidad:** Más rápida
- **Calidad:** Buena para la mayoría de casos
- **Mejor para:** Archivos más pequeños, procesamiento rápido

#### Gemma 2 (2.6GB) - Muy rápida

- **Tamaño:** 2.6GB
- **Velocidad:** Muy rápida
- **Calidad:** Buena para audio simple
- **Mejor para:** Necesidades de entrega rápida

### Modelos Whisper

**Large V3** - Precisión máxima (97-99%)
**Medium** - Rendimiento equilibrado (95-97%)
**Base** - Prioridad de velocidad (90-92%)

---

## Configuración

Acceda a la configuración a través del menú **Configuración** o `⌘,` (Command-Coma)

### Proveedor LLM

Elija su proveedor de IA:

**LLM Local (Gratis, Offline)**
- No requiere internet
- Privacidad completa
- Sin costos de API
- Recomendado para la mayoría de usuarios

**OpenAI API**
- Requiere clave API
- Pago por uso
- Procesamiento en la nube

**Anthropic API**
- Requiere clave API
- Razonamiento avanzado
- Procesamiento en la nube

### Configuración de Transcripción

**Modelo:** Large V3 (Mejor Calidad)

**Idioma:** Detección automática
Identifica automáticamente el idioma hablado

**Aceleración GPU:**
Habilite para procesamiento 3-5x más rápido (si está disponible)

**Configuración Avanzada:**

- **Longitud de Fragmento:** 30 segundos (predeterminado)
- **Tamaño de Lote:** 16 (ajuste según RAM)

### Configuración de Salida

**Directorio de Salida:**
Elija dónde guardar los resultados

**Autoexportar después del procesamiento:**
- ✓ Autoexportar JSON
- ✓ Autoexportar PDF

**Configuración de Informe PDF:**
- ✓ Incluir transcripción completa
- ✓ Incluir desglose de puntuación

### Apariencia

**Idioma de IU:**
English · Español · 日本語 · العربية · हिन्दी · Русский · Français · 中文

**Tema:**
Oscuro · Claro · Sistema

**Accesibilidad:**
- Modo amigable para daltónicos
  Usa colores azul/morado/naranja para medidores de puntuación

---

## Exportar y Compartir

### Formatos Disponibles

**JSON**
Datos legibles por máquina con transcripción completa y puntuaciones

**PDF**
Informe profesional con formato y visualizaciones

**TXT**
Solo transcripción en texto plano

### Exportación

1. Complete el procesamiento
2. Haga clic en el botón **Exportar**
3. Elija formato(s)
4. Seleccione destino
5. Haga clic en **Guardar**

Los archivos se nombran automáticamente:
`nombre_transcripción_2026-01-18.pdf`

---

## Soporte Multilingüe

LocalMind habla su idioma.

### Idiomas de IU Compatibles

- 🇬🇧 **English** (Inglés)
- 🇪🇸 **Español**
- 🇯🇵 **日本語** (Japonés)
- 🇦🇪 **العربية** (Árabe) - con diseño RTL
- 🇮🇳 **हिन्दी** (Hindi)
- 🇷🇺 **Русский** (Ruso)
- 🇫🇷 **Français** (Francés)
- 🇨🇳 **中文** (Chino Simplificado)

### Cambiar Idioma

**Configuración → Apariencia → Idioma de IU**

Los cambios se aplican inmediatamente. No se requiere reinicio.

### Idiomas de Transcripción

LocalMind transcribe **más de 50 idiomas** incluyendo:

Inglés · Español · Francés · Alemán · Italiano · Portugués · Holandés · Ruso · Árabe · Hindi · Japonés · Coreano · Chino · y muchos más

---

## Solución de Problemas

### El Procesamiento Tarda Demasiado

**Pruebe esto:**
- Use modelo Whisper más pequeño (Medium en lugar de Large)
- Habilite la aceleración GPU en Configuración
- Cierre otras aplicaciones para liberar RAM
- Procese segmentos de audio más cortos

### Puntuaciones de Calidad Bajas

**Recuerde:**
- La puntuación de calidad requiere que LLM esté descargado
- La primera ejecución descarga modelos (puede tomar tiempo)
- Asegúrese de que "Habilitar Puntuación de Calidad" esté marcado
- Verifique que la calidad del audio sea buena

### El Audio No Se Carga

**Verifique:**
- El formato del archivo es compatible (MP3, WAV, M4A, FLAC, OGG, WEBM)
- El tamaño del archivo es menor de 2GB
- El archivo no está corrupto
- Tiene permisos de lectura para el archivo

### La Aplicación No Se Abre

**Seguridad de macOS:**
1. Haga clic derecho en LocalMind
2. Seleccione "Abrir"
3. Haga clic en "Abrir" en el diálogo de seguridad
4. Otorgue permisos si se solicita

### Los Modelos No Se Descargan

**Verifique:**
- Tiene conexión a internet (para la primera descarga)
- Suficiente espacio en disco (los modelos son de 2-7GB cada uno)
- El firewall permite conexiones a HuggingFace
- Ninguna VPN bloquea las descargas

---

## Privacidad y Seguridad

### Qué Recopila LocalMind

**Nada.**

- Sin telemetría
- Sin analíticas
- Sin informes de fallos
- Sin estadísticas de uso

Su audio nunca deja su dispositivo en modo offline.

### Almacenamiento de Datos

Todos los datos se almacenan localmente:
- **Transcripciones:** Su directorio de salida elegido
- **Modelos:** `~/.cache/localmind/`
- **Configuración:** `~/Library/Application Support/localmind/`

### Código Abierto

LocalMind es de código abierto (Licencia MIT).

Audite el código usted mismo: [github.com/prepladder/localmind](https://github.com/prepladder/localmind)

---

## Consejos Avanzados

### Optimizar la Velocidad de Procesamiento

1. **Use aceleración GPU** si tiene una Mac con chip de serie M
2. **Elija el tamaño de modelo apropiado** - Medium es suficiente para la mayoría de necesidades
3. **Aumente el tamaño del lote** en configuración avanzada (si tiene 16GB+ RAM)
4. **Procese durante horas de baja actividad** para operación en segundo plano

### Mejorar la Precisión de Transcripción

1. **Use audio de la más alta calidad** posible
2. **Habilite el preprocesamiento de audio** para grabaciones con ruido
3. **Seleccione el idioma correcto** en lugar de detección automática
4. **Use el modelo Large V3** para transcripciones críticas

### Procesamiento por Lotes

Procese múltiples archivos eficientemente:

1. Procese el primer archivo con la configuración deseada
2. La configuración se recuerda para el siguiente archivo
3. Habilite la autoexportación para ahorrar tiempo
4. Use el mismo directorio de salida para resultados organizados

### Perfiles de Puntuación Personalizados

Cree perfiles para diferentes casos de uso:

**Llamadas de Ventas:**
- Conocimiento del Producto: 2.5x
- Claridad de Comunicación: 2.0x
- Cierre de Llamada: 2.0x

**Llamadas de Soporte:**
- Empatía y Rapport: 2.5x
- Identificación del Problema: 2.0x
- Solución Proporcionada: 2.5x

**Auditorías de Cumplimiento:**
- Cumplimiento del Guión: 3.0x
- Saludo e Introducción: 2.0x
- Cierre de Llamada: 2.0x

---

## Requisitos del Sistema

### Mínimo

- macOS 10.15 Catalina o posterior
- 4GB RAM
- 10GB espacio libre en disco
- Procesador Intel o Apple Silicon

### Recomendado

- macOS 12 Monterey o posterior
- 8GB RAM o más
- 20GB espacio libre en disco
- Chip de serie M de Apple (para aceleración GPU)

---

## Obtener Ayuda

### Documentación

Documentación completa: [docs.localmind.ai](https://docs.localmind.ai)

### Comunidad

- GitHub Issues: [github.com/prepladder/localmind/issues](https://github.com/prepladder/localmind/issues)
- Discusiones: [github.com/prepladder/localmind/discussions](https://github.com/prepladder/localmind/discussions)

### Contacto

- Email: support@localmind.ai
- Sitio web: [localmind.ai](https://localmind.ai)

---

## Acerca de LocalMind

LocalMind fue construido para dar a todos acceso a transcripción y análisis de calidad de nivel profesional sin sacrificar privacidad ni pagar suscripciones mensuales.

**Nuestra Promesa:**

- ✓ Siempre gratis
- ✓ Siempre con capacidad offline
- ✓ Siempre de código abierto
- ✓ Siempre enfocado en privacidad

**Versión:** 1.0.0
**Última Actualización:** Enero 2026

---

**Hecho con cuidado para investigadores, podcasters, periodistas, centros de llamadas, profesionales legales y cualquiera que valore su privacidad.**

---

© 2026 LocalMind. Liberado bajo Licencia MIT.
