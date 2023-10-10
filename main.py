import sys
from PySide6.QtWidgets import QApplication
from MainWindow import MainWindow
from MongoDBHandler import MongoDBHandler

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Conectar a la base de datos MongoDB
    mongo_handler = MongoDBHandler()

    # Crear la ventana principal y pasar el manejador de MongoDB
    window = MainWindow(mongo_handler)
    window.show()

    sys.exit(app.exec())
