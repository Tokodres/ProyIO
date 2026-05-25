import numpy as np
from itertools import combinations

class MetodoGrafico:
    def __init__(self, datos):
        self.datos = datos
        self.restricciones = datos['restricciones_datos']
        self.func_obj = datos['funcion_objetivo']

    def calcular(self):
        # 1. Preparar líneas para graficar
        x_vals = np.linspace(0, 20, 400)
        lineas = []
        for r in self.restricciones:
            a, b = float(r['coeficientes'][0]), float(r['coeficientes'][1])
            sol = float(r['solucion'])
            if b != 0:
                y = (sol - a * x_vals) / b
                lineas.append({'x': x_vals, 'y': y, 'a': a, 'b': b, 'sol': sol})
            else:
                lineas.append({'x': np.full_like(x_vals, sol/a), 'y': x_vals, 'vertical': True, 'x_const': sol/a})

        # 2. Encontrar vértices (intersecciones)
        puntos = [(0, 0)] # Incluimos origen
        for i in range(len(self.restricciones)):
            for j in range(i + 1, len(self.restricciones)):
                # Resolver sistema 2x2
                r1, r2 = self.restricciones[i], self.restricciones[j]
                A = np.array([[float(r1['coeficientes'][0]), float(r1['coeficientes'][1])],
                              [float(r2['coeficientes'][0]), float(r2['coeficientes'][1])]])
                B = np.array([float(r1['solucion']), float(r2['solucion'])])
                try:
                    p = np.linalg.solve(A, B)
                    if p[0] >= 0 and p[1] >= 0: # Solo primer cuadrante
                        puntos.append(tuple(p))
                except: pass

        # 3. Filtrar puntos que cumplen TODAS las restricciones
        vertices_validos = []
        for p in puntos:
            valido = True
            for r in self.restricciones:
                a, b = float(r['coeficientes'][0]), float(r['coeficientes'][1])
                res = a * p[0] + b * p[1]
                # Tolerancia de redondeo
                if r['operador'] == '<=' and res > float(r['solucion']) + 1e-6: valido = False
                if r['operador'] == '>=' and res < float(r['solucion']) - 1e-6: valido = False
            if valido: vertices_validos.append(p)

        # 4. Evaluar función objetivo
        c1 = float(self.func_obj['coeficientes'][0])
        c2 = float(self.func_obj['coeficientes'][1])
        tipo = self.func_obj['optimizacion']
        
        evaluaciones = [(v, c1*v[0] + c2*v[1]) for v in vertices_validos]
        if tipo == 'Max':
            optimo = max(evaluaciones, key=lambda x: x[1])
        else:
            optimo = min(evaluaciones, key=lambda x: x[1])

        return {'lineas': lineas, 
            'vertices': vertices_validos, 
            'optimo': optimo}