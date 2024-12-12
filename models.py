from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_usuario = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(50), nullable=False, unique=True)
    contrasena = db.Column(db.String(100), nullable=False)
    estatus = db.Column(db.Integer, nullable=False)
    usu_mod = db.Column(db.String(50), nullable=False)
    ult_mod = db.Column(db.String(50), nullable=False)
    fecha_mov = db.Column(db.Date, nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)

    rol = db.relationship('Rol', backref=db.backref('usuarios', lazy=True))

class Rol(db.Model):
    __tablename__ = 'roles'
    id_rol = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_rol = db.Column(db.Enum('Administrador', 'Usuario'), nullable=False)
    estatus = db.Column(db.Integer, nullable=False)
    usu_mod = db.Column(db.String(50), nullable=False)
    ult_mod = db.Column(db.String(50), nullable=False)
    fecha_mov = db.Column(db.Date, nullable=False)

