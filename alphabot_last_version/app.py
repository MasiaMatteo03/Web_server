from flask import Flask, app, render_template, url_for, redirect, request, make_response

import socket as sck
import threading as thr
import time
import RPi.GPIO as GPIO
import time as T
import sqlite3 as SQL
import subprocess as sb
import random
import string
import datetime


token=''.join(random.choices(string.ascii_letters + string.digits, k=30))

class AlphaBot(object):
    
    def __init__(self, in1=13, in2=12, ena=6, in3=21, in4=20, enb=26):
        self.IN1 = in1
        self.IN2 = in2
        self.IN3 = in3
        self.IN4 = in4
        self.ENA = ena
        self.ENB = enb
        self.PA  = 41  #left engine
        self.PB  = 38  #right engine

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.ENB, GPIO.OUT)
        self.PWMA = GPIO.PWM(self.ENA,500)
        self.PWMB = GPIO.PWM(self.ENB,500)
        self.PWMA.start(self.PA)
        self.PWMB.start(self.PB)
        self.stop()

    def forward(self, time_ms = 1000):  #that function move the alphabot forward for {time_ms} milliseconds
        print("The Alphabot moves forward...")
        

        self.PWMA.ChangeDutyCycle(self.PA)      #setting the engines
        self.PWMB.ChangeDutyCycle(self.PB)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)

        T.sleep(time_ms/1000)
        self.stop()


    def backward(self, time_ms = 1000):        #this funtion move the alphabot backward for {time_ms} milliseconds
        print("The Alphabot moves backward...")

        self.PWMA.ChangeDutyCycle(self.PA)      #setting the engines
        self.PWMB.ChangeDutyCycle(self.PB)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)

        T.sleep(time_ms/1000)
        self.stop()

    def left(self, time_ms = 1000):        #this function turn the alphabot left for {time_ms} milliseconds
        print("The Alphabot moves left...")
        
        self.PWMA.ChangeDutyCycle(self.PA)      #setting the engines
        self.PWMB.ChangeDutyCycle(self.PB)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)

        T.sleep(time_ms/1000)
        self.stop()

    def right(self, time_ms = 1000):       #this function turn the alphabot right for {time_ms} milliseconds
        print("The Alphabot moves right...")
        
        self.PWMA.ChangeDutyCycle(self.PA)      #setting the engines
        self.PWMB.ChangeDutyCycle(self.PB)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)

        T.sleep(time_ms/1000)
        self.stop()

    def stop(self, time_ms = 0):        #this function stops the alphabot for {time_ms} milliseconds
        print("The Alphabot stops...")

        self.PWMA.ChangeDutyCycle(0)
        self.PWMB.ChangeDutyCycle(0)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.LOW)

        T.sleep(time_ms/1000)

    def basicMovements(self, way, time=1000):       #understand if the command given is a basic movement or not and does it
        if 'exit' in way:
            alphabot.stop()
            print("Disconnection...")
        
        #recognise the letter (w-a-s-d) for the direction
        elif 'w' in way:        #forward
            alphabot.forward(time)
        
        elif 's' in way:        #backward
            alphabot.backward(time)
        
        elif 'a' in way:    #left
            alphabot.left(time)

        elif 'd' in way:    #right
            alphabot.right(time)

        elif 'e' in way:    #stop
            alphabot.stop(time)

    def complex_moves(self, text):
        connessione_db = SQL.connect('./alphabot.db')
        cursor = connessione_db.cursor()
        cursor.execute(f"SELECT Movimenti.sequenza FROM Movimenti WHERE '{text}' = Movimenti.nome")
        temporan = cursor.fetchall()
        print(temporan)
        if len (temporan)>0:
            movimenti=temporan[0][0]
            
            for m in movimenti.split(","):
                    self.basicMovements(m.split(":")[0], int(m.split(":")[1]))
            connessione_db.close()

            
    def set_pwm_a(self, value):
        self.PA = value
        self.PWMA.ChangeDutyCycle(self.PA)

    def set_pwm_b(self, value):
        self.PB = value
        self.PWMB.ChangeDutyCycle(self.PB)    
        
    def set_motor(self, left, right):       #this function sets engines
        if (right >= 0) and (right <= 100):
            GPIO.output(self.IN1, GPIO.HIGH)
            GPIO.output(self.IN2, GPIO.LOW)
            self.PWMA.ChangeDutyCycle(right)
        elif (right < 0) and (right >= -100):
            GPIO.output(self.IN1, GPIO.LOW)
            GPIO.output(self.IN2, GPIO.HIGH)
            self.PWMA.ChangeDutyCycle(0 - right)
        if (left >= 0) and (left <= 100):
            GPIO.output(self.IN3, GPIO.HIGH)
            GPIO.output(self.IN4, GPIO.LOW)
            self.PWMB.ChangeDutyCycle(left)
        elif (left < 0) and (left >= -100):
            GPIO.output(self.IN3, GPIO.LOW)
            GPIO.output(self.IN4, GPIO.HIGH)
            self.PWMB.ChangeDutyCycle(0 - left)

alphabot = AlphaBot()

app = Flask(__name__)

def validate(username, password):
    completion = False
    con = SQL.connect('./alphabot.db')
    #with sqlite3.connect('static/db.db') as con:
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

def aggAccessiDatabase(user, ora):
    mex = f'INSERT INTO Accessi (nome, ora) VALUES ("{user}","{str(ora)}")'
    con = SQL.connect('./alphabot.db')
    cur = con.cursor()
    cur.execute(mex)
    cur.execute("commit")

def aggCronologiaMovimenti(user, ora, move):
    connessione_db = SQL.connect('./alphabot.db')
    cur = connessione_db.cursor()
    cur.execute(f'INSERT INTO Cronologia (utente, ora, comando) VALUES ("{user}","{str(ora)}","{move}")')
    cur.execute("commit")
    temporan = cur.fetchall()
    print(temporan)

@app.route("/", methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        completion = validate(username, password)
        if completion == False:
            error = 'Invalid Credentials. Please try again.'
        else:
            aggAccessiDatabase(username, datetime.datetime)
            resp = make_response(redirect(url_for("movimenti")))
            resp.set_cookie("username", username)
    return render_template('login.html', error=error)


@app.route(f"/{token}", methods=['GET', 'POST'])

def movimenti():
    if request.method == 'POST':

        user_cookie = request.cookies.get("username")

        if request.form.get('forward') == 'Forward':
            print("Forward")
            alphabot.forward()
            move = "avanti"

        elif request.form.get('backward') == "Backward":
            print("Backward")
            alphabot.backward()
            move = "indietro"
        
        elif request.form.get('left') == "Left":
            print("Left")
            alphabot.left()
            move = "sinistra"

        elif request.form.get('right') == "Right":
            print("Right")
            alphabot.right()
            move = "destra"

        elif request.form.get("stop") == "Stop":
            print("Stop")
            alphabot.stop()
            move = "stop"

        elif request.form.get("submit_db") == "Submit":
            alphabot.complex_moves(request.form.get('txt_db'))
            move = request.form.get('txt_db')

        else:
            print("Stop")
            alphabot.stop()
            move = "stop"
            

        print(f"USER: {user_cookie}")
        aggCronologiaMovimenti(user_cookie, datetime.datetime, move)

    elif request.method == 'GET':
        return render_template('index.html')
    
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.128')