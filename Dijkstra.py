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
    def __init__(self):
        super().__init__()
        self.title("Algoritmo de Dijkstra - Grafo Dirigido N x N")
        self.geometry("1100x700")  # Corregido aquí

        self.n = 0
        self.grafo = None
        self.nodo_inicio = None
        self.nodo_fin = None
        self.camino_actual = []
        self.costo_actual = float("inf")

        self._crear_pantalla_inicial()

    def _crear_pantalla_inicial(self):
        """Frame inicial para solicitar el tamaño N x N."""
        self.frame_inicio = ttk.Frame(self)
        self.frame_inicio.pack(expand=True)

        lbl = ttk.Label(
            self.frame_inicio,
            text="¿Cuánto va a medir la Grid (N x N)?",
            font=("Arial", 16),
        )
        lbl.pack(pady=10)

        self.ent_n = ttk.Entry(
            self.frame_inicio, font=("Arial", 14), width=10, justify="center"
        )
        self.ent_n.pack(pady=10)
        self.ent_n.focus()

        btn = ttk.Button(
            self.frame_inicio, text="Generar Grafo", command=self._inicializar_grafo
        )
        btn.pack(pady=10)

    def _inicializar_grafo(self):
        try:
            val = int(self.ent_n.get())
            if val < 2:
                messagebox.showerror("Error", "El tamaño debe ser al menos 2x2.")
                return
            self.n = val
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número entero válido.")
            return

        self.frame_inicio.destroy()

        # Construir Grafo Dirigido N x N
        self.grafo = Grafo()
        for r in range(self.n):
            for c in range(self.n):
                etiqueta = r * self.n + c + 1
                self.grafo.agregar_nodo(etiqueta, c, r)

        # Conexiones dirigidas en 4 direcciones con pesos aleatorios
        for r in range(self.n):
            for c in range(self.n):
                curr = r * self.n + c + 1
                # Derecha
                if c + 1 < self.n:
                    self.grafo.agregar_arista_dirigida(curr, r * self.n + (c + 1) + 1)
                # Izquierda
                if c - 1 >= 0:
                    self.grafo.agregar_arista_dirigida(curr, r * self.n + (c - 1) + 1)
                # Abajo
                if r + 1 < self.n:
                    self.grafo.agregar_arista_dirigida(curr, (r + 1) * self.n + c + 1)
                # Arriba
                if r - 1 >= 0:
                    self.grafo.agregar_arista_dirigida(curr, (r - 1) * self.n + c + 1)

        self._crear_interfaz_principal()

    def _crear_interfaz_principal(self):
        # Panel Izquierdo: Lienzo (Canvas)
        self.canvas = tk.Canvas(self, bg="white", width=750, height=680)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        # Panel Derecho: Edición de pesos e información
        self.panel_control = ttk.Frame(self, width=300)
        self.panel_control.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        lbl_info = ttk.Label(
            self.panel_control, text="CONTROLES Y EDICIÓN", font=("Arial", 12, "bold")
        )
        lbl_info.pack(anchor="w", pady=5)

        instrucciones = (
            "• Clic en Nodo:\n"
            "  1° Clic: Inicio (Verde)\n"
            "  2° Clic: Fin (Rojo)\n"
            "  Siguientes: Seleccionar para editar pesos\n\n"
            "• Modificar Pesos:\n"
            "  Selecciona un nodo y cambia\n"
            "  los pesos de sus conexiones salientes."
        )
        ttk.Label(self.panel_control, text=instrucciones, font=("Arial", 9)).pack(
            anchor="w", pady=5
        )

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

    def _recalcular_dijkstra(self):
        if self.nodo_inicio and self.nodo_fin:
            self.camino_actual, self.costo_actual = self.grafo.dijkstra(
                self.nodo_inicio.etiqueta, self.nodo_fin.etiqueta
            )
        else:
            self.camino_actual, self.costo_actual = [], float("inf")

    def redibujar_grafo(self):
        self.canvas.delete("all")
        self._recalcular_dijkstra()

        # Dimensiones y escalado
        w = self.canvas.winfo_width() or 750
        h = self.canvas.winfo_height() or 680
        margin = 50
        cell_w = (w - 2 * margin) / max(1, self.n - 1)
        cell_h = (h - 2 * margin) / max(1, self.n - 1)

        # Mapear coordenadas de los nodos
        coords = {}
        for nodo in self.grafo.nodos.values():
            x = margin + nodo.gx * cell_w
            y = margin + nodo.gy * cell_h
            coords[nodo.etiqueta] = (x, y)

        conjunto_camino = set(self.camino_actual)

        # 1. Dibujar Aristas Dirigidas
        for u, vecinos in self.grafo.adyacencia.items():
            x1, y1 = coords[u.etiqueta]
            for v, peso in vecinos.items():
                x2, y2 = coords[v.etiqueta]

                # Comprobar si la arista forma parte de la ruta óptima
                es_del_camino = False
                for i in range(len(self.camino_actual) - 1):
                    if self.camino_actual[i] == u and self.camino_actual[i + 1] == v:
                        es_del_camino = True
                        break

                color = "#2b5cff" if es_del_camino else "#cccccc"
                grosor = 3 if es_del_camino else 1

                # Desplazar ligeramente líneas paralelas opuestas para que no se traslapen
                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy)
                if dist == 0:
                    continue
                nx, ny = -dy / dist * 6, dx / dist * 6

                sx, sy = x1 + nx, y1 + ny
                ex, ey = x2 + nx, y2 + ny

                # Dibujar flecha dirigida
                self.canvas.create_line(
                    sx,
                    sy,
                    ex,
                    ey,
                    arrow=tk.LAST,
                    arrowshape=(8, 10, 3),
                    fill=color,
                    width=grosor,
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
        radio = 18
        for nodo in self.grafo.nodos.values():
            x, y = coords[nodo.etiqueta]

            color = "#e0e0e0"  # Normal
            if nodo == self.nodo_inicio:
                color = "#2ecc71"  # Inicio (Verde)
            elif nodo == self.nodo_fin:
                color = "#e74c3c"  # Fin (Rojo)
            elif nodo in conjunto_camino:
                color = "#a2d2ff"  # En camino (Azul claro)

            self.canvas.create_oval(
                x - radio,
                y - radio,
                x + radio,
                y + radio,
                fill=color,
                outline="black",
                width=2,
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

    def _on_canvas_click(self, event):
        """Detecta qué nodo se presionó con el cursor."""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        margin = 50
        cell_w = (w - 2 * margin) / max(1, self.n - 1)
        cell_h = (h - 2 * margin) / max(1, self.n - 1)

        nodo_cliqueado = None
        for nodo in self.grafo.nodos.values():
            nx = margin + nodo.gx * cell_w
            ny = margin + nodo.gy * cell_h
            if (event.x - nx) ** 2 + (event.y - ny) ** 2 <= 18**2:
                nodo_cliqueado = nodo
                break

        if not nodo_cliqueado:
            return

        # Lógica de selección de Inicio/Fin
        if not self.nodo_inicio:
            self.nodo_inicio = nodo_cliqueado
        elif not self.nodo_fin and nodo_cliqueado != self.nodo_inicio:
            self.nodo_fin = nodo_cliqueado

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
