from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_usuario = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    contrasena = db.Column(db.String(11), nullable=False)
    estatus = db.Column(db.Integer, default=1)  
    usu_mod = db.Column(db.String(50))
    ult_mod = db.Column(db.String(50))
    fecha_mov = db.Column(db.Date)
    id_rol = db.Column(db.Integer, nullable=False)

class Nivelusuario(db.Model):
    __tablename__ = 'niveles'

    id_nivel = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nivel = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Nivelusuario {self.nivel}>'

