import tkinter as tk
from tkinter import ttk, messagebox
import random
import heapq
import math

# --- CLASES DEL MODELO ---

class Nodo:
    """Clase que representa un nodo dentro del grafo."""

    def __init__(self, etiqueta, grid_x, grid_y):
        self.etiqueta = etiqueta  # Identificador único (ej: 1, 2, 3...)
        self.gx = grid_x
        self.gy = grid_y

    def __eq__(self, otro):
        if isinstance(otro, Nodo):
            return self.etiqueta == otro.etiqueta
        return False

    def __hash__(self):
        return hash(self.etiqueta)

    def __repr__(self):
        return f"Nodo({self.etiqueta})"


class Grafo:
    """Grafo Dirigido con pesos personalizables."""

    def __init__(self):
        self.nodos = {}  # {etiqueta: objeto_nodo}
        self.adyacencia = {}  # {nodo_origen: {nodo_destino: peso}}

    def agregar_nodo(self, etiqueta, grid_x, grid_y):
        if etiqueta not in self.nodos:
            nodo = Nodo(etiqueta, grid_x, grid_y)
            self.nodos[etiqueta] = nodo
            self.adyacencia[nodo] = {}
            return nodo
        return self.nodos[etiqueta]

    def agregar_arista_dirigida(self, etiqueta_u, etiqueta_v, peso=None):
        """Crea una arista dirigida (u -> v). Si no se da un peso, asigna uno aleatorio."""
        u = self.nodos[etiqueta_u]
        v = self.nodos[etiqueta_v]

        if peso is None:
            peso = random.randint(1, 9)

        self.adyacencia[u][v] = peso

    def actualizar_peso(self, etiqueta_u, etiqueta_v, nuevo_peso):
        """Actualiza el peso de una conexión existente."""
        u = self.nodos[etiqueta_u]
        v = self.nodos[etiqueta_v]
        if v in self.adyacencia[u]:
            self.adyacencia[u][v] = nuevo_peso

    def dijkstra(self, etiqueta_inicio, etiqueta_fin):
        """Algoritmo de Dijkstra para grafos dirigidos con pesos."""
        if etiqueta_inicio not in self.nodos or etiqueta_fin not in self.nodos:
            return [], float("inf")

        inicio = self.nodos[etiqueta_inicio]
        fin = self.nodos[etiqueta_fin]

        distancias = {nodo: float("inf") for nodo in self.adyacencia}
        predecesores = {nodo: None for nodo in self.adyacencia}
        distancias[inicio] = 0

        # Cola de prioridad: (distancia, etiqueta, nodo)
        pq = [(0, inicio.etiqueta, inicio)]

        while pq:
            dist_actual, _, nodo_actual = heapq.heappop(pq)

            if dist_actual > distancias[nodo_actual]:
                continue

            if nodo_actual == fin:
                break

            for vecino, peso in self.adyacencia[nodo_actual].items():
                nueva_dist = dist_actual + peso
                if nueva_dist < distancias[vecino]:
                    distancias[vecino] = nueva_dist
                    predecesores[vecino] = nodo_actual
                    heapq.heappush(pq, (nueva_dist, vecino.etiqueta, vecino))

        # Reconstrucción de la ruta
        camino = []
        actual = fin
        while actual is not None:
            camino.insert(0, actual)
            actual = predecesores[actual]

        if distancias[fin] == float("inf"):
            return [], float("inf")

        return camino, distancias[fin]


# --- INTERFAZ GRÁFICA (TKINTER) ---


class AplicacionDijkstra(tk.Tk):
    # Parámetros de la animación del camino
    ANIM_PASO_MS = 450      # Tiempo entre un nodo iluminado y el siguiente
    ANIM_FINAL_MS = 1600    # Tiempo que se muestra el camino completo resaltado
    ANIM_PAUSA_MS = 500     # Pausa antes de reiniciar el bucle
    COLOR_BASE_ARISTA = "#999999"
    COLOR_ARISTA_ILUMINADA = "#2b5cff"
    COLOR_NODO_ILUMINADO = "#a2d2ff"
    COLOR_NODO_ACTUAL = "#ff9f1c"
    COLOR_FINAL = "#ff2e93"          # Color llamativo del camino completo
    COLOR_FINAL_NODO = "#ffc2dd"

    def __init__(self):
        super().__init__()
        self.title("Algoritmo de Dijkstra - Grafo Dirigido N x M")
        self._ajustar_ventana()
        self._redibujo_pendiente = None

        self.filas = 0      # N
        self.columnas = 0   # M
        self.grafo = None
        self.nodo_inicio = None
        self.nodo_fin = None
        self.modo_clic = tk.StringVar(value="inicio")  # "inicio" | "fin" | "editar"
        self.camino_actual = []
        self.costo_actual = float("inf")
        self._anim_job = None   # id del after() pendiente
        self._anim_paso = 0     # cuántos nodos del camino se han iluminado

        self._crear_pantalla_inicial()

    def _ajustar_ventana(self, espacio=50):
        """Dimensiona la ventana al tamaño de la pantalla dejando `espacio` px por lado."""
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()
        ancho = max(600, ancho_pantalla - 2 * espacio)
        alto = max(400, alto_pantalla - 2 * espacio)
        self.geometry(f"{ancho}x{alto}+{espacio}+{espacio}")
        self.minsize(600, 400)

    def _on_canvas_resize(self, event):
        """Redibuja el grafo cada vez que el canvas cambia de tamaño (incluida la carga inicial)."""
        if self._redibujo_pendiente is not None:
            self.after_cancel(self._redibujo_pendiente)
        self._redibujo_pendiente = self.after(50, self._redibujo_diferido)

    def _redibujo_diferido(self):
        self._redibujo_pendiente = None
        if self.grafo is not None:
            self.redibujar_grafo()

    def _crear_pantalla_inicial(self):
        """Frame inicial para solicitar el tamaño N x M (filas x columnas)."""
        self.frame_inicio = ttk.Frame(self)
        self.frame_inicio.pack(expand=True)

        ttk.Label(
            self.frame_inicio,
            text="¿Cuánto va a medir la Grid (N x M)?",
            font=("Arial", 16),
        ).pack(pady=10)

        frame_campos = ttk.Frame(self.frame_inicio)
        frame_campos.pack(pady=10)

        # Filas (N)
        col_filas = ttk.Frame(frame_campos)
        col_filas.pack(side=tk.LEFT, padx=15)
        ttk.Label(col_filas, text="Filas (N)", font=("Arial", 11)).pack()
        self.ent_filas = ttk.Entry(
            col_filas, font=("Arial", 14), width=8, justify="center"
        )
        self.ent_filas.pack(pady=5)

        ttk.Label(frame_campos, text="x", font=("Arial", 16, "bold")).pack(
            side=tk.LEFT, pady=(20, 0)
        )

        # Columnas (M)
        col_cols = ttk.Frame(frame_campos)
        col_cols.pack(side=tk.LEFT, padx=15)
        ttk.Label(col_cols, text="Columnas (M)", font=("Arial", 11)).pack()
        self.ent_columnas = ttk.Entry(
            col_cols, font=("Arial", 14), width=8, justify="center"
        )
        self.ent_columnas.pack(pady=5)

        self.ent_filas.focus()

        # Enter genera el grafo desde cualquiera de los dos campos
        self.ent_filas.bind("<Return>", lambda e: self.ent_columnas.focus())
        self.ent_columnas.bind("<Return>", lambda e: self._inicializar_grafo())

        ttk.Button(
            self.frame_inicio, text="Generar Grafo", command=self._inicializar_grafo
        ).pack(pady=10)

    def _inicializar_grafo(self):
        try:
            filas = int(self.ent_filas.get())
            columnas = int(self.ent_columnas.get())
        except ValueError:
            messagebox.showerror("Error", "Ingresa números enteros válidos.")
            return

        if filas < 1 or columnas < 1:
            messagebox.showerror("Error", "Filas y columnas deben ser al menos 1.")
            return
        if filas * columnas < 2:
            messagebox.showerror("Error", "La grid debe tener al menos 2 nodos.")
            return

        self.filas = filas
        self.columnas = columnas

        self.frame_inicio.destroy()

        # Construir Grafo Dirigido N x M
        self.grafo = Grafo()
        for r in range(self.filas):
            for c in range(self.columnas):
                etiqueta = r * self.columnas + c + 1
                self.grafo.agregar_nodo(etiqueta, c, r)

        # Conexiones dirigidas en 4 direcciones con pesos aleatorios
        for r in range(self.filas):
            for c in range(self.columnas):
                curr = r * self.columnas + c + 1
                # Derecha
                if c + 1 < self.columnas:
                    self.grafo.agregar_arista_dirigida(
                        curr, r * self.columnas + (c + 1) + 1
                    )
                # Izquierda
                if c - 1 >= 0:
                    self.grafo.agregar_arista_dirigida(
                        curr, r * self.columnas + (c - 1) + 1
                    )
                # Abajo
                if r + 1 < self.filas:
                    self.grafo.agregar_arista_dirigida(
                        curr, (r + 1) * self.columnas + c + 1
                    )
                # Arriba
                if r - 1 >= 0:
                    self.grafo.agregar_arista_dirigida(
                        curr, (r - 1) * self.columnas + c + 1
                    )

        self._crear_interfaz_principal()

    def _crear_interfaz_principal(self):
        # Panel Derecho: Edición de pesos e información
        # (se empaqueta primero para que el canvas no lo desplace ni lo recorte)
        self.panel_control = ttk.Frame(self, width=300)
        self.panel_control.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Panel Izquierdo: Lienzo (Canvas) que ocupa todo el espacio restante
        self.canvas = tk.Canvas(self, bg="white", width=400, height=400)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        lbl_info = ttk.Label(
            self.panel_control, text="CONTROLES Y EDICIÓN", font=("Arial", 12, "bold")
        )
        lbl_info.pack(anchor="w", pady=5)

        instrucciones = (
            "• Elige un modo y haz clic en un nodo.\n"
            "  Inicio y Fin se pueden cambiar las\n"
            "  veces que quieras.\n\n"
            "• Modificar Pesos:\n"
            "  En modo \"Editar pesos\" selecciona un\n"
            "  nodo y cambia sus conexiones salientes."
        )
        ttk.Label(self.panel_control, text=instrucciones, font=("Arial", 9)).pack(
            anchor="w", pady=5
        )

        # Selector del modo de clic
        frame_modo = ttk.LabelFrame(self.panel_control, text="Al hacer clic en un nodo")
        frame_modo.pack(fill="x", pady=5)
        ttk.Radiobutton(
            frame_modo,
            text="Definir Inicio (verde)",
            variable=self.modo_clic,
            value="inicio",
        ).pack(anchor="w", padx=8, pady=2)
        ttk.Radiobutton(
            frame_modo,
            text="Definir Fin (rojo)",
            variable=self.modo_clic,
            value="fin",
        ).pack(anchor="w", padx=8, pady=2)
        ttk.Radiobutton(
            frame_modo,
            text="Editar pesos",
            variable=self.modo_clic,
            value="editar",
        ).pack(anchor="w", padx=8, pady=2)
        ttk.Button(
            frame_modo, text="Limpiar Inicio y Fin", command=self._limpiar_inicio_fin
        ).pack(fill="x", padx=8, pady=(6, 8))

        self.lbl_ruta = ttk.Label(
            self.panel_control,
            text="Ruta: Ninguna",
            font=("Arial", 10, "bold"),
            wraplength=280,
        )
        self.lbl_ruta.pack(anchor="w", pady=10)

        self.lbl_costo = ttk.Label(
            self.panel_control, text="Costo Total: -", font=("Arial", 10, "bold")
        )
        self.lbl_costo.pack(anchor="w", pady=5)

        # Separador para formulario de edición
        ttk.Separator(self.panel_control, orient="horizontal").pack(fill="x", pady=15)

        self.lbl_nodo_sel = ttk.Label(
            self.panel_control,
            text="Nodo Seleccionado: Ninguno",
            font=("Arial", 10, "bold"),
        )
        self.lbl_nodo_sel.pack(anchor="w", pady=5)

        self.frame_edicion = ttk.Frame(self.panel_control)
        self.frame_edicion.pack(fill="x", pady=5)

        self.redibujar_grafo()

    def _calcular_celdas(self, w, h, margin=50):
        """Tamaño de celda horizontal y vertical según filas (N) y columnas (M)."""
        cell_w = (w - 2 * margin) / max(1, self.columnas - 1)
        cell_h = (h - 2 * margin) / max(1, self.filas - 1)
        return margin, cell_w, cell_h

    def _recalcular_dijkstra(self):
        if self.nodo_inicio and self.nodo_fin:
            self.camino_actual, self.costo_actual = self.grafo.dijkstra(
                self.nodo_inicio.etiqueta, self.nodo_fin.etiqueta
            )
        else:
            self.camino_actual, self.costo_actual = [], float("inf")

    def redibujar_grafo(self):
        self._detener_animacion()
        self.canvas.delete("all")
        self._recalcular_dijkstra()

        # Dimensiones y escalado
        # Antes de mostrarse, Tk reporta 1 px; en ese caso se usa el tamaño solicitado
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            w = self.canvas.winfo_reqwidth()
            h = self.canvas.winfo_reqheight()
        margin, cell_w, cell_h = self._calcular_celdas(w, h)

        # Mapear coordenadas de los nodos
        coords = {}
        for nodo in self.grafo.nodos.values():
            x = margin + nodo.gx * cell_w
            y = margin + nodo.gy * cell_h
            coords[nodo.etiqueta] = (x, y)

        # Aristas del camino óptimo (para identificarlas con una etiqueta y animarlas)
        aristas_camino = {
            (self.camino_actual[i].etiqueta, self.camino_actual[i + 1].etiqueta)
            for i in range(len(self.camino_actual) - 1)
        }

        radio = 18  # Radio de los nodos
        desplazamiento = 6  # Separación entre flechas de sentidos opuestos
        # Distancia a recortar en cada extremo para que la flecha termine
        # en el borde del nodo (y no quede oculta debajo del círculo)
        recorte = math.sqrt(radio**2 - desplazamiento**2) + 2

        # 1. Dibujar Aristas Dirigidas
        for u, vecinos in self.grafo.adyacencia.items():
            x1, y1 = coords[u.etiqueta]
            for v, peso in vecinos.items():
                x2, y2 = coords[v.etiqueta]

                # Las aristas del camino se etiquetan para iluminarlas después
                tag_arista = (
                    f"arista_{u.etiqueta}_{v.etiqueta}"
                    if (u.etiqueta, v.etiqueta) in aristas_camino
                    else ""
                )

                # Desplazar ligeramente líneas paralelas opuestas para que no se traslapen
                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy)
                if dist <= 2 * recorte:
                    continue
                ux, uy = dx / dist, dy / dist  # Vector unitario u -> v
                nx, ny = -uy * desplazamiento, ux * desplazamiento

                # Extremos recortados al borde de cada nodo
                sx, sy = x1 + nx + ux * recorte, y1 + ny + uy * recorte
                ex, ey = x2 + nx - ux * recorte, y2 + ny - uy * recorte

                # Dibujar flecha dirigida (punta en el nodo destino)
                self.canvas.create_line(
                    sx,
                    sy,
                    ex,
                    ey,
                    arrow=tk.LAST,
                    arrowshape=(12, 14, 5),
                    fill=self.COLOR_BASE_ARISTA,
                    width=1,
                    tags=(tag_arista,) if tag_arista else (),
                )

                # Etiqueta con el Peso
                mx, my = (sx + ex) / 2, (sy + ey) / 2
                self.canvas.create_rectangle(
                    mx - 8, my - 8, mx + 8, my + 8, fill="white", outline=""
                )
                self.canvas.create_text(
                    mx, my, text=str(peso), font=("Arial", 8), fill="#333333"
                )

        # 2. Dibujar Nodos
        for nodo in self.grafo.nodos.values():
            x, y = coords[nodo.etiqueta]

            color = "#e0e0e0"  # Normal
            if nodo == self.nodo_inicio:
                color = "#2ecc71"  # Inicio (Verde)
            elif nodo == self.nodo_fin:
                color = "#e74c3c"  # Fin (Rojo)

            self.canvas.create_oval(
                x - radio,
                y - radio,
                x + radio,
                y + radio,
                fill=color,
                outline="black",
                width=2,
                tags=(f"nodo_{nodo.etiqueta}",),
            )
            self.canvas.create_text(
                x, y, text=str(nodo.etiqueta), font=("Arial", 10, "bold")
            )

        # Actualizar textos de resultado
        if self.camino_actual:
            ruta_str = " -> ".join([str(n.etiqueta) for n in self.camino_actual])
            self.lbl_ruta.config(text=f"Ruta: {ruta_str}")
            self.lbl_costo.config(text=f"Costo Total: {self.costo_actual}")
        else:
            self.lbl_ruta.config(text="Ruta: No encontrada / No seleccionada")
            self.lbl_costo.config(text="Costo Total: -")

        self._iniciar_animacion()

    # --- ANIMACIÓN DEL CAMINO ---

    def _detener_animacion(self):
        if self._anim_job is not None:
            self.after_cancel(self._anim_job)
            self._anim_job = None

    def _iniciar_animacion(self):
        """Arranca el bucle de animación si hay un camino con al menos una arista."""
        self._detener_animacion()
        self._anim_paso = 0
        if len(self.camino_actual) >= 2:
            self._anim_job = self.after(self.ANIM_PAUSA_MS, self._animar_tick)

    def _animar_tick(self):
        """Un paso del bucle: ilumina nodo a nodo, resalta el camino completo y reinicia."""
        self._anim_job = None
        camino = self.camino_actual
        n = len(camino)
        if n < 2:
            return

        if self._anim_paso < n:
            self._iluminar_nodo(self._anim_paso)
            self._anim_paso += 1
            espera = self.ANIM_PASO_MS
        elif self._anim_paso == n:
            self._resaltar_camino_completo()
            self._anim_paso += 1
            espera = self.ANIM_FINAL_MS
        else:
            self._limpiar_iluminacion()
            self._anim_paso = 0
            espera = self.ANIM_PAUSA_MS

        self._anim_job = self.after(espera, self._animar_tick)

    def _iluminar_nodo(self, k):
        """Ilumina el nodo k del camino y la arista que llega hasta él."""
        camino = self.camino_actual
        if k == 0:
            self._limpiar_iluminacion()
        else:
            previo = camino[k - 1]
            self.canvas.itemconfig(f"arista_{previo.etiqueta}_{camino[k].etiqueta}",
                                   fill=self.COLOR_ARISTA_ILUMINADA, width=3)
            # El nodo anterior queda iluminado (azul claro) y deja de ser el "actual"
            self._pintar_nodo(previo, actual=False)
        self._pintar_nodo(camino[k], actual=True)

    def _pintar_nodo(self, nodo, actual):
        tag = f"nodo_{nodo.etiqueta}"
        if actual:
            self.canvas.itemconfig(tag, outline=self.COLOR_NODO_ACTUAL, width=4)
        else:
            self.canvas.itemconfig(tag, outline="black", width=2)
        # Inicio y Fin conservan su color; el resto se ilumina al ser recorrido
        if nodo != self.nodo_inicio and nodo != self.nodo_fin:
            self.canvas.itemconfig(tag, fill=self.COLOR_NODO_ILUMINADO)

    def _resaltar_camino_completo(self):
        """Pinta todo el camino con un color llamativo al llegar al final."""
        camino = self.camino_actual
        for i in range(len(camino) - 1):
            self.canvas.itemconfig(
                f"arista_{camino[i].etiqueta}_{camino[i + 1].etiqueta}",
                fill=self.COLOR_FINAL,
                width=5,
            )
        for nodo in camino:
            tag = f"nodo_{nodo.etiqueta}"
            self.canvas.itemconfig(tag, outline=self.COLOR_FINAL, width=4)
            if nodo != self.nodo_inicio and nodo != self.nodo_fin:
                self.canvas.itemconfig(tag, fill=self.COLOR_FINAL_NODO)

    def _limpiar_iluminacion(self):
        """Devuelve el camino a su aspecto neutro para reiniciar la animación."""
        camino = self.camino_actual
        for i in range(len(camino) - 1):
            self.canvas.itemconfig(
                f"arista_{camino[i].etiqueta}_{camino[i + 1].etiqueta}",
                fill=self.COLOR_BASE_ARISTA,
                width=1,
            )
        for nodo in camino:
            tag = f"nodo_{nodo.etiqueta}"
            self.canvas.itemconfig(tag, outline="black", width=2)
            if nodo != self.nodo_inicio and nodo != self.nodo_fin:
                self.canvas.itemconfig(tag, fill="#e0e0e0")

    def _definir_inicio(self, nodo):
        """Establece el nodo de inicio. Si coincide con el fin, se intercambian."""
        if nodo == self.nodo_fin:
            self.nodo_fin = self.nodo_inicio
        self.nodo_inicio = nodo
        self._avanzar_modo()

    def _definir_fin(self, nodo):
        """Establece el nodo de fin. Si coincide con el inicio, se intercambian."""
        if nodo == self.nodo_inicio:
            self.nodo_inicio = self.nodo_fin
        self.nodo_fin = nodo
        self._avanzar_modo()

    def _avanzar_modo(self):
        """Pasa a pedir lo que falte; si ya están ambos, cambia a editar pesos."""
        if self.nodo_inicio is None:
            self.modo_clic.set("inicio")
        elif self.nodo_fin is None:
            self.modo_clic.set("fin")
        else:
            self.modo_clic.set("editar")

    def _limpiar_inicio_fin(self):
        """Quita el inicio y el fin para volver a elegirlos."""
        self.nodo_inicio = None
        self.nodo_fin = None
        self.modo_clic.set("inicio")
        self.redibujar_grafo()

    def _on_canvas_click(self, event):
        """Detecta qué nodo se presionó con el cursor."""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        margin, cell_w, cell_h = self._calcular_celdas(w, h)

        nodo_cliqueado = None
        for nodo in self.grafo.nodos.values():
            nx = margin + nodo.gx * cell_w
            ny = margin + nodo.gy * cell_h
            if (event.x - nx) ** 2 + (event.y - ny) ** 2 <= 18**2:
                nodo_cliqueado = nodo
                break

        if not nodo_cliqueado:
            return

        # Lógica de selección de Inicio/Fin según el modo activo
        modo = self.modo_clic.get()
        if modo == "inicio":
            self._definir_inicio(nodo_cliqueado)
        elif modo == "fin":
            self._definir_fin(nodo_cliqueado)

        # Cargar panel de edición para el nodo cliqueado
        self._mostrar_editor_nodo(nodo_cliqueado)
        self.redibujar_grafo()

    def _mostrar_editor_nodo(self, nodo):
        """Genera campos dinámicos para editar las aristas salientes del nodo."""
        for widget in self.frame_edicion.winfo_children():
            widget.destroy()

        self.lbl_nodo_sel.config(text=f"Nodo Seleccionado: {nodo.etiqueta}")

        vecinos = self.grafo.adyacencia[nodo]
        if not vecinos:
            ttk.Label(
                self.frame_edicion, text="Este nodo no tiene conexiones salientes."
            ).pack()
            return

        entries = {}
        for vecino, peso in vecinos.items():
            f = ttk.Frame(self.frame_edicion)
            f.pack(fill="x", pady=2)
            ttk.Label(f, text=f"Hacia Nodo {vecino.etiqueta}:", width=15).pack(
                side=tk.LEFT
            )
            ent = ttk.Entry(f, width=8)
            ent.insert(0, str(peso))
            ent.pack(side=tk.LEFT, padx=5)
            entries[vecino.etiqueta] = ent

        def guardar_cambios():
            for v_etiqueta, entry_widget in entries.items():
                try:
                    nuevo_peso = int(entry_widget.get())
                    if nuevo_peso < 0:
                        raise ValueError()
                    self.grafo.actualizar_peso(nodo.etiqueta, v_etiqueta, nuevo_peso)
                except ValueError:
                    messagebox.showerror(
                        "Error",
                        f"El peso para el nodo {v_etiqueta} debe ser un número entero positivo.",
                    )
                    return
            # Recalcular automáticamente tras guardar
            self.redibujar_grafo()

        btn_guardar = ttk.Button(
            self.frame_edicion, text="Actualizar Pesos", command=guardar_cambios
        )
        btn_guardar.pack(pady=10)


if __name__ == "__main__":
    app = AplicacionDijkstra()
    app.mainloop()