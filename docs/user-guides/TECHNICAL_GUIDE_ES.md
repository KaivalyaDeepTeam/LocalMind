# Guía Técnica de LocalMind
## Versión 1.2.0

---

**Transforme Audio en Inteligencia**

Transcripción de grado profesional con análisis de calidad impulsado por IA.
100% sin conexión. Costo cero. Privacidad completa.

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación y Primer Inicio](#instalación-y-primer-inicio)
4. [Sección A: Transcripción (Voz a Texto)](#sección-a-transcripción-voz-a-texto)
5. [Sección B: Análisis de Calidad con LLM](#sección-b-análisis-de-calidad-con-llm)
6. [Opciones de Exportación](#opciones-de-exportación)
7. [Referencia de Configuración](#referencia-de-configuración)
8. [Solución de Problemas](#solución-de-problemas)
9. [Privacidad y Seguridad](#privacidad-y-seguridad)

---

## Introducción

LocalMind es una aplicación de escritorio que realiza dos tareas distintas de IA:

| Tarea | Tecnología | Propósito |
|-------|------------|-----------|
| **Transcripción** | OpenAI Whisper | Convertir voz a texto |
| **Análisis de Calidad** | LLM Local/Nube | Puntuar y analizar conversaciones |

Estos son **sistemas separados** que trabajan juntos pero pueden utilizarse de forma independiente.

---

## Requisitos del Sistema

### Requisitos Mínimos

| Componente | Requisito |
|------------|-----------|
| Sistema Operativo | macOS 12 (Monterey) o posterior |
| RAM | 8 GB |
| Almacenamiento | 10 GB de espacio libre |
| Procesador | Intel o Apple Silicon |

### Requisitos Recomendados

| Componente | Requisito |
|------------|-----------|
| Sistema Operativo | macOS 14 (Sonoma) o posterior |
| RAM | 16 GB o más |
| Almacenamiento | 20 GB de espacio libre |
| Procesador | Chip Apple M1/M2/M3 |

### Descargas en el Primer Inicio

| Tipo de Modelo | Tamaño | Cuándo se Descarga |
|----------------|--------|---------------------|
| Whisper (transcripción) | ~1.5 GB | Primera transcripción |
| LLM Local (análisis) | ~4 GB | Primer análisis de calidad |

**Se requiere internet solo para las descargas iniciales de modelos.**

---

## Instalación y Primer Inicio

### Paso 1: Descargar

Descargue `LocalMind-1.2.0-macOS.dmg` desde:
[github.com/KaivalyaDeepTeam/LocalMind/releases](https://github.com/KaivalyaDeepTeam/LocalMind/releases)

### Paso 2: Instalar

1. Abra el archivo DMG descargado
2. Arrastre LocalMind a su carpeta de Aplicaciones
3. Expulse el DMG

### Paso 3: Primer Inicio

**Importante:** macOS puede bloquear la aplicación porque no proviene de la App Store.

**Para abrir LocalMind:**

1. Haga clic derecho en LocalMind.app
2. Seleccione "Open" del menú
3. Haga clic en "Open" en el diálogo de seguridad

---

# Sección A: Transcripción (Voz a Texto)

Esta sección cubre **la conversión de audio a texto** usando la tecnología Whisper de OpenAI.

---

## ¿Qué es la Transcripción?

La transcripción convierte las palabras habladas en archivos de audio en texto escrito. LocalMind utiliza **OpenAI Whisper**, uno de los sistemas de reconocimiento de voz más precisos disponibles.

### Cómo Funciona

```
Archivo de Audio → Whisper AI → Transcripción Escrita
     (MP3)           (Local)         (Texto)
```

### Características Principales

- **Más de 50 idiomas** soportados
- **Detección automática de idioma**
- **Identificación de hablantes** (diarización)
- **Marcas de tiempo** para cada segmento
- **Funciona completamente sin conexión** después de la descarga del modelo

### Formatos de Audio Soportados

| Formato | Extensión | Descripción |
|---------|-----------|-------------|
| MP3 | .mp3 | Formato más común |
| WAV | .wav | Sin comprimir, alta calidad |
| M4A | .m4a | Formato Apple/iTunes |
| FLAC | .flac | Compresión sin pérdidas |
| OGG | .ogg | Formato de código abierto |
| WebM | .webm | Formato de audio web |

**Tamaño máximo de archivo:** 2 GB por archivo

---

## Modelos Whisper Explicados

| Modelo | Tamaño | Precisión | Velocidad | Ideal Para |
|--------|--------|-----------|-----------|------------|
| **Large V3** | 1.5 GB | 97-99% | Lento | Uso profesional |
| **Medium** | 750 MB | 95-97% | Medio | Uso diario |
| **Small** | 250 MB | 92-95% | Rápido | Transcripciones rápidas |
| **Base** | 150 MB | 88-92% | Muy Rápido | Pruebas |
| **Tiny** | 75 MB | 80-88% | El Más Rápido | Tiempo real |

---

## Soporte de Idiomas de Transcripción

**Europeos:** Inglés, Español, Francés, Alemán, Italiano, Portugués, Neerlandés, Polaco, Ruso, Ucraniano

**Asiáticos:** Chino (Mandarín), Japonés, Coreano, Hindi, Bengalí, Tamil, Telugu, Tailandés, Vietnamita

**Medio Oriente:** Árabe, Hebreo, Turco, Persa, Urdu

**Y muchos más...**

---

# Sección B: Análisis de Calidad con LLM

Esta sección cubre el **análisis de conversaciones impulsado por IA** usando Modelos de Lenguaje Grande.

---

## ¿Qué es el Análisis LLM?

El análisis LLM lee su transcripción y evalúa la calidad de la conversación. Proporciona:

- **Puntuación general** (0-100%)
- **Puntuaciones por parámetro** (criterios personalizables)
- **Fortalezas** identificadas en la conversación
- **Áreas de mejora**
- **Retroalimentación detallada** para cada parámetro

### Diferencia Clave con la Transcripción

| Aspecto | Transcripción | Análisis LLM |
|---------|---------------|--------------|
| **Entrada** | Archivo de audio | Transcripción de texto |
| **Salida** | Texto escrito | Puntuaciones y retroalimentación |
| **Tecnología** | Whisper | LLM (Phi/Qwen/GPT) |
| **Propósito** | Convertir voz | Evaluar calidad |
| **¿Requerido?** | Sí | Opcional |

---

## Opciones de Proveedores LLM

### 1. LLM Local (Recomendado)

**Se ejecuta completamente en su computadora.**

| Ventajas | Desventajas |
|----------|-------------|
| 100% gratuito | Más lento que la nube |
| Privacidad completa | Requiere 8GB+ de RAM |
| No necesita internet | Descarga de modelo grande |

### 2. API de OpenAI

| Ventajas | Desventajas |
|----------|-------------|
| Muy rápido | Cuesta dinero (por uso) |
| Alta calidad | Requiere internet |

### 3. API de Anthropic

| Ventajas | Desventajas |
|----------|-------------|
| Excelente razonamiento | Cuesta dinero (por uso) |
| Ideal para análisis | Requiere internet |

---

## Modelos LLM Locales

| Modelo | Tamaño | Velocidad | Calidad | Ideal Para |
|--------|--------|-----------|---------|------------|
| **Phi-3.5 Mini** | 2.4 GB | Rápido | Buena | Predeterminado |
| **Qwen 2.5 3B** | 2.0 GB | Muy Rápido | Buena | Análisis rápido |
| **Qwen 2.5 7B** | 4.4 GB | Medio | Excelente | Uso profesional |
| **Mistral 7B** | 4.1 GB | Medio | Excelente | Retroalimentación detallada |
| **Gemma 2 2B** | 1.6 GB | El Más Rápido | Moderada | Prioridad de velocidad |

---

## Parámetros de Puntuación de Calidad

### Parámetros Predeterminados

| Parámetro | Peso | Qué Mide |
|-----------|------|----------|
| Greeting & Introduction | 1.0x | Apertura profesional |
| Active Listening | 1.0x | Atención y compromiso |
| Problem Identification | 1.0x | Comprensión del asunto |
| Solution Provided | 1.0x | Resolución útil |
| Product Knowledge | 1.0x | Precisión de la información |
| Communication Clarity | 1.0x | Explicaciones claras |
| Empathy & Rapport | 1.0x | Conexión emocional |
| Call Control | 1.0x | Manejo del flujo |
| Call Closing | 1.0x | Finalización profesional |
| Script Compliance | 1.0x | Seguimiento de directrices |

### Comprensión de los Pesos

| Peso | Significado | Impacto |
|------|-------------|---------|
| 0.1x - 0.5x | Baja prioridad | Impacto menor |
| 1.0x | Estándar | Impacto normal |
| 1.5x - 2.0x | Alta prioridad | Impacto significativo |
| 2.5x - 3.0x | Crítico | Impacto mayor |

---

## Opciones de Exportación

| Formato | Atajo | Ideal Para |
|---------|-------|------------|
| **PDF** | Cmd + Shift + P | Gerencia, clientes |
| **Markdown** | Cmd + Shift + M | Compartir rápido |
| **JSON** | Cmd + Shift + J | Integración de sistemas |
| **Texto** | Cmd + Shift + T | Archivo simple |

---

## Privacidad y Seguridad

### Manejo de Datos

| Modo | Datos de Audio | Transcripción |
|------|----------------|---------------|
| **Local LLM** | Permanece en el dispositivo | Permanece en el dispositivo |
| **OpenAI API** | Permanece en el dispositivo | Enviada a OpenAI |
| **Anthropic API** | Permanece en el dispositivo | Enviada a Anthropic |

**Sus archivos de audio NUNCA se suben a la nube.**

### Qué Recopila LocalMind

**Nada.**

- Sin telemetría
- Sin analíticas
- Sin informes de fallos
- Sin cuenta requerida

---

## Atajos de Teclado

| Acción | Atajo |
|--------|-------|
| Abrir Archivo | Cmd + O |
| Iniciar Procesamiento | Cmd + Return |
| Detener | Escape |
| Exportar PDF | Cmd + Shift + P |
| Exportar Markdown | Cmd + Shift + M |
| Exportar JSON | Cmd + Shift + J |
| Exportar Transcripción | Cmd + Shift + T |
| Parámetros de Puntuación | Cmd + Shift + S |
| Configuración | Cmd + , |
| Salir | Cmd + Q |

---

## Obtener Ayuda

- **Documentación:** [github.com/KaivalyaDeepTeam/LocalMind](https://github.com/KaivalyaDeepTeam/LocalMind)
- **Problemas:** [github.com/KaivalyaDeepTeam/LocalMind/issues](https://github.com/KaivalyaDeepTeam/LocalMind/issues)

---

**Versión:** 1.2.0
**Última Actualización:** Enero 2026
**Licencia:** MIT

© 2026 Equipo LocalMind. Hecho con cuidado para todos los que valoran la privacidad.
