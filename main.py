#!/usr/bin/env python3

import time
import threading
import json
import sqlite3
from ourgroceries import OurGroceries
import asyncio
import os
from flask import Flask
from flask import Markup

app = Flask(__name__)
app.config['DEBUG'] = True

conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()


def createdatabase():
    c.execute('''CREATE TABLE IF NOT EXISTS varor (namn,typ,datum)''')
    conn.commit()
    conn.close()


def writeproduct():
    namn = input("Vad heter produkten? \n")
    typ = input("Vad för typ är produkten? \n")
    datum = str(input("När går denna produkt ut? \n"))
    c.execute("INSERT INTO varor VALUES (?,?,?);", (namn, typ, datum))
    conn.commit()
    conn.close()

def readdatabase():
    cursor = c.execute("SELECT namn,typ,datum FROM varor")
    results = cursor.fetchall()
    conn.close()
    return results
    
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

@app.route("/")
def hello():
    row = readdatabase()
    print(row)
    #return(str(row))
    #return "\n".join([f"Du har en {productInfo[0]} vilket är en {productInfo[1]} som går ut {productInfo[2]}" for productInfo in row])
    return Markup("<pre>" + ("<br>".join([f"Du har en {productInfo[0]} vilket är en {productInfo[1]} som går ut {productInfo[2]}" for productInfo in row])) + "</pre>")
    #for x in row:
    #    return x
 
def main():
    app.run()
    #readdatabase()
    #writeproduct()
    #getlist()

if __name__ == "__main__":
    main()
