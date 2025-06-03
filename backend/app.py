from flask import Flask, render_template, request, jsonify
from src.module import funbslf3, subfunc
#from src.module import funbslf3, sysbslf3
app = Flask(__name__)
calc = funbslf3.Create()

@app.route("/")
def main():
    return(render_template("start.html"))

@app.route("/symsub")
def symsub():
    return(render_template("symsub.html"))

@app.route("/symsubprefix")
def symsubprefix():
    return(render_template("symsubprefix.html"))

@app.route("/api/symsub", methods=["POST"])
def apisymsub():
    data = request.get_json()
    ipv4 = data.get('ip')
    countnet = int(data.get('subnets'))
    result = calc.symsub(ipv4, countnet)
    return jsonify(result)

@app.route("/api/symsubprefix", methods=["POST"])
def apisymsubprefix():
    data = request.get_json()
    ipv4 = data.get('ipv4')
    prefix = data.get('prefix')
    countnet = data.get('countnet')
    result = calc.symsubprefix(ipv4, prefix, countnet)
    return jsonify(result)

@app.route("/symsubany")
def symsubany():
    return(render_template("symsubany.html"))

app.run(host="0.0.0.0",port=3000,debug=True)