# Iz velike tabele podatkov sestavi bazo igralec

import sqlite3
import json

# odpremo json datoteko in bazo v katero bomo zapisovali

json_file_path = "Obdelava Podatkov\Data.json"
conn = sqlite3.connect("rekreacija.sqlite")
cur = conn.cursor()

with open(json_file_path, 'r', encoding="utf-8") as j:
    dict = json.loads(j.read())

# Za vsak slučaj najprej pobrišemo tabeli igralec in vzdevek, če slučajno obstajata
pobrisi_tabelo = 'DROP TABLE IF EXISTS igralec'
cur.execute(pobrisi_tabelo)
pobrisi_tabelo = 'DROP TABLE IF EXISTS vzdevek'
cur.execute(pobrisi_tabelo)


# ustvarimo novi tabeli

ustvari_igralec = """
CREATE TABLE igralec (
    id INTEGER PRIMARY KEY,
    ime TEXT NOT NULL,
    priimek TEXT
);
"""
cur.execute(ustvari_igralec)

ustvari_vzdevek = """
CREATE TABLE vzdevek (
    id INTEGER PRIMARY KEY,
    igralec_id INTEGER REFERENCES igralec(id),
    vzdevek TEXT
);
"""
cur.execute(ustvari_vzdevek)

# dodamo igralce

def vstavi_igralec(ime, priimek = ""):
    if priimek == "":
        poizvedba = f"INSERT INTO igralec (ime) VALUES ('{ime}')"
    else:
        poizvedba = f"INSERT INTO igralec (ime, priimek) VALUES ('{ime}', '{priimek}')"
    cur.execute(poizvedba)
    return None

def vzdevek(id, vzdevek):
    poizvedba = f"INSERT INTO vzdevek (igralec_id, vzdevek) VALUES ('{id}', '{vzdevek}')"
    cur.execute(poizvedba)
    return None


counter = 0
i = 1
for x in dict:
    if counter == 0 or counter == 1:
        pass
    
    else:
        vstavi_igralec(dict[x]['name'], dict[x]['surname'])
        
        # print(f"Dodan igralec {dict[x]['name']} {dict[x]['surname']}")

        vzdevek(i, dict[x]['name'])
        

        if dict[x]['surname'] != "":
            vzdevek(i, dict[x]['surname'])
            

        for nick in dict[x]['nickname']:
            vzdevek(i, nick)
            
        
        i += 1

    counter += 1
    
conn.commit()