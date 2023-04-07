import os
import sqlboiler

def getkeypaths():
    #no sql as causes circular path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'aubrushli.db')
    return current_dir, db_path

def getstylepaths():
    current_dir, db_path = getkeypaths()
    stylesfolder = current_dir + "/styles/"
    currstyle = sqlboiler.getstyle()
    style_path = os.path.join(stylesfolder, currstyle)
    return stylesfolder, currstyle, style_path