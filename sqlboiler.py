import sqlite3

def getstyle(db_path): 
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    stylesql= f"SELECT stylesheetpath FROM settings" 
    cursor.execute(stylesql)
    currstyle = cursor.fetchone()[0]
    connection.commit()
    connection.close()
    return currstyle