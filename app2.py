from flask import Flask, render_template


app = Flask(__name__)

#carga de apartados en la página

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/servicios')
def servicios():
    return render_template("servicios.html")

@app.route('/about')
def galeria():
    return render_template("galeria.html")


@app.route('/portfolio')
def portfolio():
    return render_template("portfolio.html")


@app.route('/index')
def index():
    return render_template("index.html")




#api para el index de sesion 


if __name__=='__main__':
    app.run(debug=True)