import os
import psycopg2
import bcrypt
from dotenv import load_dotenv

# Carga las variables del archivo .env automáticamente
load_dotenv()

# ── Configuración de conexión (desde variables de entorno o valores por defecto) ──────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.environ.get("DATABASE_HOST", os.environ.get("DB_HOST", "localhost")),
    "port":     int(os.environ.get("DATABASE_PORT", os.environ.get("DB_PORT", "5433"))),
    "dbname":   os.environ.get("DATABASE_NAME", os.environ.get("DB_NAME", "nicaplex")),
    "user":     os.environ.get("DATABASE_USER", os.environ.get("DB_USER", "nicaplex_user")),
    "password": os.environ.get("DATABASE_PASSWORD", os.environ.get("DB_PASSWORD", "nicaplex_pass")),
}


def get_conexion():
    """Retorna una conexión activa a PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


# ── Inicialización de tablas ───────────────────────────────────────────────────

def inicializar_bd():
    """Crea las tablas necesarias si no existen."""
    with get_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id          SERIAL PRIMARY KEY,
                    username    VARCHAR(50)  UNIQUE NOT NULL,
                    email       VARCHAR(100) UNIQUE NOT NULL,
                    password    VARCHAR(255) NOT NULL,
                    creado_en   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()


# ── Operaciones de usuario ─────────────────────────────────────────────────────

def registrar_usuario(username: str, email: str, password: str) -> dict:
    """
    Registra un nuevo usuario.
    Retorna {"ok": True, "mensaje": "..."} o {"ok": False, "mensaje": "..."}
    """
    if not username or not email or not password:
        return {"ok": False, "mensaje": "Todos los campos son obligatorios."}

    if len(password) < 6:
        return {"ok": False, "mensaje": "La contraseña debe tener al menos 6 caracteres."}

    # Hash seguro de la contraseña
    hash_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        with get_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO usuarios (username, email, password) VALUES (%s, %s, %s)",
                    (username.strip(), email.strip().lower(), hash_pw)
                )
            conn.commit()
        return {"ok": True, "mensaje": "Registro exitoso."}

    except psycopg2.errors.UniqueViolation:
        return {"ok": False, "mensaje": "El correo o nombre de usuario ya está registrado."}
    except Exception as e:
        return {"ok": False, "mensaje": f"Error al registrar: {e}"}


def login_usuario(email: str, password: str) -> dict:
    """
    Verifica credenciales.
    Retorna {"ok": True, "username": "...", "email": "..."} o {"ok": False, "mensaje": "..."}
    """
    if not email or not password:
        return {"ok": False, "mensaje": "Ingresá tu correo y contraseña."}

    try:
        with get_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT username, email, password FROM usuarios WHERE email = %s",
                    (email.strip().lower(),)
                )
                fila = cur.fetchone()

        if not fila:
            return {"ok": False, "mensaje": "Correo o contraseña incorrectos."}

        username, email_db, hash_pw = fila

        if not bcrypt.checkpw(password.encode("utf-8"), hash_pw.encode("utf-8")):
            return {"ok": False, "mensaje": "Correo o contraseña incorrectos."}

        return {"ok": True, "username": username, "email": email_db}

    except Exception as e:
        return {"ok": False, "mensaje": f"Error de conexión: {e}"}
