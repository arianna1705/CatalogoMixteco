import os
from flask_sqlalchemy import SQLAlchemy

# Configuración de la base de datos
class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:@localhost/catalogo'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 
    SECRET_KEY = 'catamixteco123'

# Inicialización de SQLAlchemy
db = SQLAlchemy()

def init_app(app):
    app.config.from_object(Config)
    db.init_app(app)
