from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QCalendarWidget,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtCore import Qt
from MongoDBHandler import MongoDBHandler

class MainWindow(QMainWindow):
    def __init__(self, mongo_handler: MongoDBHandler):
        super().__init__()

        self.mongo_handler = mongo_handler

        self.setWindowTitle("Gestión de Aulas")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        
        self.label = QLabel("Gestión de Disponibilidad de Aulas")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        # Formulario
        self.form_layout = QFormLayout()

        self.day_calendar = QCalendarWidget()
        self.form_layout.addRow("Día:", self.day_calendar)

        self.time_combobox = QComboBox()
        for hour in range(7, 21):
            self.time_combobox.addItem(f"{hour}:00")
        self.form_layout.addRow("Hora:", self.time_combobox)

        self.name_lineedit = QLineEdit()
        self.form_layout.addRow("Nombre:", self.name_lineedit)

        self.subject_lineedit = QLineEdit()
        self.form_layout.addRow("Materia:", self.subject_lineedit)

        self.classroom_combobox = QComboBox()
        self.classroom_combobox.addItems(["Sala de capacitación A", "Sala de capacitación B"])
        self.form_layout.addRow("Aula:", self.classroom_combobox)

        self.form_layout.addRow("", QPushButton("Guardar", clicked=self.save_data))
        self.layout.addLayout(self.form_layout)
        
        # Botón para eliminar registros
        self.delete_button = QPushButton("Eliminar Registro Seleccionado", clicked=self.delete_data)
        self.layout.addWidget(self.delete_button)
        
        # Tabla de Datos
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Día", "Hora", "Nombre", "Materia", "Aula"])
        self.layout.addWidget(self.table)

        # Cargar datos al iniciar
        self.load_data()

    def save_data(self):
        # Obtener datos del formulario
        day = self.day_calendar.selectedDate().toString("yyyy-MM-dd")
        time = self.time_combobox.currentText()
        name = self.name_lineedit.text()
        subject = self.subject_lineedit.text()
        classroom = self.classroom_combobox.currentText()  # Nuevo campo para el aula

        # Validaciones y evitar duplicados
        if not day or not time or not name or not subject:
            print("Todos los campos son obligatorios.")
            return

        if self.mongo_handler.check_duplicate(day, time, classroom):
            print("Registro duplicado.")
            return

        # Guardar en la base de datos
        self.mongo_handler.insert_data(day, time, name, subject, classroom)
        print("Datos guardados correctamente.")

        # Actualizar la tabla
        self.load_data()

    def load_data(self):
        # Limpiar la tabla
        self.table.setRowCount(0)

        # Obtener datos de la base de datos
        data = self.mongo_handler.get_all_data()

        # Llenar la tabla
        for row, record in enumerate(data):
            self.table.insertRow(row)
            for col, value in enumerate(record.values()):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)

    def delete_data(self):
        # Verificar si se ha seleccionado una fila
        selected_row = self.table.currentRow()
        if selected_row == -1:
            print("Seleccione una fila para eliminar.")
            return

        # Obtener datos de la fila seleccionada
        day = self.table.item(selected_row, 0).text()
        time = self.table.item(selected_row, 1).text()

        # Eliminar el registro de la base de datos
        self.mongo_handler.delete_data(day, time)
        print("Registro eliminado correctamente.")

        # Actualizar la tabla
        self.load_data()
        
