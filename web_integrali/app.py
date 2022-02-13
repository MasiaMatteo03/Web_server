from flask import Flask, app, render_template, url_for, redirect, request, make_response

from sympy import *
x, y, z = symbols('x y z')
init_printing(use_unicode=True)

import datetime
import time as T
import sqlite3 as SQL
import subprocess as sb
import string
import datetime


app = Flask(__name__)

def validate(username, password):
    completion = False
    con = SQL.connect('./db_integrali.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM Users")
    rows = cur.fetchall()
    for row in rows:
        dbUser = row[0]
        dbPass = row[1]
        if dbUser == username:
            completion = check_password(dbPass, password)
            
    return completion

def check_password(hashed_password, user_password):
    return hashed_password == user_password

def aggAccessiDatabase(user, ora, integrale, soluzione):
    mex = f'INSERT INTO Integrals (user, ora, integrale, soluzione) VALUES ("{user}","{str(ora)}","{integrale}","{str(soluzione)}")'
    con = SQL.connect('./db_integrali.db')
    cur = con.cursor()
    cur.execute(mex)
    cur.execute("commit")
    con.close()

def accessi(username, ora):
    mex = f'INSERT INTO Accessi (username, ora) VALUES ("{username}","{ora}")'
    con = SQL.connect('./db_integrali.db')
    cur = con.cursor()
    cur.execute(mex)
    cur.execute("commit")
    con.close()

def integral_normal(integral):
    print(integrate(integral, x))
    return integrate(integral, x)

def definite_integral(integral, side1, side2):
    print(integrate(integral, (x, side1, side2)))
    return integrate(integral, (x, side1, side2))

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        completion = validate(username, password)
        if completion == False:
            error = 'Invalid Credentials. Please try again.'
        else:
            date = T.ctime()
            date = date.split()
            ora = date[3]
            
            accessi(username, ora)
            resp = make_response(redirect(url_for("integrali")))
            resp.set_cookie("username", username)
            return resp

    return render_template('login.html', error=error)

@app.route('/integrali', methods=['GET', 'POST'])
def integrali():

    date = T.ctime()
    date = date.split()
    ora = date[3]

    user_cookie = request.cookies.get("username")

    if request.method == 'POST':
        if request.form.get('submit') == "Submit":
            integral = request.form.get('integral')
            side1 = request.form.get('side1')
            side2 = request.form.get('side2')

            if side1 == "" or side2 == "":
                solution = integral_normal(integral)

                aggAccessiDatabase(user_cookie, ora, integral, solution)
            
            else:
                if  side1 != "-oo":
                    side1 = float(side1)
                if side2 != "oo":
                    side2 = float(side2)
                
                solution = definite_integral(integral, side1, side2)
                integral_sides = integral + " (" + str(side1) + ":" + str(side2) + ")"
                
                aggAccessiDatabase(user_cookie, ora, integral_sides, solution)

    return render_template('integrali.html')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')