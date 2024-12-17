from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_usuario = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(50), nullable=False, unique=True)
    contrasena = db.Column(db.String(100), nullable=False)  # Contraseña hasheada
    estatus = db.Column(db.Integer, nullable=False, default=1)  # Activo (1) o Inactivo (0)
    usu_mod = db.Column(db.String(50), nullable=True)
    ult_mod = db.Column(db.String(50), nullable=True)
    fecha_mov = db.Column(db.Date, nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)

    # Relación con la tabla Rol
    rol = db.relationship('Rol', backref=db.backref('usuarios', lazy=True))

    # Métodos para manejar la contraseña
    def set_password(self, password):
        """Genera un hash de la contraseña."""
        self.contrasena = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
        return check_password_hash(self.contrasena, password)

    def to_dict(self):
        """Convierte un objeto Usuario en un diccionario para facilitar la conversión a JSON."""
        return {
            'id_usuario': self.id_usuario,
            'nom_usuario': self.nom_usuario,
            'correo': self.correo,
            'estatus': self.estatus,
            'usu_mod': self.usu_mod,
            'ult_mod': self.ult_mod,
            'fecha_mov': self.fecha_mov.isoformat(),  # Convertir la fecha a formato ISO
            'id_rol': self.id_rol,
            'rol': self.rol.nom_rol  # Si deseas incluir el nombre del rol en la respuesta
        }

    def __repr__(self):
        return f'<Usuario {self.nom_usuario}, Rol: {self.rol.nom_rol}>'


class Rol(db.Model):
    __tablename__ = 'roles'
    id_rol = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_rol = db.Column(db.String(20), nullable=False)  # Ejemplo: 'Administrador', 'Usuario'
    estatus = db.Column(db.Integer, nullable=False, default=1)  # Activo (1) o Inactivo (0)
    usu_mod = db.Column(db.String(50), nullable=True)
    ult_mod = db.Column(db.String(50), nullable=True)
    fecha_mov = db.Column(db.Date, nullable=False)




class Imagen(db.Model):
    __tablename__ = 'imagenes'
    id_imagen = db.Column(db.Integer, primary_key=True)
    ruta_imagen = db.Column(db.String(100), nullable=False)
    titulo_img = db.Column(db.String(50), nullable=False)
    estatus = db.Column(db.Integer, nullable=False)
    usu_mod = db.Column(db.String(50), nullable=False)
    ult_mod = db.Column(db.String(50), nullable=False)
    fecha_mov = db.Column(db.Date, nullable=False)
    id_lugar = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id_imagen': self.id_imagen,
            'ruta_imagen': self.ruta_imagen,
            'titulo_img': self.titulo_img,
            'estatus': self.estatus,
            'usu_mod': self.usu_mod,
            'ult_mod': self.ult_mod,
            'fecha_mov': str(self.fecha_mov),
            'id_lugar': self.id_lugar
        }



class Lugares(db.Model):
    __tablename__ = 'lugares'

    # Definición de las columnas según tu estructura
    id_lugar = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_lugar = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(50), nullable=False)
    ubicacion = db.Column(db.String(50), nullable=False)
    estatus = db.Column(db.Integer, nullable=False)
    usu_mod = db.Column(db.String(50), nullable=False)
    ult_mod = db.Column(db.String(50), nullable=False)
    fecha_mov = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    def __init__(self, nom_lugar, descripcion, ubicacion, estatus, usu_mod, ult_mod, fecha_mov=None):
        self.nom_lugar = nom_lugar
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.estatus = estatus
        self.usu_mod = usu_mod
        self.ult_mod = ult_mod
        if fecha_mov:
            self.fecha_mov = fecha_mov
        else:
            self.fecha_mov = datetime.utcnow().date()

    def to_dict(self):
        return {
            'id_lugar': self.id_lugar,
            'nom_lugar': self.nom_lugar,
            'descripcion': self.descripcion,
            'ubicacion': self.ubicacion,
            'estatus': self.estatus,
            'usu_mod': self.usu_mod,
            'ult_mod': self.ult_mod,
            'fecha_mov': str(self.fecha_mov),
        }

    # Método para actualizar un lugar
    def actualizar(self, nom_lugar, descripcion, ubicacion, estatus, usu_mod, ult_mod, fecha_mov=None):
        self.nom_lugar = nom_lugar
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.estatus = estatus
        self.usu_mod = usu_mod
        self.ult_mod = ult_mod
        if fecha_mov:
            self.fecha_mov = fecha_mov
        else:
            self.fecha_mov = datetime.utcnow().date()






    def __repr__(self):
        return f'<Rol {self.nom_rol}>'
