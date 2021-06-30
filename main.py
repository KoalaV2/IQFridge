#!/usr/bin/env python3

import time
import threading
import json
import mariadb
import os
from dotenv import load_dotenv
from ourgroceries import OurGroceries
import asyncio
from flask import Flask
from flask import Markup
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for
from flask import Response
import cv2
from pyzbar.pyzbar import decode
import requests

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'super secret key'

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWD = os.getenv("DB_PASSWD")
DB_IP = os.getenv("DB_IP")
DB_DATABASE = os.getenv("DB_DATABASE")


try:
    conn = mariadb.connect(
        user=DB_USER,
        password=DB_PASSWD,
        host=DB_IP,
        port=3306,
        database=DB_DATABASE

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    exit()


def writeproduct():
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS fridge (namn VARCHAR(255),typ VARCHAR(255),datum VARCHAR(255))''')
    namn = input("Vad heter produkten? \n")
    typ = input("Vad för typ är produkten? \n")
    datum = str(input("När går denna produkt ut? \n"))
    c.execute("INSERT INTO fridge VALUES (?,?,?);", (namn, typ, datum))
    conn.commit()
    conn.close()

def readdatabase():
    c = conn.cursor()
    cursor = c.execute("SELECT namn,typ,datum FROM fridge")
    return c

def getlist():
    user = os.getenv('GROC_USER')
    password = os.getenv('GROC_PASSWORD')

    og = OurGroceries(user,password)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(og.login())


    my_lists = dict(loop.run_until_complete(og.get_list_items('LrliG1FKlpquJHWH6pRLmn')))
    for x in my_lists['list']['items']:
        temp = f"{x['value']}"
        print(temp)

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes(),image




def gen(camera):
    resultthing = False
    while resultthing == False:
        frame,image = camera.get_frame()
        result = decode(image)
        if result:
            resultthing = True
        else:
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    return redirect(url_for('readbar'))

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/readdatabase")
def vadikylen():
    row = readdatabase()
    return render_template('readdatabase.html',data=row)
@app.route("/readbar")
def readbar(image):

    detectedBarcodes = decode(image)

    prodid = None
    # If not detected then print the message
    if not detectedBarcodes:
        return(False)
    else:
          # Traveres through all the detected barcodes in image
        for barcode in detectedBarcodes:
            if barcode.data!="":
            # Print the barcode data
                prodid = barcode.data.decode()
                print(prodid)

    url = f"https://world.openfoodfacts.org/api/v0/product/{prodid}.json"
    print(url)
    response = requests.get(url)
    json_data = json.loads(response.text)
    json_data_product = json_data['product']
    return json_data_product

    try:
        productimage = result['image_front_url']
    except:
        productimage = "Image not found."
    prodname = result['product_name']
    try:
        prodcategory = result['categories_tags'][0]
    except:
        prodcategory = "Category not found."
    return render_template('readbarcode.html',prodname=prodname,prodcategory=prodcategory,productimage=productimage)

@app.route("/seecam")
def seecam():
    return render_template("video_feed.html")

def main():
    app.run(host= "0.0.0.0")

if __name__ == "__main__":
    main()
