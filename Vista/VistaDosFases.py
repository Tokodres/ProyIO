import customtkinter as ctk


class VistaDosFases(ctk.CTkToplevel):
    """
    Ventana emergente que muestra el procedimiento completo del
    método Simplex de Dos Fases: tablas de cada iteración y resultado final.
    El estilo (dark / blue / fuentes) es idéntico al del programa principal.
    """

    def __init__(self, master, resultados: dict):
        super().__init__(master)
        self.resultados = resultados

        self.title("Simplex – Método de Dos Fases")
        self.geometry("1050x680")
        self.minsize(750, 500)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # ── frame raíz ───────────────────────────────────────────────────
        root = ctk.CTkFrame(self, corner_radius=15)
        root.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        # ── título ───────────────────────────────────────────────────────
        ctk.CTkLabel(
            root,
            text="Método Simplex – Dos Fases",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, pady=(25, 15), sticky="n")

        # ── área principal con tabs ───────────────────────────────────────
        tabs = ctk.CTkTabview(root, corner_radius=10)
        tabs.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

        tabs.add("Fase I")
        tabs.add("Fase II")
        tabs.add("Resultado")
        tabs.add("Log completo")

        # configurar peso en cada tab
        for nombre in ("Fase I", "Fase II", "Resultado", "Log completo"):
            tabs.tab(nombre).columnconfigure(0, weight=1)
            tabs.tab(nombre).rowconfigure(0, weight=1)

        self._construir_tab_tablas(tabs.tab("Fase I"),  resultados.get('tablas_f1', []))
        self._construir_tab_tablas(tabs.tab("Fase II"), resultados.get('tablas_f2', []))
        self._construir_tab_resultado(tabs.tab("Resultado"), resultados)
        self._construir_tab_log(tabs.tab("Log completo"), resultados.get('texto', ''))

        # ── botón cerrar ─────────────────────────────────────────────────
        ctk.CTkButton(
            root,
            text="Cerrar",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=130,
            height=36,
            command=self.destroy,
        ).grid(row=2, column=0, pady=(0, 20))

    # ------------------------------------------------------------------ #
    #  TAB: TABLAS DE ITERACIONES                                         #
    # ------------------------------------------------------------------ #
    def _construir_tab_tablas(self, parent, tablas: list):
        """Muestra cada tabla (iteración) dentro de un frame scrollable."""
        if not tablas:
            ctk.CTkLabel(
                parent,
                text="Sin iteraciones registradas.",
                font=ctk.CTkFont(size=14),
                text_color="gray",
            ).grid(row=0, column=0, pady=30)
            return

        scroll = ctk.CTkScrollableFrame(parent, corner_radius=8)
        scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scroll.columnconfigure(0, weight=1)

        for idx, info in enumerate(tablas):
            # sub-frame por iteración
            bloque = ctk.CTkFrame(scroll, corner_radius=8)
            bloque.grid(row=idx, column=0, sticky="ew", padx=10, pady=(8, 4))
            bloque.columnconfigure(0, weight=1)

            # título de la iteración
            ctk.CTkLabel(
                bloque,
                text=info.get('titulo', f'Iteración {idx}'),
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
            ).grid(row=0, column=0, padx=12, pady=(10, 6), sticky="w")

            # tabla
            self._tabla_widget(bloque, info['cabeceras'], info['filas'], info['z_fila'], fila_inicio=1)

    def _tabla_widget(self, parent, cabeceras, filas, z_fila, fila_inicio=0):
        """Dibuja una tabla CTk con cabeceras, filas de restricciones y fila Z."""
        COL_W   = 72
        HEADER_H = 28
        CELL_H   = 28
        FONT_H  = ctk.CTkFont(size=12, weight="bold")
        FONT_C  = ctk.CTkFont(size=12)
        FONT_Z  = ctk.CTkFont(size=12, weight="bold")

        # ── cabeceras ────────────────────────────────────────────────────
        for j, cab in enumerate(cabeceras):
            color = "#1f6aa5" if cab != "SOL" else "#144870"
            ctk.CTkLabel(
                parent,
                text=cab,
                font=FONT_H,
                fg_color=color,
                text_color="white",
                corner_radius=4,
                width=COL_W,
                height=HEADER_H,
            ).grid(row=fila_inicio, column=j, padx=2, pady=2)

        # ── filas de restricciones ────────────────────────────────────────
        for i, fila in enumerate(filas):
            for j, val in enumerate(fila):
                ctk.CTkLabel(
                    parent,
                    text=val,
                    font=FONT_C,
                    fg_color=("gray85", "gray25"),
                    corner_radius=4,
                    width=COL_W,
                    height=CELL_H,
                ).grid(row=fila_inicio + 1 + i, column=j, padx=2, pady=2)

        # ── fila Z ───────────────────────────────────────────────────────
        fila_z_row = fila_inicio + 1 + len(filas)
        for j, val in enumerate(z_fila):
            ctk.CTkLabel(
                parent,
                text=val,
                font=FONT_Z,
                fg_color=("#2d6a9f", "#1a3f5c"),
                text_color="white",
                corner_radius=4,
                width=COL_W,
                height=CELL_H,
            ).grid(row=fila_z_row, column=j, padx=2, pady=(2, 10))

    # ------------------------------------------------------------------ #
    #  TAB: RESULTADO FINAL                                               #
    # ------------------------------------------------------------------ #
    def _construir_tab_resultado(self, parent, resultados: dict):
        scroll = ctk.CTkScrollableFrame(parent, corner_radius=8)
        scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scroll.columnconfigure(0, weight=1)

        if not resultados.get('factible', False):
            # mostrar error
            ctk.CTkLabel(
                scroll,
                text=f"❌  {resultados.get('error', 'Error desconocido')}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#e05252",
            ).grid(row=0, column=0, pady=40)
            return

        # ── card resultado ────────────────────────────────────────────────
        card = ctk.CTkFrame(scroll, corner_radius=10)
        card.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        card.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card,
            text="Resultado Óptimo",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(18, 12), padx=20, sticky="w")

        separador = ctk.CTkFrame(card, height=2, fg_color=("gray70", "gray35"))
        separador.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 12))

        # variables
        sol = resultados.get('solucion', {})
        for idx, (var, val) in enumerate(sol.items()):
            ctk.CTkLabel(
                card,
                text=f"  {var}",
                font=ctk.CTkFont(size=15, weight="bold"),
                anchor="w",
            ).grid(row=2 + idx, column=0, padx=20, pady=4, sticky="w")
            ctk.CTkLabel(
                card,
                text=f"= {val}",
                font=ctk.CTkFont(size=15),
                anchor="w",
            ).grid(row=2 + idx, column=1, padx=10, pady=4, sticky="w")

        # Z
        fila_z = 2 + len(sol)
        sep2 = ctk.CTkFrame(card, height=2, fg_color=("gray70", "gray35"))
        sep2.grid(row=fila_z, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        ctk.CTkLabel(
            card,
            text=f"  Z  ({resultados.get('z_tipo', '')})",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1f6aa5", "#5ba3d9"),
            anchor="w",
        ).grid(row=fila_z + 1, column=0, padx=20, pady=(0, 18), sticky="w")
        ctk.CTkLabel(
            card,
            text=f"= {resultados.get('z_valor', '')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1f6aa5", "#5ba3d9"),
            anchor="w",
        ).grid(row=fila_z + 1, column=1, padx=10, pady=(0, 18), sticky="w")

    # ------------------------------------------------------------------ #
    #  TAB: LOG COMPLETO                                                  #
    # ------------------------------------------------------------------ #
    def _construir_tab_log(self, parent, texto: str):
        txt = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none",
            corner_radius=8,
        )
        txt.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        txt.insert("0.0", texto)
        txt.configure(state="disabled")