import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from Vista.Grafica import GraficaFrame


class Vista(ctk.CTk):

    def __init__(self, controlador=None):
        super().__init__()
        self.controlador = controlador

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)

        self.title("Calculadora Simplex")
        self.geometry("700x500")
        self.minsize(550, 400)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.frPrincipal()
        self.tomaDatos()

    # ------------------------------------------------------------------ #
    def frPrincipal(self):
        self.main_frame.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)
        self.main_frame.rowconfigure(1, weight=1)

        self.lblTitle = ctk.CTkLabel(
            self.main_frame,
            text="Configuración Modelo",
            font=ctk.CTkFont(size=35, weight="bold"),
        )
        self.lblTitle.grid(row=0, column=0, pady=(30, 10), sticky="n")

    # ------------------------------------------------------------------ #
    def tomaDatos(self):
        self.form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="n")
        self.form_frame.columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            self.form_frame, text="Cantidad de Variables",
            font=ctk.CTkFont(size=16),
        ).grid(row=0, column=0, padx=15, pady=(0, 5), sticky="w")
        self.txtVar = ctk.CTkEntry(
            self.form_frame, fg_color="white", text_color="black",
            placeholder_text="Ej. 4", width=180, height=35,
        )
        self.txtVar.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")

        ctk.CTkLabel(
            self.form_frame, text="Número de Restricciones",
            font=ctk.CTkFont(size=16),
        ).grid(row=0, column=1, padx=15, pady=(0, 5), sticky="w")
        self.txtRes = ctk.CTkEntry(
            self.form_frame, fg_color="white", text_color="black",
            placeholder_text="Ej. 5", width=180, height=35,
        )
        self.txtRes.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="w")

        ctk.CTkButton(
            self.form_frame,
            text="Generar Matriz",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40, width=200,
            command=self.Envio,
        ).grid(row=2, column=0, columnspan=2, pady=(20, 0))

    # ------------------------------------------------------------------ #
    def Envio(self):
        variables    = self.txtVar.get().strip()
        restricciones = self.txtRes.get().strip()

        if not variables or not restricciones:
            messagebox.showerror("Error", "Todos los campos se deben llenar.")
            return
        if not variables.isdigit() or not restricciones.isdigit():
            messagebox.showerror("Error", "Los campos solo pueden contener números enteros.")
            return
        if self.controlador is not None:
            self.controlador.Datos(int(variables), int(restricciones))
        else:
            print(f"[Sin controlador] Vars={variables}, Res={restricciones}")

    def volverAInicio(self):
        if hasattr(self, 'canvas_frame'):
            self.canvas_frame.destroy()
            del self.canvas_frame
        if hasattr(self, 'btn_frame'):
            self.btn_frame.destroy()
            del self.btn_frame
        if hasattr(self, 'form_frame'):
            self.form_frame.destroy()

        self.lblTitle.configure(text="Configuración Modelo")
        self.tomaDatos()

    # ------------------------------------------------------------------ #
    def generarMatriz(self, variables, restricciones):
        self.form_frame.grid_forget()
        self.lblTitle.configure(text="Ingrese los Coeficientes")
        self.variables    = variables
        self.restricciones = restricciones

        self.main_frame.columnconfigure(0, weight=1)

        # Canvas con scrollbars para si hay muchas restricciones / variables
        canvas_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        canvas_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        self.canvas_frame = canvas_frame

        canvas = tk.Canvas(canvas_frame, bg="#212121", highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        scroll = ctk.CTkFrame(canvas, fg_color="transparent")
        canvas.create_window((0, 0), window=scroll, anchor="nw")
        matriz_frame = scroll

        v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scroll.bind("<Configure>", on_frame_configure)

        # Rueda del ratón: vertical; Shift+rueda: horizontal
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * int(e.delta/120), "units"))
        canvas.bind_all("<Shift-MouseWheel>", lambda e: canvas.xview_scroll(-1 * int(e.delta/120), "units"))

        self.datos_matriz = []

        # ── restricciones ──────────────────────────────────────────────
        for i in range(restricciones):
            fila_datos = {'coeficientes': [], 'operador': None, 'solucion': None}
            col_actual = 0

            ctk.CTkLabel(
                matriz_frame, text=f"R{i+1}:",
                font=ctk.CTkFont(weight="bold"),
            ).grid(row=i, column=col_actual, padx=(0, 15), pady=8)
            col_actual += 1

            for j in range(variables):
                celda = ctk.CTkEntry(
                    matriz_frame, fg_color="white", text_color="black",
                    placeholder_text="0", width=50, height=30,
                )
                celda.grid(row=i, column=col_actual, padx=2, pady=8)
                fila_datos['coeficientes'].append(celda)
                col_actual += 1

                ctk.CTkLabel(matriz_frame, text=f"X{j+1}").grid(
                    row=i, column=col_actual, padx=2, pady=8)
                col_actual += 1

                if j < variables - 1:
                    ctk.CTkLabel(matriz_frame, text="+").grid(
                        row=i, column=col_actual, padx=4, pady=8)
                    col_actual += 1

            cb_signo = ctk.CTkComboBox(
                matriz_frame, values=["<=", ">=", "="],
                width=65, height=30, state="readonly",
            )
            cb_signo.set("<=")
            cb_signo.grid(row=i, column=col_actual, padx=10, pady=8)
            fila_datos['operador'] = cb_signo
            col_actual += 1

            txt_sol = ctk.CTkEntry(
                matriz_frame, fg_color="white", text_color="black",
                placeholder_text="Sol", width=60, height=30,
            )
            txt_sol.grid(row=i, column=col_actual, padx=2, pady=8)
            fila_datos['solucion'] = txt_sol

            self.datos_matriz.append(fila_datos)

        # ── función objetivo ───────────────────────────────────────────
        fila_z_datos = {'coeficientes': [], 'operador': None, 'solucion': None}
        fila_z_idx   = restricciones
        col_actual   = 0

        ctk.CTkLabel(
            matriz_frame, text="f(x) =",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=fila_z_idx, column=col_actual, padx=(0, 5), pady=15)
        col_actual += 1

        cb_opt = ctk.CTkComboBox(
            matriz_frame, values=["Max", "Min"],
            width=75, height=30, state="readonly",
        )
        cb_opt.set("Max")
        cb_opt.grid(row=fila_z_idx, column=col_actual, padx=5, pady=15)
        fila_z_datos['operador'] = cb_opt
        col_actual += 1

        ctk.CTkLabel(
            matriz_frame, text="Z =",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=fila_z_idx, column=col_actual, padx=(5, 10), pady=15)
        col_actual += 1

        for j in range(variables):
            celda_z = ctk.CTkEntry(
                matriz_frame, fg_color="white", text_color="black",
                placeholder_text="0", width=50, height=30,
            )
            celda_z.grid(row=fila_z_idx, column=col_actual, padx=2, pady=15)
            fila_z_datos['coeficientes'].append(celda_z)
            col_actual += 1

            ctk.CTkLabel(matriz_frame, text=f"X{j+1}").grid(
                row=fila_z_idx, column=col_actual, padx=2, pady=15)
            col_actual += 1

            if j < variables - 1:
                ctk.CTkLabel(matriz_frame, text="+").grid(
                    row=fila_z_idx, column=col_actual, padx=4, pady=15)
                col_actual += 1

        self.datos_matriz.append(fila_z_datos)

        # ── botones de métodos ─────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=(10, 5))

        ctk.CTkButton(
            btn_frame,
            text="Método Gráfico",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=40, width=200,
            command=lambda: self.enviarDatos("Grafico"),
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Dos Fases",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=40, width=200,
            fg_color="#2d6a4f",
            hover_color="#1b4332",
            command=lambda: self.enviarDatos("DosFases"),
        ).grid(row=0, column=1, padx=10)

        self.btn_frame = btn_frame
        ctk.CTkButton(
            btn_frame,
            text="Volver",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=40, width=200,
            fg_color="#714d0a",
            hover_color="#8a5f1b",
            command=self.volverAInicio,
        ).grid(row=0, column=2, padx=10)

    # ------------------------------------------------------------------ #
    def _normalizarValor(self, valor):
        valor = valor.strip()
        return valor if valor != "" else "0"

    def leerRestricciones(self):
        restricciones = []
        for fila in self.datos_matriz[:self.restricciones]:
            restricciones.append({
                'coeficientes': [self._normalizarValor(e.get()) for e in fila['coeficientes']],
                'operador':     self._normalizarValor(fila['operador'].get()),
                'solucion':     self._normalizarValor(fila['solucion'].get()),
            })
        return restricciones

    def leerFuncionObjetivo(self):
        fila_obj = self.datos_matriz[-1]
        return {
            'optimizacion': self._normalizarValor(fila_obj['operador'].get()),
            'coeficientes': [self._normalizarValor(e.get()) for e in fila_obj['coeficientes']],
        }

    def obtenerDatosMatriz(self):
        return {
            'variables':          self.variables,
            'restricciones':      self.restricciones,
            'restricciones_datos': self.leerRestricciones(),
            'funcion_objetivo':   self.leerFuncionObjetivo(),
        }

    def enviarDatos(self, metodo):
        if not hasattr(self, 'datos_matriz') or not self.datos_matriz:
            messagebox.showwarning("Atención", "Primero genere la matriz.")
            return
        datos = self.obtenerDatosMatriz()
        if self.controlador is not None:
            self.controlador.procesar_matriz(datos, metodo)
        else:
            print("[Sin controlador] Datos:", datos)

    # ------------------------------------------------------------------ #
    def mostrar_grafica(self, resultados):
        from Vista.Grafica import GraficaVentana
        ventana = GraficaVentana(self, resultados)
        ventana.grab_set()
        ventana.focus()

    def mostrar_dos_fases(self, resultados):
        """Abre la ventana emergente VistaDosFases con los resultados."""
        from Vista.VistaDosFases import VistaDosFases
        ventana = VistaDosFases(self, resultados)
        ventana.grab_set()   # modal: bloquea la ventana principal
        ventana.focus()