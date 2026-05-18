from Vista.Vista import Vista
from tkinter import messagebox

class Controlador:
    def __init__(self):
        self.vista = Vista(controlador=self)
        
    def iniciar_app(self):
        self.vista.mainloop()
        
    def Datos(self, variables, restricciones):
        if variables < 1 or restricciones < 1:
            messagebox.showwarning("Atención", "Se requiere mínimo una variable y 1 restricción.")
            return
        else:                
            print(f"Controlador: Construyendo matriz de {variables + 1}x{restricciones + 1}")    
            self.vista.generarMatriz(variables, restricciones)