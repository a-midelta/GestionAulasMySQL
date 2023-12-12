import sys
from PySide6.QtWidgets import QApplication
from MainWindow import MainWindow
# from MongoDBHandler import MongoDBHandler
from MySQLHandler import MySQLHandler

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Conectar a la base de datos MySQL
    mysql_handler = MySQLHandler()
    # Crear la tabla "disponibilidad" en caso de que no exista ya.
    mysql_handler.create_table()

    # Crear la ventana principal y pasar el manejador de MongoDB
    window = MainWindow(mysql_handler)
    window.show()

    sys.exit(app.exec())
