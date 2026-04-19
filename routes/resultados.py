from flask import Blueprint, jsonify, request
from database import get_connection 
from routes.partidos import generar_error

resultados = Blueprint('resultados', __name__)


@resultados.route('/partidos/<int:id>/resultado', methods=['PUT'])
def cargar_resultado(id):
    data = request.get_json()

    campos_requeridos = ['goles_local', 'goles_visitante']
    if not data:
        return generar_error("Cuerpo de solicitud vacío", "BAD_REQUEST"), 400

    for campo in campos_requeridos:
        if campo not in data:
            return generar_error(f"Falta el campo obligatorio: {campo}", "MISSING_FIELD"), 400
        
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT id FROM partidos WHERE id = {id}")
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return generar_error("Partido no encontrado", "NOT_FOUND"), 404
    
    try:
        sql = """
            INSERT INTO resultados (partido_id, goles_local, goles_visitante) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                goles_local = VALUES(goles_local),
                goles_visitante = VALUES(goles_visitante)
        """
        valores = (id, data['goles_local'], data['goles_visitante'])

        cursor.execute(sql, valores)
        conn.commit()

        cursor.close()
        conn.close()

        return "", 204

    except Exception as e:
        return generar_error("Error interno", "SERVER_ERROR", descripcion=str(e)), 500
