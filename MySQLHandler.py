import mysql.connector
from mysql.connector import errorcode

class MySQLHandler:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='aula',
                password='12345',
                database='aulas'
            )
            self.cursor = self.connection.cursor(buffered=True)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Error: Acceso denegado. Verificar usuario y contraseña.")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Error: No existe la base de datos especificada.")
            else:
                print(f"Error: {err}")
    
    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS disponibilidad (
            id INT AUTO_INCREMENT PRIMARY KEY,
            day DATE,
            time VARCHAR(5),
            name VARCHAR(255),
            subject VARCHAR(255),
            classroom VARCHAR(255)
        )
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def insert_data(self, day, time, name, subject, classroom):
        insert_query = "INSERT INTO disponibilidad (day, time, name, subject, classroom) VALUES (%s, %s, %s, %s, %s)"
        data = (day, time, name, subject, classroom)
        self.cursor.execute(insert_query, data)
        self.connection.commit()

    def check_duplicate(self, day, time, classroom):
        duplicate_query = "SELECT COUNT(*) FROM disponibilidad WHERE day = %s AND time = %s AND classroom = %s"
        data = (day, time, classroom)
        self.cursor.execute(duplicate_query, data)
        count = self.cursor.fetchone()[0]
        return count > 0

    def get_all_data(self, classroom=None, name=None, time=None):
        select_query = "SELECT day, time, name, subject, classroom FROM disponibilidad WHERE 1"

        # if classroom and classroom != "Todas":
        #     select_query += " AND classroom = %s"

        # if name:
        #     select_query += " AND name LIKE %s"

        # if time and time != "Cualquiera":
        #     select_query += " AND time = %s"

        # # data = (classroom, f"%{name}%", time)

        # # Asegurarse de que el número de marcadores de posición coincida con el
        # # número de elementos en la tupla.
        # data = (classroom,) if classroom else ()
        # data += (f"%{name}%",) if name else ()
        # data += (time,) if time else ()

        conditions = []

        if classroom and classroom != "Todas":
            conditions.append("classroom = %s")

        if name:
            conditions.append("name LIKE %s")

        if time and time != "Cualquiera":
            conditions.append("time = %s")
        elif time == "Cualquiera":
            # Omitir condición cuando "Cualquiera" está seleccionado.
            time = None

        if conditions:
            select_query += " AND " + " AND ".join(conditions)

        data = ()
        if classroom:
            data += (classroom,)
        if name:
            data += (f"%{name}%",)
        if time:
            data += (time,)
            
        self.cursor.execute(select_query, data)
        result = self.cursor.fetchall()

        return result

    def delete_data(self, day, time):
        delete_query = "DELETE FROM disponibilidad WHERE day = %s AND time = %s"
        data = (day, time)
        self.cursor.execute(delete_query, data)
        self.connection.commit()

    def update_data(self, day, time, name, subject, classroom):
        update_query = "UPDATE disponibilidad SET name = %s, subject = %s, classroom = %s WHERE day = %s AND time = %s"
        data = (name, subject, classroom, day, time)
        self.cursor.execute(update_query, data)
        self.connection.commit()

    def __del__(self):
        self.cursor.close()
        self.connection.close()
