from flask import Blueprint, request, jsonify
from utils import paginar

partidos_bp = Blueprint('partidos', __name__)

@partidos_bp.route('/partidos', methods=['GET'])
def listar_partidos():
    equipo = request.args.get('equipo')
    fecha = request.args.get('fecha')
    fase = request.args.get('fase')

    total_registros = 48
    partidos_db = []

    links, limit, offset = paginar(request, total_registros)

    return jsonify({
        "data": partidos_db,
        "total": total_registros,
        "links": links
    }), 200