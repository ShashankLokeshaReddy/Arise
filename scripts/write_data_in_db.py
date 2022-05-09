# Write data in db and check db
import pyodbc
import pandas as pd
import datetime as dt
import arise_prototype.capacity_check as cc


def write_data_to_db():
    """ Writes data from a static table into the database
    """
    # Load data
    start = pd.to_datetime('2019-01-01', format='%Y-%m-%d')
    end = pd.to_datetime('2021-11-30', format='%Y-%m-%d')
    df = cc.load_static_orders(start, end)
    # Create connection to mssql
    server = '0.0.0.0:1434'
    username =  'mssql_arise'
    password =  'planer'
    db_info = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';UID='+username+';PWD='+password+''
    cnxn = pyodbc.connect(db_info)
    cursor = cnxn.cursor()
    # Create db and table
    cursor.execute("create database ARISE")
    cursor.execute("""create table ARISE.Auftragsfolgen(
        AKNR int not null,
        Fefco_Teil string not null,
        ArtNr_Teil int not null,
        Menge_Soll int not null,
        LTermin string not null,
        KndNr int,
        Suchname string,
        TeilNr int not null,
        ID_Druck int,
        Bogen_Laenge_Brutto float,
        Bogen_Breite_Brutto float,
        MaschNr string,
        Ruestzeit_Soll float,
        Laufzeit_Soll float,
        Lieferdatum_Rohmaterial string)""")
    #sql_query = 'create table Auftragsfolgen('
    for index, row in df.iterrows():
         cursor.execute("INSERT INTO ARISE.Auftragsfolgen (AKNR, Fefco_Teil, ArtNr_Teil, Menge_Soll, LTermin, KndNr, Suchname, TeilNr, ID_Druck, Bogen_Laenge_Brutto, Bogen_Breite_Brutto, MaschNr, Ruestzeit_Soll, Laufzeit_Soll, Lieferdatum_Rohmaterial) values(AKNR, Fefco_Teil, ArtNr_Teil, Menge_Soll, LTermin, KndNr, Suchname, TeilNr, ID_Druck, Bogen_Laenge_Brutto, Bogen_Breite_Brutto, MaschNr, Ruestzeit_Soll, Laufzeit_Soll, Lieferdatum_Rohmaterial)", 
         row.AKNR, row.Fefco_Teil, row.ArtNr_Teil, row.Menge_Soll, row.LTermin, row.KndNr, row.Suchname, row.TeilNr, row.ID_Druck, row.Bogen_Laenge_Brutto, row.Bogen_Breite_Brutto, row.MaschNr, row.Ruestzeit_Soll, row.Laufzeit_Soll, row.Lieferdatum_Rohmaterial)
    cnxn.commit()
    cursor.close()


def load_table_from_db(server, database, username, password, sql_query):
    """Makes a request to a database and catches the answer table.

    Parameters
    ----------
    server : string
        Server adress
    database : string
        Name of database
    username : string
        Username for db login
    password : string
        Password for db login
    sql_query : string
        SQL query

    Returns
    -------
    pd.Dataframe
        Received table in dataframe format
    """
    db_info = 'DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password+''
    cnxn = pyodbc.connect(db_info)
    cursor = cnxn.cursor()
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    cnxn.close()
    df = pd.DataFrame(rows)
    return df


def check_order_table():
    """Checks if data is written into db
    """
    sql_query = """
        select AKNR, Fefco_Teil, ArtNr_Teil, Menge_Soll, LTermin, KndNr, Suchname, TeilNr, ID_Druck, Bogen_Laenge_Brutto, 
            Bogen_Breite_Brutto, MaschNr, Ruestzeit_Soll, Laufzeit_Soll, Lieferdatum_Rohmaterial
        from Auftragsfolgen"""
    server = '0.0.0.0:1434'
    username =  'mssql_arise'
    password =  'planer'
    database = 'ARISE'
    df = load_table_from_db(server, database, username, password, sql_query)
    print(df)    
    return 
  
write_data_to_db()
check_order_table()