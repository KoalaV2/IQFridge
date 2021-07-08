#!/usr/bin/env python3

import time
import threading
import json
import mariadb
import os
# from dotenv import load_dotenv
from ourgroceries import OurGroceries
import asyncio
from flask import Flask
from flask import Markup
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for
import cv2
from pyzbar.pyzbar import decode
import requests
import sys
import argparse
import requests
import json
import html



app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'super secret key'

# # load_dotenv()
# DB_USER = os.getenv("DB_USER")
# DB_PASSWD = os.getenv("DB_PASSWD")
# DB_IP = os.getenv("DB_IP")
# DB_DATABASE = os.getenv("DB_DATABASE")


# try:
#     conn = mariadb.connect(
#         user=DB_USER,
#         password=DB_PASSWD,
#         host=DB_IP,
#         port=3306,
#         database=DB_DATABASE

#     )
# except mariadb.Error as e:
#     print(f"Error connecting to MariaDB Platform: {e}")
#     exit()


def readdatabase():
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS fridge (name VARCHAR(255),category VARCHAR(255),expdate VARCHAR(255))''')
    cursor = c.execute("SELECT name,category,expdate FROM fridge")
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

# Make one method to decode the barcode
def BarcodeReader(args=None):
    img = cv2.imread('image.jpg')
    prodid = None

    # Decode the barcode image
    try:
        detectedBarcodes = decode(img)
    except:
        return "Not detected"
    # while detectedBarcodes == []:
    #     detectedBarcodes = decode(img)
    #     print(detectedBarcodes)

    # If not detected then print the message
    if not detectedBarcodes:
        print("Barcode Not Detected or your barcode is blank/corrupted!")
        return("Not detected")
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


@app.route("/")
def index():
    return render_template("index.html")
@app.route('/findmeal', methods=['GET','POST'])
def findmeal():
    recipies = []

    try:
        form_data = request.form
        print(form_data['Name'])
        get_prodid_url = "https://www.ica.se/api/search/v2/quicksearch?query="
        product = form_data['Name']
        response = requests.get(f"{get_prodid_url}{product}")
        product_response = response.json()



        for x in range(min(3, len(product_response['RecipeResult']['Documents']))):
            product_documents = product_response['RecipeResult']['Documents'][x]
            recipe_id = product_documents['_id']
            recipe_title = product_documents['Title'].strip()
            recipe_cook_time = product_documents['CookingTimeValue']
            recipe_rating = product_documents['Rating']['AverageRating']
            recipe_image = product_documents['Images'][0]['AbsoluteUrl']
            # print(recipe_image[0]['AbsoluteUrl'])
            # print(f"{x+1}. {recipe_title} med ID {recipe_id} tar {recipe_cook_time} minuter att laga och har betyget {recipe_rating} stjärnor")


            recipies.append({
                "recipe_id":recipe_id,
                "recipe_title":recipe_title,
                "recipe_image":recipe_image,
                "recipe_rating":recipe_rating,
                "recipe_cook_time":recipe_cook_time
            })

    except:pass
    return render_template('findmeal.html',recipies=recipies)

@app.route('/makemeal/<recipe_id>')
def makemeal(recipe_id):

    url = f"https://handla.api.ica.se//api/recipes/recipe/{recipe_id}"
    response = requests.get(url)
    json_data = response.json()
    recipe_title = json_data['Title']
    avalible_portions = json_data['ExtraPortions']
    cooking_steps = json_data['CookingStepsWithTimers']
    cooking_time = json_data['CookingTime']
    recipe_ingredients = json_data['IngredientGroups']
    recipe_image = json_data['ImageUrl']
    ingredients = []
    directions = []
    for k in recipe_ingredients[0]['Ingredients']:
        print(k['Text'])
        ingredients.append(k['Text'])
    for k in cooking_steps:
        directions.append(html.unescape(k['Description']))



    return render_template('makemeal.html',recipe_title=recipe_title,avalible_portions=avalible_portions,cooking_steps=directions,cooking_time=cooking_time,recipe_ingredients=ingredients,recipe_image=recipe_image)
    # How to render åäö: html.unescape


    # AVALIBLE PORTIONS
    #for x in avalible_portions:
        #print(x['Portions'])



@app.route("/readdatabase")
def vadikylen():
    row = readdatabase()
    return render_template('readdatabase.html',data=row)
@app.route("/readbar")
def readbar():
    result = BarcodeReader()
    if result == "Not detected":
        return redirect(url_for('takeimage'))
    else:
        try:
            productimage = result['image_front_url']
        except:
            productimage = "Image not found."
        prodname = result['product_name']
        try:
            prodcategory = result['categories_tags'][0]
            prodcategory = prodcategory.replace("en:","")
        except:
            prodcategory = "Category not found."
        return render_template('readbarcode.html',prodname=prodname,prodcategory=prodcategory,productimage=productimage)
@app.route('/takeimage')
def takeimage():
    return render_template('upload.html')
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        fs = request.files.get('snap')
        if fs:
            print('FileStorage:', fs)
            print('filename:', fs.filename)
            fs.save('image.jpg')
            print("Saved file")
            return ""
        else:
            return "You forgot Snap!"
@app.route('/writeproduct', methods=['GET', 'POST'])
def writeproduct():
    content = request.json
    print(content)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS fridge (name VARCHAR(255),category VARCHAR(255),expdate VARCHAR(255))''')
    prodname = content['prodname']
    prodcategory = content['prodcategory']
    # prodexpdate = content['prodexpdate']
    prodexpdate = "2021-02-02"
    c.execute("INSERT INTO fridge VALUES (?,?,?);", (prodname, prodcategory, prodexpdate))
    conn.commit()
    return(f"Product: {prodname} has been added to the database.")



def main():
    app.run(ssl_context='adhoc')

if __name__ == "__main__":
    main()
