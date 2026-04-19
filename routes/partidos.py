from flask import Blueprint, jsonify, request
from database import get_connection  

partidos = Blueprint('partidos', __name__)

def generar_error(mensaje, codigo="XXX", nivel="error", descripcion=None):
    return jsonify({
        "errors": [
            {
                "code": codigo,
                "message": mensaje,
                "level": nivel,
                "description": descripcion or mensaje
            }
        ]
    })

@partidos.route('/partidos', methods=['POST'])
def crear_partido():
    data = request.get_json()

    # Validaciones obligatorias del contrato
    campos_requeridos = ['equipo_local', 'equipo_visitante', 'fecha', 'fase']
    if not data:
        return generar_error("Cuerpo de solicitud vacío", "BAD_REQUEST"), 400

    for campo in campos_requeridos:
        if campo not in data:
            return generar_error(f"Falta el campo obligatorio: {campo}", "MISSING_FIELD"), 400
    # Validar enum de Fase según contrato
    fases_validas = ["grupos", "dieciseisavos", "octavos", "cuartos", "semis", "final"]
    if data['fase'].lower() not in fases_validas:
        return generar_error("Fase no válida", "INVALID_FASE"), 400
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO partidos (equipo_local, equipo_visitante, fecha, fase) 
            VALUES (%s, %s, %s, %s)
        """
        valores = (data['equipo_local'], data['equipo_visitante'], data['fecha'], data['fase'].lower())

        cursor.execute(sql, valores)
        conn.commit()

        cursor.close()
        conn.close()

        # Respuesta 201 Created según contrato
        return "", 201

    except Exception as e:
        return generar_error("Error interno", "SERVER_ERROR", descripcion=str(e)), 500

@partidos.route('/partidos/<int:id>', methods=['DELETE'])
def eliminar_partido(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar existencia para devolver 404
        cursor.execute("SELECT id FROM partidos WHERE id = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return generar_error("Partido no encontrado", "NOT_FOUND"), 404

        cursor.execute("DELETE FROM partidos WHERE id = %s", (id,))
        conn.commit()

        cursor.close()
        conn.close()

        # Respuesta 204 No Content según contrato
        return "", 204

    except Exception as e:
         return generar_error("Error al eliminar", "SERVER_ERROR", 
    descripcion=str(e)), 500 
