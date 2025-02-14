## Naredi bazo tekem iz poročil tekem (Match report)

import os
import sqlite3
import csv
import pandas as pd
import numpy as np

from datetime import datetime


conn = sqlite3.connect("rekreacija.sqlite")
cur = conn.cursor()

# Za vsak slučaj najprej pobrišemo tabelo tekma, če slučajno obstaja
pobrisi_tabelo = 'DROP TABLE IF EXISTS tekma'
cur.execute(pobrisi_tabelo)
pobrisi_tabelo = 'DROP TABLE IF EXISTS prisotnost'
cur.execute(pobrisi_tabelo)


# ustvarimo novo tabelo tekma

ustvari_tekma = """
CREATE TABLE tekma (
    id INTEGER PRIMARY KEY,
    datum DATE NOT NULL,
    goli_a INTEGER NOT NULL,
    goli_b INTEGER NOT NULL
);
"""
cur.execute(ustvari_tekma)


# ustvarimo novo tabelo prisotnost

ustvari_prisotnost = """
CREATE TABLE prisotnost (
    id INTEGER PRIMARY KEY,
    igralec_id  INTEGER REFERENCES igralec(id),
    tekma_id  INTEGER REFERENCES tekma(id),
    ekipa INTEGER NOT NULL,
    goli INTEGER NOT NULL DEFAULT 0,
    asistence INTEGER NOT NULL DEFAULT 0,
    avto_goli INTEGER NOT NULL DEFAULT 0
);
"""
cur.execute(ustvari_prisotnost)


reports = os.listdir("Match History")

def vstavi_tekma(datum, goli_a, goli_b):
    poizvedba = f"""INSERT 
                    INTO tekma 
                    (datum, goli_a, goli_b) 
                    VALUES ('{datum}', {goli_a}, {goli_b})"""
    cur.execute(poizvedba)    
    return None

# def niz_v_datum(datum):
#     return datetime.strptime('2014-12-04', '%Y-%m-%d').date()


def isNaN(num):
        return num != num
    
def vstavi_prisotnost(igralec_id, tekma_id, ekipa, goli, asistence, avtogoli):
    poizvedba = f"""INSERT 
                    INTO prisotnost 
                    (igralec_id, tekma_id, ekipa, goli, asistence, avto_goli)
                    VALUES ({igralec_id}, {tekma_id}, {ekipa}, {goli}, {asistence}, {avtogoli})"""
    cur.execute(poizvedba)
    return None



def pretvori(file):
    path = f"Match History\{file}"
    vsebina = pd.read_csv(path, skiprows=[0], dtype=str)

    f = open(path, "r")
    prva_vrstica = f.readline()
    tip = prva_vrstica[0]   # Če tekma -> 'M', če turnir -> 'T'
    f.close()
             
    ekipa_a = []
    ekipa_b = []
    # ekipa_c = []  coming soon ... maybe
    # ekipa_d = []  coming soon ... maybe
    
    datum = vsebina.columns[0]


    # ločimo dva različna primera, glede na tip tekme 'M' / 'T'

    

    if tip == 'M':

        for k in [0, 1]: # 2 ekipi

            i = 0
            while i < 7:    #vsaka ima največ 7 igralcev
                igralec = vsebina.iloc[i+7*k][1]

                if not isNaN(igralec):
                    poizvedba = f"""SELECT igralec_id 
                                    FROM vzdevek 
                                    WHERE vzdevek = '{igralec}'"""
                    rezultat = cur.execute(poizvedba).fetchall()
                    try: 
                        igralec_id = rezultat[0][0]

                    except Exception as e: 
                        print(igralec, file)    # Lovimo morda nepravilno izpolnjene obrazce

                    goli = vsebina.iloc[i+7*k][2]
                    if isNaN(goli):
                        G = 0
                    else:
                        G = len(str(goli))

                    asistence = vsebina.iloc[i+7*k][3]
                    if isNaN(asistence):
                        A = 0
                    else:
                        A = len(str(asistence))

                    avtogoli = vsebina.iloc[i+7*k][4]
                    if isNaN(avtogoli):
                        AG = 0
                    else:
                        AG = len(str(avtogoli))

                    ekipa = k

                    stat_igralec = (igralec_id, ekipa, G, A, AG)

                    if ekipa == 0:
                        ekipa_a.append(stat_igralec)
                    elif ekipa == 1:
                        ekipa_b.append(stat_igralec)
                    else:
                        print(datum, igralec)

                    
                else:
                    break
                i+=1

        if ekipa_a == []:
            # print('Dummy tekma', datum)
            return None

        goli_skupaj_a = 0
        goli_skupaj_b = 0

        for stat in ekipa_a:
            goli_skupaj_a += stat[2]
            goli_skupaj_b += stat[4]

        for stat in ekipa_b:
            goli_skupaj_b += stat[2]
            goli_skupaj_a += stat[4]

        

        vstavi_tekma(datum, goli_skupaj_a, goli_skupaj_b)
        conn.commit()

        # sedaj pa želimo id tekme

        poizvedba = f"""SELECT id
                        FROM tekma
                        WHERE datum = '{datum}'
                    """
        rezultat = cur.execute(poizvedba).fetchall()
        tekma_id = rezultat[0][0]

        for ekipa in [ekipa_a, ekipa_b]:
            for igralec in ekipa:
                vstavi_prisotnost(igralec[0], tekma_id, igralec[1], igralec[2], igralec[3], igralec[4])
        
        conn.commit()


    if tip == 'T': 
        cetrta_ekipa = vsebina.iloc[15][0]

        if cetrta_ekipa == 'None':
           tip = 'T3x3'
        else:
            tip = 'T4x4'
        
        if tip == 'T3x3':
            pass
           ## coming soon ... maybe

        if tip == 'T4x4':
            pass
            # comming soon ... maybe

    return None


for file in reports:
    pretvori(file)




