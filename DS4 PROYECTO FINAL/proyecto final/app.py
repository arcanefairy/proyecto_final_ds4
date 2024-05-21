from flask import Flask, render_template, request
from funciones import carga_csv, crea_diccionario_alfabetico, crea_diccionario_revistas, realizar_busqueda

csv_revistas = "datos/revistas/REVISTAS_INFO.csv"

app = Flask(__name__)

# Cargar datos del CSV
lista_revistas = carga_csv(csv_revistas)
diccionario_revistas = crea_diccionario_revistas(lista_revistas)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/creditos')
def credits():
    return render_template('creditos.html')

@app.route('/explorar')
def explore():
    diccionario_alfabetico = crea_diccionario_alfabetico(lista_revistas)
    return render_template("explorar.html", dicc_alfabetico=diccionario_alfabetico)

@app.route('/buscar')
def buscar():
    query = request.args.get('q', '')
    resultados = realizar_busqueda(query, [diccionario_revistas])
    return render_template('resultados.html', resultados=resultados, query=query)

@app.route('/revista/<titulo>')
def revista(titulo):
    revista = next((revista for revista in lista_revistas if revista['TITULO'] == titulo), None)

    if revista:
        return render_template('revista.html', revista=revista)
    else:
        return 'Revista no encontrada', 404
    '''
    @app.route('/revista/<int:id>')
    def revista_id(id):
    if id >= 0 and id < len(lista_revistas):
        revista = lista_revistas[id]
        return render_template('revista.html', revista=revista)
    
    '''

if __name__ == '__main__':
    app.run(debug=True)
