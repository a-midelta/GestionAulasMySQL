from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QCalendarWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt, QSize, QDate
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
        self.h_layout = QHBoxLayout()
        self.filters_v_layout = QFormLayout()
        
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

        self.clear_button = QPushButton("Vaciar", clicked=self.clear_form)  # Botón para vaciar el formulario
        self.form_layout.addRow("", self.clear_button)

        # Botóm para actualizar registros
        self.update_button = QPushButton("Actualizar Registro Seleccionado", clicked=self.update_selected_row)
        self.layout.addWidget(self.update_button)

        # Botón para eliminar registros
        self.delete_button = QPushButton("Eliminar Registro Seleccionado", clicked=self.delete_data)
        self.layout.addWidget(self.delete_button)

        
        # Tabla de Datos
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Día", "Hora", "Nombre", "Materia", "Aula"])
        # Estirar encabezados horizontales de modo que usen todo el espacio
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Modo de selección para seleccionar filas enteras
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        # Cargar datos de fila seleccionada
        self.table.cellClicked.connect(self.load_data_from_selected_row)
        
        # Filtros
        self.filters_label = QLabel("Filtros")
        self.filters_label.setAlignment(Qt.AlignCenter)
        self.filters_v_layout.addWidget(self.filters_label)
        # Filtro aula
        self.filters_classroom_combobox = QComboBox()
        self.filters_classroom_combobox.addItems(["Todas", "Sala de capacitación A", "Sala de capacitación B"])
        self.filters_v_layout.addRow("Aula:", self.filters_classroom_combobox)
        self.filters_classroom_combobox.currentIndexChanged.connect(self.filter_table)
        # Filtro nombre
        self.filters_name_lineedit = QLineEdit()
        self.filters_v_layout.addRow("Nombre:", self.filters_name_lineedit)
        self.filters_name_lineedit.textChanged.connect(self.filter_table)
        # Filtro hora
        self.filters_time_combobox = QComboBox()
        self.filters_time_combobox.addItems(["Cualquiera"])
        for hour in range(7, 21):
            self.filters_time_combobox.addItem(f"{hour}:00")
        self.filters_v_layout.addRow("Hora:", self.filters_time_combobox)
        self.filters_time_combobox.currentIndexChanged.connect(self.filter_table)

        # Espaciador equis
        spacer = QWidget()
        spacer.setFixedSize(QSize(10, 10))  # Ajustar tamaño según se necesite
        self.layout.addWidget(spacer)

        # Finalizar layout
        self.h_layout.addLayout(self.filters_v_layout, 1)
        self.h_layout.addWidget(self.table, 7)
        self.layout.addLayout(self.h_layout)
        # self.layout.addWidget(self.table)


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
            print("Registro duplicado (día, hora y/o aula ya ocupados).")
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

    def filter_table(self):
        aula_seleccionada = self.filters_classroom_combobox.currentText()
        nombre_tecleado = self.filters_name_lineedit.text()
        hora_seleccionada = self.filters_time_combobox.currentText()
        if aula_seleccionada == "Todas":
            # No filtrar por aula, solo nombre y hora
            self.load_filtered_data(classroom=None, name=nombre_tecleado, time=hora_seleccionada)  
        else:
            # Filtrar por aula, nombre y hora
            self.load_filtered_data(classroom=aula_seleccionada, name=nombre_tecleado, time=hora_seleccionada) 

    def load_filtered_data(self, classroom=None, name=None, time=None):
        # Limpiar tabla
        self.table.setRowCount(0)

        # Obtener datos filtrados desde la base de datos
        filtered_data = self.mongo_handler.get_all_data(classroom, name, time)

        # Llenar la tabla con los datos ya filtrados
        for row, record in enumerate(filtered_data):
            self.table.insertRow(row)
            for col, value in enumerate(record.values()):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)
        
    def load_data_from_selected_row(self, row, col):
        # Obtener datos de la fila seleccionada
        day = self.table.item(row, 0).text()
        time = self.table.item(row, 1).text()
        name = self.table.item(row, 2).text()
        subject = self.table.item(row, 3).text()
        classroom = self.table.item(row, 4).text()

        # Ponerle a los widgets del formulario los datos correspondientes
        self.day_calendar.setSelectedDate(self.day_calendar.selectedDate().fromString(day, "yyyy-MM-dd"))
        index = self.time_combobox.findText(time, Qt.MatchExactly)
        if index >= 0:
            self.time_combobox.setCurrentIndex(index)
        self.name_lineedit.setText(name)
        self.subject_lineedit.setText(subject)
        index = self.classroom_combobox.findText(classroom, Qt.MatchExactly)
        if index >= 0:
            self.classroom_combobox.setCurrentIndex(index)

    def clear_form(self):
        # Vaciar todos los campos del formulario
        self.day_calendar.setSelectedDate(QDate.currentDate())
        self.time_combobox.setCurrentIndex(0)
        self.name_lineedit.clear()
        self.subject_lineedit.clear()
        self.classroom_combobox.setCurrentIndex(0)

        # Deseleccionar selección de la tabla
        self.table.clearSelection()
        self.table.setCurrentItem(None)

    def update_selected_row(self):
        # Checar si la tabla está seleccionada
        selected_row = self.table.currentRow()
        if selected_row == -1:
            print("Seleccione una fila para actualizar.")
            return

        # Obtener datos actualizados del formulario
        day = self.day_calendar.selectedDate().toString("yyyy-MM-dd")
        time = self.time_combobox.currentText()
        name = self.name_lineedit.text()
        subject = self.subject_lineedit.text()
        classroom = self.classroom_combobox.currentText()

        # Actualizar tabla (esto es solo algo visual)
        self.table.item(selected_row, 0).setText(day)
        self.table.item(selected_row, 1).setText(time)
        self.table.item(selected_row, 2).setText(name)
        self.table.item(selected_row, 3).setText(subject)
        self.table.item(selected_row, 4).setText(classroom)

        # Actualizar en la base de datos
        self.mongo_handler.update_data(day, time, name, subject, classroom)

        print("Registro actualizado correctamente.")



