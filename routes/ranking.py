from flask import Blueprint, jsonify, request
from database import get_connection
from utils import paginar

ranking = Blueprint('ranking', __name__)

@ranking.route('/ranking', methods=['GET'])
def obtener_ranking():

    #obtener parametros de la URL
    limit_param = request.args.get('_limit', type=int)
    offset_param = request.args.get('_offset', type=int)

    # validar tipo de parametros
    if request.args.get('_limit') is not None and limit_param is None:
        return jsonify({
            "errors": [
                {
                    "code": "400",
                    "message": "Bad Request",
                    "level": "error",
                    "description": "_limit debe ser un número entero"
                }
            ]
        }), 400
    
    if request.args.get('_offset') is not None and offset_param is None:
        return jsonify({
            "errors": [
                {
                    "code": "400",
                    "message": "Bad Request",
                    "level": "error",
                    "description": "_offset debe ser un número entero"
                }
            ]
        }), 400
    
    #validar valores
    if limit_param is not None and limit_param <= 0:
        return jsonify({
            "errors": [
                {
                    "code": "400",
                    "message": "Bad Request",
                    "level": "error",
                    "description": "_limit debe ser mayor a 0"
                }
            ]
        }), 400
    
    if offset_param is not None and offset_param < 0:
        return jsonify({
            "errors": [
                {
                    "code": "400",
                    "message": "Bad Request",
                    "level": "error",
                    "description": "_offset no puede ser menor a 0"
                }
            ]
        }), 400
    

    try:
        #conectar a la base de datos
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        #traer prediccciones y resultados
        cursor.execute("""
            SELECT
                p.usuario_id,
                p.goles_local AS pred_local,
                p.goles_visitante AS pred_visitante,
                r.goles_local AS real_local,
                r.goles_visitante AS real_visitante
            FROM predicciones p
            JOIN resultados r ON p.partido_id = r.partido_id
        """)
        
        filas = cursor.fetchall()

        #dicionario para acumular puntos
        puntos_por_usuario = {}

        #calcular puntaje por usuario
        for fila in filas:
            usuario_id = fila["usuario_id"]
            pred_local = fila["pred_local"]
            pred_visitante = fila["pred_visitante"]
            real_local = fila["real_local"]
            real_visitante = fila["real_visitante"]

            if usuario_id not in puntos_por_usuario:
                puntos_por_usuario[usuario_id] = 0

            if pred_local == real_local and pred_visitante == real_visitante:
                puntos_por_usuario[usuario_id] += 3
            else:
                if real_local > real_visitante:
                    ganador_real = "local"
                elif real_visitante > real_local:
                    ganador_real = "visitante"
                else:
                    ganador_real = "empate"

                if pred_local > pred_visitante:
                    ganador_predicho = "local"
                elif pred_visitante > pred_local:
                    ganador_predicho = "visitante"
                else:
                    ganador_predicho = "empate"

                if ganador_real == ganador_predicho:
                    puntos_por_usuario[usuario_id] += 1

        #convertir a lista
        ranking_lista = []
        for usuario_id, puntos in puntos_por_usuario.items():
            ranking_lista.append({
                "id_usuario": usuario_id,
                "puntos": puntos
        })

        #ordenar por puntos(descendente)
        ranking_lista.sort(key=lambda x: x["puntos"], reverse=True)
        
        if len(ranking_lista) == 0:
            cursor.close()
            conn.close()
            return '', 204
        
        #aplicar paginacion
        total = len(ranking_lista)
        links, limit, offset = paginar(request, total)
        pagina = ranking_lista[offset:offset + limit]
    
        cursor.close()
        conn.close()
    
        return jsonify({
            "ranking": pagina,
            "_links": {
                "_first": {"href": links["_first"]},
                "_prev": {"href": links["_prev"]} if links["_prev"] else None,
                "_next": {"href": links["_next"]} if links["_next"] else None,
                "_last": {"href": links["_last"]}
            }
        }), 200
    
    except Exception as e: 
        return jsonify({
            "errors": [
                {
                    "code": "500",
                    "message": "Error interno del servidor",
                    "level": "error",
                    "description": str(e)
                }
            ]
        }), 500