from flask import Flask

from routes.partidos import partidos_bp
from routes.resultados import resultados
from routes.usuarios import usuarios
from routes.predicciones import predicciones
from routes.ranking import ranking

app = Flask(__name__)

app.register_blueprint(partidos_bp)
app.register_blueprint(resultados)
app.register_blueprint(usuarios)
app.register_blueprint(predicciones)
app.register_blueprint(ranking)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
