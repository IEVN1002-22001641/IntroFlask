from flask import Flask, render_template, request
import math

app = Flask(__name__)

@app.route("/")
def index():
    titulo = "Hola"
    lista = ['Luis', 'Paco', 'Pedro']
    return render_template("index.html", titulo=titulo, lista=lista)

@app.route("/distancia", methods=["GET","POST"])
def distancia():
    n1=0
    n2=0
    n3=0
    n4=0
    resSr=0
    res=0
    
    if request.method=="POST":
        n1=request.form.get("n1")
        n2=request.form.get("n2")
        n3=request.form.get("n3")
        n4=request.form.get("n4")

        if n1 and n2 and n3 and n4:
            try:
                resSr= ((float(n3)-float(n1))**2) + ((float(n4)-float(n2))**2)
                res= math.sqrt(resSr)
            except ValueError:
                res=0

    return render_template("distancia.html", n1=n1, n2=n2, n3=n3, n4=n4, resSr=resSr, res=res)

@app.route("/operasbas", methods=["GET","POST"])
def operasbas():
    n1=0
    n2=0
    res=0
    operacion=""

    if request.method=="POST":
        n1=request.form.get("n1")
        n2=request.form.get("n2")
        if request.form.get("operacion")=="suma":
            res=float(n1)+float(n2)
        
    return render_template("operasbas.html", n1=n1, n2=n2, res=res)

@app.route("/cinepolis", methods=["GET", "POST"])
def cinepolis():
    nombre = ""
    cc = 0
    cineco = False
    cb = 0
    total_pagar = 0
    mensaje_error = ""
    precio_boleto = 12.0

    if request.method == "POST":
        nombre = request.form.get("nombre", "")
        cc = int(request.form.get("cc", 0))
        cineco = request.form.get("cineco") == "true"
        cb = int(request.form.get("cb", 0))
 
        if cb <= cc * 7:
            
            if cb > 5:
                descuento = 0.15
            elif cb >= 3:
                descuento = 0.10
            else:
                descuento = 0.0

            total_sd = precio_boleto * cb
            total_pagar = total_sd - (total_sd * descuento)

            if cineco:
                total_pagar = total_pagar - (total_pagar * 0.10)
        else:
            mensaje_error = "Solo se pueden 7 boletos máximo por persona"

    return render_template("cinepolis.html", nombre=nombre, cc=cc,  cineco=cineco, cb=cb, total_pagar=round(total_pagar, 2), mensaje_error=mensaje_error)


@app.route("/hola")
def hola():
    return "<h3> Saludo desde hola </h3>"

@app.route("/user/<string:user>")
def user(user):
    return "Hola " + user

@app.route("/numero/<int:n>")
def numero(n):
    return "Numero: {}".format(n)

@app.route("/user/<int:id>/<string:username>")
def username(id, username):
    return "ID: {} nombre: {}".format(id, username)

@app.route("/suma/<float:n1>/<float:n2>")
def func(n1, n2):
    return "la suma es: {}".format(n1 + n2)



if __name__ == "__main__":
    app.run(debug=True)