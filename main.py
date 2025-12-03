import machine
import network
import socket
import time
import json
from machine import Pin, PWM

# Configuración de pines
# LEDs
led1 = Pin(20, Pin.OUT)
led2 = Pin(19, Pin.OUT)
led3 = Pin(21, Pin.OUT)

# Fotoceldas (LDR)
ldr1 = machine.ADC(26)
ldr2 = machine.ADC(27)

# Botones (con PULL_UP porque los botones conectan a GND)
btn_salida = Pin(16, Pin.IN, Pin.PULL_UP)
btn_entrada = Pin(17, Pin.IN, Pin.PULL_UP)

# Servomotor
servo = PWM(Pin(2))
servo.freq(50)

# 7 Segmentos (Cátodo común)
seg_e = Pin(3, Pin.OUT)
seg_d = Pin(4, Pin.OUT)
seg_c = Pin(5, Pin.OUT)
seg_dp = Pin(6, Pin.OUT)
seg_g = Pin(13, Pin.OUT)
seg_f = Pin(12, Pin.OUT)
seg_a = Pin(11, Pin.OUT)
seg_b = Pin(10, Pin.OUT)

# Configuración WiFi
SSID = "ol"
PASSWORD = "661064Ra"

# Variables globales
espacios_disponibles = 3
entrada_timestamp = {}
espacios_ocupados = [False, False, False]  # Estado manual de cada espacio
estado_aguja = False
ultimo_costo = 0
btn_salida_anterior = 0
btn_entrada_anterior = 0
esperando_pago = False
# Control manual de cada LED
led1_manual = True
led2_manual = True  
led3_manual = True

# Mapeo de números para 7 segmentos (Cátodo común: 1=encendido, 0=apagado)
NUMEROS = {
    0: [1,1,1,1,1,1,0],
    1: [0,1,1,0,0,0,0],
    2: [1,1,0,1,1,0,1],
    3: [1,1,1,1,0,0,1],
    4: [0,1,1,0,0,1,1],
    5: [1,0,1,1,0,1,1],
    6: [1,0,1,1,1,1,1],
    7: [1,1,1,0,0,0,0],
    8: [1,1,1,1,1,1,1],
    9: [1,1,1,1,0,1,1]
}

def set_servo_angle(angle):
    """Mueve el servo al ángulo especificado (0-180)"""
    # Cálculo corregido para servos estándar (SG90)
    # 0 grados = 0.5ms (1024), 90 grados = 1.5ms (3072), 180 grados = 2.5ms (5120)
    min_duty = 1640  # ~0.5ms
    max_duty = 8200  # ~2.5ms
    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    servo.duty_u16(duty)

def mostrar_numero(num):
    """Muestra un número en el display de 7 segmentos"""
    if num < 0 or num > 9:
        num = 0
    
    segmentos = [seg_a, seg_b, seg_c, seg_d, seg_e, seg_f, seg_g]
    patron = NUMEROS[num]
    
    for i, seg in enumerate(segmentos):
        seg.value(patron[i])
    
    seg_dp.value(0)

def leer_fotoceldas():
    """Lee el estado de las fotoceldas y actualiza espacios"""
    # Umbral: valores BAJOS = luz (espacio libre), valores ALTOS = oscuro (ocupado)
    umbral = 30000
    
    val1 = ldr1.read_u16()
    val2 = ldr2.read_u16()
    
    # Si el valor es BAJO (más luz), el espacio está LIBRE
    # Retornamos el estado REAL de la fotocelda, no lo modificamos aquí
    espacio1_libre = val1 < umbral
    espacio2_libre = val2 < umbral
    
    print(f"LDR1: {val1}, LDR2: {val2}")
    
    return espacio1_libre, espacio2_libre

def actualizar_leds():
    """Actualiza los LEDs según estado manual"""
    global led1_manual, led2_manual, led3_manual
    
    # Todos los LEDs se controlan manualmente
    led1.value(1 if led1_manual else 0)
    led2.value(1 if led2_manual else 0)
    led3.value(1 if led3_manual else 0)

def contar_espacios_disponibles():
    """Cuenta espacios disponibles basado en estados manuales"""
    global led1_manual, led2_manual, led3_manual
    
    total = (1 if led1_manual else 0) + (1 if led2_manual else 0) + (1 if led3_manual else 0)
    print(f"Espacios: LED1={led1_manual}, LED2={led2_manual}, LED3={led3_manual}, Total={total}")
    return total

def abrir_aguja():
    """Abre la aguja del parqueo"""
    global estado_aguja
    set_servo_angle(90)
    estado_aguja = True

def cerrar_aguja():
    """Cierra la aguja del parqueo"""
    global estado_aguja
    set_servo_angle(0)
    estado_aguja = False

def conectar_wifi():
    """Conecta a la red WiFi"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Esperando conexión...')
        time.sleep(1)
    
    if wlan.status() != 3:
        raise RuntimeError('Fallo en conexión WiFi')
    else:
        print('Conectado')
        status = wlan.ifconfig()
        print('IP:', status[0])
    
    return wlan

def procesar_entrada():
    """Procesa el ingreso de un vehículo"""
    global espacios_disponibles, entrada_timestamp, led1_manual, led2_manual, led3_manual
    
    espacios = contar_espacios_disponibles()
    print(f"Procesando entrada - Espacios disponibles: {espacios}")
    
    if espacios > 0:
        print("Abriendo aguja...")
        abrir_aguja()
        time.sleep(3)
        print("Cerrando aguja...")
        cerrar_aguja()
        
        timestamp = time.time()
        vehiculo_id = len(entrada_timestamp)
        entrada_timestamp[vehiculo_id] = timestamp
        print(f"Vehículo {vehiculo_id} registrado")
        
        # Ocupar un espacio: prioridad LED3 -> LED2 -> LED1
        if led3_manual:
            led3_manual = False
            print("Espacio 3 (LED3) ocupado")
        elif led2_manual:
            led2_manual = False
            print("Espacio 2 (LED2) ocupado")
        elif led1_manual:
            led1_manual = False
            print("Espacio 1 (LED1) ocupado")
        
        time.sleep(0.5)
    else:
        print("¡No hay espacios disponibles!")

def calcular_costo(tiempo_entrada):
    """Calcula el costo del parqueo (1000 colones por 10 segundos)"""
    tiempo_actual = time.time()
    tiempo_estancia = tiempo_actual - tiempo_entrada
    
    periodos = int(tiempo_estancia / 10)
    costo = periodos * 1000
    
    digito = (costo // 1000) % 10
    
    return digito

def procesar_salida():
    """Procesa la salida de un vehículo"""
    global esperando_pago, ultimo_costo, entrada_timestamp, led1_manual, led2_manual, led3_manual
    
    if not esperando_pago:
        if len(entrada_timestamp) > 0:
            vehiculo_id = list(entrada_timestamp.keys())[0]
            tiempo_entrada = entrada_timestamp[vehiculo_id]
            
            costo = calcular_costo(tiempo_entrada)
            ultimo_costo = costo
            mostrar_numero(costo)
            esperando_pago = True
            print(f"Mostrando costo: {costo} (presiona de nuevo para salir)")
        else:
            print("No hay vehículos para procesar salida")
    else:
        print("Procesando salida...")
        abrir_aguja()
        time.sleep(3)
        cerrar_aguja()
        
        if len(entrada_timestamp) > 0:
            vehiculo_id = list(entrada_timestamp.keys())[0]
            del entrada_timestamp[vehiculo_id]
            print(f"Vehículo {vehiculo_id} salió del parqueo")
            
            # Liberar un espacio: prioridad LED1 -> LED2 -> LED3
            if not led1_manual:
                led1_manual = True
                print("Espacio 1 (LED1) liberado")
            elif not led2_manual:
                led2_manual = True
                print("Espacio 2 (LED2) liberado")
            elif not led3_manual:
                led3_manual = True
                print("Espacio 3 (LED3) liberado")
        
        esperando_pago = False
        time.sleep(0.5)

def manejar_comandos(conn):
    """Maneja comandos recibidos desde la aplicación remota"""
    global espacios_disponibles, led1_manual, led2_manual, led3_manual
    
    try:
        data = conn.recv(1024)
        if data:
            comando = json.loads(data.decode())
            
            if comando['accion'] == 'estado':
                espacios = contar_espacios_disponibles()
                estado = {
                    'espacios': espacios,
                    'aguja': estado_aguja,
                    'vehiculos': len(entrada_timestamp),
                    'ldr1': ldr1.read_u16(),
                    'ldr2': ldr2.read_u16(),
                    'led1': led1_manual,
                    'led2': led2_manual,
                    'led3': led3_manual
                }
                conn.send(json.dumps(estado).encode())
            
            elif comando['accion'] == 'led':
                espacio = comando['espacio']
                estado = comando['estado']
                if espacio == 1:
                    led1_manual = bool(estado)
                    led1.value(estado)
                elif espacio == 2:
                    led2_manual = bool(estado)
                    led2.value(estado)
                elif espacio == 3:
                    led3_manual = bool(estado)
                    led3.value(estado)
                conn.send(b'OK')
            
            elif comando['accion'] == 'aguja':
                if comando['estado']:
                    abrir_aguja()
                else:
                    cerrar_aguja()
                conn.send(b'OK')
            
            elif comando['accion'] == 'registro':
                vehiculo_id = comando['vehiculo']
                if comando['tipo'] == 'entrada':
                    entrada_timestamp[vehiculo_id] = time.time()
                elif comando['tipo'] == 'salida' and vehiculo_id in entrada_timestamp:
                    del entrada_timestamp[vehiculo_id]
                conn.send(b'OK')
    
    except Exception as e:
        print(f"Error: {e}")

def servidor():
    """Inicia el servidor socket"""
    addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    s.setblocking(False)
    
    print('Servidor escuchando en puerto 8080')
    
    return s

def test_componentes():
    """Prueba todos los componentes al inicio"""
    print("\n=== PRUEBA DE COMPONENTES ===")
    
    # Probar 7 segmentos (mostrar 0-9)
    print("Probando 7 segmentos...")
    for i in range(10):
        mostrar_numero(i)
        print(f"  Mostrando: {i}")
        time.sleep(0.3)
    
    # Probar servo
    print("Probando servomotor...")
    print("  Posición 0 grados")
    set_servo_angle(0)
    time.sleep(1)
    print("  Posición 90 grados")
    set_servo_angle(90)
    time.sleep(1)
    print("  Posición 0 grados")
    set_servo_angle(0)
    time.sleep(1)
    
    # Probar LEDs
    print("Probando LEDs...")
    print("  Encendiendo todos...")
    led1.value(1)
    led2.value(1)
    led3.value(1)
    time.sleep(1)
    print("  Apagando todos...")
    led1.value(0)
    led2.value(0)
    led3.value(0)
    time.sleep(0.5)
    
    print("=== PRUEBA COMPLETA ===\n")

def main():
    """Función principal"""
    global btn_salida_anterior, btn_entrada_anterior
    
    # Probar componentes al inicio
    test_componentes()
    
    # Inicializar
    cerrar_aguja()
    time.sleep(0.5)
    
    # Inicializar todos los LEDs encendidos (3 espacios disponibles)
    led1.value(1)
    led2.value(1)
    led3.value(1)
    led1_manual = True
    led2_manual = True
    led3_manual = True
    
    # Mostrar 3 espacios disponibles
    mostrar_numero(3)
    
    # Conectar WiFi
    print("Conectando a WiFi...")
    wlan = conectar_wifi()
    s = servidor()
    
    print("Sistema iniciado - Presiona los botones para probar")
    
    # Inicializar estado de botones
    btn_entrada_anterior = btn_entrada.value()
    btn_salida_anterior = btn_salida.value()
    
    while True:
        # Leer botones con debounce (invertido porque usamos PULL_UP)
        btn_entrada_actual = btn_entrada.value()
        btn_salida_actual = btn_salida.value()
        
        # Botón presionado = 0 (porque está conectado a GND con PULL_UP)
        if not btn_entrada_actual and btn_entrada_anterior:
            print("¡Botón ENTRADA presionado!")
            procesar_entrada()
        
        if not btn_salida_actual and btn_salida_anterior:
            print("¡Botón SALIDA presionado!")
            procesar_salida()
        
        btn_entrada_anterior = btn_entrada_actual
        btn_salida_anterior = btn_salida_actual
        
        # Actualizar display si no está esperando pago
        if not esperando_pago:
            espacios = contar_espacios_disponibles()
            mostrar_numero(espacios)
        
        # Actualizar LEDs según fotoceldas
        actualizar_leds()
        
        # Manejar conexiones entrantes
        try:
            conn, addr = s.accept()
            print('Conexión desde:', addr)
            conn.setblocking(False)
            manejar_comandos(conn)
            conn.close()
        except OSError:
            pass
        
        time.sleep(0.1)

if __name__ == '__main__':
    main()