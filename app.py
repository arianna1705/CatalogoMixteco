from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from models import db, Usuario, Rol, Imagen, Lugares
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from datetime import date
from werkzeug.utils import secure_filename
from functools import wraps
from config import Config, init_app

app = Flask(__name__)
app.secret_key = 'catamixteco123'
app.config.from_object(Config)
db.init_app(app)



@app.route('/')
def login():
    return render_template('sesion.html')



# Decorador para verificar sesión
def login_required(f):
    def wrap(*args, **kwargs):
        if 'id_usuario' not in session:
            return redirect(url_for('show_login_page'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route('/index', methods=['GET'])
@login_required
def index():
    return render_template('index.html')

@app.route('/lugares', methods=['GET'])
@login_required
def lugares():
    return render_template('lugares.html')

@app.route('/imagenes', methods=['GET'])
@login_required
def imagenes():
    return render_template('imagenes.html')

@app.route('/usuarios', methods=['GET'])
@login_required
def usuarios():
    return render_template('usuarios.html')


# SESION
@app.route('/sesion', methods=['GET'])
def show_login_page():
    return render_template('sesion.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    correo = request.json.get('correo')
    contrasena = request.json.get('contrasena')

    print(f"Correo recibido: {correo}")
    print(f"Contraseña recibida: {contrasena}")

    # Buscar el usuario por correo
    usuario = Usuario.query.filter_by(correo=correo).first()

    if usuario:
        print(f"Usuario encontrado: {usuario.correo}, Contraseña almacenada: {usuario.contrasena}")
        
        # Verificar la contraseña usando check_password_hash
        #resultado_comparacion = check_password_hash(usuario.contrasena, contrasena)

        resultado_comparacion = check_password_hash(usuario.contrasena, contrasena)
        print(f"Resultado de la comparación: {resultado_comparacion}")
        
        if resultado_comparacion:  # Si la contraseña es correcta
            session['id_usuario'] = usuario.id_usuario
            session['rol'] = usuario.id_rol

            return jsonify({'status': 'success', 'id_rol':session['rol'],'message':'Bienvenido...!'})
        else:
            return jsonify({'status': 'error', 'message':'Datos erroneos...!'})
    else:
        return jsonify({'status': 'error', 'message':'No se encontro el correo...!'})


#CEERRAR SESION
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Elimina la sesión del usuario
    return redirect(url_for('login'))


#REGISTRO

# Ruta para la página de registro
@app.route('/registrarse', methods=['GET'])
def show_register_page():
    return render_template('registrarse.html')


# Ruta para registrar nuevos usuarios
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nombre = data.get('nombre')
    correo = data.get('correo')
    contrasena = data.get('contrasena')

    if not nombre or not correo or not contrasena:
        return jsonify({'status': 'error', 'message': 'Todos los campos son obligatorios'})

    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({'status': 'error', 'message': 'El correo ya está registrado'})

    nuevo_usuario = Usuario(
        nom_usuario=nombre,
        correo=correo,
        contrasena=generate_password_hash(contrasena),
        estatus=1,
        usu_mod=nombre,
        ult_mod='Registro inicial',
        fecha_mov=date.today(),
        id_rol=2  # Rol de usuario por defecto
    )

    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Usuario registrado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Error al registrar el usuario: {str(e)}'})

#ApIS IMAGENES
# Obtener todas las imágenes activas
@app.route('/api/imagenes', methods=['GET'])
def get_imagenes():
    try:
        imagenes = Imagen.query.filter_by(estatus=1).all()
        if not imagenes:
            return jsonify({'error': 'No hay imágenes activas'}), 404
        return jsonify([imagen.to_dict() for imagen in imagenes])  # Suponiendo que tienes el método `to_dict()` en tu modelo Imagen
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Obtener una imagen por ID
@app.route('/api/imagenes/<int:id>', methods=['GET'])
def get_imagen(id):
    try:
        imagen = Imagen.query.filter_by(id_imagen=id, estatus=1).first()
        if imagen is None:
            return jsonify({'error': 'Imagen no encontrada o está inactiva'}), 404
        return jsonify(imagen.to_dict())  # Suponiendo que tienes el método `to_dict()` en tu modelo Imagen
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Crear una nueva imagen
@app.route('/api/imagenes', methods=['POST'])
def create_imagen():
    try:
        data = request.json
        required_fields = ['ruta_imagen', 'titulo_img', 'usu_mod', 'id_lugar']

        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'El campo {field} es obligatorio'}), 400

        estatus = data.get('estatus', 1)
        now = datetime.now().date()
        action = "Creación"

        nueva_imagen = Imagen(
            ruta_imagen=data['ruta_imagen'],
            titulo_img=data['titulo_img'],
            estatus=estatus,
            usu_mod=data['usu_mod'],
            ult_mod=action,
            fecha_mov=now,
            id_lugar=data['id_lugar']
        )

        db.session.add(nueva_imagen)
        db.session.commit()

        return jsonify({'message': 'Imagen creada con éxito', 'id_imagen': nueva_imagen.id_imagen}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Actualizar una imagen existente
@app.route('/api/imagenes/<int:id>', methods=['PUT'])
def update_imagen(id):
    try:
        data = request.json
        required_fields = ['ruta_imagen', 'titulo_img', 'estatus', 'usu_mod', 'id_lugar']

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'El campo {field} es obligatorio'}), 400

        if data['estatus'] not in [0, 1]:
            return jsonify({'error': 'El campo estatus debe ser 0 o 1'}), 400

        imagen = Imagen.query.filter_by(id_imagen=id).first()

        if not imagen:
            return jsonify({'error': 'Imagen no encontrada'}), 404

        imagen.ruta_imagen = data['ruta_imagen']
        imagen.titulo_img = data['titulo_img']
        imagen.estatus = data['estatus']
        imagen.usu_mod = data['usu_mod']
        imagen.ult_mod = "Actualización"
        imagen.fecha_mov = datetime.now().date()
        imagen.id_lugar = data['id_lugar']

        db.session.commit()

        return jsonify({'message': f'Imagen con ID {id} actualizada con éxito'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Baja lógica de una imagen
@app.route('/api/imagenes/<int:id>', methods=['DELETE'])
def delete_imagen(id):
    try:
        imagen = Imagen.query.filter_by(id_imagen=id, estatus=1).first()

        if not imagen:
            return jsonify({'error': 'Imagen no encontrada o ya está inactiva'}), 404

        imagen.estatus = 0
        imagen.ult_mod = "Eliminación"
        imagen.fecha_mov = datetime.now().date()

        db.session.commit()

        return jsonify({'message': f'Imagen con ID {id} marcada como inactiva'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#APIS DE ROLES

# Obtener todos los roles activos
@app.route('/api/roles', methods=['GET'])
def get_roles():
    conn = db.session.connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM roles WHERE estatus = 1")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(roles)

# Obtener un rol por ID
@app.route('/api/roles/<int:id>', methods=['GET'])
def get_rol(id):
    conn = db.session.connection()
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

    conn = db.session.connection()
    cursor = conn.cursor(dictionary=True)
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

    conn = db.session.connection()
    cursor = conn.cursor(dictionary=True)
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

    conn = db.session.connection()
    cursor = conn.cursor(dictionary=True)
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






# Obtener todos los lugares activos
@app.route('/api/lugares', methods=['GET'])
def get_lugares():
    lugares = Lugares.query.filter_by(estatus=1).all()
    return jsonify([lugar.to_dict() for lugar in lugares])

# Obtener un lugar por ID 
@app.route('/api/lugares/<int:id>', methods=['GET'])
def get_lugar(id):
    lugar = Lugares.query.filter_by(id_lugar=id, estatus=1).first()
    if lugar:
        return jsonify(lugar.to_dict())
    return jsonify({'error': 'Lugar no encontrado o está inactivo'}), 404

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

    new_lugar = Lugares(
        nom_lugar=data['nom_lugar'],
        descripcion=data['descripcion'],
        ubicacion=data['ubicacion'],
        estatus=estatus,
        usu_mod=data['usu_mod'],
        ult_mod=action,
        fecha_mov=now
    )

    try:
        db.session.add(new_lugar)
        db.session.commit()
        return jsonify({'message': 'Lugar creado con éxito', 'id_lugar': new_lugar.id_lugar}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Actualizar un lugar existente
@app.route('/api/lugares/<int:id>', methods=['PUT'])
def update_lugar(id):
    data = request.json
    lugar = Lugares.query.get(id)
    if not lugar:
        return jsonify({'error': 'Lugar no encontrado'}), 404
    
    for field, value in data.items():
        setattr(lugar, field, value)
    
    try:
        db.session.commit()
        return jsonify({'message': f'Lugar con ID {id} actualizado con éxito'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Baja lógica de un lugar
@app.route('/api/lugares/<int:id>', methods=['DELETE'])
def delete_lugar(id):
    lugar = Lugares.query.get(id)
    if not lugar:
        return jsonify({'error': 'Lugar no encontrado'}), 404

    lugar.estatus = 0
    lugar.ult_mod = "Eliminación"
    lugar.fecha_mov = datetime.now()

    try:
        db.session.commit()
        return jsonify({'message': f'Lugar con ID {id} marcado como inactivo'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    
# Obtener todos los usuarios activos
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = Usuario.query.filter_by(estatus=1).all()  # Filtrar solo usuarios activos
    if not usuarios:
        return jsonify({'error': 'No hay usuarios activos'}), 404
    return jsonify([usuario.to_dict() for usuario in usuarios])  # Usando `to_dict()` para convertir los objetos

# Obtener un usuario por ID
@app.route('/api/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    usuario = Usuario.query.filter_by(id_usuario=id, estatus=1).first()  # Filtrar por id y estatus activo
    if usuario is None:
        return jsonify({'error': 'Usuario no encontrado o está inactivo'}), 404
    return jsonify(usuario.to_dict())  # Usando `to_dict()` para convertir el objeto

# Crear un nuevo usuario
@app.route('/api/usuarios', methods=['POST'])
def create_usuario():
    data = request.json
    required_fields = ['nom_usuario', 'correo', 'contrasena', 'usu_mod']

    # Validación de campos requeridos
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    # Crear nuevo usuario
    estatus = data.get('estatus', 1)  # Valor por defecto estatus = 1 (activo)
    now = datetime.now().date()
    action = "Creación"

    # Usar el modelo Usuario para crear un nuevo registro
    nuevo_usuario = Usuario(
        nom_usuario=data['nom_usuario'],
        correo=data['correo'],
        contrasena=generate_password_hash(data['contrasena']),
        estatus=estatus,
        usu_mod=data['usu_mod'],
        ult_mod=action,
        fecha_mov=now
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({'message': 'Usuario creado con éxito', 'id_usuario': nuevo_usuario.id_usuario}), 201

# Actualizar un usuario existente
@app.route('/api/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.json
    required_fields = ['nom_usuario', 'correo', 'contrasena', 'estatus', 'usu_mod']

    # Validación de campos requeridos
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    if data['estatus'] not in [0, 1]:
        return jsonify({'error': 'El campo estatus debe ser 0 o 1'}), 400

    # Buscar el usuario a actualizar
    usuario = Usuario.query.filter_by(id_usuario=id).first()
    if usuario is None:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # Actualizar los campos
    usuario.nom_usuario = data['nom_usuario']
    usuario.correo = data['correo']
    usuario.contrasena = generate_password_hash(data['contrasena'])
    usuario.estatus = data['estatus']
    usuario.usu_mod = data['usu_mod']
    usuario.ult_mod = "Actualización"
    usuario.fecha_mov = datetime.now().date()

    db.session.commit()

    return jsonify({'message': f'Usuario con ID {id} actualizado con éxito'})

# Baja lógica de un usuario
@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    # Buscar el usuario a eliminar
    usuario = Usuario.query.filter_by(id_usuario=id, estatus=1).first()
    if usuario is None:
        return jsonify({'error': 'Usuario no encontrado o ya está inactivo'}), 404

    # Marcar como inactivo
    usuario.estatus = 0
    usuario.ult_mod = "Eliminación"
    usuario.fecha_mov = datetime.now().date()

    db.session.commit()

    return jsonify({'message': f'Usuario con ID {id} marcado como inactivo'})









#carga de apartados en la página de usurios


@app.route('/servicios')
def servicios():
    return render_template("servicios.html")

@app.route('/about')
def galeria():
    return render_template("galeria.html")


@app.route('/portfolio')
def portfolio():
    return render_template("portfolio.html")





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

