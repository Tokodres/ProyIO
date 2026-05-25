import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from fractions import Fraction

class GraficaFrame(ctk.CTkFrame):
    def __init__(self, master, resultados, **kwargs):
        super().__init__(master, **kwargs)
        
        # --- Configuración de la figura de Matplotlib ---
        fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')
        
        # Dibujar líneas de restricciones
        for linea in resultados['lineas']:
            if 'vertical' in linea:
                ax.axvline(x=linea['x_const'], color='white', linestyle='--', alpha=0.5)
            else:
                ax.plot(linea['x'], linea['y'], label="Restricción")
        
        # Marcar el punto óptimo
        optimo = resultados['optimo']
        x_opt, y_opt = optimo[0]
        z_opt = optimo[1]
        
        ax.plot(x_opt, y_opt, 'ro', markersize=10, label="Óptimo")
        
        # Estilo de ejes
        ax.tick_params(colors='white')
        ax.set_xlabel("X1", color='white')
        ax.set_ylabel("X2", color='white')
        ax.set_xlim(0, max(x_opt + 5, 10))
        ax.set_ylim(0, max(y_opt + 5, 10))
        ax.grid(color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
        ax.legend(facecolor='#2b2b2b', labelcolor='white')
        
        # --- Convertir resultados a fracciones ---
        x_frac = Fraction(x_opt).limit_denominator(1000)
        y_frac = Fraction(y_opt).limit_denominator(1000)
        z_frac = Fraction(z_opt).limit_denominator(1000)
        
        # --- Panel de Resultados ---
        info_frame = ctk.CTkFrame(self, fg_color="#333333", width=200)
        info_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(info_frame, text="RESULTADOS", font=("Arial", 18, "bold")).pack(pady=20)
        
        ctk.CTkLabel(info_frame, text=f"X1 = {x_frac}", font=("Arial", 16)).pack(pady=10)
        ctk.CTkLabel(info_frame, text=f"X2 = {y_frac}", font=("Arial", 16)).pack(pady=10)
        ctk.CTkLabel(info_frame, text=f"Z = {z_frac}", font=("Arial", 16, "bold"), text_color="#3b8ed0").pack(pady=10)
        
        # --- Frame contenedor para gráfica + toolbar ---
        grafica_frame = ctk.CTkFrame(self, fg_color="transparent")
        grafica_frame.pack(side="left", fill="both", expand=True)
        
        # Crear canvas
        self.canvas = FigureCanvasTkAgg(fig, master=grafica_frame)
        self.canvas.draw()
        
        # --- Barra de herramientas (zoom, pan, home) ---
        toolbar = NavigationToolbar2Tk(self.canvas, grafica_frame, pack_toolbar=False)
        toolbar.update()
        # Empaquetar toolbar arriba
        toolbar.pack(side="top", fill="x")
        
        # Empaquetar canvas debajo de la toolbar
        self.canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True)


class GraficaVentana(ctk.CTkToplevel):
    def __init__(self, master, resultados, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Método Gráfico")
        self.geometry("950x650")
        self.minsize(850, 520)
        self.resizable(True, True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, corner_radius=15)
        container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        grafica_frame = GraficaFrame(container, resultados)
        grafica_frame.grid(row=0, column=0, sticky="nsew")

        ctk.CTkButton(
            container,
            text="Cerrar",
            font=("Arial", 14, "bold"),
            width=130,
            height=36,
            command=self.destroy,
        ).grid(row=1, column=0, pady=(15, 0), sticky="e")