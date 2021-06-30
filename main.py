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

app = Flask(__name__)
app.config['DEBUG'] = True

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

import cv2
from pyzbar.pyzbar import decode
import requests
import json
import sys
import argparse


# Make one method to decode the barcode
def BarcodeReader(args=None):
    if len(sys.argv) == 1:
        cam = cv2.VideoCapture(4)
        while(True):
            ret,frame = cam.read()
            cv2.imshow('img1',frame) #display the captured image
            if cv2.waitKey(1) & 0xFF == ord('y'): #save on pressing 'y'
                cv2.imwrite('c1.png',frame)
                cv2.destroyAllWindows()
                break
        img = cv2.imread('c1.png')
    else:
        parser = argparse.ArgumentParser(
            description='Reads barcodes in images, using the zbar library'
        )
        parser.add_argument('image', nargs='+')
        args = parser.parse_args(args)
        img = cv2.imread(args.image[0])
        ##img = args.image

    prodid = None

    # Decode the barcode image
    detectedBarcodes = decode(img)
    # while detectedBarcodes == []:
    #     detectedBarcodes = decode(img)
    #     print(detectedBarcodes)

    # If not detected then print the message
    if not detectedBarcodes:
        print("Barcode Not Detected or your barcode is blank/corrupted!")
        return None
    else:
          # Traveres through all the detected barcodes in image
        for barcode in detectedBarcodes:
            # Locate the barcode position in image
            # (x, y, w, h) = barcode.rect
            # Put the rectangle in image using
            # cv2 to heighlight the barcode
            # cv2.rectangle(img, (x-10, y-10),
            #               (x + w+10, y + h+10),
            #               (255, 0, 0), 2)
            if barcode.data!="":
            # Print the barcode data
                #print(barcode())
                prodid = barcode.data.decode()
                print(prodid)
                #print(barcode.type)

    url = f"https://world.openfoodfacts.org/api/v0/product/{prodid}.json"
    print(url)
    response = requests.get(url)
    json_data = json.loads(response.text)
    json_data_product = json_data['product']
    return json_data_product


@app.route("/")
def hello():
    return render_template("index.html")
@app.route("/readdatabase")
def vadikylen():
    row = readdatabase()
    return render_template('readdatabase.html',data=row)
@app.route("/readbar")
def readbarcode():
    result = BarcodeReader()
    if result == None:
        return("Barcode not found in image.")
    prodname = result['product_name']
    return render_template('readbarcode.html',prodname=prodname)

def main():
    #BarcodeReader()
    #getlist()
    app.run(host= "0.0.0.0")
    # writeproduct()
    #readdatabase()

    #getlist()

if __name__ == "__main__":
    main()
