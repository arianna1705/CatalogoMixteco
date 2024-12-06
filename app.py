from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from config import create_connection
from models import db, Usuario, Nivelusuario
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# Ruta principal (home)
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/index.html')
def index():
    return render_template("index.html")

# Ruta para la página de usuarios
@app.route('/usuarios.html')
def usuarios():
    return render_template('usuarios.html')

# Ruta para la página de lugares
@app.route('/lugares.html')
def lugares():
    return render_template("lugares.html")

@app.route('/imagenes.html')
def imagenes():
    return render_template("imagenes.html")

@app.route('/perfil.html')
def perfil():
    return render_template("perfil.html")

@app.route('/sesion.html')
def sesion():
    return render_template("sesion.html")


@app.route('/registrarse.html')
def registrarse():
    return render_template("registrarse.html")
# Ruta para mostrar el formulario de registro (GET)
@app.route('/registrarse', methods=['GET'])
def mostrar_registro():
    return render_template('registrarse.html')

# Ruta para procesar el formulario de registro (POST)
@app.route('/registrarse', methods=['POST'])
def procesar_registro():
    data = request.get_json()
    nombre = data.get('nombre')
    correo = data.get('correo')
    contrasena = data.get('contrasena')

    # Hash de la contraseña para guardarla de forma segura
    contrasena_hash = generate_password_hash(contrasena)

    # Crear la conexión a la base de datos
    connection = create_connection()
    cursor = connection.cursor()

    # Insertar el nuevo usuario en la base de datos
    try:
        cursor.execute("INSERT INTO usuarios (nom_usuario, correo, contrasena) VALUES (%s, %s, %s)", 
                       (nombre, correo, contrasena_hash))  
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'status': 'success', 'message': 'Usuario registrado correctamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# Ruta para mostrar el formulario de inicio de sesión
@app.route('/sesion', methods=['GET'])
def mostrar_sesion():
    return render_template('sesion.html')

# Ruta para autenticar al usuario
@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.json
    correo = data.get('correo')
    contrasena = data.get('contrasena')

    # Conexión a la base de datos
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
    user = cursor.fetchone()

    if user:
        # Verificar que el usuario exista y la contraseña sea correcta
        hashed_password = user[4]  # Asumiendo que el campo contrasena está en la posición 3
        if check_password_hash(hashed_password, contrasena):
            
            return redirect(url_for('index.html'))  
        else:
            return jsonify({'status': 'error', 'message': 'Contraseña incorrecta'})
    else:
        return jsonify({'status': 'error', 'message': 'Correo no encontrado'})
    

# apis para lugares
# Obtener todos los lugares activos
@app.route('/api/lugares', methods=['GET'])
def get_lugares():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lugares WHERE estatus = 1")
    lugares = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(lugares)

# Obtener un lugar por ID 
@app.route('/api/lugares/<int:id>', methods=['GET'])
def get_lugar(id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lugares WHERE id_lugar = %s", (id,))
    lugar = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if lugar is None or lugar['estatus'] == 0:
        return jsonify({'error': 'Lugar no encontrado o está inactivo'}), 404
    return jsonify(lugar)

# Crear un nuevo lugar
@app.route('/api/lugares', methods=['POST'])
def create_lugar():
    data = request.json
    required_fields = ['nom_lugar', 'descripcion', 'ubicacion', 'usu_mod']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    estatus = data.get('estatus', 1)

    now = datetime.now().date()
    action = "Creación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO lugares (nom_lugar, descripcion, ubicacion, estatus, usu_mod, ult_mod, fecha_mov) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (data['nom_lugar'], data['descripcion'], data['ubicacion'], estatus, data['usu_mod'], action, now)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    
    return jsonify({'message': f'Lugar creado con éxito', 'id_lugar': new_id}), 201

# Actualizar un lugar existente
@app.route('/api/lugares/<int:id>', methods=['PUT'])
def update_lugar(id):
    data = request.json
    required_fields = ['nom_lugar', 'descripcion', 'ubicacion', 'estatus', 'usu_mod']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    if data['estatus'] not in [0, 1]:
        return jsonify({'error': 'El campo estatus debe ser 0 o 1'}), 400

    now = datetime.now().date()
    action = "Actualización"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE lugares SET nom_lugar = %s, descripcion = %s, ubicacion = %s, estatus = %s, usu_mod = %s, ult_mod = %s, fecha_mov = %s WHERE id_lugar = %s",
        (data['nom_lugar'], data['descripcion'], data['ubicacion'], data['estatus'], data['usu_mod'], action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Lugar no encontrado'}), 404

    return jsonify({'message': f'Lugar con ID {id} actualizado con éxito'})

# Baja lógica de un lugar 
@app.route('/api/lugares/<int:id>', methods=['DELETE'])
def delete_lugar(id):
    now = datetime.now().date()
    action = "Eliminación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE lugares SET estatus = 0, ult_mod = %s, fecha_mov = %s WHERE id_lugar = %s AND estatus = 1",
        (action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Lugar no encontrado o ya está inactivo'}), 404

    return jsonify({'message': f'Lugar con ID {id} marcado como inactivo'})


#apis de imagens
# Obtener todas las imágenes activas
@app.route('/api/imagenes', methods=['GET'])
def get_imagenes():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM imagenes WHERE estatus = 1")
    imagenes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(imagenes)

# Obtener una imagen por ID
@app.route('/api/imagenes/<int:id>', methods=['GET'])
def get_imagen(id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM imagenes WHERE id_imagen = %s", (id,))
    imagen = cursor.fetchone()
    cursor.close()
    conn.close()

    if imagen is None or imagen['estatus'] == 0:
        return jsonify({'error': 'Imagen no encontrada o está inactiva'}), 404
    return jsonify(imagen)

# Crear una nueva imagen
@app.route('/api/imagenes', methods=['POST'])
def create_imagen():
    data = request.json
    required_fields = ['ruta_imagen', 'titulo_img', 'usu_mod', 'id_lugar']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    estatus = data.get('estatus', 1)
    now = datetime.now().date()
    action = "Creación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO imagenes (ruta_imagen, titulo_img, estatus, usu_mod, ult_mod, fecha_mov, id_lugar) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (data['ruta_imagen'], data['titulo_img'], estatus, data['usu_mod'], action, now, data['id_lugar'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({'message': 'Imagen creada con éxito', 'id_imagen': new_id}), 201

# Actualizar una imagen existente
@app.route('/api/imagenes/<int:id>', methods=['PUT'])
def update_imagen(id):
    data = request.json
    required_fields = ['ruta_imagen', 'titulo_img', 'estatus', 'usu_mod', 'id_lugar']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    if data['estatus'] not in [0, 1]:
        return jsonify({'error': 'El campo estatus debe ser 0 o 1'}), 400

    now = datetime.now().date()
    action = "Actualización"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE imagenes SET ruta_imagen = %s, titulo_img = %s, estatus = %s, usu_mod = %s, ult_mod = %s, fecha_mov = %s, id_lugar = %s WHERE id_imagen = %s",
        (data['ruta_imagen'], data['titulo_img'], data['estatus'], data['usu_mod'], action, now, data['id_lugar'], id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Imagen no encontrada'}), 404

    return jsonify({'message': f'Imagen con ID {id} actualizada con éxito'})

# Baja lógica de una imagen
@app.route('/api/imagenes/<int:id>', methods=['DELETE'])
def delete_imagen(id):
    now = datetime.now().date()
    action = "Eliminación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE imagenes SET estatus = 0, ult_mod = %s, fecha_mov = %s WHERE id_imagen = %s AND estatus = 1",
        (action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Imagen no encontrada o ya está inactiva'}), 404

    return jsonify({'message': f'Imagen con ID {id} marcada como inactiva'})

#apis de roles

# Obtener todos los roles activos
@app.route('/api/roles', methods=['GET'])
def get_roles():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM roles WHERE estatus = 1")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(roles)

# Obtener un rol por ID
@app.route('/api/roles/<int:id>', methods=['GET'])
def get_rol(id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM roles WHERE id_rol = %s", (id,))
    rol = cursor.fetchone()
    cursor.close()
    conn.close()

    if rol is None or rol['estatus'] == 0:
        return jsonify({'error': 'Rol no encontrado o está inactivo'}), 404
    return jsonify(rol)

# Crear un nuevo rol
@app.route('/api/roles', methods=['POST'])
def create_rol():
    data = request.json
    required_fields = ['nom_rol', 'usu_mod']

    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    estatus = data.get('estatus', 1)
    now = datetime.now().date()
    action = "Creación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO roles (nom_rol, estatus, usu_mod, ult_mod, fecha_mov) VALUES (%s, %s, %s, %s, %s)",
        (data['nom_rol'], estatus, data['usu_mod'], action, now)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({'message': 'Rol creado con éxito', 'id_rol': new_id}), 201

# Actualizar un rol existente
@app.route('/api/roles/<int:id>', methods=['PUT'])
def update_rol(id):
    data = request.json
    required_fields = ['nom_rol', 'estatus', 'usu_mod']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    if data['estatus'] not in [0, 1]:
        return jsonify({'error': 'El campo estatus debe ser 0 o 1'}), 400

    now = datetime.now().date()
    action = "Actualización"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE roles SET nom_rol = %s, estatus = %s, usu_mod = %s, ult_mod = %s, fecha_mov = %s WHERE id_rol = %s",
        (data['nom_rol'], data['estatus'], data['usu_mod'], action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Rol no encontrado'}), 404

    return jsonify({'message': f'Rol con ID {id} actualizado con éxito'})

# Baja lógica de un rol
@app.route('/api/roles/<int:id>', methods=['DELETE'])
def delete_rol(id):
    now = datetime.now().date()
    action = "Eliminación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE roles SET estatus = 0, ult_mod = %s, fecha_mov = %s WHERE id_rol = %s AND estatus = 1",
        (action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Rol no encontrado o ya está inactivo'}), 404

    return jsonify({'message': f'Rol con ID {id} marcado como inactivo'})

#apis usuarios

# Obtener todos los usuarios activos
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE estatus = 1")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(usuarios)

# Obtener un usuario por ID
@app.route('/api/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    if usuario is None or usuario['estatus'] == 0:
        return jsonify({'error': 'Usuario no encontrado o está inactivo'}), 404
    return jsonify(usuario)

# Crear un nuevo usuario
@app.route('/api/usuarios', methods=['POST'])
def create_usuario():
    data = request.json
    required_fields = ['nom_usuario', 'correo', 'contrasena', 'usu_mod']

    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    estatus = data.get('estatus', 1)
    now = datetime.now().date()
    action = "Creación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nom_usuario, correo, contrasena, estatus, usu_mod, ult_mod, fecha_mov) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (data['nom_usuario'], data['correo'], data['contrasena'], estatus, data['usu_mod'], action, now)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({'message': 'Usuario creado con éxito', 'id_usuario': new_id}), 201

# Actualizar un usuario existente
@app.route('/api/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.json
    required_fields = ['nom_usuario', 'correo', 'contrasena', 'estatus', 'usu_mod']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    if data['estatus'] not in [0, 1]:
        return jsonify({'error': 'El campo estatus debe ser 0 o 1'}), 400

    now = datetime.now().date()
    action = "Actualización"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET nom_usuario = %s, correo = %s, contrasena = %s, estatus = %s, usu_mod = %s, ult_mod = %s, fecha_mov = %s WHERE id_usuario = %s",
        (data['nom_usuario'], data['correo'], data['contrasena'], data['estatus'], data['usu_mod'], action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({'message': f'Usuario con ID {id} actualizado con éxito'})

# Baja lógica de un usuario
@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    now = datetime.now().date()
    action = "Eliminación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET estatus = 0, ult_mod = %s, fecha_mov = %s WHERE id_usuario = %s AND estatus = 1",
        (action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Usuario no encontrado o ya está inactivo'}), 404

    return jsonify({'message': f'Usuario con ID {id} marcado como inactivo'})


# Ejecutar la aplicación si este archivo se ejecuta directamente
if __name__ == "__main__":
    app.run(debug=True)