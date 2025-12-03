# 🅿️ CEstaciona - Sistema de Parqueo Inteligente

Sistema de parqueo inteligente desarrollado con Raspberry Pi Pico W y Python, que permite controlar y monitorear espacios de estacionamiento de forma inalámbrica.

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Requisitos de Hardware](#requisitos-de-hardware)
- [Requisitos de Software](#requisitos-de-software)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Documentación Técnica](#documentación-técnica)
- [Autores](#autores)
- [Licencia](#licencia)

## 🎯 Descripción

CEstaciona es un prototipo de parqueo inteligente que gestiona automáticamente el ingreso y salida de vehículos, calculando tarifas basadas en el tiempo de estancia. El sistema cuenta con control remoto mediante una interfaz gráfica y monitoreo en tiempo real de los espacios disponibles.

### Proyecto desarrollado para:
- **Curso:** CE-1104 Fundamentos de Sistemas Computacionales
- **Institución:** Tecnológico de Costa Rica
- **Escuela:** Ingeniería en Computadores
- **Semestre:** II-2025

## ✨ Características

### Hardware
- 🚗 **3 espacios de parqueo** con indicadores LED
- 🚧 **Sistema de aguja** controlado por servomotor
- 🔢 **Display de 7 segmentos** para mostrar espacios disponibles y costos
- 💡 **2 fotoceldas (LDR)** para detección automática de vehículos
- 🔘 **2 botones físicos** para entrada y salida
- 📡 **Conexión WiFi** para control remoto

### Software
- 📊 **Monitoreo en tiempo real** de espacios disponibles
- 💰 **Cálculo automático de tarifas** (₡1000 por cada 10 segundos)
- 🎮 **Control remoto** de aguja y LEDs
- 📈 **Estadísticas detalladas** (vehículos totales, promedio de estancia, ganancias)
- 💵 **Conversión automática** de colones a dólares usando API de tipo de cambio
- 🖥️ **Interfaz gráfica moderna** con actualización automática

## 🔧 Requisitos de Hardware

| Cantidad | Componente | Especificación |
|----------|-----------|----------------|
| 1 | Raspberry Pi Pico W | Con WiFi integrado |
| 3 | LED | Cualquier color |
| 2 | Resistencia 220Ω | Para LEDs |
| 2 | Fotocelda (LDR) | Sensor de luz |
| 2 | Resistencia 10kΩ | Para LDR |
| 2 | Push Button | Pulsadores normalmente abiertos |
| 2 | Resistencia 10kΩ | Para botones (opcional con PULL_UP interno) |
| 1 | Display 7 segmentos | Cátodo común |
| 1 | Servomotor | SG90 o similar (0-180°) |
| 1 | Protoboard | Para montaje |
| - | Cables jumper | Macho-macho y macho-hembra |

### Pines Utilizados

```
LEDs:
- LED 1 (Espacio 1): GP20
- LED 2 (Espacio 2): GP19
- LED 3 (Espacio 3): GP21

Fotoceldas:
- LDR 1: GP26 (ADC0)
- LDR 2: GP27 (ADC1)

Botones:
- Botón Salida: GP16
- Botón Entrada: GP17

Servomotor:
- Control PWM: GP2

Display 7 Segmentos:
- Segmento A: GP11
- Segmento B: GP10
- Segmento C: GP5
- Segmento D: GP4
- Segmento E: GP3
- Segmento F: GP12
- Segmento G: GP13
- Punto Decimal: GP6
```

## 💻 Requisitos de Software

### Raspberry Pi Pico W
- MicroPython v1.19 o superior
- Thonny IDE (recomendado)

### PC (Interfaz Gráfica)
- Python 3.8 o superior
- Tkinter (incluido en Python estándar)
- Bibliotecas adicionales (ver `requirements.txt`)

## 📥 Instalación

### 1. Configurar Raspberry Pi Pico W

1. **Instalar MicroPython en el Pico:**
   - Descarga el firmware desde [micropython.org](https://micropython.org/download/rp2-pico-w/)
   - Mantén presionado el botón BOOTSEL y conecta el Pico al USB
   - Copia el archivo `.uf2` al dispositivo que aparece

2. **Cargar el código en Thonny:**
   ```bash
   # Abre Thonny y configura el intérprete:
   # Tools > Options > Interpreter > MicroPython (Raspberry Pi Pico)
   ```

3. **Guardar el código:**
   - Copia el contenido de `main.py` del repositorio
   - En Thonny: File > Save As > Raspberry Pi Pico
   - Guarda como `main.py` (importante)

### 2. Configurar Interfaz Gráfica (PC)

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/marcekiwi01/cestaciona.git
   cd cestaciona
   ```

2. **Crear entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuración

### Configurar WiFi en el Pico

Edita las siguientes líneas en `main.py`:

```python
# Líneas 35-36
SSID = "tu_red_wifi"
PASSWORD = "tu_contraseña"
```

### Configurar IP en la Interfaz

1. Ejecuta el código en el Pico y anota la IP que muestra en la consola:
   ```
   Conectado
   IP: 172.20.10.X
   ```

2. Edita `interfaz.py` línea 11:
   ```python
   self.pico_ip = "172.20.10.X"  # Usa la IP que anotaste
   ```

## 🚀 Uso

### Iniciar el Sistema

1. **Raspberry Pi Pico W:**
   ```bash
   # En Thonny, presiona el botón "Run" (F5)
   # O desconecta y reconecta el Pico (auto-ejecuta main.py)
   ```

2. **Interfaz Gráfica:**
   ```bash
   python interfaz.py
   ```

### Operación Básica

#### Usando Botones Físicos:

**Entrada de Vehículo:**
1. Presiona el botón de ENTRADA (GP17)
2. La aguja se abre automáticamente por 3 segundos
3. Un LED se apaga (espacio ocupado)
4. El display actualiza el contador

**Salida de Vehículo:**
1. Primera presión: Muestra el costo en el display
2. Segunda presión: Abre la aguja y libera el espacio
3. Un LED se enciende (espacio disponible)

#### Usando Interfaz Gráfica:

- **Control de Aguja:** Botones "Abrir/Cerrar Aguja"
- **Control de Espacios:** Botones "Liberar/Ocupar" para cada espacio
- **Registro Manual:** Botones "Registrar Entrada/Salida"
- **Estadísticas:** Se actualizan automáticamente cada 2 segundos

### Cálculo de Tarifas

```
Tarifa: ₡1000 por cada 10 segundos
Ejemplo: 35 segundos = 3 períodos = ₡3000
Display muestra: último dígito (3)
```

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    RASPBERRY PI PICO W                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • Control de LEDs (GP20, GP19, GP21)            │  │
│  │  • Lectura de Fotoceldas (GP26, GP27)            │  │
│  │  • Control de Servomotor (GP2)                   │  │
│  │  • Display 7 Segmentos (GP3-GP6, GP10-GP13)     │  │
│  │  • Lectura de Botones (GP16, GP17)               │  │
│  │  • Servidor Socket WiFi (Puerto 8080)            │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ WiFi
┌─────────────────────────────────────────────────────────┐
│                   INTERFAZ GRÁFICA (PC)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • Monitoreo en Tiempo Real                      │  │
│  │  • Control Remoto                                │  │
│  │  • Estadísticas y Reportes                       │  │
│  │  • Cliente Socket TCP                            │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Flujo de Comunicación

```
PC → Envía comando JSON → Pico
Pico → Ejecuta acción → Responde JSON → PC
```

Ejemplo de comando:
```json
{
  "accion": "led",
  "espacio": 1,
  "estado": 1
}
```

## 📖 Documentación Técnica

### Estructura de Archivos

```
cestaciona/
│
├── main.py                 # Código del Raspberry Pi Pico W
├── interfaz.py            # Interfaz gráfica para PC
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
│
├── docs/
│   ├── esquematicos/     # Diagramas de circuito
│   └── manual_usuario.pdf # Manual de usuario
│
└── ejemplos/
    └── pruebas_componentes.py  # Scripts de prueba
```

### Protocolo de Comunicación

El sistema usa **JSON sobre TCP/IP** para la comunicación:

#### Comandos soportados:

1. **Obtener Estado:**
   ```json
   Envío: {"accion": "estado"}
   Respuesta: {
     "espacios": 3,
     "aguja": false,
     "vehiculos": 0,
     "ldr1": 25000,
     "ldr2": 28000,
     "led1": true,
     "led2": true,
     "led3": true
   }
   ```

2. **Controlar LED:**
   ```json
   Envío: {"accion": "led", "espacio": 1, "estado": 1}
   Respuesta: "OK"
   ```

3. **Controlar Aguja:**
   ```json
   Envío: {"accion": "aguja", "estado": true}
   Respuesta: "OK"
   ```

4. **Registro Manual:**
   ```json
   Envío: {"accion": "registro", "vehiculo": 0, "tipo": "entrada"}
   Respuesta: "OK"
   ```

## 🐛 Solución de Problemas

### El Pico no se conecta a WiFi
- Verifica SSID y contraseña en `main.py`
- Asegúrate de que la red sea 2.4GHz (el Pico W no soporta 5GHz)
- Revisa que el Pico tenga antena WiFi funcional

### La interfaz no conecta con el Pico
- Verifica que ambos estén en la misma red WiFi
- Confirma la IP del Pico en la consola de Thonny
- Desactiva temporalmente el firewall de Windows
- Prueba: `ping 172.20.10.X` desde CMD

### Los LEDs no responden
- Verifica las conexiones físicas
- Revisa que las resistencias sean de 220Ω
- Confirma que los pines en el código coincidan con el hardware

### El servomotor no se mueve
- Verifica alimentación del servo (5V)
- Revisa la conexión del pin de señal (GP2)
- Confirma que el servo funcione con otro código de prueba

### El display no muestra números
- Verifica que sea cátodo común (no ánodo común)
- Revisa todas las conexiones de segmentos
- Confirma que los pines en el código coincidan

## 👥 Autores

- **Jimena Vargas** - Desarrollo de todo el proyecto

**Profesor:** Luis Barboza  
**Curso:** CE-1104 Fundamentos de Sistemas Computacionales  
**Institución:** Tecnológico de Costa Rica

## 📄 Licencia

Este proyecto fue desarrollado con fines educativos para el curso CE-1104.

## 🙏 Agradecimientos

- Tecnológico de Costa Rica - Escuela de Ingeniería en Computadores
- Profesor Luis Barboza por la guía y apoyo
- Comunidad de MicroPython por la documentación

## 📞 Contacto

Para preguntas o sugerencias sobre el proyecto:
- Email: j.vargas.4@estudiantec.cr

---

**Nota:** Este es un proyecto académico desarrollado en el II Semestre 2025 para el Tecnológico de Costa Rica.
