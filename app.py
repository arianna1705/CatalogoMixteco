from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from config import create_engine
from models import db, Usuario, Rol
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from functools import wraps

# Inicialización de la app
app = Flask(__name__)
app.secret_key = "123456"  
app.config.from_object(create_engine)




app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/catalogo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la extensión SQLAlchemy
db = SQLAlchemy(app)


# Crear las tablas si no existen        
with app.app_context():
    db.create_all()

# Decorador para rutas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))  # Redirigir al login
        return f(*args, **kwargs)
    return decorated_function

# Página de login
@app.route('/')
def login():
    return render_template('sesion.html')


@app.route('/registrarse.html', methods=['POST'])
def registrarse():
    data = request.get_json()
    if 'nombre' not in data or 'correo' not in data or 'contrasena' not in data:
        return jsonify({'status': 'error', 'message': 'Faltan datos requeridos'}), 400

    nombre = data['nombre']
    correo = data['correo']
    contrasena = data['contrasena']

    # Verificar si el correo ya está registrado
    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({'status': 'error', 'message': 'El correo ya está registrado'}), 400

    # Crear un nuevo usuario
    nuevo_usuario = Usuario(
        nom_usuario=nombre,
        correo=correo,
        contrasena=generate_password_hash(contrasena),
        estatus=1,
        usu_mod='Admin',
        ult_mod='Creación',
        fecha_mov=datetime.now(),
        id_rol=1
    )

    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Autenticación del usuario
@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.json  # Obtiene los datos en formato JSON
    correo = data.get('correo')
    contrasena = data.get('contrasena')

    # Verifica si el usuario existe y está activo
    user = Usuario.query.filter_by(correo=correo, estatus=1).first()
    if user and check_password_hash(user.contrasena, contrasena):
        # Guardar la sesión del usuario
        session['usuario_id'] = user.id_usuario
        session['correo'] = user.correo
        session['rol'] = Rol.query.get(user.id_rol).nom_rol  # Obtener rol
        return jsonify({"status": "success", "message": "Inicio de sesión exitoso"})
    
    return jsonify({"status": "error", "message": "Correo o contraseña incorrectos"}), 401

#authenticación paea mandarte de una pagina a otra

# Dashboard protegido
@app.route('/registro')
@login_required
def dashboard():
    #return render_template('index.html', usuario=session['correo'], rol=session['rol'])
    rol = session['rol']
    if rol == 'admin':
       return redirect(url_for('lugares'))
    else:
       return redirect(url_for('index'))

# Cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "success")
    return redirect(url_for('login'))

# Ruta para el apartado de usuarios
@app.route('/usuarios.html')
@login_required
def usuarios():
    return render_template('usuarios.html', usuario=session['correo'], rol=session['rol'])

# Ruta para la página de lugares
@app.route('/lugares.html')
@login_required
def lugares():
    return render_template("lugares.html", usuario=session['correo'], rol=session['rol'])

@app.route('/imagenes.html')
@login_required
def imagenes():
    return render_template("imagenes.html", usuario=session['correo'], rol=session['rol'])

@app.route('/perfil.html')
@login_required
def perfil():
    return render_template("perfil.html", usuario=session['correo'], rol=session['rol'])





# APIs para lugares

# Obtener todos los lugares activos
@app.route('/api/lugares', methods=['GET'])
def get_lugares():
    lugares = lugares.query.filter_by(estatus=1).all()
    return jsonify([lugar.to_dict() for lugar in lugares])

# Obtener un lugar por ID 
@app.route('/api/lugares/<int:id>', methods=['GET'])
def get_lugar(id):
    lugar = lugares.query.filter_by(id_lugar=id, estatus=1).first()
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

    new_lugar = lugares(
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
    lugar = lugares.query.get(id)
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
    lugar = lugares.query.get(id)
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
    

#carga de apartados en la página de usurios

@app.route('/index')
def home():
    return render_template("index.html")
#pagina de servicios

@app.route('/servicios')
def servicios():
    return render_template("servicios.html")

@app.route('/about')
def galeria():
    return render_template("galeria.html")


@app.route('/portfolio')
def portfolio():
    return render_template("portfolio.html")

#vuelve a redirigirte al index de usuario

@app.route('/index')
def index():
    return render_template("index.html")




if __name__ == '__main__':
    app.run(debug=True)
