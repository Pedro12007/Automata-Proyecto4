import sys
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bitácora de Transiciones")
        self.resize(400, 300)
        self.setStyleSheet("background-color: #0b0b0e; color: #f4f4f6; font-family: 'Segoe UI';")
        layout = QtWidgets.QVBoxLayout(self)
        self.txtBitacora = QtWidgets.QTextEdit()
        self.txtBitacora.setReadOnly(True)
        self.txtBitacora.setStyleSheet("QTextEdit { background-color: #17171d; border: 1px solid #2a1a1f; font-family: 'Consolas'; font-size: 14px; padding: 10px; }")
        
        log_html = "<span style='color: #8d8d97;'>1.</span> <span style='color: #f4f4f6;'>q0</span> <span style='color: #e63950;'>--1--></span> <span style='color: #f4f4f6;'>q1</span><br><br>"
        self.txtBitacora.setHtml(log_html)
        layout.addWidget(self.txtBitacora)

class SimuladorCajaFuerte(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('cajafuerte.ui', self)
        
        # Botones emergentes
        self.btnTabla = QtWidgets.QPushButton("📊 Tabla de estados")
        self.btnTabla.setStyleSheet("background-color: #1d1d24; border: 1px solid #33333d; padding: 10px;")
        self.colDerecha.addWidget(self.btnTabla)
        self.btnTabla.clicked.connect(lambda: VentanaTablaEstados(self).exec_())
        
        self.btnBitacora = QtWidgets.QPushButton("☰ Bitácora de transiciones")
        self.btnBitacora.setStyleSheet("background-color: #1d1d24; border: 1px solid #33333d; padding: 10px; margin-top: 5px;")
        self.colDerecha.addWidget(self.btnBitacora)
        self.btnBitacora.clicked.connect(lambda: VentanaBitacora(self).exec_())
        
        # Configurar lienzo del grafo
        self.escena = QtWidgets.QGraphicsScene(self)
        self.canvasAFND.setScene(self.escena)
        self.canvasAFND.setRenderHint(QtGui.QPainter.Antialiasing)
        self.canvasAFND.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop) # Alineación clave
        self.dibujar_grafo()

    def dibujar_grafo(self):
        self.escena.clear()
        self.escena.setSceneRect(0, 0, 750, 350) # Fija el área visible

        pen_borde = QtGui.QPen(QtGui.QColor("#c7c7cf"), 2)
        brush_fondo = QtGui.QBrush(QtGui.QColor("#141419"))
        fuente = QtGui.QFont("Segoe UI", 12, QtGui.QFont.Bold)

        posiciones = {
            "q0": (50, 150), "q1": (200, 50), "q2": (200, 250),
            "q3": (350, 150), "q4": (500, 150), "q5": (650, 150)
        }

        # Transiciones
        self.dibujar_transicion(posiciones["q0"], posiciones["q1"], "1")
        self.dibujar_transicion(posiciones["q0"], posiciones["q2"], "1")
        self.dibujar_transicion(posiciones["q1"], posiciones["q2"], "2")
        self.dibujar_transicion(posiciones["q2"], posiciones["q3"], "3")
        self.dibujar_transicion(posiciones["q3"], posiciones["q4"], "4")
        self.dibujar_transicion(posiciones["q4"], posiciones["q5"], "A")
        
        # Bucles
        self.dibujar_bucle(posiciones["q0"], "1,2,3,4,A")
        self.dibujar_bucle(posiciones["q5"], "1,2,3,4,A")

        # Estados
        for estado, (x, y) in posiciones.items():
            radio = 20
            if estado == "q5":
                self.escena.addEllipse(x - radio - 6, y - radio - 6, (radio + 6)*2, (radio + 6)*2, pen_borde, QtGui.QBrush(QtCore.Qt.NoBrush))
            
            self.escena.addEllipse(x - radio, y - radio, radio*2, radio*2, pen_borde, brush_fondo)
            texto = self.escena.addText(estado, fuente)
            texto.setDefaultTextColor(QtGui.QColor("#f4f4f6"))
            texto.setPos(x - texto.boundingRect().width()/2, y - texto.boundingRect().height()/2)

    def dibujar_transicion(self, p1, p2, etiqueta):
        pen_linea = QtGui.QPen(QtGui.QColor("#cfcfd4"), 2)
        self.escena.addLine(p1[0], p1[1], p2[0], p2[1], pen_linea)
        texto = self.escena.addText(etiqueta)
        texto.setDefaultTextColor(QtGui.QColor("#e63950"))
        texto.setPos((p1[0] + p2[0])/2, (p1[1] + p2[1])/2 - 25)

    def dibujar_bucle(self, p, etiqueta):
        pen_linea = QtGui.QPen(QtGui.QColor("#cfcfd4"), 2)
        self.escena.addEllipse(p[0] - 15, p[1] - 45, 30, 30, pen_linea)
        texto = self.escena.addText(etiqueta)
        texto.setDefaultTextColor(QtGui.QColor("#e63950"))
        texto.setPos(p[0] - 30, p[1] - 70)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ventana = SimuladorCajaFuerte()
    ventana.show()
    sys.exit(app.exec_())