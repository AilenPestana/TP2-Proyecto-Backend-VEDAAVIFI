from flask import Blueprint, request, jsonify
from database import get_connection
from utils import paginar

# Blueprint unificado
partidos = Blueprint('partidos', __name__)

# --- FUNCIÓN AUXILIAR PARA ERRORES (CONTRATO OPENAPI) ---
def generar_error(codigo, mensaje, nivel="error", descripcion=None):
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

# =======================================================
# PERSONAS 2 y 3: GET /partidos (Listado y Filtros)
# =======================================================
@partidos.route('/partidos', methods=['GET'])
def get_partidos():
    equipo = request.args.get('equipo')
    fecha  = request.args.get('fecha')
    fase   = request.args.get('fase')

    filtros_sql = "WHERE 1=1"
    params = []

    if equipo:
        filtros_sql += " AND (equipo_local = %s OR equipo_visitante = %s)"
        params.extend([equipo, equipo])
    if fecha:
        filtros_sql += " AND fecha = %s"
        params.append(fecha)
    if fase:
        filtros_sql += " AND fase = %s"
        params.append(fase)

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT COUNT(*) as total FROM partidos {filtros_sql}", params)
        total = cursor.fetchone()['total']

        links, limit, offset = paginar(request, total)

        sql_data = f"SELECT * FROM partidos {filtros_sql} LIMIT %s OFFSET %s"
        cursor.execute(sql_data, params + [limit, offset])
        lista_partidos = cursor.fetchall()
        
        return jsonify({"total": total, "partidos": lista_partidos, "_links": links}), 200
    except Exception as e:
        return generar_error("SERVER_ERROR", "Error al listar", descripcion=str(e)), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# =======================================================
# PERSONA 5: GET /partidos/{id} (Detalle con Resultado)
# =======================================================
@partidos.route('/partidos/<id>', methods=['GET'])
def obtener_partido(id):
    if not id.isdigit():
        return generar_error("Bad Request", "El ID del partido tiene que ser un numero."), 400
    try: 
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, r.goles_local, r.goles_visitante
            FROM partidos p
            LEFT JOIN resultados r ON r.partido_id = p.id   
            WHERE p.id = %s
        """, (id,))
        partido = cursor.fetchone()
        
        if not partido:
            return generar_error("NOT_FOUND", "Partido no encontrado"), 404
            
        resultado_formateado = {
            "id": partido['id'],
            "equipo_local": partido['equipo_local'],
            "equipo_visitante": partido['equipo_visitante'],
            "fecha": str(partido['fecha']),
            "fase": partido['fase'],
            "resultado": None
        }
        
        if partido['goles_local'] is not None:
            resultado_formateado['resultado'] = {
                "local": partido['goles_local'],
                "visitante": partido['goles_visitante']
            }
        
        return jsonify(resultado_formateado), 200
    except Exception as e: 
        return generar_error("SERVER_ERROR", "Error al obtener el detalle", descripcion=str(e)), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# =======================================================
# PERSONA 4 (VOS): POST /partidos (Creación)
# =======================================================
@partidos.route('/partidos', methods=['POST'])
def crear_partido():
    data = request.get_json()
    campos_req = ['equipo_local', 'equipo_visitante', 'fecha', 'fase']
    
    if not data or not all(k in data for k in campos_req):
        return generar_error("BAD_REQUEST", "Faltan campos obligatorios"), 400

    fases_validas = ["grupos", "dieciseisavos", "octavos", "cuartos", "semis", "final"]
    if data['fase'].lower() not in fases_validas:
        return generar_error("INVALID_FASE", "Fase no válida"), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO partidos (equipo_local, equipo_visitante, fecha, fase) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (data['equipo_local'], data['equipo_visitante'], data['fecha'], data['fase'].lower()))
        conn.commit()
        return "", 201
    except Exception as e:
        return generar_error("SERVER_ERROR", "Error al crear", descripcion=str(e)), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# =======================================================
# PERSONA 5: PATCH /partidos/{id} (Modificación parcial)
# =======================================================
@partidos.route('/partidos/<int:id>', methods=['PATCH'])
def modificar_partido(id):
    data = request.get_json()
    if not data:
        return generar_error("BAD_REQUEST", "El cuerpo no puede estar vacío"), 400

    campos_permitidos = ['equipo_local', 'equipo_visitante', 'fecha', 'fase']
    if 'fase' in data and data['fase'].lower() not in ["grupos", "dieciseisavos", "octavos", "cuartos", "semis", "final"]:
        return generar_error("INVALID_FASE", "Valor de fase inválido"), 400

    sets, params = [], []
    for campo in campos_permitidos:
        if campo in data:
            sets.append(f"{campo} = %s")
            params.append(data[campo])

    if not sets:
        return generar_error("BAD_REQUEST", "No se enviaron campos válidos"), 400

    params.append(id)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM partidos WHERE id = %s", (id,))
        if not cursor.fetchone():
            return generar_error("NOT_FOUND", "Partido no encontrado"), 404

        cursor.execute(f"UPDATE partidos SET {', '.join(sets)} WHERE id = %s", params)
        conn.commit()
        return '', 204
    except Exception as e:
        return generar_error("SERVER_ERROR", "Error al actualizar", descripcion=str(e)), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# =======================================================
# PERSONA 4 (VOS): DELETE /partidos/{id} (Eliminación)
# =======================================================
@partidos.route('/partidos/<int:id>', methods=['DELETE'])
def eliminar_partido(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM partidos WHERE id = %s", (id,))
        if not cursor.fetchone():
            return generar_error("NOT_FOUND", "Partido no encontrado"), 404
            
        cursor.execute("DELETE FROM partidos WHERE id = %s", (id,))
        conn.commit()
        return "", 204
    except Exception as e:
        return generar_error("SERVER_ERROR", "Error al eliminar", descripcion=str(e)), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()