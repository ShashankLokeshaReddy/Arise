import pyodbc
import pandas as pd

# Set up the connection details
Driver = 'ODBC Driver 17 for SQL Server'
server = '192.168.1.9'
database = 'schulte_copy'
username = 'ARISE'
password = '4FbC2zF2'

def execute_query(conn, query):
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(query)

    # Fetch all the result rows
    rows = cursor.fetchall()

    # Get the column names from the cursor's description
    columns = [column[0] for column in cursor.description]

    # Create a DataFrame from the rows and column names
    df = pd.DataFrame.from_records(rows, columns=columns)

    # Close the cursor
    cursor.close()

    return df

# def get_df_mit_MachStatus():
#     # Create the connection string
#     conn_str = f'DRIVER={Driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

#     # Establish the database connection
#     with pyodbc.connect(conn_str) as conn:
#         query = '''
#         SELECT t3.Fefco_Teil, t3.ArtNr_Teil, t3.ID_Druck, t3.Druckflaeche, t3.Bogen_Laenge_Brutto, t3.Bogen_Breite_Brutto, t8.Kennung AS Maschine, t1.Ruestzeit_Ist, t1.Ruestzeit_Soll, t1.Laufzeit_Ist, t1.Laufzeit_Soll,
#                t1.Zeit_Ist, t1.Zeit_Soll, t3.Werkzeug_Nutzen, t3.Bestell_Nutzen, t1.Menge_Soll, t1.Menge_Ist, t3.Bemerkung, t2.LTermin, t2.KndNr, t4.Suchname, t1.AKNR, t1.TeilNr, t1.SchrittNr, t5.Start, t5.Ende,
#                t5.Summe_Minuten, t5.ID_Maschstatus, t6.Maschstatus, t7.Lieferdatum AS Lieferdatum_Rohmaterial, t7.BE_Erledigt
#         FROM schulte_copy.dbo.tbl_PRODUKTION_FERTIGUNGSSCHRITTE t1
#         INNER JOIN schulte_copy.dbo.tbl_PRODUKTION t2 ON t1.AKNR = t2.AKNr
#         INNER JOIN schulte_copy.dbo.tbl_PRODUKTION_TEIL t3 ON t1.AKNR = t3.AKNR
#         INNER JOIN schulte_copy.dbo.tbl_KUNDEN t4 ON t2.KndNr = t4.KndNr
#         INNER JOIN schulte_copy.dbo.tbl_MASCHINE_AK_ZEITEN t5 ON t1.AKNR = t5.AKNR AND t1.TEILNR = t5.TeilNr AND t1.ID_MASCHNR = t5.MASCHNR
#         INNER JOIN schulte_copy.dbo.tbl_MASCHINE_STATUS t6 ON t5.ID_MASCHSTATUS = t6.ID_MASCHSTATUS
#         LEFT OUTER JOIN schulte_copy.dbo.tbl_BESTELLUNG_KOPF t7 ON t3.BESTNR = t7.BENR
#         LEFT OUTER JOIN schulte_copy.dbo.tbl_MASCHINENPARAMETER t8 ON t1.ID_MASCHNR = t8.MASCHNR
#         WHERE t1.SCHRITTNR <> 0 AND t1.ID_MASCHNR <> 1
#         AND t6.Maschstatus='Produktion'
#         '''

#         return execute_query(conn, query)

def get_scheduled_jobs_ohne_MachStatus(startDate, endDate):
    # Create the connection string
    conn_str = f'DRIVER={Driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

    # Establish the database connection
    with pyodbc.connect(conn_str) as conn:
        query = f'''
        SELECT t3.Fefco_Teil, t3.ArtNr_Teil, t3.ID_Druck, t3.Druckflaeche, t3.Bogen_Laenge_Brutto, t3.Bogen_Breite_Brutto, t8.Kennung AS Maschine, t1.Ruestzeit_Ist, t1.Ruestzeit_Soll, t1.Laufzeit_Ist, t1.Laufzeit_Soll,
               t1.Zeit_Ist, t1.Zeit_Soll, t3.Werkzeug_Nutzen, t3.Bestell_Nutzen, t1.Menge_Soll, t1.Menge_Ist, t3.Bemerkung, t2.LTermin, t2.KndNr, t4.Suchname, t1.AKNR, t1.TeilNr, t1.SchrittNr, t7.Lieferdatum AS Lieferdatum_Rohmaterial, t7.BE_Erledigt, t1.Start, t1.Ende
        FROM schulte_copy.dbo.tbl_PRODUKTION_FERTIGUNGSSCHRITTE t1
        INNER JOIN schulte_copy.dbo.tbl_PRODUKTION t2 ON t1.AKNR = t2.AKNr
        INNER JOIN schulte_copy.dbo.tbl_PRODUKTION_TEIL t3 ON t1.AKNR = t3.AKNR
        INNER JOIN schulte_copy.dbo.tbl_KUNDEN t4 ON t2.KndNr = t4.KndNr
        INNER JOIN schulte_copy.dbo.tbl_BESTELLUNG_KOPF t7 ON t3.BESTNR = t7.BENR
        LEFT OUTER JOIN schulte_copy.dbo.tbl_MASCHINENPARAMETER t8 ON t1.ID_MASCHNR = t8.MASCHNR
        WHERE t1.SCHRITTNR <> 0 AND t1.ID_MASCHNR <> 1
        AND t1.Start IS NOT NULL AND t1.Ende IS NOT NULL
        AND t2.LTermin between '{startDate}' AND '{endDate}'
        '''

        return execute_query(conn, query)

# def get_df_ohne_MachStatus():
#     # Create the connection string
#     conn_str = f'DRIVER={Driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

#     # Establish the database connection
#     with pyodbc.connect(conn_str) as conn:
#         query = '''
#         SELECT t3.Fefco_Teil, t3.ArtNr_Teil, t3.ID_Druck, t3.Druckflaeche, t3.Bogen_Laenge_Brutto, t3.Bogen_Breite_Brutto, t8.Kennung AS Maschine, t1.Ruestzeit_Ist, t1.Ruestzeit_Soll, t1.Laufzeit_Ist, t1.Laufzeit_Soll,
#                t1.Zeit_Ist, t1.Zeit_Soll, t3.Werkzeug_Nutzen, t3.Bestell_Nutzen, t1.Menge_Soll, t1.Menge_Ist, t3.Bemerkung, t2.LTermin, t2.KndNr, t4.Suchname, t1.AKNR, t1.TeilNr, t1.SchrittNr, t7.Lieferdatum AS Lieferdatum_Rohmaterial, t7.BE_Erledigt, t1.Start, t1.Ende
#         FROM schulte_copy.dbo.tbl_PRODUKTION_FERTIGUNGSSCHRITTE t1
#         INNER JOIN schulte_copy.dbo.tbl_PRODUKTION t2 ON t1.AKNR = t2.AKNr
#         INNER JOIN schulte_copy.dbo.tbl_PRODUKTION_TEIL t3 ON t1.AKNR = t3.AKNR
#         INNER JOIN schulte_copy.dbo.tbl_KUNDEN t4 ON t2.KndNr = t4.KndNr
#         INNER JOIN schulte_copy.dbo.tbl_BESTELLUNG_KOPF t7 ON t3.BESTNR = t7.BENR
#         LEFT OUTER JOIN schulte_copy.dbo.tbl_MASCHINENPARAMETER t8 ON t1.ID_MASCHNR = t8.MASCHNR
#         WHERE t1.SCHRITTNR <> 0 AND t1.ID_MASCHNR <> 1
#         '''

#         return execute_query(conn, query)

def get_unscheduled_jobs_ohne_MachStatus(startDate, endDate):
    # Create the connection string
    conn_str = f'DRIVER={Driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

    # Establish the database connection
    with pyodbc.connect(conn_str) as conn:
        query = f'''
        SELECT t3.Fefco_Teil, t3.ArtNr_Teil, t3.ID_Druck, t3.Druckflaeche, t3.Bogen_Laenge_Brutto, t3.Bogen_Breite_Brutto, t8.Kennung AS Maschine, t1.Ruestzeit_Ist, t1.Ruestzeit_Soll, t1.Laufzeit_Ist, t1.Laufzeit_Soll,
                t1.Zeit_Ist, t1.Zeit_Soll, t3.Werkzeug_Nutzen, t3.Bestell_Nutzen, t1.Menge_Soll, t1.Menge_Ist, t3.Bemerkung, t2.LTermin , t2.KndNr, t4.Suchname, t1.AKNR, t1.TeilNr, t1.SchrittNr, t7.Lieferdatum AS Lieferdatum_Rohmaterial, t7.BE_Erledigt, t1.Start, t1.Ende
        FROM schulte_copy.dbo.tbl_PRODUKTION_FERTIGUNGSSCHRITTE t1 inner join
            schulte_copy.dbo.tbl_PRODUKTION t2 ON t1.AKNR = t2.AKNr inner join
            schulte_copy.dbo.tbl_PRODUKTION_TEIL t3 ON t1.AKNR = t3.AKNR inner join
            schulte_copy.dbo.tbl_KUNDEN t4 on t2.KndNr = t4.KndNr inner join
            schulte_copy.dbo.tbl_BESTELLUNG_KOPF t7 ON t3.BESTNR = t7.BENR LEFT OUTER JOIN
            schulte_copy.dbo.tbl_MASCHINENPARAMETER t8 ON t1.ID_MASCHNR = t8.MASCHNR
        WHERE SchrittNr <> 0 AND ID_MaschNr <> 1 AND t1.erledigt = 0 AND t1.Start IS NULL
        AND t2.LTermin between '{startDate}' AND '{endDate}'
        '''

        return execute_query(conn, query)

# Get df_mit_MachStatus
# df_mit_MachStatus = get_df_mit_MachStatus()
# print("df_mit_MachStatus:")
# print(df_mit_MachStatus)

# # Get df_ohne_MachStatus
# df_ohne_MachStatus = get_df_ohne_MachStatus()
# print("df_ohne_MachStatus:")
# print(df_ohne_MachStatus)
