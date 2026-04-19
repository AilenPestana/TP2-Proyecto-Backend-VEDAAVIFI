from flask import Blueprint, request, jsonify
from database import get_connection
from utils import paginar

partidos_bp = Blueprint('partidos', __name__)

@partidos_bp.route('/partidos', methods=['GET'])
def get_partidos():
    # 1. Leer parámetros de filtro desde la URL 
    equipo = request.args.get('equipo')   # ?equipo=Argentina
    fecha  = request.args.get('fecha')    # ?fecha=2026-06-15
    fase   = request.args.get('fase')     # ?fase=Cuartos

    # 2. Base de la consulta (WHERE 1=1 permite concatenar AND libremente) 
    filtros_sql = "WHERE 1=1"
    params = []  # lista de valores que reemplazarán los %s
    # 3. Filtros dinámicos

    # Filtro equipo: busca en ambas columnas con OR dentro del mismo AND
    if equipo:
        filtros_sql += " AND (equipo_local = %s OR equipo_visitante = %s)"
        params.append(equipo)
        params.append(equipo)  # se agrega dos veces, uno por cada %s

    # Filtro fecha: coincidencia exacta con el campo DATE
    if fecha:
        filtros_sql += " AND fecha = %s"
        params.append(fecha)

    # Filtro fase: coincidencia exacta (ej: "Grupos", "Cuartos", "Final")
    if fase:
        filtros_sql += " AND fase = %s"
        params.append(fase)

    # 4. Consulta COUNT para que paginar() sepa el total 
    sql_count = f"SELECT COUNT(*) FROM partidos {filtros_sql}"

    # 5. Paginación 
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(sql_count, params)
    total = cursor.fetchone()['COUNT(*)']

    links, limit, offset = paginar(request, total)

    # 6. Consulta final con LIMIT y OFFSET 
    sql_data = f"SELECT * FROM partidos {filtros_sql} LIMIT %s OFFSET %s"
    params_paginados = params + [limit, offset]  # params original + los 2 nuevos

    cursor.execute(sql_data, params_paginados)
    partidos = cursor.fetchall()

    cursor.close()
    conn.close()

    # 7. Respuesta
    return jsonify({
        "total": total,
        "links": links,
        "partidos": partidos
    }), 200