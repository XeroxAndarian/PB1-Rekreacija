import sqlite3
import math
import scipy
import time
import datetime

conn = sqlite3.connect("rekreacija.sqlite")
DANES = datetime.datetime.today().strftime('%Y-%m-%d')
def start():
    '''Vrne prvi termin.'''
    poizvedba = """SELECT datum
                FROM tekma"""
    rezultat = conn.execute(poizvedba).fetchone()[0]
    return rezultat

PRVIC = start()
def prevedi_None(vrednost):
    '''Funkcija sprejme vrensot in, če je None, vrne 0.'''
    if vrednost == None:
        return 0
    else:
        return vrednost

zbirka_zbirk_SR = {}

def zaokrozi(x, decimalke):
    return f"{x:.{decimalke}f}" 

class Igralec:

    def __init__(self, id, ime, priimek, prisotnost, zmage, porazi, goli, asistence, avtogoli, zacetek, konec):
        
        self.id = id
        self.ime = ime
        self.priimek = priimek
        self.zmage = prevedi_None(zmage)   
        self.porazi = prevedi_None(porazi)
        self.prisotnost = prevedi_None(prisotnost)
        self.goli = prevedi_None(goli)
        self.asistence = prevedi_None(asistence)
        self.avtogoli = prevedi_None(avtogoli)

        self.zacetek = zacetek
        self.konec = konec

        # izračunljivi

        # -> MMR
        self.mmr = 0

        # -> SR
        self.sr = []

        # Winrate, lossrate
        self.winrate = 0
        self.lossrate = 0

        # winstreak
        self.winstreak = 0

        # neodlocena
        self.neodlocena = prisotnost - zmage - porazi
        self.tierate = 0

        # rates
        if self.prisotnost != 0:
            self.golirate = goli/prisotnost
            self.asistencerate = asistence/prisotnost
            self.avtogolirate = avtogoli/prisotnost
        else:
            self.golirate = 0
            self.asistencerate = 0
            self.avtogolirate = 0
    



    def __repr__(self):
        return f"ID:{str(self.id)} > {self.ime} {self.priimek}"
    
    def __str__(self):
        if self.mmr == 0:
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
        izpis = f"""
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
MMR: {round(self.mmr)}
Winstreak: {self.winstreak}
-----------------------------
"""
        vse_sezone = Sezona.vse_sezone(self.zacetek, self.konec)
        i = 0
        for sezona in vse_sezone:
            izpis += f"Sezona {sezona}: {self.sr[i][1]}\n"
            i+=1
        izpis += "-----------------------------"

        return izpis
        
    def __lt__(self, other):
        return self.id < other.id
    


    @staticmethod
    def razsirjena_statistika(self):
        '''Metoda igralcu izračuna MMR, winstreak in vse SR za izbrano obdobje.'''
        start = time.time()
        print("Računanje MMR - matchmaiking rating")
        self.nastavi_mmr(self)
        print("Računanje winstreaka")
        self.nastavi_winstreak(self)
        print("Računanje SR - seasonal rating, za vse dosedanje sezone")
        sezone = Sezona.vse_sezone(self.zacetek, self.konec)
        i = 1
        for sezona in sezone:
            print(f"> Računanje za sezono {sezona} ({i} od {len(sezone)})")
            self.sr.append((sezona, SR(sezone[int(sezona)].konec)[int(self.id)]))
            i+=1
        end = time.time()
        cas = end - start
        cas = round(cas)
        minute = cas // 60
        sekunde = cas - minute * 60
        print(f"Opravljeno! Porabljen čas: {minute} min {sekunde} sec")
        return None
    
    @staticmethod
    def pridobi_statistiko(id, zacetek=PRVIC, konec = DANES):
        '''Metoda pridobi statistiko igralca z idejem id in vrne objekt oblike Igralec.'''
        
        # Prisotnost
        poizvedba = """SELECT COUNT(*) 
                    FROM prisotnost
                    JOIN tekma ON (tekma.id = prisotnost.tekma_id)
                    WHERE igralec_id = ? AND 
                    datum >= ? AND
                    datum <= ?"""
        prisotnost = conn.execute(poizvedba, [str(id), zacetek, konec]).fetchone()[0]

        # goli, asistence, avtogoli
        poizvedba = """SELECT SUM(goli), SUM(asistence), SUM(avto_goli) 
                    FROM prisotnost 
                    JOIN tekma ON (tekma.id = prisotnost.tekma_id) 
                    WHERE igralec_id = ? AND datum >= ? AND
                    datum <= ?"""
        statistika = conn.execute(poizvedba, [str(id), zacetek, konec]).fetchone()
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
        zmage = conn.execute(poizvedba, [str(id), zacetek, konec]).fetchone()[0]

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
        porazi = conn.execute(poizvedba, [str(id), zacetek, konec]).fetchone()[0]

        # ime in priimek
        poizvedba = """SELECT vzdevek FROM vzdevek WHERE igralec_id = ?"""
        try: 
            ime = conn.execute(poizvedba, [str(id)]).fetchall()[0][0]
            priimek = conn.execute(poizvedba, [str(id)]).fetchall()[1][0]
        except Exception as e:
            ime = ''
            priimek = ''

        return Igralec(id, ime, priimek, prisotnost, zmage, porazi,  goli, asistence, avtogoli, zacetek, konec)

    
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
    def vsi_igralci(zacetek=PRVIC, konec=DANES):
        '''Metoda vrne slovar vseh igralcev v obliki razreda Igralec.'''
        poizvedba = """SELECT id FROM igralec"""
        slovar = {}
        for igralec_id in conn.execute(poizvedba):
            slovar[igralec_id[0]] = Igralec.pridobi_statistiko(igralec_id[0], zacetek, konec)
        return slovar


    @staticmethod
    def nastavi_winrate(self):
        '''Nastavi winrate igralca.'''
        try:
            winrate = self.zmage / self.prisotnost
        except:
            winrate = 0
        self.winrate = winrate 
        return None
    
    @staticmethod
    def nastavi_lossrate(self):
        '''Nastavi lossrate igralca.'''
        try:
            lossrate = self.zmage / self.prisotnost
        except:
            lossrate = 0
        self.lossrate = lossrate 
        return None
    
    @staticmethod
    def nastavi_tierate(self):
        '''Nastavi tierate igralca.'''
        try:
            tierate = self.zmage / self.prisotnost
        except:
            tierate = 0
        self.tierate = tierate 
        return None
    
    @staticmethod
    def nastavi_mmr(self):
        '''Nastavi MMR igralca.'''
        self.nastavi_winrate(self)
        self.mmr = MMR(self)
        return None
    
    @staticmethod
    def nastavi_winstreak(self):
        '''Nastavi winstreak igralca.'''
        
        tekme = Tekma.tekme_igralca(self.id, self.zacetek, self.konec)
        st_tekem = len(tekme)
        winstreak = 0

        if st_tekem == 0:
            self.winstreak = 0
            return None
        
        tekma = tekme[st_tekem-1]

        if st_tekem == 1:
            if Tekma.zmagovalec_tekme(tekma.id, self.id):
                self.winstreak = 1
            else:
                winstreak = 0
            return None
        
        i = 1
        while Tekma.zmagovalec_tekme(tekma.id, self.id):
            winstreak +=1
            tekma = tekme[st_tekem-1-i]
            i+=1
        
        self.winstreak = winstreak
        return None

    @staticmethod
    def naj_strelec(seznam):
        '''Iz seznama igralcev vrne tistega, ki ima največ golov. Če jih je več takih, ne vrne nobenega.'''
        slovar = {}
        maks_golov = 0
        for igralec in seznam:
            slovar[igralec] = igralec.goli
            if igralec.goli > maks_golov:
                maks_golov = igralec.goli
        najboljsi = []
        for igralec in seznam:
            if slovar[igralec] == maks_golov:
                najboljsi.append(igralec)
        
        if len(najboljsi) == 1:
            return najboljsi[0]
        else:
            return None
        
    
    @staticmethod
    def naj_podajalec(seznam):
        '''Iz seznama igralcev vrne tistega, ki ima največ golov. Če jih je več takih, ne vrne nobenega.'''
        slovar = {}
        maks_asistenc = 0
        for igralec in seznam:
            slovar[igralec] = igralec.asistence
            if igralec.asistence > maks_asistenc:
                maks_asistenc = igralec.asistence
        najboljsi = []
        for igralec in seznam:
            if slovar[igralec] == maks_asistenc:
                najboljsi.append(igralec)
        
        if len(najboljsi) == 1:
            return najboljsi[0]
        else:
            return None
        
    @staticmethod
    def nastavi_sr(self):
        self.sr = [SR(self.konec)[self.id]]
        return None

class Tekma:

    def __init__(self, id, datum="", goli_ekipa_0=0, goli_ekipa_1=0, ekipa_0=[], ekipa_1=[]):
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
            return Tekma(0)

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
                ekipi[ekipa_id].append(Igralec.pridobi_statistiko(igralec[0], datum, datum))
        

        return Tekma(id_tekme, datum, goli_A, goli_B, ekipi[0], ekipi[1])
    
    @staticmethod
    def najdi_tekmo_id(id):
        '''Metoda najde in vrne tekmo v obliki objekta Tekma, ki ima ID id.'''

        # id,  goli A, goli B
        poizvedba = """SELECT id, goli_a, goli_b, datum
                    FROM tekma
                    WHERE id = ? """
        rezultat = conn.execute(poizvedba, [str(id)]).fetchall()
        
        if rezultat == []:
            return Tekma(id)

        goli_A = rezultat[0][1]
        goli_B = rezultat[0][2]
        datum = rezultat[0][3]
        # ekipi
        ekipi = {0:[], 1:[]}
        for ekipa_id in [0, 1]:
            poizvedba = """SELECT prisotnost.igralec_id
                        FROM tekma
                        JOIN prisotnost ON (prisotnost.tekma_id = tekma.id)
                        WHERE tekma.id = ? AND prisotnost.ekipa = ?"""
            rezultat = conn.execute(poizvedba, [id, ekipa_id]).fetchall()
            for igralec in rezultat:
                ekipi[ekipa_id].append(Igralec.pridobi_statistiko(igralec[0], datum, datum))
        

        return Tekma(id, datum, goli_A, goli_B, ekipi[0], ekipi[1])
    
    @staticmethod
    def vse_tekme(zacetek=PRVIC, konec=DANES):
        '''Metoda vrne slovar objektov vseh tekem v določenem časovnem obdobju.'''
        tekme = []
        poizvedba = """SELECT id
                    FROM tekma
                    WHERE datum >= ? AND datum <= ?"""
        rezultat = conn.execute(poizvedba,[zacetek, konec]).fetchall()
        for i in rezultat:
            tekme.append(Tekma.najdi_tekmo_id(i[0]))
        return tekme
    
    @staticmethod
    def eno_vrsticni_izpis(tekma):
        '''Metoda v eni vrstici na krato izpiše podatke o tekmi.'''
        return f"Tekma id: {tekma.id}; datum: {tekma.datum} --> A:B = {tekma.goli_ekipa_0}:{tekma.goli_ekipa_1}"
    
    @staticmethod
    def tekme_igralca(id=0, zacetek = PRVIC, konec = DANES):
        '''Metoda vrne seznam tekem, na katerih je igral igralec z ID-jem id v izbranem časovnem obdobju.'''
        tekme = []
        poizvedba = """SELECT *
                    FROM tekma
                    JOIN prisotnost ON (prisotnost.tekma_id = tekma.id) 
                    WHERE tekma.datum > ? 
                            AND 
                            tekma.datum < ? 
                            AND
                            prisotnost.igralec_id = ?
                            """
        rezultat = conn.execute(poizvedba,[zacetek, konec, id]).fetchall()
        for i in rezultat:
            tekme.append(Tekma.najdi_tekmo_id(i[0]))
        return tekme

    @staticmethod
    def prisotni_id(tekma):
        '''Vrne seznam ID-jev prisotnih igralcev na tekmi.'''
        prisotni_id = []
        prisotni = tekma.ekipa_0 + tekma.ekipa_1
        for igralec in prisotni:
            prisotni_id.append(igralec.id)
        return prisotni_id
    
    @staticmethod
    def prisotni_id_po_ekipah(tekma):
        '''Vrne seznam ID-jev prisotnih igralcev na tekmi.'''
        prisotni_id_0 = []
        prisotni = tekma.ekipa_0
        for igralec in prisotni:
            prisotni_id_0.append(igralec.id)

        prisotni_id_1 = []
        prisotni = tekma.ekipa_1
        for igralec in prisotni:
            prisotni_id_1.append(igralec.id)
        return prisotni_id_0, prisotni_id_1

    @staticmethod
    def zmagovalec(tekma):
        '''Vrne:
        0 - če zmagala ekipa 0
        1 - če zmagala ekipa 1
        None - izenačeno'''

        if tekma.goli_ekipa_0 > tekma.goli_ekipa_1:
            return 0
        elif tekma.goli_ekipa_0 < tekma.goli_ekipa_1:
            return 1
        else:
            return None


    @staticmethod
    def zmagovalec_tekme(tekma_id, igralec_id):
        '''Vrne true, če je igralec bil v zmagovalni ekipi oz. false, če ne. Vrne None, če igralca sploh ni bilo na tekmi.'''
        tekma = Tekma.najdi_tekmo_id(tekma_id)
        sodeloval = None
        prisotni = Tekma.prisotni_id(tekma)
        
        if igralec_id not in prisotni:
            return None
        
        if tekma.goli_ekipa_0 > tekma.goli_ekipa_1:
            zmagovalec = Tekma.prisotni_id_po_ekipah(tekma)[0]
        elif tekma.goli_ekipa_0 < tekma.goli_ekipa_1:
            zmagovalec = Tekma.prisotni_id_po_ekipah(tekma)[1]
        else:
            zmagovalec = []

        return (igralec_id in zmagovalec)

    @staticmethod
    def mvp(tekma):
        '''Vrne par igralcev ( G , A ), kjer igralec G najboljši strelec tekme in A najboljši podajalec tekme.'''
        prisotni = []
        for id_igralec in Tekma.prisotni_id(tekma):
            prisotni.append(Igralec.pridobi_statistiko(id_igralec, tekma.datum, tekma.datum))
        mvp_goli = Igralec.naj_strelec(prisotni)
        mvp_asistence = Igralec.naj_podajalec(prisotni)
        return mvp_goli, mvp_asistence
        
    @staticmethod
    def izpisi_tekmo_dodatno(tekma):
        izpis = ""
        izpis += "Tekma\n"
        izpis += ("-" * 59 + "\n")
        izpis += f"Tekma ID: {tekma.id}\n"
        izpis += f"datum: {tekma.datum}\n"
        izpis += f"rezultat:  {tekma.goli_ekipa_0}:{tekma.goli_ekipa_1}\n"
        izpis += (" Ekipa A" + " " * 21 + " " + " Ekipa B\n")
        izpis += (" Igralec" + " " * 12 +"|Go"+ "|As" + "|AG|"+  " Igralec" + " " * 12 +"|Go"+ "|As" + "|AG"+ "\n")
        izpis +=  ("-" * 20 + "|" + "--" + "|" + "--" + "|" + "--" + "|" + 20 * "-" + "|" + "--" + "|" + "--" + "|" + "--" + "\n")
        
        tabela = [""] * max(len(tekma.ekipa_0), len(tekma.ekipa_1))  
        ekipa0 = tekma.ekipa_0
        ekipa1 = tekma.ekipa_1
        j = 1
        for ekipa in [ekipa0, ekipa1]:
            i = 0
            while i < len(tabela):
                try: 
                    igralec = ekipa[i]
                except:
                    igralec = Igralec.pridobi_statistiko(0, tekma.datum, tekma.datum)
                ime_priimek = f"{igralec.ime} {igralec.priimek}"
                dolzina_ime = len(ime_priimek)
                tabela[i] += (" " + ime_priimek + " " * (19 - dolzina_ime))
                tabela[i] +=  ("|" + " " * len(str(igralec.goli)) + (str(igralec.goli))) 
                tabela[i] += ("|" + " " * len(str(igralec.asistence)) + (str(igralec.asistence))) 
                tabela[i] += ("|" + " " * len(str(igralec.avtogoli)) + (str(igralec.avtogoli)))
                tabela[i] += ("|" * j + "\n" * (abs(j-1)))
                i+=1
            j-=1

        for vrstica in tabela:
            izpis += vrstica
        
        mvp = Tekma.mvp(tekma)
        mvp_goli = mvp[0]
        mvp_asistence = mvp[1]

        izpis += "\n"
        return izpis

class Sezona:

    def __init__(self, sezona, zacetek, konec, tekme=0, goli=0, assitence=0, avtogoli=0):
        self.id = sezona
        self.zacetek = zacetek
        self.konec = konec
        self.tekme = tekme
        self.goli = goli
        self.asistence = assitence
        self.avtogoli = avtogoli

    def __repr__(self):
        return f"Sezona {self.id} [{self.zacetek} - {self.konec}]"
    
    def __str__(self):
        if self.tekme == 0:
            return f"Sezona {self.id} [{self.zacetek} - {self.konec}]"
        else:
            izpis =  f"""
Sezona {self.id}
---------------
ID: {self.id}
Začetek: {self.zacetek}
Konec: {self.konec}
Tekem: {self.tekme}
Golov: {self.goli}
Asistenc: {self.asistence}
Avtogolov: {self.avtogoli}
---------------
Seznam tekem:
""" 
            seznam_tekem = Tekma.vse_tekme(self.zacetek, self.konec)
            for tekma in seznam_tekem:
                izpis += "  "
                izpis += Tekma.eno_vrsticni_izpis(tekma)
                izpis += "\n"
            
            return izpis



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
    def vse_sezone(zacetek = PRVIC, konec = "2099-12-31"):
        '''Metoda vrne slovar objektov vseh sezon.'''
        sezone = {}
        poizvedba = """SELECT id
                    FROM sezona
                    WHERE zacetek >= ? AND konec <= ?"""
        rezultat = conn.execute(poizvedba, [zacetek, konec]).fetchall()
        # print(rezultat)
        for i in rezultat:
            zacetek = Sezona.sezona_zacetek(i[0])
            konec = Sezona.sezona_konec(i[0])
            sezone[i[0]] = Sezona(i[0], zacetek, konec)
        return sezone
    
    @staticmethod
    def najdi_sezono(datum):
        '''Metoda prejme datum in vrne sezono, v katero datum spada.'''
        sezone = Sezona.vse_sezone()
        i = 1
        while i <= len(sezone) and datum > sezone[i].konec:
            i+=1
        i = min(i, len(sezone))
        return sezone[i]

    @staticmethod
    def pridobi_podatke(self):
        '''Metoda izračuna osnovne podatke o sezoni (tekme, goli, asistence, avtogoli).'''
        poizvedba = """SELECT COUNT(DISTINCT tekma_id), SUM(goli), SUM(asistence), SUM(avto_goli) 
                    FROM prisotnost
                    JOIN tekma ON (tekma.id = prisotnost.tekma_id)
                    WHERE tekma.datum > ? AND tekma.datum < ?"""
        rezultat = conn.execute(poizvedba, [self.zacetek, self.konec]).fetchall()
        self.tekme = rezultat[0][0]
        self.goli = rezultat[0][1]
        self.asistence = rezultat[0][2]
        self.avtogoli = rezultat[0][3]
        return None



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
    try:
        winrate = igralec.zmage/igralec.prisotnost
    except:
        winrate = 0
    return winrate


def MMR(igralec):
    '''Prejme igralca in zanj izračuna njegov MMR (match-making-rating).'''
    igralec.nastavi_winrate(igralec)
    winrate = igralec.winrate
    golirate = igralec.golirate
    asistencerate = igralec.asistencerate
    avtogolirate = igralec.avtogolirate
    return MMR_kalkulator(winrate, golirate, asistencerate, avtogolirate)


def SR_kalkulator(trenutni, rezultat_prejsne_tekme, goli, asistence, avtogoli, winstreak, mvpg, mvpa, soigralci, nasprotniki, slovar_SR):
    '''Vrne seasonal rating igralca pri danih podatkih.'''
    # Pomožne lambda funkcije
    G = lambda x: 10*x + max(0, 2*(x - 2))   # 10 SR for 1st and second, after that, 12 per goal
    A = lambda x: 6*x + max(0, 2*(x - 2))    # 6 SR for 1st and second, after that, 8 per assist
    AG = lambda x: -2*x                     # -2 SR per auto goal
    W = lambda x: 20*x                      # 20 SR for victory, 0 for tie and -20 for defeat, but it's weighted
    WS = lambda x: max(0, 3*(x - 1))                # 3 * winstreak SR
    H = lambda x,y: 1 + 10 * (x/y - 1)      # Weight (Heavy)

    if soigralci == []:
        SR_nasprotniki_povp = 1
        SR_soigralci_povp = 1
    else:    
        SR_soigralci = sum(soigralci)
        SR_soigralci_povp = SR_soigralci / len(soigralci)
        SR_nasprotniki = sum(nasprotniki)
        SR_nasprotniki_povp = SR_nasprotniki / len(nasprotniki)

    
    if (mvpa & mvpg):
        k = 25
    elif (mvpa | mvpg):
        k = 10
    else:
        k = 0

    if rezultat_prejsne_tekme == 1:
        return trenutni +  G(goli) + A(asistence) + AG(avtogoli) + W(rezultat_prejsne_tekme) * H(SR_nasprotniki_povp, SR_soigralci_povp) + k + WS(winstreak)
    elif rezultat_prejsne_tekme == -1:
        return trenutni +  G(goli) + A(asistence) + AG(avtogoli) + W(rezultat_prejsne_tekme) * H(SR_soigralci_povp, SR_nasprotniki_povp) + k + WS(winstreak)
    else:
        return trenutni +  G(goli) + A(asistence) + AG(avtogoli) + k + WS(winstreak)

def nastavi_zbirko_SR():
    '''Nastavi zbirko seasonal ratingov na začetku sezone -> vsi so 1000.'''
    slovar_SR = Igralec.vsi_igralci()
    
    for igralec in slovar_SR:
        slovar_SR[igralec] = 1000
    return slovar_SR

def nov_SR(datum, zbirka_SR):
    '''Izračuna nov SR glede na tekmo, ki se je odvijala na datum in na prejšnji SR.'''
    if datum in zbirka_zbirk_SR:
        return zbirka_zbirk_SR[datum]
    
    tekma = Tekma.najdi_tekmo(datum)
    prisotni = Tekma.prisotni_id_po_ekipah(tekma)
    ekipa_0 = []
    ekipa_0_SR = []
    ekipa_1 = []
    ekipa_1_SR = []

    for ekipa in [(prisotni[0], ekipa_0, ekipa_0_SR), (prisotni[1], ekipa_1, ekipa_1_SR)]:
        for id_igralec in ekipa[0]:
            ekipa[1].append(Igralec.pridobi_statistiko(str(id_igralec), datum, datum))
            ekipa[2].append(zbirka_SR[id_igralec])
           
    

    zbirka_SR_kopija = zbirka_SR.copy()
    mvp = Tekma.mvp(tekma)
    
    for igralec in mvp:
        if igralec == None:
            igralec = Igralec.pridobi_statistiko(0)
            
    
    for ekipa in [ekipa_0, ekipa_1]:
        mvp_goli, mvp_asistence = False, False
        rezultat = 0
        for igralec in ekipa:
            # nastavitev mvp
            if mvp[0] != None and igralec.id == mvp[0].id:
                mvp_goli = True
            if mvp[1] != None and igralec.id == mvp[1].id:
                mvp_asistence = True

            # nastavitev prejsnjega rezultata
            if Tekma.zmagovalec_tekme(tekma, igralec) == None:
                rezultat = 0
            elif Tekma.zmagovalec_tekme(tekma, igralec):
                rezultat = 1
            else:
                rezultat = -1

            # nastavitev winstreaka
            stat_do_sedaj = Igralec.pridobi_statistiko(igralec.id, PRVIC, igralec.konec)
            stat_do_sedaj.nastavi_winstreak(stat_do_sedaj)

            # nastavitev nasprotnikov
            if ekipa == ekipa_0:
                soigralci = ekipa_0_SR
                nasprotnik = ekipa_1_SR
            else:
                soigralci = ekipa_1_SR
                nasprotnik = ekipa_0_SR
            nov_SR = SR_kalkulator(zbirka_SR_kopija[int(igralec.id)], rezultat, igralec.goli, igralec.asistence, igralec.avtogoli, stat_do_sedaj.winstreak, mvp_goli, mvp_asistence, soigralci, nasprotnik, zbirka_SR_kopija)
            zbirka_SR[int(igralec.id)] = nov_SR
            
    zbirka_zbirk_SR[datum] = zbirka_SR
    return zbirka_SR


def SR(datum):
    '''Izračuna SR igralca z ID-jem igralec_id na datum datum. Za tekme proti koncu sezone lahko traja nekaj dalj časa.'''
    if datum in zbirka_zbirk_SR:
        return zbirka_zbirk_SR[datum]
    
    zbirka_SR = nastavi_zbirko_SR()
    sezona = Sezona.najdi_sezono(datum)
    tekme = Tekma.vse_tekme(sezona.zacetek, datum)

    stevec = 0
    skok = 100 / len(tekme)
    dolzina_crte = 40  
    i = 0
    bar = "-" * dolzina_crte
    print(f"\rRačunam SR |{bar}| {round(stevec)}%", end="", flush=True)

    for tekma in tekme:
        zbirka_SR = nov_SR(tekma.datum, zbirka_SR)

        i+=1
        stevec += skok
        progress = int((i / len(tekme)) * dolzina_crte)
        bar = "█" * progress + "-" * (dolzina_crte - progress)
        print(f"\rRačunam SR |{bar}| {round(stevec)}%", end="", flush=True)

    print("")
    
    return zbirka_SR

class Lestvica:

    def __init__(self, kategorija="", datum="", stevilo=0, vsebina=[], zacetek = ""):
        self.kategorija = kategorija
        self.stevilo = stevilo
        self.vsebina = vsebina
        self.datum = datum
        self.zacetek = zacetek

    def __repr__(self):
        if self.stevilo == 0:
            return f"Lestvica najboljših v kategoriji: {self.kategorija} za obdobje: {self.zacetek} - {self.datum}."
        else:
            return f"Lestvica najboljših {self.stevilo} v kategoriji: {self.kategorija} za obdobje: {self.zacetek} - {self.datum}."

    def __str__(self):
        if self.stevilo == 0:
            uvod = f"Lestvica najboljših v kategoriji: {self.kategorija}.\nOd: {self.zacetek}\nDo: {self.datum}\n"
        else:
            uvod = f"Lestvica najboljših {self.stevilo} v kategoriji: {self.kategorija}.\nOd: {self.zacetek}\nDo: {self.datum}\n"      

        premor = "-" * 50 + "\n"
        jedro = ""
        i = 1
        for igralec in self.vsebina:
            ime = f"{i}. {igralec.ime} {igralec.priimek} "
            if self.kategorija == 'Prisotnost':
                statistika = f"{str(igralec.prisotnost)}"
            if self.kategorija == 'Zmage':
                statistika = f"{str(igralec.zmage)}"
            if self.kategorija == 'Porazi':
                statistika = f"{str(igralec.porazi)}"    
            if self.kategorija == 'Goli':
                statistika = f"{str(igralec.goli)}"
            if self.kategorija == 'Asistence':
                statistika = f"{str(igralec.asistence)}"
            if self.kategorija == 'Avtogoli':
                statistika = f"{str(igralec.avtogoli)}"
            if self.kategorija == 'Neodločenosti':
                statistika = f"{str(igralec.neodlocena)}"
            if self.kategorija == 'winstreak':
                statistika = f"{str(igralec.winstreak)}"
            if self.kategorija == 'MMR':
                statistika = f"{str(round(igralec.mmr))}"
            if self.kategorija == 'Winrate':
                statistika = f"{str(zaokrozi(igralec.winrate, 2))}"
            if self.kategorija == 'Lossrate':
                statistika = f"{str(zaokrozi(igralec.lossrate, 2))}"
            if self.kategorija == 'Tierate':
                statistika = f"{str(zaokrozi(igralec.tierate, 2))}"
            if self.kategorija == 'Goalrate':
                statistika = f"{str(zaokrozi(igralec.golirate, 2))}"
            if self.kategorija == 'Assistencerate':
                statistika = f"{str(zaokrozi(igralec.asistencerate, 2))}"
            if self.kategorija == 'AGrate':
                statistika = f"{str(zaokrozi(igralec.avtogolirate, 2))}"
            if self.kategorija == 'SR' and igralec.sr != []:
                statistika = f"{str(round(igralec.sr[0]))}"
            praznina = " " * (30 - len(ime)) + "|" + " " * (5 - len(statistika))
            vrstica = ime + praznina + statistika + "\n"
            jedro += vrstica
            i+=1
        return uvod + premor + jedro + premor
                               
    @staticmethod
    def prevajalnik(kategorija):
        '''Metoda prejme kateogirjo in ji priredi ime, ki se ujema v SQL-ju.'''
        if kategorija == "Goli":
            return "goli"
        if kategorija == "Asistence":
            return "asistence"
        if kategorija == "Avtogoli":
            return "avto_goli"
        if kategorija == "Prisotnost":
            return "prisotnost"
        if kategorija == "Zmage":
            return "zmage"
        if kategorija == "Porazi":
            return "porazi"
        if kategorija == "Neodlocene":
            return "neodlocene"
        if kategorija == "MMR":
            return "mmr"
        if kategorija == "Winrate":
            return "winrate"
        if kategorija == "Winstreak":
            return "winstreak"
        if kategorija == "Winrate":
            return "winrate"
        if kategorija == "Lossrate":
            return "lossrate"
        if kategorija == "Tierate":
            return "tierate"
        if kategorija == "Goalrate":
            return "golirate"
        if kategorija == "Assistencerate":
            return "asistencerate"
        if kategorija == "AGrate":
            return "avtogolirate"
        else:
            return kategorija
        


    @staticmethod
    def pridobi_lestvico_g_a_ag(kategorija, datum, stevilo=0, zacetek = PRVIC):
        '''Metoda vrne lestvice velikosti stevilo za kategorijo goli / asistence / avtogoli.'''
        vsebina = []
        kat = Lestvica.prevajalnik(kategorija)
        if stevilo == 0:
            poizvedba = f"""SELECT igralec_id, igralec.ime, igralec.priimek, SUM({kat})
                    FROM igralec
                    JOIN prisotnost ON (igralec.id = prisotnost.igralec_id)
                    JOIN tekma ON (prisotnost.tekma_id = tekma.id)
                    WHERE tekma.datum <= ? AND tekma.datum >= ?
                    GROUP BY igralec.id
                    ORDER BY SUM({kat}) DESC"""
            rezultat = conn.execute(poizvedba, [datum, zacetek]).fetchall()
        else: 
            poizvedba = f"""SELECT igralec_id, igralec.ime, igralec.priimek, SUM({kat})
                    FROM igralec
                    JOIN prisotnost ON (igralec.id = prisotnost.igralec_id)
                    JOIN tekma ON (prisotnost.tekma_id = tekma.id)
                    WHERE tekma.datum <= ? AND tekma.datum >= ?
                    GROUP BY igralec.id
                    ORDER BY SUM({kat}) DESC
                    LIMIT ?"""
            rezultat = conn.execute(poizvedba, [datum, zacetek, stevilo]).fetchall()
        for i in rezultat:
            igralec = Igralec.pridobi_statistiko(i[0], PRVIC, datum)
            if igralec.ime != "":
                vsebina.append(igralec)
        return Lestvica(kategorija, datum, stevilo, vsebina, PRVIC)
    
    @staticmethod
    def pridobi_lestvico_prisotnost(datum, stevilo=0,  zacetek = PRVIC):
        '''Metoda vrne lestvice velikosti stevilo za kategorijo prisotnost.'''
        vsebina = []
        kat = "prisotnost"
        if stevilo == 0:
            poizvedba = f"""SELECT igralec_id, igralec.ime, igralec.priimek, COUNT(*)
                    FROM igralec
                    JOIN prisotnost ON (igralec.id = prisotnost.igralec_id)
                    JOIN tekma ON (prisotnost.tekma_id = tekma.id)
                    WHERE tekma.datum <= ? AND tekma.datum >= ?
                    GROUP BY igralec.id
                    ORDER BY COUNT(*) DESC"""
            rezultat = conn.execute(poizvedba, [datum, zacetek]).fetchall()
        else: 
            poizvedba = f"""SELECT igralec_id, igralec.ime, igralec.priimek, COUNT(*)
                    FROM igralec
                    JOIN prisotnost ON (igralec.id = prisotnost.igralec_id)
                    JOIN tekma ON (prisotnost.tekma_id = tekma.id)
                    WHERE tekma.datum <= ? AND tekma.datum >= ?
                    GROUP BY igralec.id
                    ORDER BY COUNT(*) DESC
                    LIMIT ?"""
            rezultat = conn.execute(poizvedba, [datum, zacetek, stevilo]).fetchall()
        for i in rezultat:
            igralec = Igralec.pridobi_statistiko(i[0], zacetek, datum)
            if igralec.ime != "":
                vsebina.append(igralec)
        return Lestvica("Prisotnost", datum, stevilo, vsebina, PRVIC)
    
    @staticmethod
    def pridobi_lestvico_razno(kategorija, datum, stevilo=0,  zacetek = PRVIC):
        '''Vrne lestvico najboljsih (stevilo) za kategorijo zmage / porazi / neodlocene / MMR / winrate / winstreak.'''
        igralci = Igralec.vsi_igralci(zacetek, datum)
        prazni = []
        for igralec_id in igralci:
            if igralci[igralec_id].ime == "":
                prazni.append(igralec_id)
        for igralec_id in prazni:
            del igralci[igralec_id]

        for i in igralci:
            igralci[i].nastavi_winstreak(igralci[i])
            igralci[i].nastavi_winrate(igralci[i])
            igralci[i].nastavi_lossrate(igralci[i])
            igralci[i].nastavi_tierate(igralci[i])
            igralci[i].nastavi_mmr(igralci[i])

        kat = Lestvica.prevajalnik(kategorija)

        def sortiraj_igralce(igralci, atribut, padajoce=True):
            return sorted(igralci.values(), key=lambda igralec: getattr(igralec, atribut), reverse=padajoce)
        
        
        seznam_igralcev = sortiraj_igralce(igralci, kat)
        if stevilo == 0:
            vsebina = seznam_igralcev
        else:
            vsebina = seznam_igralcev[:stevilo]

        return Lestvica(kategorija, datum, stevilo, vsebina, PRVIC)
    
    @staticmethod
    def pridobi_lestvico_SR(datum, stevilo=0,  zacetek = PRVIC):
        '''Vrne lestvico najboljsih (stevilo) za kategorijo zmage / porazi / neodlocene / MMR / winrate / winstreak.'''
        igralci = Igralec.vsi_igralci(zacetek, datum)
        prazni = []
        for igralec_id in igralci:
            if igralci[igralec_id].ime == "":
                prazni.append(igralec_id)
        for igralec_id in prazni:
            del igralci[igralec_id]

        zbirka_SR = SR(datum)
       
        seznam_igralcev = []
        seznam_igralcev_id = [k for k, v in sorted(zbirka_SR.items(), key=lambda item: item[1], reverse=True)]

        i=0
        for igralec_id in seznam_igralcev_id:
            seznam_igralcev.append(Igralec.pridobi_statistiko(igralec_id, zacetek, datum))
            if zbirka_SR[igralec_id] != 1000:
                seznam_igralcev[i].sr = [zbirka_SR[igralec_id]]
            i+=1


        if stevilo == 0:
            vsebina = seznam_igralcev
        else:
            vsebina = seznam_igralcev[:stevilo]

        return Lestvica("SR", datum, stevilo, vsebina, PRVIC)

# l = Lestvica.pridobi_lestvico_prisotnost("2029-02-21") 
# print(l)
# 
# t = Lestvica.pridobi_lestvico_SR("2024-02-01", 0, "2022-09-01")
# print(t)
