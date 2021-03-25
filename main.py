#!/usr/bin/env python3

import time
import threading
import json
import sqlite3
from ourgroceries import OurGroceries
import asyncio
import os
import flask

conn = sqlite3.connect('database.db')
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
    for row in cursor:
        print(f"Du har en {row[0]} vilket är en {row[1]} som går ut {row[2]}")
    
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

def main():
    readdatabase()
    #writeproduct()
    #getlist()

if __name__ == "__main__":
    main()
