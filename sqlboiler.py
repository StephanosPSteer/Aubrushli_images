import sqlite3
import pandas as pd
import pathboiler

current_dir,db_path = pathboiler.getkeypaths()

def openconscur():
    conn = sqlite3.connect(db_path)
    return conn

def closeconn(conn):
    conn.commit()
    conn.close()


def getstyle(): 
    conn = openconscur()
    currstyle = pd.read_sql_query("SELECT StylesheetPath FROM settings", conn)
    closeconn(conn)
    #just return the style string rightnow
    return currstyle.iloc[0]["StylesheetPath"]

def getallproduction():
    conn = openconscur()
    prods = pd.read_sql_query("SELECT * from production", conn)
    closeconn(conn)
    return prods

def getshotlist(prodid):
    conn = openconscur()
    #print(prodid)
    shotlist  = pd.read_sql_query("SELECT * FROM Shotlists where productionid=?", conn, params=(prodid,))
    closeconn(conn)
    #just returning shotlistpath right now - revisit if need to return more
    return shotlist.iloc[0]["ShotlistPath"], shotlist.iloc[0]["PreferredSeed"], shotlist.iloc[0]["numberofimages"], shotlist.iloc[0]["ShotlistImagesFolder"]