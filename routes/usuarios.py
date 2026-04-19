from flask import Blueprint, jsonify, request
from database import get_connection
from utils import paginar # Importa la función de paginación (limit, offset y links)
usuarios = Blueprint('usuarios', __name__)


@usuarios.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()

    # Validación: chequea que existan los campos obligatorios
    if not data or 'nombre' not in data or 'email' not in data:
        return jsonify({"error": "Se requieren nombre y email"}), 400

    
    conn = get_connection() # Abre conexión a la base de datos
    cursor = conn.cursor() # Crea un cursor para ejecutar queries SQL

    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, email) VALUES (%s, %s)",
            (data['nombre'], data['email'])
        )
        conn.commit()
        nuevo_id = cursor.lastrowid  # Obtiene el ID del último registro insertado
      
    except Exception:
         # Si hay error (por ejemplo email duplicado)
        return jsonify({"error": "El email ya esta registrado"}), 409
    finally:
        cursor.close()
        conn.close()

    return jsonify({"id": nuevo_id, "mensaje": "Usuario creado"}), 201  # Devuelve respuesta exitosa con el ID creado


@usuarios.route('/usuarios', methods=['GET'])
def listar_usuarios():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # Cursor en modo diccionario (devuelve resultados como dict y no tuplas)

    cursor.execute("SELECT COUNT(*) as total FROM usuarios")  # Cuenta la cantidad total de usuarios en la tabla
    total = cursor.fetchone()['total']

    links, limit, offset = paginar(request, total) # Llama a la función de paginación

    cursor.execute("SELECT * FROM usuarios LIMIT %s OFFSET %s", (limit, offset)) # Ejecuta query con paginación
    usuarios = cursor.fetchall()  # Trae todos los usuarios de la query

    cursor.close()
    conn.close()

    return jsonify({
        "data": usuarios,
        "total": total,
        "links": links
    }), 200

