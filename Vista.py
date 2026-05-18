import customtkinter as ctk 
from tkinter import messagebox

class Vista(ctk.CTk):
    
    #Constructor
    def __init__(self, controlador=None):
        super().__init__()
        self.controlador = controlador
              
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.title("Calculadora Simplex")
        self.geometry("600x400")
        self.minsize(500, 350) 
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

        lblTitle = ctk.CTkLabel(self.main_frame,
                                text="Configuración Modelo",
                                font=ctk.CTkFont(size=40, weight="bold")
                                )
        lblTitle.grid(row=0, column=0, pady=(30, 10), sticky="n")

    def tomaDatos(self):
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form_frame.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="n") 
        form_frame.columnconfigure((0, 1), weight=1)

        # -- Variables --
        lblVar = ctk.CTkLabel(form_frame,
                              text="Cantidad de Variables",
                              font=ctk.CTkFont(size=16)
                            )
        lblVar.grid(row=0, column=0, padx=15, pady=(0, 5), sticky="w")
        self.txtVar = ctk.CTkEntry(form_frame,
                                   fg_color="white",
                                   text_color="black",
                                   placeholder_text="Ej. 4",
                                   width=180,
                                   height=35)
        self.txtVar.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")

        # -- Restricciones --
        lblRes = ctk.CTkLabel(form_frame,
                              text="Número de Restricciones",
                              font=ctk.CTkFont(size=16)
                            )
        lblRes.grid(row=0, column=1, padx=15, pady=(0, 5), sticky="w")
        self.txtRes = ctk.CTkEntry(form_frame,
                                   fg_color="white",
                                   text_color="black",
                                   placeholder_text="Ej. 5",
                                   width=180,
                                   height=35
                                )
        self.txtRes.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="w")
        
        # -- Botón --
        btnEnviar = ctk.CTkButton(form_frame,
                                  text="Generar Matriz",
                                  font=ctk.CTkFont(size=16, weight="bold"),
                                  height=40,
                                  width=200,
                                  command=self.Envio)
        btnEnviar.grid(row=2, column=0, columnspan=2, pady=(20, 0))

    # -- Envio Controlador --
    def Envio(self):
        variables = self.txtVar.get().strip()
        restricciones = self.txtRes.get().strip()
        
        # Validacion si están vacíos
        if (not variables or not restricciones) :
            messagebox.showerror("Error", "Todos, los campos se deben llenar.")
            return
        elif (not variables.isdigit() or not restricciones.isdigit()):       
            messagebox.showerror("Error", "los campos solo pueden contener numeros.")
            return
        elif (self.controlador is not None):
            self.controlador.Datos(int(variables), int(restricciones))
        else:
            print(f"[No controlador] Datos válidos: Vars={variables}, Res={restricciones}")