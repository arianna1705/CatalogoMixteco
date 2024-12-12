from sqlalchemy import create_engine

try:
    # Crear el motor de conexión
    engine = create_engine('mysql+pymysql://root:@localhost/catalogo')
    
    # Intentar conectarse a la base de datos
    connection = engine.connect()
    
    print("Conexión exitosa a la base de datos")
    
except Exception as e:
    print(f"Error de conexión: {e}")
    
finally:
    # Asegúrate de cerrar la conexión
    if connection:
        connection.close()
