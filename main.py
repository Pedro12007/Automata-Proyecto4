import sys
import math
from PyQt5 import QtWidgets, uic, QtGui, QtCore

class VentanaTablaEstados(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tabla de Estados")
        self.resize(850, 400)
        self.setStyleSheet("background-color: #0b0b0e; color: #f4f4f6; font-family: 'Segoe UI';")
        layout = QtWidgets.QVBoxLayout(self)
        tabla = QtWidgets.QTableWidget(6, 6)
        tabla.setHorizontalHeaderLabels(["Estado", "Botón 1", "Botón 2", "Botón 3", "Botón 4", "Botón A"])
        tabla.setStyleSheet("QTableWidget { background-color: #0b0b0e; border: none; } QTableWidget::item { border-bottom: 1px solid #1f1f23; padding-left: 10px; } QHeaderView::section { background-color: #0b0b0e; color: #e0e0e0; font-size: 13px; border: none; border-bottom: 1px solid #1f1f23; padding-left: 10px; padding-bottom: 8px; }")
        tabla.setShowGrid(False)
        tabla.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        tabla.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        tabla.verticalHeader().setVisible(False)
        tabla.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        datos = [
            ("q0 (Inicial)", "{q0, q1, q2}", "{q0}", "{q0}", "{q0}", "{q0}"),
            ("q1", "∅", "{q2}", "∅", "∅", "∅"),
            ("q2", "∅", "∅", "{q3}", "∅", "∅"),
            ("q3", "∅", "∅", "∅", "{q4}", "∅"),
            ("q4", "∅", "∅", "∅", "∅", "{q5}"),
            ("q5 (Aceptada)", "{q5}", "{q5}", "{q5}", "{q5}", "{q5}")
        ]

        fuente_math = QtGui.QFont("Segoe UI", 12)
        for fila, fila_datos in enumerate(datos):
            for col, valor in enumerate(fila_datos):
                item = QtWidgets.QTableWidgetItem(valor)
                item.setFont(fuente_math)
                if col == 0 and ("Inicial" in valor or "Aceptada" in valor):
                    item.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold))
                tabla.setItem(fila, col, item)
        layout.addWidget(tabla)

class VentanaBitacora(QtWidgets.QDialog):
    def __init__(self, parent=None, log=None):
        super().__init__(parent)
        self.setWindowTitle("Bitácora de Transiciones")
        self.resize(400, 300)
        self.setStyleSheet("background-color: #0b0b0e; color: #f4f4f6; font-family: 'Segoe UI';")
        layout = QtWidgets.QVBoxLayout(self)
        self.txtBitacora = QtWidgets.QTextEdit()
        self.txtBitacora.setReadOnly(True)
        self.txtBitacora.setStyleSheet("QTextEdit { background-color: #17171d; border: 1px solid #2a1a1f; font-family: 'Consolas'; font-size: 14px; padding: 10px; }")

        log = log or []
        if log:
            lineas = []
            for i, entrada in enumerate(log, start=1):
                origen, resto = entrada.split(" --", 1)
                simbolo, destino = resto.split("--> ", 1)
                lineas.append(f"<span style='color: #8d8d97;'>{i}.</span> <span style='color: #f4f4f6;'>{origen}</span> <span style='color: #e63950;'>--{simbolo}--></span> <span style='color: #f4f4f6;'>{destino}</span><br><br>")
            self.txtBitacora.setHtml("".join(lineas))
        else:
            self.txtBitacora.setHtml("<span style='color: #8d8d97;'>Sin transiciones registradas aún.</span>")
        layout.addWidget(self.txtBitacora)

class SimuladorCajaFuerte(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('cajafuerte.ui', self)

        self.delta = {
            'q0': {'1': {'q0', 'q1', 'q2'}, '2': {'q0'}, '3': {'q0'}, '4': {'q0'}, 'A': {'q0'}},
            'q1': {'2': {'q2'}},
            'q2': {'3': {'q3'}},
            'q3': {'4': {'q4'}},
            'q4': {'A': {'q5'}},
            'q5': {'1': {'q5'}, '2': {'q5'}, '3': {'q5'}, '4': {'q5'}, 'A': {'q5'}},
        }
        self.estado_final = 'q5'
        self.estado_inicial = 'q0'

        self.buffer = ""
        self.paso_index = 0
        self.estados_actuales = {self.estado_inicial}
        self.log = []

        self.btnTabla = QtWidgets.QPushButton("Tabla de estados")
        self.btnTabla.setStyleSheet("background-color: #1d1d24; border: 1px solid #33333d; padding: 10px;")
        self.colDerecha.addWidget(self.btnTabla)
        self.btnTabla.clicked.connect(lambda: VentanaTablaEstados(self).exec_())

        self.btnBitacora = QtWidgets.QPushButton("Bitácora de transiciones")
        self.btnBitacora.setStyleSheet("background-color: #1d1d24; border: 1px solid #33333d; padding: 10px; margin-top: 5px;")
        self.colDerecha.addWidget(self.btnBitacora)
        self.btnBitacora.clicked.connect(lambda: VentanaBitacora(self, self.log).exec_())

        self.configurar_tabla_historial()
        self.colDerecha.setStretch(0, 1)
        self.colDerecha.setStretch(1, 1)

        self.escena = QtWidgets.QGraphicsScene(self)
        self.canvasAFND.setScene(self.escena)
        self.canvasAFND.setRenderHint(QtGui.QPainter.Antialiasing)
        self.canvasAFND.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        botones_simbolos = {
            self.btn1: '1', self.btn2: '2', self.btn3: '3',
            self.btn4: '4', self.btnA: 'A',
        }
        for boton, simbolo in botones_simbolos.items():
            boton.clicked.connect(lambda checked, s=simbolo: self.ingresar_simbolo(s))

        self.btnClear.clicked.connect(self.limpiar_buffer)
        self.btnEnter.clicked.connect(self.procesar_completo)
        self.btnPaso.clicked.connect(self.avanzar_paso)
        self.btnReiniciar.clicked.connect(self.reiniciar_todo)
        self.btnSalir.clicked.connect(self.close)

        self.reiniciar_todo()

    def ingresar_simbolo(self, simbolo):
        if self.buffer == "":
            self.estados_actuales = {self.estado_inicial}
            self.log = []
            self.paso_index = 0
            self.tablaHistorial.setRowCount(0)
            self.agregar_fila_historial(0, "—", f"{{{self.estado_inicial}}}", "Estado inicial", tipo='normal')
            self.lblEstadoActual.setText(f"Estado actual: {self.estado_inicial}")
            self.lblSimboloActual.setText("Símbolo actual: —")
            self.dibujar_grafo(self.estados_actuales)

        self.buffer += simbolo
        self.lblLCD.setText(' '.join(self.buffer))
        self.lblEstadoInfo.setText("Esperando entrada")
        self.lblAceptada.setVisible(False)
        self.btnPaso.setEnabled(True)
        self.lblPasoInfo.setText(f"Clave lista ({len(self.buffer)} símbolos). Presiona Avanzar paso a paso o Ingresar para procesar todo de una vez.")

    def limpiar_buffer(self):
        self.buffer = ""
        self.paso_index = 0
        self.lblLCD.setText("Esperando clave...")
        self.btnPaso.setEnabled(False)
        self.lblPasoInfo.setText("Ingresa una clave y presiona el botón para avanzar símbolo por símbolo.")

    def procesar_completo(self):
        if not self.buffer:
            return
        self.estados_actuales = {self.estado_inicial}
        self.log = []
        self.paso_index = 0
        self.tablaHistorial.setRowCount(0)
        self.agregar_fila_historial(0, "—", f"{{{self.estado_inicial}}}", "Estado inicial", tipo='normal')
        for idx, simbolo in enumerate(self.buffer, start=1):
            self.avanzar_simbolo(simbolo, idx)
        self.paso_index = len(self.buffer)
        self.lblPasoInfo.setText(f"Clave completa procesada ({len(self.buffer)}/{len(self.buffer)} símbolos).")
        self.finalizar_procesamiento()

    def avanzar_paso(self):
        if self.paso_index >= len(self.buffer):
            self.lblPasoInfo.setText("No hay más símbolos por procesar. Ingresa una nueva clave o reinicia.")
            return
        simbolo = self.buffer[self.paso_index]
        self.avanzar_simbolo(simbolo, self.paso_index + 1)
        self.paso_index += 1
        self.lblLCD.setText(self.resaltar_progreso())
        if self.paso_index < len(self.buffer):
            siguiente = self.buffer[self.paso_index]
            self.lblPasoInfo.setText(f"Paso {self.paso_index}/{len(self.buffer)} — se consumió '{simbolo}'. Siguiente símbolo: '{siguiente}'.")
        else:
            self.lblPasoInfo.setText(f"Paso {self.paso_index}/{len(self.buffer)} — se consumió '{simbolo}'. Clave completa.")
            self.finalizar_procesamiento()

    def resaltar_progreso(self):
        vistos = self.buffer[:self.paso_index]
        pendientes = self.buffer[self.paso_index:]
        return f"[{' '.join(vistos)}] {' '.join(pendientes)}".strip()

    def avanzar_simbolo(self, simbolo, paso_num=None):
        if paso_num is None:
            paso_num = self.paso_index + 1

        nuevos_estados = set()
        for estado in self.estados_actuales:
            nuevos_estados |= self.delta.get(estado, {}).get(simbolo, set())

        origen_set = set(self.estados_actuales)
        origen = ", ".join(sorted(origen_set))
        destino = ", ".join(sorted(nuevos_estados)) if nuevos_estados else "∅"
        self.log.append(f"{origen} --{simbolo}--> {destino}")

        estados_texto = f"{{{destino}}}" if nuevos_estados else "∅"
        if not nuevos_estados:
            tipo = 'bloqueada'
        elif self.estado_final in nuevos_estados:
            tipo = 'aceptada'
        else:
            tipo = 'normal'
        explicacion = self.generar_explicacion(origen_set, nuevos_estados)
        self.agregar_fila_historial(paso_num, simbolo, estados_texto, explicacion, tipo)

        self.estados_actuales = nuevos_estados
        texto_estado = f"{{{destino}}}" if nuevos_estados else "∅ (bloqueado)"
        self.lblEstadoActual.setText(f"Estado actual: {texto_estado}")
        self.lblSimboloActual.setText(f"Símbolo actual: {simbolo}")
        self.actualizar_transiciones_posibles()
        self.dibujar_grafo(self.estados_actuales)

    def finalizar_procesamiento(self):
        match (self.estado_final in self.estados_actuales, bool(self.estados_actuales)):
            case (True, _):
                self.lblEstadoInfo.setText("Acceso concedido")
                self.lblEstadoInfo.setStyleSheet("color: #33c37f;")
                self.lblAceptada.setVisible(True)
            case (False, False):
                self.lblEstadoInfo.setText("Clave incorrecta")
                self.lblEstadoInfo.setStyleSheet("color: #e63950;")
                self.lblAceptada.setVisible(False)
            case (False, True):
                self.lblEstadoInfo.setText("Clave incompleta")
                self.lblEstadoInfo.setStyleSheet("color: #e63950;")
                self.lblAceptada.setVisible(False)

    def configurar_tabla_historial(self):
        tabla = self.tablaHistorial
        tabla.setColumnCount(4)
        tabla.setHorizontalHeaderLabels(["Paso", "Símbolo", "Estados", "Explicación"])
        tabla.verticalHeader().setVisible(False)
        tabla.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        tabla.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        tabla.setShowGrid(False)
        tabla.setWordWrap(True)
        tabla.setStyleSheet(
            "QTableWidget { background-color: #141419; border: none; }"
            "QTableWidget::item { border-bottom: 1px solid #1f1f23; padding: 6px 8px; color: #f4f4f6; }"
        )

        header = tabla.horizontalHeader()
        header.setObjectName("headerHistorial")
        header.setHighlightSections(False)
        header.setSectionsClickable(False)
        header.setStyleSheet(
            "QHeaderView#headerHistorial::section {"
            " background-color: #1d1d24;"
            " color: #e0e0e0;"
            " font-size: 12px;"
            " font-weight: bold;"
            " border: 1px solid #1d1d24;"
            " border-bottom: 1px solid #33333d;"
            " padding: 6px 8px; }"
        )

        resize_mode = header.setSectionResizeMode
        resize_mode(0, QtWidgets.QHeaderView.ResizeToContents)
        resize_mode(1, QtWidgets.QHeaderView.ResizeToContents)
        resize_mode(2, QtWidgets.QHeaderView.ResizeToContents)
        resize_mode(3, QtWidgets.QHeaderView.Stretch)

    def agregar_fila_historial(self, paso, simbolo, estados_texto, explicacion, tipo='normal'):
        tabla = self.tablaHistorial
        fila = tabla.rowCount()
        tabla.insertRow(fila)

        colores_fondo = {
            'aceptada': QtGui.QColor(38, 61, 48),
            'bloqueada': QtGui.QColor(61, 30, 36),
        }
        colores_texto = {
            'aceptada': QtGui.QColor("#33c37f"),
            'bloqueada': QtGui.QColor("#e63950"),
        }

        for col, valor in enumerate([str(paso), simbolo, estados_texto, explicacion]):
            item = QtWidgets.QTableWidgetItem(valor)
            item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            if tipo in colores_fondo:
                item.setBackground(QtGui.QBrush(colores_fondo[tipo]))
                item.setForeground(QtGui.QBrush(colores_texto[tipo]))
            else:
                item.setForeground(QtGui.QBrush(QtGui.QColor("#f4f4f6")))
            tabla.setItem(fila, col, item)

        tabla.resizeRowsToContents()
        tabla.scrollToBottom()

    def generar_explicacion(self, origen, destino):
        if not destino:
            return "Ninguna ruta continúa activa: la clave se bloquea."
        if self.estado_final in destino:
            if self.estado_final in origen:
                return "Se mantiene una ruta en el estado de aceptación."
            return "Una ruta llega al estado de aceptación."

        agregados = destino - origen
        descartados = origen - destino
        if not agregados and not descartados:
            return "Las rutas activas se mantienen sin cambios."

        partes = []
        if agregados:
            verbo = "aparece" if len(agregados) == 1 else "aparecen"
            partes.append(f"{verbo} {', '.join(sorted(agregados))}")
        if descartados:
            verbo = "se descarta" if len(descartados) == 1 else "se descartan"
            partes.append(f"{verbo} {', '.join(sorted(descartados))}")

        texto = " y ".join(partes)
        return texto[0].upper() + texto[1:] + "."

    def actualizar_transiciones_posibles(self):
        lineas = []
        for estado in sorted(self.estados_actuales):
            for simbolo, destinos in self.delta.get(estado, {}).items():
                lineas.append(f"{estado} --{simbolo}--> {{{', '.join(sorted(destinos))}}}")
        self.txtTransiciones.setPlainText("\n".join(lineas) if lineas else "Sin transiciones disponibles")

    def reiniciar_todo(self):
        self.buffer = ""
        self.paso_index = 0
        self.estados_actuales = {self.estado_inicial}
        self.log = []
        self.lblLCD.setText("Esperando clave...")
        self.lblEstadoActual.setText(f"Estado actual: {self.estado_inicial}")
        self.lblSimboloActual.setText("Símbolo actual: —")
        self.lblEstadoInfo.setText("Esperando entrada")
        self.lblEstadoInfo.setStyleSheet("color: #e63950;")
        self.lblAceptada.setVisible(False)
        self.txtTransiciones.clear()
        self.tablaHistorial.setRowCount(0)
        self.agregar_fila_historial(0, "—", f"{{{self.estado_inicial}}}", "Estado inicial", tipo='normal')
        self.btnPaso.setEnabled(False)
        self.lblPasoInfo.setText("Ingresa una clave y presiona el botón para avanzar símbolo por símbolo.")
        self.dibujar_grafo(self.estados_actuales)

    def dibujar_grafo(self, estados_activos=None):
        estados_activos = estados_activos or {self.estado_inicial}
        self.escena.clear()
        self.escena.setSceneRect(0, 0, 750, 350)

        pen_borde = QtGui.QPen(QtGui.QColor("#c7c7cf"), 2)
        brush_fondo = QtGui.QBrush(QtGui.QColor("#141419"))
        pen_activo = QtGui.QPen(QtGui.QColor("#e63950"), 3)
        brush_activo = QtGui.QBrush(QtGui.QColor("#3a1620"))
        pen_glow = QtGui.QPen(QtGui.QColor(230, 57, 80, 120), 5)
        fuente = QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold)

        posiciones = {
            "q0": (50, 175), "q1": (220, 60), "q2": (220, 290),
            "q3": (390, 175), "q4": (540, 175), "q5": (680, 175)
        }

        self.dibujar_transicion(posiciones["q0"], posiciones["q1"], "1")
        self.dibujar_transicion(posiciones["q0"], posiciones["q2"], "1")
        self.dibujar_transicion(posiciones["q1"], posiciones["q2"], "2")
        self.dibujar_transicion(posiciones["q2"], posiciones["q3"], "3")
        self.dibujar_transicion(posiciones["q3"], posiciones["q4"], "4")
        self.dibujar_transicion(posiciones["q4"], posiciones["q5"], "A")

        self.dibujar_bucle(posiciones["q0"], "1,2,3,4,A")
        self.dibujar_bucle(posiciones["q5"], "1,2,3,4,A")

        for estado, (x, y) in posiciones.items():
            radio = 22
            activo = estado in estados_activos

            if estado == self.estado_final:
                self.escena.addEllipse(x - radio - 6, y - radio - 6, (radio + 6) * 2, (radio + 6) * 2, pen_borde, QtGui.QBrush(QtCore.Qt.NoBrush))

            if activo:
                self.escena.addEllipse(x - radio - 8, y - radio - 8, (radio + 8) * 2, (radio + 8) * 2, pen_glow, QtGui.QBrush(QtCore.Qt.NoBrush))

            pen_nodo, brush_nodo = (pen_activo, brush_activo) if activo else (pen_borde, brush_fondo)
            self.escena.addEllipse(x - radio, y - radio, radio * 2, radio * 2, pen_nodo, brush_nodo)
            texto = self.escena.addText(estado, fuente)
            texto.setDefaultTextColor(QtGui.QColor("#f4f4f6") if activo else QtGui.QColor("#c7c7cf"))
            texto.setPos(x - texto.boundingRect().width() / 2, y - texto.boundingRect().height() / 2)

    def dibujar_transicion(self, p1, p2, etiqueta):
        pen_linea = QtGui.QPen(QtGui.QColor("#cfcfd4"), 2)
        self.escena.addLine(p1[0], p1[1], p2[0], p2[1], pen_linea)
        self.dibujar_flecha(p1, p2)
        texto = self.escena.addText(etiqueta)
        texto.setDefaultTextColor(QtGui.QColor("#e63950"))
        texto.setPos((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 - 25)

    def dibujar_flecha(self, p1, p2):
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        distancia = math.hypot(dx, dy)
        if distancia == 0:
            return
        ux, uy = dx / distancia, dy / distancia
        radio_nodo = 22
        punta = (p2[0] - ux * radio_nodo, p2[1] - uy * radio_nodo)
        angulo = math.atan2(uy, ux)
        tam = 9
        p_izq = (punta[0] + tam * math.cos(angulo + math.radians(150)), punta[1] + tam * math.sin(angulo + math.radians(150)))
        p_der = (punta[0] + tam * math.cos(angulo - math.radians(150)), punta[1] + tam * math.sin(angulo - math.radians(150)))
        triangulo = QtGui.QPolygonF([QtCore.QPointF(*punta), QtCore.QPointF(*p_izq), QtCore.QPointF(*p_der)])
        color = QtGui.QColor("#cfcfd4")
        self.escena.addPolygon(triangulo, QtGui.QPen(color), QtGui.QBrush(color))

    def dibujar_bucle(self, p, etiqueta):
        radio_bucle = 13
        cx, cy = p[0], p[1] - 60
        pen_linea = QtGui.QPen(QtGui.QColor("#4a4a52"), 2)
        self.escena.addLine(cx, cy + radio_bucle, p[0], p[1] - 22, pen_linea)
        self.escena.addEllipse(cx - radio_bucle, cy - radio_bucle, radio_bucle * 2, radio_bucle * 2, pen_linea)
        fuente_pequena = QtGui.QFont("Segoe UI", 8)
        texto = self.escena.addText(etiqueta, fuente_pequena)
        texto.setDefaultTextColor(QtGui.QColor("#8d8d97"))
        ancho = texto.boundingRect().width()
        texto.setPos(cx - ancho / 2, cy - radio_bucle - 15)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ventana = SimuladorCajaFuerte()
    ventana.showMaximized()
    sys.exit(app.exec_())