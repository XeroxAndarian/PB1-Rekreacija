import sqlite3
from datetime import datetime


conn = sqlite3.connect("rekreacija.sqlite")
cur = conn.cursor()


# Za vsak slučaj najprej pobrišemo tabelo sezona, če slučajno obstaja
pobrisi_tabelo = 'DROP TABLE IF EXISTS sezona'
cur.execute(pobrisi_tabelo)

ustvari_sezona = """
CREATE TABLE sezona (
    id INTEGER PRIMARY KEY,
    sezona INTEGER NOT NULL,
    zacetek TEXT NOT NULL,
    konec TEXT NOT NULL
);
"""
cur.execute(ustvari_sezona)

def vstavi_sezona(sezona, zacetek, konec):
    poizvedba = f"""INSERT 
                    INTO sezona 
                    (sezona, zacetek, konec)
                    VALUES ('{sezona}', '{zacetek}', '{konec}')"""
    cur.execute(poizvedba)
    return None

def string_to_datetime(datum):
    return datetime.strptime(datum, "%Y-%m-%d")

def datetime_to_string(datum):
    return datum.strftime("%Y-%m-%d")

zacetek_prve = '2022-09-01'
zacetek = string_to_datetime(zacetek_prve)

sezona = 1
while zacetek < datetime.today():
    zacetek_str = datetime_to_string(zacetek)
    mesec = zacetek.month
    if mesec == 2:
        konec = datetime(zacetek.year, 6, 30)
        konec_str = datetime_to_string(konec)
        vstavi_sezona(sezona, zacetek_str, konec_str)
        sezona += 1
        zacetek = datetime(zacetek.year, 9, 1)
    elif mesec == 9:
        konec = datetime(zacetek.year + 1, 1, 31)
        konec_str = datetime_to_string(konec)
        vstavi_sezona(sezona, zacetek_str, konec_str)
        sezona += 1
        zacetek = datetime(zacetek.year + 1, 2, 1)
    else:
        print('Napaka', zacetek_str)


conn.commit()