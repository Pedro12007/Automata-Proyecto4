import tkinter as tk

BG          = "#0b0b0e"   # fondo general
PANEL_BG    = "#141419"   # fondo de tarjetas/paneles
PANEL_BG_2  = "#17171d"   # fondo secundario (teclado, listas)
BORDER      = "#2a1a1f"   # borde sutil de tarjetas
LINE_DIM    = "#3a1c22"   # línea divisoria bajo títulos

RED         = "#e63950"   # rojo de acento principal
RED_DARK    = "#c62339"   # rojo oscuro (bordes / hover)
RED_DIM     = "#3a1620"   # rojo muy oscuro (relleno tenue)

GREEN       = "#33c37f"   # verde de éxito
GREEN_DIM   = "#12291f"   # relleno verde oscuro

TEXT        = "#f4f4f6"   # texto principal
SUBTEXT     = "#8d8d97"   # texto secundario / gris
FAINT       = "#5c5c66"   # texto tenue (listas)
GRAY_LINE   = "#6f6f79"   # líneas de aristas / bordes de nodos no activos

KEY_BG      = "#1d1d24"   # fondo de tecla
KEY_BORDER  = "#33333d"   # borde de tecla
KEY_HOVER   = "#26262f"

LCD_BG      = "#050506"   # pantalla LCD de la caja fuerte

FONT_UI      = "Segoe UI"
FONT_MONO    = "Consolas"

def rounded_rect(canvas, x1, y1, x2, y2, r=14, **kwargs):
    points = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

def measure(parent, text, font):
    tmp = tk.Label(parent, text=text, font=font)
    tmp.update_idletasks()
    w, h = tmp.winfo_reqwidth(), tmp.winfo_reqheight()
    tmp.destroy()
    return w, h


def rounded_badge(parent, text, fg, border_color, fill, font=None,
                   padx=16, pady=8, radius=14, dot=None):
    font = font or (FONT_UI, 10, "bold")
    dot_w = 16 if dot else 0
    tw, th = measure(parent, text, font)
    w = tw + padx * 2 + dot_w
    h = th + pady * 2
    c = tk.Canvas(parent, width=w, height=h, bg=parent["bg"], highlightthickness=0)
    rounded_rect(c, 1, 1, w - 1, h - 1, radius, outline=border_color, width=1.4, fill=fill)
    tx = w / 2 + dot_w / 2
    if dot:
        c.create_oval(padx - 4, h / 2 - 4, padx + 4, h / 2 + 4, fill=dot, outline="")
    c.create_text(tx, h / 2, text=text, fill=fg, font=font)
    return c

def section_header(parent, icon, title, icon_color=RED):
    row = tk.Frame(parent, bg=parent["bg"])
    tk.Label(row, text=icon, font=(FONT_UI, 12, "bold"), bg=parent["bg"],
              fg=icon_color).pack(side="left")
    tk.Label(row, text=title, font=(FONT_UI, 11, "bold"), bg=parent["bg"],
              fg=TEXT).pack(side="left", padx=(8, 0))
    return row

def make_panel(parent, title, icon="◆", icon_color=RED, pad=(15, 12, 15, 12)):
    outer = tk.Frame(parent, bg=PANEL_BG, highlightbackground=BORDER,
                      highlightthickness=1, bd=0)
    header = tk.Frame(outer, bg=PANEL_BG)
    header.pack(side="top", fill="x", padx=pad[0], pady=(pad[1], 8))
    section_header(header, icon, title, icon_color).pack(side="left")

    line = tk.Frame(outer, bg=LINE_DIM, height=1)
    line.pack(side="top", fill="x", padx=pad[0])

    content = tk.Frame(outer, bg=PANEL_BG)
    content.pack(side="top", fill="both", expand=True, padx=pad[2], pady=(10, pad[3]))
    return outer, content


def flat_button(parent, text, bg, fg, hover_bg=None, font=None, height=42,
                 border=None, anchor="center"):
    font = font or (FONT_UI, 11, "bold")
    hover_bg = hover_bg or bg
    btn = tk.Label(parent, text=text, bg=bg, fg=fg, font=font, height=1,
                    cursor="hand2", anchor=anchor, padx=16)
    btn.configure(height=1)
    frame = tk.Frame(parent, bg=bg, height=height, highlightthickness=1,
                      highlightbackground=(border or bg))
    frame.pack_propagate(False)
    lbl = tk.Label(frame, text=text, bg=bg, fg=fg, font=font, anchor="w",
                    padx=16, cursor="hand2")
    lbl.pack(fill="both", expand=True)
    btn.destroy()

    def on_enter(_):
        frame.configure(bg=hover_bg)
        lbl.configure(bg=hover_bg)

    def on_leave(_):
        frame.configure(bg=bg)
        lbl.configure(bg=bg)

    frame.bind("<Enter>", on_enter)
    lbl.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)
    lbl.bind("<Leave>", on_leave)
    return frame, lbl

class SafeSimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Caja Fuerte - AFND")
        self.configure(bg=BG)
        self.geometry("1600x900+60+30")
        self.minsize(1280, 760)

        try:
            self.overrideredirect(True)
        except tk.TclError:
            pass

        self._build_titlebar()
        self._build_body()
        self._make_draggable(self.titlebar)

    def _build_titlebar(self):
        self.titlebar = tk.Frame(self, bg=BG, height=70)
        self.titlebar.pack(side="top", fill="x")
        self.titlebar.pack_propagate(False)

        left = tk.Frame(self.titlebar, bg=BG)
        left.pack(side="left", padx=22)

        shield = tk.Canvas(left, width=44, height=44, bg=BG, highlightthickness=0)
        rounded_rect(shield, 2, 2, 42, 42, 10, fill=RED, outline="")
        shield.create_arc(15, 12, 29, 26, start=0, extent=180, style="arc",
                           outline="white", width=2.4)
        shield.create_rectangle(13, 20, 31, 32, fill="white", outline="")
        shield.pack(side="left", pady=13)

        title_frame = tk.Frame(left, bg=BG)
        title_frame.pack(side="left", padx=12)
        tk.Label(title_frame, text="SIMULADOR DE CAJA FUERTE",
                  font=(FONT_UI, 16, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(10, 0))
        tk.Label(title_frame, text="AUTÓMATA FINITO NO DETERMINISTA (AFND)",
                  font=(FONT_UI, 9), bg=BG, fg=SUBTEXT).pack(anchor="w")

        right = tk.Frame(self.titlebar, bg=BG)
        right.pack(side="right", padx=18)

        def win_btn(sym, cmd, hover=KEY_HOVER, danger=False):
            b = tk.Label(right, text=sym, font=(FONT_UI, 12), bg=BG,
                          fg=(RED if danger else SUBTEXT), width=3, cursor="hand2")
            b.pack(side="left")
            b.bind("<Button-1>", lambda e: cmd())
            b.bind("<Enter>", lambda e: b.configure(bg=hover))
            b.bind("<Leave>", lambda e: b.configure(bg=BG))
            return b

        win_btn("\u2715", self.destroy, danger=True)
        win_btn("\u25A1", self._toggle_maximize)
        win_btn("\u2014", self._minimize)

        sep = tk.Frame(self, bg=RED, height=2)
        sep.pack(side="top", fill="x")

    def _make_draggable(self, widget):
        state = {"x": 0, "y": 0}

        def start(e):
            state["x"], state["y"] = e.x, e.y

        def move(e):
            x = self.winfo_x() + (e.x - state["x"])
            y = self.winfo_y() + (e.y - state["y"])
            self.geometry(f"+{x}+{y}")

        for w in (widget,):
            w.bind("<ButtonPress-1>", start)
            w.bind("<B1-Motion>", move)

    def _minimize(self):
        try:
            self.overrideredirect(False)
            self.iconify()
            self.bind("<Map>", lambda e: self.overrideredirect(True))
        except tk.TclError:
            pass

    def _toggle_maximize(self):
        # Solo decorativo: alterna entre dos tamaños de ventana
        if getattr(self, "_maximized", False):
            self.geometry("1600x900+60+30")
            self._maximized = False
        else:
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            self.geometry(f"{w}x{h}+0+0")
            self._maximized = True

    def _build_body(self):
        body = tk.Frame(self, bg=BG)
        body.pack(side="top", fill="both", expand=True, padx=16, pady=16)

        body.columnconfigure(0, weight=0, minsize=310)
        body.columnconfigure(1, weight=1)
        body.columnconfigure(2, weight=0, minsize=300)
        body.rowconfigure(0, weight=1)

        self._build_left_column(body)
        self._build_center_column(body)
        self._build_right_column(body)

    def _build_left_column(self, parent):
        col = tk.Frame(parent, bg=BG)
        col.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        safe_panel, safe_content = make_panel(col, "CAJA FUERTE", icon="\u25A3")
        safe_panel.pack(side="top", fill="x", pady=(0, 12))
        self._draw_safe_display(safe_content)

        keypad_panel, keypad_content = make_panel(col, "TECLADO DE SEGURIDAD", icon="\u2328")
        keypad_panel.pack(side="top", fill="x", pady=(0, 14))
        self._build_keypad(keypad_content)

        actions = tk.Frame(col, bg=BG)
        actions.pack(side="top", fill="x")

        f, _ = flat_button(actions, "\u25B6   Procesar", bg=RED, fg="white",
                            hover_bg=RED_DARK, height=40)
        f.pack(fill="x", pady=(0, 8))

        f, _ = flat_button(actions, "\u23ED   Avanzar paso a paso", bg=PANEL_BG,
                            fg=TEXT, hover_bg=KEY_HOVER, height=38, border=BORDER)
        f.pack(fill="x", pady=(0, 8))

        f, _ = flat_button(actions, "\u21BA   Reiniciar", bg=PANEL_BG, fg=TEXT,
                            hover_bg=KEY_HOVER, height=38, border=BORDER)
        f.pack(fill="x", pady=(0, 8))

        f, _ = flat_button(actions, "\u21A9   Salir", bg=PANEL_BG, fg=SUBTEXT,
                            hover_bg=KEY_HOVER, height=38, border=BORDER)
        f.pack(fill="x")
        f.children[list(f.children.keys())[0]].bind("<Button-1>", lambda e: self.destroy())
        f.bind("<Button-1>", lambda e: self.destroy())

    def _draw_safe_display(self, parent):
        w, h = 268, 128
        c = tk.Canvas(parent, width=w, height=h, bg=PANEL_BG, highlightthickness=0)
        c.pack()

        rounded_rect(c, 2, 2, w - 2, h - 2, 14, fill="#1a1a20", outline=KEY_BORDER)

        for cx, cy in [(16, 16), (w - 16, 16), (16, h - 16), (w - 16, h - 16)]:
            c.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill="#0e0e12", outline="#3a3a44")

        rounded_rect(c, 22, 24, w - 22, h - 40, 8, fill=LCD_BG, outline="#26262e")
        dots_y = 24 + (h - 40 - 24) / 2 - 6
        for i in range(4):
            cx = w / 2 - 45 + i * 30
            c.create_oval(cx - 5, dots_y - 5, cx + 5, dots_y + 5, fill=RED, outline="")
        c.create_text(w / 2, h - 54, text="Esperando clave...", fill=SUBTEXT,
                       font=(FONT_MONO, 9))

    def _build_keypad(self, parent):
        ind = tk.Frame(parent, bg=PANEL_BG)
        ind.pack(anchor="w", pady=(0, 8))
        colors = [RED, "#3a3a44", "#3a3a44"]
        for col_i, color in enumerate(colors):
            dot = tk.Canvas(ind, width=16, height=16, bg=PANEL_BG, highlightthickness=0)
            dot.create_oval(2, 2, 14, 14, fill=color, outline="")
            dot.grid(row=0, column=col_i, padx=4)

        grid = tk.Frame(parent, bg=PANEL_BG)
        grid.pack(fill="x")
        keys = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["A", "0", "B"],
        ]
        for r, row in enumerate(keys):
            for cc, k in enumerate(row):
                self._key_button(grid, k).grid(row=r, column=cc, padx=3, pady=3, sticky="nsew")
        for i in range(3):
            grid.columnconfigure(i, weight=1)

        bottom = tk.Frame(parent, bg=PANEL_BG)
        bottom.pack(fill="x", pady=(5, 0))
        self._key_button(bottom, "\u25A3 LOCK", small=True).pack(
            side="left", expand=True, fill="both", padx=(0, 4))
        self._key_button(bottom, "CLEAR", small=True).pack(
            side="left", expand=True, fill="both", padx=4)
        self._key_button(bottom, "ENTER", small=True, accent=True).pack(
            side="left", expand=True, fill="both", padx=(4, 0))

    def _key_button(self, parent, text, small=False, accent=False):
        bg = RED_DIM if accent else KEY_BG
        fg = RED if accent else TEXT
        f = tk.Frame(parent, bg=bg, height=44 if not small else 34,
                      highlightthickness=1, highlightbackground=KEY_BORDER)
        f.pack_propagate(False)
        lbl = tk.Label(f, text=text, bg=bg, fg=fg, cursor="hand2",
                        font=(FONT_UI, 9 if small else 12, "bold"), justify="center")
        lbl.pack(fill="both", expand=True)

        def enter(_):
            f.configure(bg=KEY_HOVER if not accent else RED_DARK)
            lbl.configure(bg=KEY_HOVER if not accent else RED_DARK)

        def leave(_):
            f.configure(bg=bg)
            lbl.configure(bg=bg)

        f.bind("<Enter>", enter); lbl.bind("<Enter>", enter)
        f.bind("<Leave>", leave); lbl.bind("<Leave>", leave)
        return f

    def _build_center_column(self, parent):
        col = tk.Frame(parent, bg=BG)
        col.grid(row=0, column=1, sticky="nsew", padx=(0, 14))
        col.rowconfigure(1, weight=1)
        col.columnconfigure(0, weight=1)

        panel = tk.Frame(col, bg=PANEL_BG, highlightbackground=BORDER, highlightthickness=1)
        panel.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        panel.rowconfigure(2, weight=1)
        panel.columnconfigure(0, weight=1)

        header = tk.Frame(panel, bg=PANEL_BG)
        header.pack(side="top", fill="x", padx=18, pady=(14, 10))
        section_header(header, "\u2B21", "AUTÓMATA FINITO NO DETERMINISTA").pack(side="left")

        line = tk.Frame(panel, bg=LINE_DIM, height=1)
        line.pack(side="top", fill="x", padx=18)

        info = tk.Frame(panel, bg=PANEL_BG)
        info.pack(side="top", fill="x", padx=18, pady=12)

        def stat(lbl, val):
            f = tk.Frame(info, bg=PANEL_BG)
            tk.Label(f, text=lbl, font=(FONT_UI, 9), bg=PANEL_BG, fg=SUBTEXT).pack(anchor="w")
            tk.Label(f, text=val, font=(FONT_UI, 15, "bold"), bg=PANEL_BG, fg=TEXT).pack(anchor="w")
            return f

        stat("Estado actual:", "q0").pack(side="left", padx=(0, 40))
        stat("Símbolo actual:", "\u2014").pack(side="left")

        badge = rounded_badge(info, "Esperando entrada", fg=RED, border_color=RED,
                               fill=RED_DIM, dot=RED)
        badge.pack(side="right", pady=6)

        graph_wrap = tk.Frame(panel, bg=PANEL_BG)
        graph_wrap.pack(side="top", fill="both", expand=True, padx=18, pady=(0, 16))

        self.graph_canvas = tk.Canvas(graph_wrap, bg=PANEL_BG, highlightthickness=0)
        self.graph_canvas.pack(fill="both", expand=True)
        self.graph_canvas.bind("<Configure>", self._redraw_graph)

        bottom = tk.Frame(col, bg=BG)
        bottom.grid(row=1, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=3)
        bottom.columnconfigure(1, weight=2)

        result_wrap = tk.Frame(bottom, bg=BG)
        result_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self._build_result_bar(result_wrap)

        valid_panel, valid_content = make_panel(bottom, "Validación", icon="\u2714",
                                                 pad=(14, 12, 14, 12))
        valid_panel.grid(row=0, column=1, sticky="nsew")
        row1 = tk.Frame(valid_content, bg=PANEL_BG)
        row1.pack(anchor="w", pady=(0, 8))
        dot = tk.Canvas(row1, width=10, height=10, bg=PANEL_BG, highlightthickness=0)
        dot.create_oval(0, 0, 10, 10, fill=GREEN, outline="")
        dot.pack(side="left", padx=(0, 6))
        tk.Label(row1, text="Entrada válida", font=(FONT_UI, 10, "bold"),
                  bg=PANEL_BG, fg=GREEN).pack(side="left")
        tk.Label(valid_content, text="Símbolos: 0-9, A, B",
                  font=(FONT_UI, 9), bg=PANEL_BG, fg=SUBTEXT, anchor="w",
                  justify="left").pack(anchor="w")

    def _build_result_bar(self, parent):
        c = tk.Canvas(parent, height=70, bg=BG, highlightthickness=0)
        c.pack(fill="both", expand=True)

        def draw(event=None):
            c.delete("all")
            w = c.winfo_width() or 500
            h = c.winfo_height() or 70
            rounded_rect(c, 1, 1, w - 1, h - 1, 16, outline=GREEN, width=1.5, fill=GREEN_DIM)
            cx, cy, r = 42, h / 2, 16
            c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=GREEN, width=2, fill=GREEN_DIM)
            c.create_text(cx, cy, text="\u2713", fill=GREEN, font=(FONT_UI, 15, "bold"))
            c.create_text(cx + 34, cy, text="Cadena aceptada", fill=GREEN,
                           font=(FONT_UI, 16, "bold"), anchor="w")

        c.bind("<Configure>", draw)

    def _redraw_graph(self, event=None):
        c = self.graph_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 50 or h < 50:
            return

        def P(fx, fy):
            return (w * fx, h * fy)

        q0 = (*P(0.10, 0.50), 38)
        q1 = (*P(0.34, 0.24), 36)
        q2 = (*P(0.34, 0.76), 36)
        q3 = (*P(0.60, 0.24), 36)
        q4 = (*P(0.86, 0.50), 42)

        def edge(p1, p2, label, active=False, curve=0, ldx=0, ldy=-12):
            x1, y1, r1 = p1
            x2, y2, r2 = p2
            color = RED if active else GRAY_LINE
            width = 2.6 if active else 1.6
            dx, dy = x2 - x1, y2 - y1
            dist = max((dx ** 2 + dy ** 2) ** 0.5, 1)
            ux, uy = dx / dist, dy / dist
            sx, sy = x1 + ux * r1, y1 + uy * r1
            ex, ey = x2 - ux * r2, y2 - uy * r2
            if curve:
                mx, my = (sx + ex) / 2, (sy + ey) / 2
                px, py = -uy, ux
                cx, cy = mx + px * curve, my + py * curve
                c.create_line(sx, sy, cx, cy, ex, ey, smooth=True, fill=color,
                              width=width, arrow=tk.LAST, arrowshape=(10, 12, 4))
                lx, ly = cx, cy
            else:
                c.create_line(sx, sy, ex, ey, fill=color, width=width,
                              arrow=tk.LAST, arrowshape=(10, 12, 4))
                lx, ly = (sx + ex) / 2, (sy + ey) / 2
            c.create_text(lx + ldx, ly + ldy, text=label,
                           fill=(RED if active else "#cfcfd4"),
                           font=(FONT_UI, 10, "bold"))

        def self_loop(p, label, side="top", active=False):
            x, y, r = p
            color = RED if active else GRAY_LINE
            if side == "top":
                cx, cy = x, y - r - 26
                c.create_oval(cx - 22, cy - 16, cx + 22, cy + 16, outline=color, width=1.8)
                c.create_line(cx + 14, cy + 13, x + 13, y - r + 2, fill=color,
                              width=1.8, arrow=tk.LAST, arrowshape=(8, 10, 3))
                c.create_text(cx, cy - 22, text=label, fill=(RED if active else "#cfcfd4"),
                              font=(FONT_UI, 10, "bold"))
            else:
                cx, cy = x, y + r + 26
                c.create_oval(cx - 22, cy - 16, cx + 22, cy + 16, outline=color, width=1.8)
                c.create_line(cx + 14, cy - 13, x + 13, y + r - 2, fill=color,
                              width=1.8, arrow=tk.LAST, arrowshape=(8, 10, 3))
                c.create_text(cx, cy + 22, text=label, fill=(RED if active else "#cfcfd4"),
                              font=(FONT_UI, 10, "bold"))

        def state(p, label, active=False, accepting=False):
            x, y, r = p
            border = RED if active else "#c7c7cf"
            if accepting:
                c.create_oval(x - r - 6, y - r - 6, x + r + 6, y + r + 6,
                              outline=border, width=2.2, fill=PANEL_BG)
            c.create_oval(x - r, y - r, x + r, y + r, outline=border, width=2.4, fill=PANEL_BG)
            c.create_text(x, y, text=label, fill=TEXT, font=(FONT_UI, 13, "bold"))

        # --- Aristas (dibujadas antes que los nodos para quedar detrás) ---
        edge(q0, q1, "A", active=True, ldy=-14)
        edge(q0, q2, "0", ldy=16)
        edge(q1, q3, "B", active=True, ldy=-14)
        edge(q1, q2, "0", ldx=-14)
        edge(q2, q3, "1", ldx=10, ldy=-4)
        edge(q2, q4, "B", ldy=16)
        edge(q3, q4, "B", active=True, ldy=-14, curve=-18)
        edge(q3, q4, "\u03B5", ldy=16, curve=18)

        self_loop(q1, "A", side="top", active=True)
        self_loop(q2, "0,1", side="bottom")
        self_loop(q3, "A,1", side="top")
        self_loop(q4, "0,1", side="bottom")

        # flecha "Inicio"
        x0, y0, r0 = q0
        c.create_line(x0 - 70, y0, x0 - r0 - 4, y0, fill="#c7c7cf", width=2,
                       arrow=tk.LAST, arrowshape=(10, 12, 4))
        c.create_text(x0 - 74, y0 - 14, text="Inicio", fill="#c7c7cf",
                       font=(FONT_UI, 10, "bold"), anchor="e")

        # --- Nodos ---
        state(q0, "q0", active=True)
        state(q1, "q1", active=True)
        state(q2, "q2")
        state(q3, "q3", active=True)
        state(q4, "q4", accepting=True)

    def _build_right_column(self, parent):
        col = tk.Frame(parent, bg=BG)
        col.grid(row=0, column=2, sticky="nsew")

        p1, c1 = make_panel(col, "Estados activos", icon="\u25C9")
        p1.pack(side="top", fill="x", pady=(0, 14))
        tk.Label(c1, text="{ q1, q3 }", font=(FONT_MONO, 16, "bold"),
                  bg=PANEL_BG, fg=TEXT).pack(anchor="w", pady=(0, 14))

        tk.Label(c1, text="Símbolo procesado:", font=(FONT_UI, 9),
                  bg=PANEL_BG, fg=SUBTEXT).pack(anchor="w")
        tk.Label(c1, text="A", font=(FONT_UI, 13, "bold"),
                  bg=PANEL_BG, fg=RED).pack(anchor="w", pady=(0, 12))

        tk.Label(c1, text="Ruta actual:", font=(FONT_UI, 9),
                  bg=PANEL_BG, fg=SUBTEXT).pack(anchor="w")
        tk.Label(c1, text="q0  \u2192  q1  \u2192  q3", font=(FONT_MONO, 12, "bold"),
                  bg=PANEL_BG, fg=TEXT).pack(anchor="w")

        # --- Transiciones y rutas posibles ------------------------------------
        p2, c2 = make_panel(col, "Transiciones y rutas posibles", icon="\u279C")
        p2.pack(side="top", fill="x", pady=(0, 14))
        transitions = [
            ("q0", "A", "q1"), ("q0", "0", "q2"),
            ("q1", "B", "q3"), ("q1", "0", "q2"),
            ("q2", "1", "q3"), ("q2", "B", "q4"),
            ("q3", "A", "q3"), ("q3", "B", "q4"), ("q3", "\u03B5", "q4"),
        ]
        txt2 = tk.Text(c2, height=len(transitions), bg=PANEL_BG, fg=TEXT,
                        font=(FONT_MONO, 10), bd=0, highlightthickness=0,
                        wrap="none")
        txt2.pack(fill="x")
        txt2.tag_configure("state", foreground=TEXT)
        txt2.tag_configure("arrow", foreground=RED)
        txt2.tag_configure("sym", foreground=SUBTEXT)
        for a, sym, b in transitions:
            txt2.insert("end", f"{a} ", "state")
            txt2.insert("end", f"--{sym}--> ", "arrow")
            txt2.insert("end", f"{b}\n", "state")
        txt2.configure(state="disabled")

        p3, c3 = make_panel(col, "Bitácora de transiciones", icon="\u2630")
        p3.pack(side="top", fill="both", expand=True)
        log = [
            ("1.", "q0", "A", "q1", False),
            ("2.", "q1", "B", "q3", False),
            ("3.", "q3", "(siguiente)", "...", True),
        ]
        txt3 = tk.Text(c3, height=len(log) + 2, bg=PANEL_BG, fg=TEXT,
                        font=(FONT_MONO, 10), bd=0, highlightthickness=0, wrap="none")
        txt3.pack(fill="both", expand=True)
        txt3.tag_configure("num", foreground=SUBTEXT)
        txt3.tag_configure("state", foreground=TEXT)
        txt3.tag_configure("arrow", foreground=RED)
        txt3.tag_configure("pending", foreground="#e6a23c")
        for num, a, sym, b, pending in log:
            txt3.insert("end", f"{num} ", "num")
            if pending:
                txt3.insert("end", f"{a}  --{sym}--> {b}\n", "pending")
            else:
                txt3.insert("end", f"{a} ", "state")
                txt3.insert("end", f"--{sym}--> ", "arrow")
                txt3.insert("end", f"{b}\n", "state")
        txt3.configure(state="disabled")

if __name__ == "__main__":
    app = SafeSimulatorApp()
    app.mainloop()
