NicaPlex - Aplicación de Películas
===================================
Proyecto escolar desarrollado con Flet (Python) y PostgreSQL.

REQUISITOS
----------
- Python 3.13+
- Docker Desktop
- pip install -r requirements.txt

CONFIGURACIÓN
-------------
1. Copiar .env.example a .env y completar las variables:
   cp .env.example .env

2. Levantar la base de datos con Docker:
   docker-compose up -d

3. (Opcional) Insertar usuario de prueba:
   python seed.py

4. Ejecutar la aplicación:
   python PaginaBienvenida.py

ESTRUCTURA
----------
PaginaBienvenida.py  - Pantalla de bienvenida
PaginaLogin.py       - Formulario de inicio de sesión
PaginaRegistro.py    - Formulario de registro
PaginaInicio.py      - Catálogo de películas (requiere login)
PaginaDetalle.py     - Detalle de película individual
database.py          - Conexión y operaciones con PostgreSQL
docker-compose.yml   - Configuración del contenedor PostgreSQL
seed.py              - Script para insertar usuario de prueba

APIS UTILIZADAS
---------------
- OMDB API (omdbapi.com) - Datos y pósters de películas
- YouTube - Trailers (abre en navegador del dispositivo)

CREDENCIALES POR DEFECTO (desarrollo)
--------------------------------------
Base de datos: nicaplex / nicaplex_user / nicaplex_pass
Puerto:        5433
