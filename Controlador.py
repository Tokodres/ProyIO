import Modelo
from Vista import Vista
from tkinter import messagebox

class Controlador:
    def __init__(self):
        self.vista = Vista(controlador=self)
        
    def iniciar_app(self):
        self.vista.mainloop()
        
    def Datos(self, variables, restricciones):
            if (variables < 1 or restricciones < 1):
                messagebox.showwarning("Atención", "Se requiere minimo una variable y 1 restriccion.")
                return
                
            print(f"Controlador: Variables {variables} variables y {restricciones} restricciones.")
            ## se debe enviar nuevamente a vista y crear la matriz para añadir estos

def main():
    app = Controlador()
    app.iniciar_app()
    
    
if __name__ == "__main__":
    main()