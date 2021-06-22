from flask import Flask, render_template, request, jsonify

from RungeKutta import RungeKutta
from simulador import Simulacion

app = Flask(__name__, template_folder='templates',
            static_url_path='',
            static_folder='static')

rungeKutta = RungeKutta()


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/principal", methods=["GET"])
def principal():
    argumentos = request.args
    desde = int(argumentos.get('desde'))
    hasta = int(argumentos.get('hasta'))
    cant = int(argumentos.get('cant'))
    resultado = Simulacion(cant, desde, hasta, rungeKutta).get_table()
    response = jsonify(resultado)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/pacientes", methods=["GET"])
def pacientes():
    resultado = Simulacion.get_pacientes_json()
    response = jsonify(resultado)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route("/inestable", methods=["GET"])
def inestable():
    resultado = rungeKutta.json_inestabilidad()
    response = jsonify(resultado)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route("/purga", methods=["GET"])
def purga():
    resultado = rungeKutta.json_purga()
    response = jsonify(resultado)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

app.run(host='0.0.0.0', port=5000)