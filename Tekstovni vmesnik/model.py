import sqlite3
import math
import scipy

conn = sqlite3.connect("rekreacija.sqlite")

class Igralec:

    def __init__(self, id, ime, priimek, prisotnost, zmage, porazi, goli, asistence, avtogoli):
        self.id = id
        self.ime = ime
        self.priimek = priimek
        self.zmage = zmage
        self.porazi = porazi
        self.prisotnost = prisotnost
        self.goli = goli
        self.asistence = asistence
        self.avtogoli = avtogoli

    def __repr__(self):
        return f"ID:{str(self.id)} > {self.ime} {self.priimek}"
    
    def __str__(self):
        return f"""Igralec:
-----------------------------
ID: {self.id}
Ime: {self.ime}
Priimek: {self.priimek}
Prisotnost: {self.prisotnost}
Zmage: {self.zmage}
Porazi: {self.porazi}
Goli: {self.goli}
Asistence: {self.asistence}
Avtogoli: {self.avtogoli}
-----------------------------
"""
    
    @staticmethod
    def pridobi_statistiko(id, zacetek='2000-01-01', konec = '2099-01-01'):
        '''Metoda pridobi statistiko igralca z idejem id in vrne objekt oblike Igralec.'''
        
        # Prisotnost
        poizvedba = """SELECT COUNT(*) 
                    FROM prisotnost
                    JOIN tekma ON (tekma.id = prisotnost.tekma_id)
                    WHERE igralec_id = ? AND 
                    datum >= ? AND
                    datum <= ?"""
        prisotnost = conn.execute(poizvedba, [id, zacetek, konec]).fetchone()[0]

        # goli, asistence, avtogoli
        poizvedba = """SELECT SUM(goli), SUM(asistence), SUM(avto_goli) 
                    FROM prisotnost 
                    JOIN tekma ON (tekma.id = prisotnost.tekma_id) 
                    WHERE igralec_id = ? AND datum >= ? AND
                    datum <= ?"""
        statistika = conn.execute(poizvedba, [id, zacetek, konec]).fetchone()
        goli = statistika[0]
        asistence = statistika[1]
        avtogoli = statistika[2]

        # zmage
        poizvedba = """SELECT COUNT(tekma.id)
                    FROM tekma
                    JOIN prisotnost ON (tekma.id = prisotnost.tekma_id)
                    WHERE prisotnost.igralec_id = ? AND 
                        ((tekma.goli_a > tekma.goli_b AND prisotnost.ekipa = 0) 
                            OR 
                        (tekma.goli_a < tekma.goli_b AND prisotnost.ekipa = 1))
                        AND
                        datum >= ? AND
                        datum <= ?"""
        zmage = conn.execute(poizvedba, [id, zacetek, konec]).fetchone()[0]

        # porazi
        poizvedba = """SELECT COUNT(tekma.id)
                    FROM tekma
                    JOIN prisotnost ON (tekma.id = prisotnost.tekma_id)
                    WHERE prisotnost.igralec_id = ? AND 
                        ((tekma.goli_a < tekma.goli_b AND prisotnost.ekipa = 0) 
                            OR 
                        (tekma.goli_a > tekma.goli_b AND prisotnost.ekipa = 1))
                        AND 
                        datum >= ? AND
                        datum <= ?"""
        porazi = conn.execute(poizvedba, [id, zacetek, konec]).fetchone()[0]

        # ime in priimek
        poizvedba = """SELECT vzdevek FROM vzdevek WHERE igralec_id = ?"""
        try: 
            ime = conn.execute(poizvedba, [id]).fetchall()[0][0]
            priimek = conn.execute(poizvedba, [id]).fetchall()[1][0]
        except Exception as e:
            ime = ''
            priimek = ''

        return Igralec(id, ime, priimek, prisotnost, zmage, porazi,  goli, asistence, avtogoli)

    
    @staticmethod
    def najdi_igralca(ime):
        '''Metoda najde igralca, ki ga iščemo po imenu, priimku ali vzdevku in vrne objekt oblike Igralec z vsemi informacijami.'''
        poizvedba = """SELECT igralec_id FROM vzdevek WHERE vzdevek = ?"""
        id_igralca = conn.execute(poizvedba, [ime]).fetchall()
        rezultat_iskanja = []
        for igralec in id_igralca:
            rezultat_iskanja.append(Igralec.pridobi_statistiko(igralec[0]))
        return rezultat_iskanja
    
    @staticmethod
    def vsi_igralci():
        '''Metoda vrne slovar vseh igralcev v obliki razreda Igralec.'''
        poizvedba = """SELECT id FROM igralec"""
        slovar = {}
        for igralec_id in conn.execute(poizvedba):
            slovar[igralec_id[0]] = Igralec.pridobi_statistiko(igralec_id[0])
        return slovar

class Tekma:

    def __init__(self, id, datum, goli_ekipa_0, goli_ekipa_1, ekipa_0, ekipa_1):
        self.id = id
        self.datum = datum
        self.goli_ekipa_0 = goli_ekipa_0
        self.goli_ekipa_1 = goli_ekipa_1
        self.ekipa_0 = ekipa_0
        self.ekipa_1 = ekipa_1


    def __repr__(self):
        return f"Tekma id: {self.id}"
    
    def __str__(self):
        return f"""
Tekma
---------------
ID: {self.id}
Datum: {self.datum}
Rezultat A:B = {self.goli_ekipa_0}:{self.goli_ekipa_1}
Ekipa A: {self.ekipa_0}
Ekipa B: {self.ekipa_1}
"""
    
    @staticmethod
    def najdi_tekmo(datum):
        '''Metoda najde in vrne tekmo v obliki objekta Tekma, ki se je dogajala na vnešeni datum.'''

        # id,  goli A, goli B
        poizvedba = """SELECT id, goli_a, goli_b
                    FROM tekma
                    WHERE datum = ? """
        rezultat = conn.execute(poizvedba, [datum]).fetchall()
        id_tekme = 0
        try:
            id_tekme = conn.execute(poizvedba, [datum]).fetchall()[0][0]
        except Exception as e:
            print('Na vnešeni datum se ni odvijala nobena tekma.')
            return None

        goli_A = rezultat[0][1]
        goli_B = rezultat[0][2]

        # ekipi
        ekipi = {0:[], 1:[]}
        for ekipa_id in [0, 1]:
            poizvedba = """SELECT prisotnost.igralec_id
                        FROM tekma
                        JOIN prisotnost ON (prisotnost.tekma_id = tekma.id)
                        WHERE datum = ? AND prisotnost.ekipa = ?"""
            rezultat = conn.execute(poizvedba, [datum, ekipa_id]).fetchall()
            for igralec in rezultat:
                ekipi[ekipa_id].append(Igralec.pridobi_statistiko(igralec[0]))
        

        return Tekma(id_tekme, datum, goli_A, goli_B, ekipi[0], ekipi[1])
        
    
class Sezona:

    def __init__(self, sezona, zacetek, konec):
        self.id = sezona
        self.zacetek = zacetek
        self.konec = konec

    def __repr__(self):
        return f"Sezona {self.id} [{self.zacetek} - {self.konec}]"
    
    def __str__(self):
        return f"Sezona {self.id} [{self.zacetek} - {self.konec}]"

    @staticmethod
    def sezona_zacetek(sezona):
        '''Metoda vrne zacetek sezone.'''
        poizvedba = """SELECT zacetek
                    FROM sezona
                    WHERE sezona = ?"""
        rezultat = conn.execute(poizvedba, [sezona]).fetchall()
        return rezultat[0][0]
        

    def sezona_konec(sezona):
        '''Metoda vrne koenc sezone.'''
        poizvedba = """SELECT konec
                    FROM sezona
                    WHERE sezona = ?"""
        rezultat = conn.execute(poizvedba, [sezona]).fetchall()
        return rezultat[0][0]

    @staticmethod
    def vse_sezone():
        '''Metoda vrne slovar objektov vseh sezon.'''
        sezone = {}
        poizvedba = """SELECT id
                    FROM sezona"""
        rezultat = conn.execute(poizvedba).fetchall()
        # print(rezultat)
        for i in rezultat:
            zacetek = Sezona.sezona_zacetek(i[0])
            konec = Sezona.sezona_konec(i[0])
            sezone[i[0]] = Sezona(i[0], zacetek, konec)
        return sezone



def MMR_kalkulator(WR, G, A, AG):
    '''Izračuna MMR po formuli.'''
    f = float(6* WR + 2 * G + A - AG)/6
    sd   = 1.5
    mean = 0
    Itg = scipy.integrate.quad(lambda x: 1 / ( sd * ( 2 * math.pi ) ** 0.5 ) * 5 / 2 * math.exp( -x ** 2 / (sd ** 2) ), 0, f)
    MMR = 250 * Itg[0] + 1000
    return MMR

def winrate_kalkulator(igralec):
    '''Izračuna winrate W(zmage)/A(prisotnost).'''
    return igralec.zmage/igralec.prisotnost


def MMR(igralec):
    '''Prejme igralca in zanj izračuna njegov MMR (match-making-rating).'''
    winrate = winrate_kalkulator(igralec)
    goli = igralec.goli
    asistence = igralec.asistence
    avtogoli = igralec.avtogoli
    return MMR_kalkulator(winrate, goli, asistence, avtogoli)



# A = Igralec.pridobi_statistiko(9)
# B = Igralec.pridobi_statistiko(9, '2024-01-01')
# 
# print(Igralec.najdi_igralca('Andraž'))
# print(Igralec.najdi_igralca('Blaž'))
# 
# # print(A)
# 
# a = Igralec.vsi_igralci()
# 
# b = Tekma.najdi_tekmo('2022-09-01')
# c = Tekma.najdi_tekmo('2019-09-01')
# 
# print(b)
# 
# x = Sezona.vse_sezone()