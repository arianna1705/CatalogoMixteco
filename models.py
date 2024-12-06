from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_usuario = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(11), nullable=False) 

    def __repr__(self):
        return f'<Usuario {self.nom_usuario}>'

class Nivelusuario(db.Model):
    __tablename__ = 'niveles'

    id_nivel = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nivel = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Nivelusuario {self.nivel}>'

