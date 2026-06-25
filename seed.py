"""
Script para insertar un usuario de prueba en la base de datos.
Ejecutar con: python seed.py
Requiere que Docker esté corriendo: docker-compose up -d
"""
from database import inicializar_bd, registrar_usuario

inicializar_bd()

resultado = registrar_usuario(
    username="admin",
    email="admin@nicaplex.com",
    password="admin123"
)

print(resultado["El Usuario Creado"])
