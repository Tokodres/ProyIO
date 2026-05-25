from fractions import Fraction
import numpy as np


class MetodoDosFases:

    def __init__(self, datos):
        """
        datos = {
            'variables': int,
            'restricciones': int,
            'restricciones_datos': [
                {'coeficientes': ['3','2',...], 'operador': '<=', 'solucion': '10'},
                ...
            ],
            'funcion_objetivo': {
                'optimizacion': 'Max' | 'Min',
                'coeficientes': ['5','4',...]
            }
        }
        """
        self.datos_raw = datos
        self.num_vars  = datos['variables']
        self.num_restr = datos['restricciones']

    # ------------------------------------------------------------------ #
    #  ENTRADA PÚBLICA                                                     #
    # ------------------------------------------------------------------ #
    def calcular(self):
        """Convierte los datos crudos (strings) y ejecuta dos fases."""
        raw = self.datos_raw

        z    = [float(c) for c in raw['funcion_objetivo']['coeficientes']]
        tipo = raw['funcion_objetivo']['optimizacion']

        restricciones = []
        for r in raw['restricciones_datos']:
            restricciones.append({
                'coeficientes': [float(c) for c in r['coeficientes']],
                'operador':     r['operador'],
                'solucion':     float(r['solucion']),
            })

        return self._dos_fases({'z': z, 'tipo': tipo, 'restricciones': restricciones})

    # ------------------------------------------------------------------ #
    #  NÚCLEO: DOS FASES                                                   #
    # ------------------------------------------------------------------ #
    def _dos_fases(self, datos):
        restricciones = datos['restricciones']
        z    = datos['z']
        tipo = datos['tipo']

        nO = len(z)
        nR = len(restricciones)

        pasos  = []   # lista de dicts que la vista consumirá
        texto  = ""   # texto plano acumulado (para el cuadro de texto)

        # ── encabezado ──────────────────────────────────────────────────
        texto += "=" * 70 + "\n"
        texto += "           MÉTODO SIMPLEX DE DOS FASES\n"
        texto += "=" * 70 + "\n\n"
        texto += f"PROBLEMA:\n  {tipo} Z = "
        texto += " ".join(
            f"{'+' if c >= 0 and i > 0 else ''}{c} X{i+1}"
            for i, c in enumerate(z)
        ) + "\n\nSujeto a:\n"
        for r in restricciones:
            texto += "  " + " ".join(
                f"{'+' if c >= 0 and j > 0 else ''}{c} X{j+1}"
                for j, c in enumerate(r['coeficientes'])
            ) + f"  {r['operador']}  {r['solucion']}\n"
        texto += "\n"

        # ── clasificar restricciones ─────────────────────────────────────
        tipos = [r['operador'] for r in restricciones]
        A     = [r['coeficientes'][:] for r in restricciones]
        b     = [r['solucion']        for r in restricciones]

        for i in range(nR):
            if b[i] < 0:
                A[i] = [-v for v in A[i]]
                b[i] = -b[i]
                if   tipos[i] == '<=': tipos[i] = '>='
                elif tipos[i] == '>=': tipos[i] = '<='
                texto += f"  R{i+1}: b negativo → multiplicada por -1\n"

        nH = sum(1 for t in tipos if t == '<=')
        nE = sum(1 for t in tipos if t == '>=')
        nA = sum(1 for t in tipos if t in ('>=', '='))
        totalF1 = nO + nH + nE + nA

        texto += f"\nESTRUCTURA:\n"
        texto += f"  Variables originales : {nO}\n"
        texto += f"  Holgura  (s)         : {nH}\n"
        texto += f"  Exceso   (e)         : {nE}\n"
        texto += f"  Artificiales (a)     : {nA}\n"
        texto += f"  Total Fase I         : {totalF1}\n\n"

        # ── cabeceras ────────────────────────────────────────────────────
        cab_f1 = (
            [f"X{j+1}" for j in range(nO)] +
            [f"s{j+1}" for j in range(nH)] +
            [f"e{j+1}" for j in range(nE)] +
            [f"a{j+1}" for j in range(nA)] +
            ["SOL"]
        )
        cab_f2 = (
            [f"X{j+1}" for j in range(nO)] +
            [f"s{j+1}" for j in range(nH)] +
            [f"e{j+1}" for j in range(nE)] +
            ["SOL"]
        )

        # ── construir tabla Fase I ───────────────────────────────────────
        def mk(r, c): return [[0.0]*c for _ in range(r)]

        tabla = mk(nR + 1, totalF1 + 1)
        for i in range(nR):
            for j in range(nO):
                tabla[i][j] = A[i][j]

        col = nO
        for i in range(nR):
            if tipos[i] == '<=':
                tabla[i][col] = 1; col += 1
        col = nO + nH
        for i in range(nR):
            if tipos[i] == '>=':
                tabla[i][col] = -1; col += 1
        col = nO + nH + nE
        for i in range(nR):
            if tipos[i] in ('>=', '='):
                tabla[i][col] = 1; col += 1
        for i in range(nR):
            tabla[i][totalF1] = b[i]
        for k in range(nA):
            tabla[nR][nO + nH + nE + k] = 1.0

        # eliminar artificiales básicas del objetivo F-I
        ai = 0
        for i in range(nR):
            if tipos[i] in ('>=', '='):
                ca = nO + nH + nE + ai
                f  = tabla[nR][ca]
                if abs(f) > 1e-9:
                    for j in range(totalF1 + 1):
                        tabla[nR][j] -= f * tabla[i][j]
                ai += 1

        texto += "-" * 70 + "\nFASE I: Minimizar suma de artificiales\n" + "-" * 70 + "\n\n"
        texto += "Tabla inicial Fase I:\n"
        texto += self._tabla_str(tabla, cab_f1)

        tablas_f1 = [{'cabeceras': cab_f1,
                      'filas':     self._copia(tabla, nR),
                      'z_fila':    self._frac_fila(tabla[nR]),
                      'titulo':    'Tabla inicial – Fase I'}]

        # ── iteraciones Fase I ───────────────────────────────────────────
        iter1 = 1
        while True:
            fz = tabla[nR][:totalF1]
            if all(v >= -1e-9 for v in fz):
                texto += f"\n✓ Fase I óptima en {iter1-1} iteraciones.\n"
                break
            cp  = fz.index(min(fz))
            raz = [tabla[i][totalF1]/tabla[i][cp]
                   if tabla[i][cp] > 1e-9 else float('inf')
                   for i in range(nR)]
            if all(r == float('inf') for r in raz):
                texto += "✗ NO ACOTADO en Fase I\n"
                return self._resultado_error("No acotado en Fase I", texto, tablas_f1, [])
            fp  = raz.index(min(raz))
            piv = tabla[fp][cp]

            texto += f"\nIteración {iter1} – col: {cab_f1[cp]}  fila: R{fp+1}  pivote: {self._af(piv)}\n"
            for j in range(totalF1 + 1): tabla[fp][j] /= piv
            for i in range(nR + 1):
                if i != fp and abs(tabla[i][cp]) > 1e-9:
                    f = tabla[i][cp]
                    for j in range(totalF1 + 1): tabla[i][j] -= f * tabla[fp][j]

            texto += self._tabla_str(tabla, cab_f1)
            tablas_f1.append({'cabeceras': cab_f1,
                               'filas':     self._copia(tabla, nR),
                               'z_fila':    self._frac_fila(tabla[nR]),
                               'titulo':    f'Iteración {iter1} – Fase I'})
            iter1 += 1
            if iter1 > 100:
                texto += "⚠️ Límite de iteraciones Fase I\n"; break

        suma_art = -tabla[nR][totalF1]
        texto += f"\nSuma de artificiales = {self._af(suma_art)}\n"
        if suma_art > 1e-6:
            texto += "❌ NO EXISTE SOLUCIÓN FACTIBLE\n"
            return self._resultado_error("No existe solución factible", texto, tablas_f1, [])
        texto += "✅ Solución factible encontrada.\n\n"

        # sacar artificiales básicas con valor 0
        for i in range(nR):
            for a in range(nA):
                ca = nO + nH + nE + a
                if abs(tabla[i][ca] - 1) < 1e-9 and abs(tabla[i][totalF1]) < 1e-9:
                    for jj in range(nO + nH + nE):
                        if abs(tabla[i][jj]) > 1e-9:
                            pv = tabla[i][jj]
                            for j in range(totalF1 + 1): tabla[i][j] /= pv
                            for k in range(nR + 1):
                                if k != i and abs(tabla[k][jj]) > 1e-9:
                                    f = tabla[k][jj]
                                    for j in range(totalF1 + 1): tabla[k][j] -= f * tabla[i][j]
                            break
                    break

        # ── Fase II ──────────────────────────────────────────────────────
        texto += "-" * 70 + "\nFASE II: Optimizar función objetivo original\n" + "-" * 70 + "\n\n"

        totalF2 = nO + nH + nE
        t2 = mk(nR + 1, totalF2 + 1)
        for i in range(nR):
            for j in range(totalF2): t2[i][j] = tabla[i][j]
            t2[i][totalF2] = tabla[i][totalF1]

        c = [-v if tipo == 'Min' else v for v in z]
        for j in range(nO): t2[nR][j] = -c[j]

        for j in range(totalF2):
            col_v = [t2[i][j] for i in range(nR)]
            if (abs(sum(abs(v) for v in col_v) - 1) < 1e-9 and
                    abs(max(col_v) - 1) < 1e-9):
                fi = col_v.index(1)
                if abs(t2[nR][j]) > 1e-9:
                    f = t2[nR][j]
                    for k in range(totalF2 + 1): t2[nR][k] -= f * t2[fi][k]

        texto += "Tabla inicial Fase II:\n"
        texto += self._tabla_str(t2, cab_f2)

        tablas_f2 = [{'cabeceras': cab_f2,
                      'filas':     self._copia(t2, nR),
                      'z_fila':    self._frac_fila(t2[nR]),
                      'titulo':    'Tabla inicial – Fase II'}]

        iter2 = 1
        while True:
            fz2 = t2[nR][:totalF2]
            if all(v >= -1e-9 for v in fz2):
                texto += f"\n✓ Óptimo en Fase II ({iter2-1} iteraciones).\n"
                break
            cp  = fz2.index(min(fz2))
            raz = [t2[i][totalF2]/t2[i][cp]
                   if t2[i][cp] > 1e-9 else float('inf')
                   for i in range(nR)]
            if all(r == float('inf') for r in raz):
                texto += "✗ NO ACOTADO en Fase II\n"; break
            fp  = raz.index(min(raz))
            piv = t2[fp][cp]

            texto += f"\nIteración {iter2} – col: {cab_f2[cp]}  fila: R{fp+1}  pivote: {self._af(piv)}\n"
            for j in range(totalF2 + 1): t2[fp][j] /= piv
            for i in range(nR + 1):
                if i != fp and abs(t2[i][cp]) > 1e-9:
                    f = t2[i][cp]
                    for j in range(totalF2 + 1): t2[i][j] -= f * t2[fp][j]

            texto += self._tabla_str(t2, cab_f2)
            tablas_f2.append({'cabeceras': cab_f2,
                               'filas':     self._copia(t2, nR),
                               'z_fila':    self._frac_fila(t2[nR]),
                               'titulo':    f'Iteración {iter2} – Fase II'})
            iter2 += 1
            if iter2 > 100:
                texto += "⚠️ Límite de iteraciones Fase II\n"; break

        # ── solución final ───────────────────────────────────────────────
        sol = [0.0] * nO
        for j in range(nO):
            col_v = [t2[i][j] for i in range(nR)]
            if (abs(sum(abs(v) for v in col_v) - 1) < 1e-9 and
                    abs(max(col_v) - 1) < 1e-9):
                fi = col_v.index(1)
                sol[j] = t2[fi][totalF2]

        vz = t2[nR][totalF2]
        if tipo == 'Min': vz = -vz

        texto += "\n" + "=" * 70 + "\nRESULTADO FINAL\n" + "=" * 70 + "\n"
        for i, v in enumerate(sol):
            texto += f"  X{i+1} = {self._af(v)}\n"
        texto += f"\n  Z ({tipo}) = {self._af(vz)}\n"

        return {
            'factible':   True,
            'texto':      texto,
            'tablas_f1':  tablas_f1,
            'tablas_f2':  tablas_f2,
            'solucion':   {f'X{i+1}': self._af(v) for i, v in enumerate(sol)},
            'z_valor':    self._af(vz),
            'z_tipo':     tipo,
            'error':      None,
        }

    # ------------------------------------------------------------------ #
    #  AUXILIARES                                                          #
    # ------------------------------------------------------------------ #
    def _af(self, valor):
        """Float → fracción legible."""
        if abs(valor) < 1e-10: return '0'
        f = Fraction(valor).limit_denominator(1000)
        return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"

    def _frac_fila(self, fila):
        return [self._af(v) for v in fila]

    def _copia(self, tabla, nR):
        """Devuelve las filas de restricciones como listas de strings fraccionarios."""
        return [[self._af(v) for v in fila] for fila in tabla[:nR]]

    def _tabla_str(self, tabla, cabeceras):
        """Genera string formateado de la tabla para el log de texto."""
        R = len(tabla)
        C = len(cabeceras)
        celdas = [[self._af(tabla[i][j]) for j in range(C)] for i in range(R)]
        anchos = [max(len(cabeceras[j]), 4, max(len(celdas[i][j]) for i in range(R)))
                  for j in range(C)]
        sep = "  " + "-" * (8 + sum(w + 3 for w in anchos))
        t = "\n  " + "      ".ljust(8) + "  ".join(c.rjust(anchos[j]) for j, c in enumerate(cabeceras)) + "\n"
        t += sep + "\n"
        for i in range(R - 1):
            t += "  " + f"R{i+1}".ljust(8) + "  ".join(celdas[i][j].rjust(anchos[j]) for j in range(C)) + "\n"
        t += sep + "\n"
        t += "  " + "Z".ljust(8) + "  ".join(celdas[-1][j].rjust(anchos[j]) for j in range(C)) + "\n"
        return t

    def _resultado_error(self, mensaje, texto, tablas_f1, tablas_f2):
        return {
            'factible':  False,
            'texto':     texto,
            'tablas_f1': tablas_f1,
            'tablas_f2': tablas_f2,
            'solucion':  {},
            'z_valor':   '-',
            'z_tipo':    '-',
            'error':     mensaje,
        }