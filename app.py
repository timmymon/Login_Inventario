from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from db_config import get_db_connection

app = Flask(__name__)

# Página principal (mostrar todos los pacientes)
@app.route('/')
def index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pacientes")
        pacientes = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        return "Error al conectar con la base de datos."
    finally:
        cursor.close()
        connection.close()
    return render_template('index.html', pacientes=pacientes)

# Crear paciente
@app.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        edad = request.form['edad']
        genero = request.form['genero']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        
        # Validación básica de campos
        if not nombre or not apellido or not edad or not genero or not direccion or not telefono:
            return "Todos los campos son obligatorios", 400  # Error 400 por solicitud incorrecta

        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''INSERT INTO pacientes (nombre, apellido, edad, genero, direccion, telefono)
                              VALUES (%s, %s, %s, %s, %s, %s)''', 
                           (nombre, apellido, edad, genero, direccion, telefono))
            connection.commit()
        except mysql.connector.Error as err:
            print(f"Error de base de datos: {err}")
            return "Error al insertar el paciente."
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('index'))
    
    return render_template('crear.html')

# Editar paciente
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pacientes WHERE id = %s", (id,))
        paciente = cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error de base de datos: {err}")
        return "Error al consultar el paciente."
    finally:
        cursor.close()
        connection.close()

    if paciente is None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        edad = request.form['edad']
        genero = request.form['genero']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        
        # Validación básica de campos
        if not nombre or not apellido or not edad or not genero or not direccion or not telefono:
            return "Todos los campos son obligatorios", 400

        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''UPDATE pacientes
                              SET nombre = %s, apellido = %s, edad = %s, genero = %s, direccion = %s, telefono = %s
                              WHERE id = %s''', 
                           (nombre, apellido, edad, genero, direccion, telefono, id))
            connection.commit()
        except mysql.connector.Error as err:
            print(f"Error de base de datos: {err}")
            return "Error al actualizar el paciente."
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('index'))

    return render_template('editar.html', paciente=paciente)

# Eliminar paciente
@app.route('/eliminar/<int:id>', methods=['GET'])
def eliminar(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM pacientes WHERE id = %s", (id,))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error de base de datos: {err}")
        return "Error al eliminar el paciente."
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
