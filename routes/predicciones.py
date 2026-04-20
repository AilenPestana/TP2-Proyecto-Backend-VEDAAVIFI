from flask import Blueprint, jsonify, request
from database import get_connection 

predicciones = Blueprint("predicciones", __name__)

@predicciones.route("/partidos/<int:id>/prediccion", methods = ["POST"]) # Ruta
def predicciones_partidos (id):
    conn = get_connection() 
    cursor = conn.cursor() 
    data = request.get_json() 

    try:
        if data is None: # Por si no se mandó ningun dato
            return jsonify({"error" : "Ingrese todo los datos"}), 400
        
        if "usuario_id" not in data or "goles_local" not in data or "goles_visitante" not in data: # Verifica que los 3 campos tengan data
            return jsonify({"error" : "Datos no correspondientes"}), 400

        cursor.execute("SELECT id FROM partidos WHERE id = %s", (id,)) # Busca si existe el partido
        partido = cursor.fetchone() # Variable que guarda el resultado

        cursor.execute("SELECT id FROM resultados WHERE partido_id = %s", (id,)) # Busca si hay resultado guardado
        resultado = cursor.fetchone()

        cursor.execute("SELECT id FROM predicciones WHERE partido_id = %s and usuario_id = %s", (id, data["usuario_id"])) # Busca si ya hay prediccion
        prediccion = cursor.fetchone()

        if partido is None: 
            return jsonify({"error" : "El partido no existe"}), 404
        
        if resultado: 
            return jsonify({"error" : "El partido ya se jugó"}), 409

        if prediccion: 
            return jsonify({"error" : "El partido ya se jugó"}), 409

        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (data["usuario_id"],))
        usuario = cursor.fetchone()
        if usuario is None:
            return jsonify({"error": "El usuario no existe"}), 404

        cursor.execute (
            "INSERT INTO predicciones (partido_id, usuario_id, goles_local, goles_visitante)" \
            "VALUES (%s, %s, %s, %s)",
            (id, data["usuario_id"], data["goles_local"], data["goles_visitante"])
        )
        conn.commit() 

        return jsonify(data), 201

    except Exception as e: # Para cualquier error inesperado
        print(e) 
        return jsonify({"error" : "Error interno del servidor"}), 500

    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()