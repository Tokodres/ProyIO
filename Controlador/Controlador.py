from Vista.Vista import Vista
from Modelo.MetodoGrafico import MetodoGrafico
from Modelo.MetodoDosFases import MetodoDosFases
from tkinter import messagebox


class Controlador:

    def __init__(self):
        self.vista = Vista(controlador=self)

    def iniciar_app(self):
        self.vista.mainloop()

    def Datos(self, variables, restricciones):
        if variables < 1 or restricciones < 1:
            messagebox.showwarning("Atención", "Se requiere mínimo 1 variable y 1 restricción.")
            return
        print(f"Controlador: matriz {variables}x{restricciones}")
        self.vista.generarMatriz(variables, restricciones)

    def procesar_matriz(self, datos, metodo):
        if metodo == "Grafico":
            self.metodo_Grafico(datos)
        elif metodo == "DosFases":
            self.metodo_DosFases(datos)
        else:
            messagebox.showerror("Error", "Método no reconocido.")

    # ------------------------------------------------------------------ #
    def metodo_Grafico(self, datos):
        if datos['variables'] != 2:
            messagebox.showerror("Error", "El método gráfico solo permite 2 variables.")
            return
        modelo    = MetodoGrafico(datos)
        resultados = modelo.calcular()
        self.vista.mostrar_grafica(resultados)

    def metodo_DosFases(self, datos):
        try:
            modelo    = MetodoDosFases(datos)
            resultados = modelo.calcular()
            self.vista.mostrar_dos_fases(resultados)
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar Dos Fases:\n{e}")