import socket
import threading as thr
import sqlite3 as sql
import subprocess


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#######################################################################
#Flask
from flask import Flask, render_template, redirect, url_for ,request
app = Flask(__name__)

def aggiungiDataBase(ip, port, res):
    con = sql.connect('indirizzi_porte.db')
    cur = con.cursor()

    if res == 0:
        status = "Open"
    
    else:
        status = "Closed"

    mex = f'INSERT INTO Ip (ip, num_porta, status) VALUES ("{ip}",{port},"{status}")'
    cur.execute(mex)
    cur.execute("commit")

    cur.close()

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        return redirect(url_for("index"))
    
    elif request.method == 'GET':
        render_template("search.html")


@app.route("/", methods=['GET', 'POST'])
def index():
    ip = request.form.get("ip")
    min_port = request.form.get("min_port")
    max_port = request.form.get("max_port")

    if request.method == 'POST':
        

        for port in range(int(min_port), int(max_port) + 1):
            result = sock.connect_ex((ip, port))

            aggiungiDataBase(ip, port, result)
        
        return redirect(url_for('search'))


    
    return render_template("index.html")



app.run(debug=True, host='127.0.0.1')
