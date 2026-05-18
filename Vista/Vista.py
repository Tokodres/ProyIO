import customtkinter as ctk 
from tkinter import messagebox

class Vista(ctk.CTk):
    
    def __init__(self, controlador=None):
        super().__init__()
        self.controlador = controlador
               
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.title("Calculadora Simplex")
        self.geometry("700x500")
        self.minsize(550, 400) 
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.frPrincipal()
        self.tomaDatos()

    def frPrincipal(self):
        self.main_frame.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0) 
        self.main_frame.rowconfigure(1, weight=1)

        ## -- Título frame Principal --
        self.lblTitle = ctk.CTkLabel(self.main_frame,
                                text="Configuración Modelo",
                                font=ctk.CTkFont(size=35, weight="bold")
                                )
        self.lblTitle.grid(row=0, column=0, pady=(30, 10), sticky="n")

    def tomaDatos(self):
        self.form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="n") 
        self.form_frame.columnconfigure((0, 1), weight=1)

        # -- Variables --
        lblVar = ctk.CTkLabel(self.form_frame, text="Cantidad de Variables", font=ctk.CTkFont(size=16))
        lblVar.grid(row=0, column=0, padx=15, pady=(0, 5), sticky="w")
        self.txtVar = ctk.CTkEntry(self.form_frame, fg_color="white", text_color="black", placeholder_text="Ej. 4", width=180, height=35)
        self.txtVar.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")

        # -- Restricciones --
        lblRes = ctk.CTkLabel(self.form_frame, text="Número de Restricciones", font=ctk.CTkFont(size=16))
        lblRes.grid(row=0, column=1, padx=15, pady=(0, 5), sticky="w")
        self.txtRes = ctk.CTkEntry(self.form_frame, fg_color="white", text_color="black", placeholder_text="Ej. 5", width=180, height=35)
        self.txtRes.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="w")
        
        # -- Botón --
        btnEnviar = ctk.CTkButton(self.form_frame, text="Generar Matriz", font=ctk.CTkFont(size=16, weight="bold"), height=40, width=200, command=self.Envio)
        btnEnviar.grid(row=2, column=0, columnspan=2, pady=(20, 0))

    def Envio(self):
        variables = self.txtVar.get().strip()
        restricciones = self.txtRes.get().strip()
        
        if not variables or not restricciones:
            messagebox.showerror("Error", "Todos los campos se deben llenar.")
            return
        elif not variables.isdigit() or not restricciones.isdigit():       
            messagebox.showerror("Error", "Los campos solo pueden contener números.")
            return
        elif self.controlador is not None:
            self.controlador.Datos(int(variables), int(restricciones))
        else:
            print(f"[No controlador] Datos válidos: Vars={variables}, Res={restricciones}")
            
    # -- Generar Matriz --
    def generarMatriz(self, variables, restricciones):
            self.form_frame.grid_forget()
            self.lblTitle.configure(text="Ingrese los Coeficientes")
            
            self.main_frame.columnconfigure(0, weight=1)
            
            matriz_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            matriz_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
            
            self.datos_matriz = []
            
            # -- RESTRICCIONES (R1, R2...) --
            for i in range(restricciones):
                fila_datos = {'coeficientes': [], 'operador': None, 'solucion': None}
                col_actual = 0
                
                # Etiqueta de la Restricción (R1, R2...)
                lbl_restriccion = ctk.CTkLabel(matriz_frame, text=f"R{i+1}:", font=ctk.CTkFont(weight="bold"))
                lbl_restriccion.grid(row=i, column=col_actual, padx=(0, 15), pady=8)
                col_actual += 1
                
                # Construcción de las variables e intercalado de signos '+'
                for j in range(variables):
                    # Entry para coeficiente
                    celda = ctk.CTkEntry(matriz_frame, fg_color="white", text_color="black", placeholder_text="0", width=50, height=30)
                    celda.grid(row=i, column=col_actual, padx=2, pady=8)
                    fila_datos['coeficientes'].append(celda)
                    col_actual += 1
                    
                    # Etiqueta variable (X1, X2...)
                    lbl_x = ctk.CTkLabel(matriz_frame, text=f"X{j+1}")
                    lbl_x.grid(row=i, column=col_actual, padx=2, pady=8)
                    col_actual += 1
                    
                    # Agregar +
                    if j < variables - 1:
                        lbl_mas = ctk.CTkLabel(matriz_frame, text="+")
                        lbl_mas.grid(row=i, column=col_actual, padx=4, pady=8)
                        col_actual += 1
                
                # ComboBox (<=, >=, =)
                cb_signo = ctk.CTkComboBox(matriz_frame, values=["<=", ">=", "="], width=65, height=30, state="readonly")
                cb_signo.set("<=") # Valor por defecto
                cb_signo.grid(row=i, column=col_actual, padx=10, pady=8)
                fila_datos['operador'] = cb_signo
                col_actual += 1
                
                # solucion
                txt_sol = ctk.CTkEntry(matriz_frame, fg_color="white", text_color="black", placeholder_text="Sol", width=60, height=30)
                txt_sol.grid(row=i, column=col_actual, padx=2, pady=8)
                fila_datos['solucion'] = txt_sol
                
                self.datos_matriz.append(fila_datos)
                
            # -- Funcion Objetivo --
            fila_z_datos = {'coeficientes': [], 'operador': None, 'solucion': None}
            fila_z_idx = restricciones  # Se posiciona abajo de la última restricción
            col_actual = 0
            
            # Texto inicial: f(x) =
            lbl_fx = ctk.CTkLabel(matriz_frame, text="f(x) =", font=ctk.CTkFont(weight="bold"))
            lbl_fx.grid(row=fila_z_idx, column=col_actual, padx=(0, 5), pady=15)
            col_actual += 1
            
            # ComboBox de Optimización (Max / Min)
            cb_opt = ctk.CTkComboBox(matriz_frame, values=["Max", "Min"], width=75, height=30, state="readonly")
            cb_opt.set("Max")
            cb_opt.grid(row=fila_z_idx, column=col_actual, padx=5, pady=15)
            fila_z_datos['operador'] = cb_opt
            col_actual += 1
            
            # Texto de la variable Z
            lbl_z = ctk.CTkLabel(matriz_frame, text="Z = ", font=ctk.CTkFont(weight="bold"))
            lbl_z.grid(row=fila_z_idx, column=col_actual, padx=(5, 10), pady=15)
            col_actual += 1
            
            # variables de z
            for j in range(variables):
                celda_z = ctk.CTkEntry(matriz_frame, fg_color="white", text_color="black", placeholder_text="0", width=50, height=30)
                celda_z.grid(row=fila_z_idx, column=col_actual, padx=2, pady=15)
                fila_z_datos['coeficientes'].append(celda_z)
                col_actual += 1
                
                lbl_xz = ctk.CTkLabel(matriz_frame, text=f"X{j+1}")
                lbl_xz.grid(row=fila_z_idx, column=col_actual, padx=2, pady=15)
                col_actual += 1
                
                if j < variables - 1:
                    lbl_mas_z = ctk.CTkLabel(matriz_frame, text="+")
                    lbl_mas_z.grid(row=fila_z_idx, column=col_actual, padx=4, pady=15)
                    col_actual += 1
                    
            self.datos_matriz.append(fila_z_datos)