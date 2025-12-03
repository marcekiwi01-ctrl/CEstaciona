import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json
import threading
import time
import requests
from datetime import datetime, timedelta

class CEstacionaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CEstaciona - Sistema de Parqueo Inteligente")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1a1a2e")
        
        # IP del Raspberry Pi Pico W
        self.pico_ip = "172.20.10.9"
        self.pico_port = 8080
        
        # Datos del sistema
        self.vehiculos = []  # Lista de vehículos: {id, entrada, salida, costo}
        self.tipo_cambio = 530.0
        self.espacios_totales = 3
        self.espacios_disponibles = 3
        self.aguja_abierta = False
        
        # Colores
        self.COLOR_BG = "#1a1a2e"
        self.COLOR_PANEL = "#16213e"
        self.COLOR_ACENTO = "#0f3460"
        self.COLOR_EXITO = "#06d6a0"
        self.COLOR_ERROR = "#ef476f"
        self.COLOR_TEXTO = "#ffffff"
        self.COLOR_DISPONIBLE = "#06d6a0"
        self.COLOR_OCUPADO = "#ef476f"
        
        self.crear_interfaz()
        self.obtener_tipo_cambio()
        self.actualizar_estado()
        
    def crear_interfaz(self):
        """Crea la interfaz gráfica completa"""
        # Header
        header = tk.Frame(self.root, bg=self.COLOR_ACENTO, height=80)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🅿️ CEstaciona",
            font=("Helvetica", 32, "bold"),
            bg=self.COLOR_ACENTO,
            fg=self.COLOR_TEXTO
        ).pack(side="left", padx=30, pady=20)
        
        tk.Label(
            header,
            text="Sistema de Parqueo Inteligente",
            font=("Helvetica", 14),
            bg=self.COLOR_ACENTO,
            fg="#95a5a6"
        ).pack(side="left", padx=10)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Panel izquierdo - Estado del parqueo
        self.crear_panel_estado(main_frame)
        
        # Panel central - Control y monitoreo
        self.crear_panel_control(main_frame)
        
        # Panel derecho - Estadísticas
        self.crear_panel_estadisticas(main_frame)
        
        # Footer
        self.crear_footer()
        
    def crear_panel_estado(self, parent):
        """Panel de estado del parqueo en tiempo real"""
        panel = tk.Frame(parent, bg=self.COLOR_PANEL, relief="raised", borderwidth=2)
        panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(
            panel,
            text="📊 Estado del Parqueo",
            font=("Helvetica", 18, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXTO
        ).pack(pady=15)
        
        # Espacios disponibles (grande)
        espacios_frame = tk.Frame(panel, bg=self.COLOR_ACENTO, relief="groove", borderwidth=3)
        espacios_frame.pack(pady=20, padx=20, fill="x")
        
        tk.Label(
            espacios_frame,
            text="Espacios Disponibles",
            font=("Helvetica", 14),
            bg=self.COLOR_ACENTO,
            fg="#95a5a6"
        ).pack(pady=(10, 5))
        
        self.label_espacios = tk.Label(
            espacios_frame,
            text="3",
            font=("Helvetica", 72, "bold"),
            bg=self.COLOR_ACENTO,
            fg=self.COLOR_DISPONIBLE
        )
        self.label_espacios.pack(pady=10)
        
        tk.Label(
            espacios_frame,
            text="de 3 espacios totales",
            font=("Helvetica", 11),
            bg=self.COLOR_ACENTO,
            fg="#95a5a6"
        ).pack(pady=(0, 10))
        
        # Visualización de espacios
        visual_frame = tk.Frame(panel, bg=self.COLOR_PANEL)
        visual_frame.pack(pady=20, padx=20)
        
        tk.Label(
            visual_frame,
            text="🚗 Vista del Parqueo",
            font=("Helvetica", 14, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXTO
        ).pack(pady=(0, 15))
        
        espacios_container = tk.Frame(visual_frame, bg=self.COLOR_PANEL)
        espacios_container.pack()
        
        self.espacios_visual = []
        for i in range(3):
            espacio_frame = tk.Frame(
                espacios_container,
                bg=self.COLOR_DISPONIBLE,
                width=110,
                height=160,
                relief="raised",
                borderwidth=4
            )
            espacio_frame.grid(row=0, column=i, padx=10)
            espacio_frame.pack_propagate(False)
            
            tk.Label(
                espacio_frame,
                text=f"Espacio {i+1}",
                font=("Helvetica", 11, "bold"),
                bg=self.COLOR_DISPONIBLE,
                fg="white"
            ).pack(pady=10)
            
            icono = tk.Label(
                espacio_frame,
                text="✓",
                font=("Helvetica", 48, "bold"),
                bg=self.COLOR_DISPONIBLE,
                fg="white"
            )
            icono.pack(expand=True)
            
            estado_label = tk.Label(
                espacio_frame,
                text="LIBRE",
                font=("Helvetica", 9, "bold"),
                bg=self.COLOR_DISPONIBLE,
                fg="white"
            )
            estado_label.pack(pady=5)
            
            self.espacios_visual.append({
                'frame': espacio_frame,
                'icono': icono,
                'estado': estado_label
            })
        
        # Estado de la aguja
        aguja_frame = tk.Frame(panel, bg=self.COLOR_PANEL)
        aguja_frame.pack(pady=20, padx=20)
        
        tk.Label(
            aguja_frame,
            text="🚧 Estado de la Aguja:",
            font=("Helvetica", 13, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXTO
        ).pack()
        
        self.label_aguja = tk.Label(
            aguja_frame,
            text="CERRADA",
            font=("Helvetica", 16, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_ERROR
        )
        self.label_aguja.pack(pady=5)
        
    def crear_panel_control(self, parent):
        """Panel de control remoto"""
        panel = tk.Frame(parent, bg=self.COLOR_PANEL, relief="raised", borderwidth=2)
        panel.pack(side="left", fill="both", expand=True, padx=10)
        
        tk.Label(
            panel,
            text="🎮 Control Remoto",
            font=("Helvetica", 18, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXTO
        ).pack(pady=15)
        
        # Control de aguja
        control_frame = tk.LabelFrame(
            panel,
            text="Control de Aguja",
            font=("Helvetica", 13, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXTO,
            relief="groove",
            borderwidth=2
        )
        control_frame.pack(pady=10, padx=20, fill="x")
        
        btn_abrir = tk.Button(
            control_frame,
            text="⬆️ ABRIR AGUJA",
            font=("Helvetica", 13, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            cursor="hand2",
            height=2,
            command=lambda: self.controlar_aguja(True)
        )
        btn_abrir.pack(pady=10, padx=20, fill="x")
        
        btn_cerrar = tk.Button(
            control_frame,
            text="⬇️ CERRAR AGUJA",
            font=("Helvetica", 13, "bold"),
            bg="#e67e22",
            fg="white",
            activebackground="#d35400",
            cursor="hand2",
            height=2,
            command=lambda: self.controlar_aguja(False)
        )
        btn_cerrar.pack(pady=10, padx=20, fill="x")
        
        # Control de LEDs
        leds_frame = tk.LabelFrame(
            panel,
            text="Control de Espacios (LEDs)",
            font=("Helvetica", 13, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXTO,
            relief="groove",
            borderwidth=2
        )
        leds_frame.pack(pady=10, padx=20, fill="x")
        
        for i in range(1, 4):
            led_control = tk.Frame(leds_frame, bg=self.COLOR_PANEL)
            led_control.pack(pady=8, padx=15, fill="x")
            
            tk.Label(
                led_control,
                text=f"💡 Espacio {i}:",
                font=("Helvetica", 11, "bold"),
                bg=self.COLOR_PANEL,
                fg=self.COLOR_TEXTO
            ).pack(side="left", padx=5)
            
            btn_on = tk.Button(
                led_control,
                text="Liberar",
                font=("Helvetica", 10, "bold"),
                bg=self.COLOR_EXITO,
                fg="white",
                width=10,
                cursor="hand2",
                command=lambda led=i: self.controlar_led(led, True)
            )
            btn_on.pack(side="left", padx=5)
            
            btn_off = tk.Button(
                led_control,
                text="Ocupar",
                font=("Helvetica", 10, "bold"),
                bg=self.COLOR_ERROR,
                fg="white",
                width=10,
                cursor="hand2",
                command=lambda led=i: self.controlar_led(led, False)
            )
            btn_off.pack(side="left", padx=5)
        
        # Registro manual
        registro_frame = tk.LabelFrame(
            panel,
            text="Registro Manual de Vehículos",
            font=("Helvetica", 13, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXTO,
            relief="groove",
            borderwidth=2
        )
        registro_frame.pack(pady=10, padx=20, fill="x")
        
        btn_entrada = tk.Button(
            registro_frame,
            text="➕ REGISTRAR ENTRADA",
            font=("Helvetica", 12, "bold"),
            bg="#16a085",
            fg="white",
            activebackground="#138d75",
            cursor="hand2",
            height=2,
            command=self.registrar_entrada
        )
        btn_entrada.pack(pady=10, padx=20, fill="x")
        
        btn_salida = tk.Button(
            registro_frame,
            text="➖ REGISTRAR SALIDA",
            font=("Helvetica", 12, "bold"),
            bg="#8e44ad",
            fg="white",
            activebackground="#7d3c98",
            cursor="hand2",
            height=2,
            command=self.registrar_salida
        )
        btn_salida.pack(pady=10, padx=20, fill="x")
        
    def crear_panel_estadisticas(self, parent):
        """Panel de estadísticas"""
        panel = tk.Frame(parent, bg=self.COLOR_PANEL, relief="raised", borderwidth=2)
        panel.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        tk.Label(
            panel,
            text="📈 Estadísticas",
            font=("Helvetica", 18, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXTO
        ).pack(pady=15)
        
        # Estadísticas en tarjetas
        stats_container = tk.Frame(panel, bg=self.COLOR_PANEL)
        stats_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Total de vehículos
        self.crear_stat_card(
            stats_container,
            "🚗 Total de Vehículos",
            "0",
            "total_vehiculos"
        )
        
        # Promedio de estancia
        self.crear_stat_card(
            stats_container,
            "⏱️ Promedio de Estancia",
            "0 min",
            "promedio_estancia"
        )
        
        # Ganancias en colones
        self.crear_stat_card(
            stats_container,
            "💰 Ganancias (Colones)",
            "₡0",
            "ganancias_colones"
        )
        
        # Ganancias en dólares
        self.crear_stat_card(
            stats_container,
            "💵 Ganancias (Dólares)",
            "$0.00",
            "ganancias_dolares"
        )
        
        # Vehículos actualmente en parqueo
        self.crear_stat_card(
            stats_container,
            "🅿️ Vehículos Actuales",
            "0",
            "vehiculos_actuales"
        )
        
        # Botón de actualizar
        tk.Button(
            panel,
            text="🔄 Actualizar Estadísticas",
            font=("Helvetica", 12, "bold"),
            bg="#9b59b6",
            fg="white",
            activebackground="#8e44ad",
            cursor="hand2",
            height=2,
            command=self.calcular_estadisticas
        ).pack(pady=15, padx=20, fill="x")
        
    def crear_stat_card(self, parent, titulo, valor_inicial, nombre):
        """Crea una tarjeta de estadística"""
        card = tk.Frame(parent, bg=self.COLOR_ACENTO, relief="raised", borderwidth=2)
        card.pack(pady=8, fill="x")
        
        tk.Label(
            card,
            text=titulo,
            font=("Helvetica", 11, "bold"),
            bg=self.COLOR_ACENTO,
            fg="#95a5a6"
        ).pack(pady=(10, 5))
        
        label = tk.Label(
            card,
            text=valor_inicial,
            font=("Helvetica", 20, "bold"),
            bg=self.COLOR_ACENTO,
            fg=self.COLOR_TEXTO
        )
        label.pack(pady=(0, 10))
        
        setattr(self, f"label_{nombre}", label)
        
    def crear_footer(self):
        """Footer con información del sistema"""
        footer = tk.Frame(self.root, bg=self.COLOR_ACENTO, height=60)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        self.label_conexion = tk.Label(
            footer,
            text=f"🔗 Conectado a: {self.pico_ip}:{self.pico_port}",
            font=("Helvetica", 11),
            bg=self.COLOR_ACENTO,
            fg=self.COLOR_EXITO
        )
        self.label_conexion.pack(side="left", padx=20, pady=15)
        
        self.label_tipo_cambio = tk.Label(
            footer,
            text=f"💱 Tipo de cambio: ₡{self.tipo_cambio:.2f}/$1",
            font=("Helvetica", 11),
            bg=self.COLOR_ACENTO,
            fg="#f39c12"
        )
        self.label_tipo_cambio.pack(side="left", padx=20)
        
        self.label_timestamp = tk.Label(
            footer,
            text=f"🕐 Última actualización: {datetime.now().strftime('%H:%M:%S')}",
            font=("Helvetica", 11),
            bg=self.COLOR_ACENTO,
            fg="#95a5a6"
        )
        self.label_timestamp.pack(side="right", padx=20)
        
    def enviar_comando(self, comando):
        """Envía comando al Raspberry Pi Pico"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((self.pico_ip, self.pico_port))
            sock.send(json.dumps(comando).encode())
            respuesta = sock.recv(1024)
            sock.close()
            return respuesta.decode()
        except Exception as e:
            print(f"Error de comunicación: {e}")
            self.label_conexion.config(
                text=f"❌ Error: No se puede conectar a {self.pico_ip}",
                fg=self.COLOR_ERROR
            )
            return None
            
    def controlar_aguja(self, abrir):
        """Controla la aguja"""
        comando = {"accion": "aguja", "estado": abrir}
        if self.enviar_comando(comando):
            self.aguja_abierta = abrir
            messagebox.showinfo(
                "Aguja",
                f"Aguja {'abierta' if abrir else 'cerrada'} correctamente"
            )
            
    def controlar_led(self, led, encender):
        """Controla un LED"""
        comando = {"accion": "led", "espacio": led, "estado": 1 if encender else 0}
        if self.enviar_comando(comando):
            messagebox.showinfo(
                "LED",
                f"Espacio {led} {'liberado' if encender else 'ocupado'}"
            )
            
    def registrar_entrada(self):
        """Registra entrada manual"""
        vehiculo_id = len(self.vehiculos)
        entrada = {
            "id": vehiculo_id,
            "entrada": datetime.now(),
            "salida": None,
            "costo": 0
        }
        self.vehiculos.append(entrada)
        
        comando = {"accion": "registro", "vehiculo": vehiculo_id, "tipo": "entrada"}
        self.enviar_comando(comando)
        
        messagebox.showinfo("Entrada", f"Vehículo #{vehiculo_id} registrado")
        self.calcular_estadisticas()
        
    def registrar_salida(self):
        """Registra salida manual"""
        for vehiculo in reversed(self.vehiculos):
            if vehiculo["salida"] is None:
                vehiculo["salida"] = datetime.now()
                tiempo = (vehiculo["salida"] - vehiculo["entrada"]).total_seconds()
                periodos = int(tiempo / 10)
                vehiculo["costo"] = periodos * 1000
                
                comando = {"accion": "registro", "vehiculo": vehiculo["id"], "tipo": "salida"}
                self.enviar_comando(comando)
                
                messagebox.showinfo(
                    "Salida",
                    f"Vehículo #{vehiculo['id']} salió\nCosto: ₡{vehiculo['costo']:,}"
                )
                self.calcular_estadisticas()
                return
        
        messagebox.showwarning("Salida", "No hay vehículos para procesar")
        
    def obtener_estado(self):
        """Obtiene el estado actual del Pico"""
        comando = {"accion": "estado"}
        respuesta = self.enviar_comando(comando)
        
        if respuesta:
            try:
                return json.loads(respuesta)
            except:
                pass
        return None
        
    def actualizar_visualizacion(self, estado):
        """Actualiza la visualización con el estado recibido"""
        if not estado:
            return
            
        # Actualizar espacios disponibles
        espacios = estado.get('espacios', 3)
        self.espacios_disponibles = espacios
        self.label_espacios.config(text=str(espacios))
        
        if espacios == 0:
            self.label_espacios.config(fg=self.COLOR_ERROR)
        elif espacios <= 1:
            self.label_espacios.config(fg="#f39c12")
        else:
            self.label_espacios.config(fg=self.COLOR_DISPONIBLE)
        
        # Actualizar aguja
        aguja = estado.get('aguja', False)
        self.aguja_abierta = aguja
        self.label_aguja.config(
            text="ABIERTA" if aguja else "CERRADA",
            fg=self.COLOR_EXITO if aguja else self.COLOR_ERROR
        )
        
        # Actualizar visualización de espacios (ahora todos manuales)
        led1 = estado.get('led1', True)
        led2 = estado.get('led2', True)
        led3 = estado.get('led3', True)
        
        # Espacio 1
        self.actualizar_espacio_visual(0, led1)
        
        # Espacio 2
        self.actualizar_espacio_visual(1, led2)
        
        # Espacio 3
        self.actualizar_espacio_visual(2, led3)
        
    def actualizar_espacio_visual(self, indice, libre):
        """Actualiza un espacio visual"""
        espacio = self.espacios_visual[indice]
        
        if libre:
            color = self.COLOR_DISPONIBLE
            icono = "✓"
            texto = "LIBRE"
        else:
            color = self.COLOR_OCUPADO
            icono = "✗"
            texto = "OCUPADO"
        
        espacio['frame'].config(bg=color)
        espacio['icono'].config(bg=color, fg="white", text=icono)
        espacio['estado'].config(bg=color, fg="white", text=texto)
        
    def calcular_estadisticas(self):
        """Calcula y actualiza estadísticas"""
        total = len(self.vehiculos)
        
        # Promedio de estancia
        tiempos = []
        for v in self.vehiculos:
            if v["salida"]:
                tiempo = (v["salida"] - v["entrada"]).total_seconds() / 60
                tiempos.append(tiempo)
        
        promedio = sum(tiempos) / len(tiempos) if tiempos else 0
        
        # Ganancias
        ganancias = sum(v["costo"] for v in self.vehiculos)
        
        # Vehículos actuales
        actuales = sum(1 for v in self.vehiculos if v["salida"] is None)
        
        # Actualizar labels
        self.label_total_vehiculos.config(text=str(total))
        self.label_promedio_estancia.config(text=f"{promedio:.1f} min")
        self.label_ganancias_colones.config(text=f"₡{ganancias:,}")
        self.label_ganancias_dolares.config(text=f"${ganancias/self.tipo_cambio:.2f}")
        self.label_vehiculos_actuales.config(text=str(actuales))
        
    def obtener_tipo_cambio(self):
        """Obtiene tipo de cambio de API"""
        try:
            response = requests.get(
                "https://api.exchangerate-api.com/v4/latest/USD",
                timeout=5
            )
            if response.status_code == 200:
                self.tipo_cambio = 530.0
                self.label_tipo_cambio.config(
                    text=f"💱 Tipo de cambio: ₡{self.tipo_cambio:.2f}/$1"
                )
        except:
            self.tipo_cambio = 530.0
            
    def actualizar_estado(self):
        """Actualiza el estado periódicamente"""
        def tarea():
            estado = self.obtener_estado()
            self.actualizar_visualizacion(estado)
            self.label_timestamp.config(
                text=f"🕐 Última actualización: {datetime.now().strftime('%H:%M:%S')}"
            )
        
        threading.Thread(target=tarea, daemon=True).start()
        self.root.after(2000, self.actualizar_estado)

def main():
    root = tk.Tk()
    app = CEstacionaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()