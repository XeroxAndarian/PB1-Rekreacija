import model
import datetime
import time


DANES = datetime.datetime.today().strftime('%Y-%m-%d')
PRVIC = model.start()


# =============== POMOŽNE FUNKCIJE ============================
def napaka(f):
    '''Kadarkoli pritisnemo napačno izbiro želimo izpisati stalno sporočilo in vrniti meni f.'''
    print("Vpisali ste neveljavno izbiro. Prosim, da izberete eno izmed navedenih možnosti.")
    return f()

def casovno_obdobje(prihod):
    '''Funkcija od od uporabnika pridobi informacije o začetku in koncu obdobja, ki ga zanima za igralca in vrne podatke o igralcu iz tega obdobja.'''
    print("=" * 50)
    print("Od kdaj do kdaj te zanima statistika?")
    
    sezone = []
    i = 1
    while i <= len(model.Sezona.vse_sezone()):
        print(f"{i} - Sezona {i} [{model.Sezona.sezona_zacetek(i)} - {model.Sezona.sezona_konec(i)}]")
        sezone.append(i)
        i+=1

    j = i+1
    print(f"{i} - Celotna statistika")
    print(f"{j} - Po Meri")
    print("0 - Nazaj na začetni zaslon")

    izbira = input("--> ")
    
    if izbira == f"{i}":
        return (PRVIC, DANES)
    
    
    if izbira == "0":
        osnovni_meni()
        return None
    
    if izbira == f"{j}":
        print(f"Navedi od kdaj do kdaj, te zanima statistika.\nČe te zanima samo začetni (ali samo končni) datum, ga samo preskoči (enter).")
        zacetek_dan = input("Od: (Dan) --> ")
        zacetek_mesec = input("Od: (Mesec) --> ")
        zacetek_leto = input("Od: (Leto) --> ")
        konec_dan = input("Do: (Dan) --> ")
        konec_mesec = input("Do: (Mesec) --> ")
        konec_leto = input("Do: (Leto) --> ")

        if len(zacetek_dan) == 1:
            zacetek_dan = "0" + zacetek_dan

        if len(zacetek_mesec) == 1:
            zacetek_mesec = "0" + zacetek_mesec

        if len(konec_dan) == 1:
            konec_dan = "0" + konec_dan

        if len(konec_mesec) == 1:
            konec_mesec = "0" + konec_mesec

        zacetek = zacetek_leto + "-" + zacetek_mesec + "-" + zacetek_dan
        konec = konec_leto + "-" + konec_mesec + "-" + konec_dan

        if zacetek == "--":
            zacetek = PRVIC
        
        if konec == "--":
            konec = DANES

        return (zacetek, konec)
    
    try:
        x = int(izbira)
    except:
        napaka(casovno_obdobje)

    if int(izbira) in sezone:
        zacetek = model.Sezona.sezona_zacetek(izbira)
        konec = model.Sezona.sezona_konec(izbira)
        return(zacetek, konec)
    
    else:
        napaka(casovno_obdobje)

def popravi_napako(ponovitev, prihod):
    '''V primeru napačnega vnosa vpraša uporabnika ali želi ponovo vpisati poizvedbo ali se vrniti nazaj na osnovni meni.'''
    print("=" * 50)
    print("Vpisali ste neveljavno izbiro. Prosim, da izberete eno izmed navedenih možnosti.")
    print("1 - Ponoven vnos")
    print("2 - Nazaj")
    print("0 - Na osnovni meni")
    izbira = input("--> ")

    if izbira == "1":
        ponovitev()
    
    if izbira == "2":
        prihod()

    if izbira == "0":
        osnovni_meni()

    else:
        napaka(popravi_napako(ponovitev, prihod))

def id_iz_imena(prihod):
    '''Vrne Igralca iz povpraševanja po igralčevem imenu, priimku ali vzdevku.'''
    print("=" * 50)
    print("Vpiši ime, priimek ali vzdevek igralca, ki te zanima:")
    igralec = input("Igralec: --> ") 
    moznosti = model.Igralec.najdi_igralca(igralec)
    if moznosti != []:
        print("=" * 50)
        print("Rezultati iskanja: ")
        for igralec in moznosti:
            print(f"ID:{str(igralec.id)} > {igralec.ime} {igralec.priimek}")
        return id_igralca(prihod)
    else:
        print("Igralec s tem imenom, vzdevkom ali priimkom ne obstaja. Preveri, če si se slučajno zatipkal. Sicer poskusi poiskati drugega igralca.")
        popravi_napako(id_igralca, meni_igralec)

def id_igralca(prihod):
    '''Vrne podatke o igralcu iz določenega časovnega obdobja.'''
    print("=" * 50)
    print("Vpiši ID igralca, za katerega te zanima statistika:")
    igralec_id = input("ID igralca: --> ")
    rezultat = model.Igralec.pridobi_statistiko(igralec_id)
    if rezultat.ime == '':
        print("Igralec s tem ID-jem ne obstaja. Preveri, če si se slučajno zatipkal. Sicer poskusi poiskati drugega igralca.")
    else: 
        obdobje = casovno_obdobje(prihod)
        rezultat = model.Igralec.pridobi_statistiko(igralec_id, obdobje[0], obdobje[1])
        return rezultat
        
def meni(uvodni_stavek , seznam_izbir, nazaj=True, na_osnovni=True):
    '''Iz seznama izbir vrne meni.'''
    locitvena_vrsta = "=" * 50
    uvod = uvodni_stavek
    izpis = locitvena_vrsta + "\n" + uvod + "\n"
    i = 1
    for izbira in seznam_izbir:
        vrstica = f"{i} - {izbira}\n"
        izpis += vrstica
        i += 1
    if nazaj:
        izpis += f"{i} - Nazaj\n"
    if na_osnovni:   
        izpis += f"0 - Nazaj na začetni meni"

    return izpis

def praznina():
    while True:
        pass
    return None

def izhod():
    print("Do prihodnjič!")
    praznina()
    return None

def opozorilo_cakanje(prihod):
    '''Uporabniku vrne informacijo o tem, da bo naslednja poteza morda trajala nekaj dalj časa.'''
    sezone = model.Sezona.vse_sezone()
    stevilo_sezon = len(sezone)
    izpis = meni(f"Opozorilo: Naslednja poizvedba lahko porabi več časa, saj je morda treba izračunati precej podatkov (< {stevilo_sezon} min).\nSte prepričani, da želite nadaljevati?", ["Da", "Ne"], False, False)
    
    print(izpis)

    izbira = input("--> ")

    if izbira == "1":
        return None
    elif izbira == "2":
        prihod()
    else:
        napaka(opozorilo_cakanje)
  
def na_osnovni_meni():
    input("Pritisnite tipko enter za vrnitev na osnovni meni: --> ")
    osnovni_meni()
    return None

def nadaljuj():
    '''Funckija ponudi pavzo pred nadaljevanjem brskanja.'''
    print("Pritisnite poljubno tipko za nadaljevanje.")
    input("--> ")
    return None

def tekma_id(prihod):
    '''Vrne podatke o tekmi z Id-jem ID.'''
    print("=" * 50)
    print("Vpiši ID tekme, za katero te zanima statistika:")
    tekma_id = input("ID tekme: --> ")
    rezultat = model.Tekma.najdi_tekmo_id(int(tekma_id))
    if rezultat.id == 0:
        popravi_napako(tekma_id, prihod)
    return rezultat

def tekma_datum(prihod):
    '''Vrne podatke o tekmi na izbrani datum.'''
    print("=" * 50)
    print("Vpiši datum tekme, za katero te zanima statistika:")
    datum_dan = input("Od: (Dan) --> ")
    datum_mesec = input("Od: (Mesec) --> ")
    datum_leto = input("Od: (Leto) --> ")
    if len(datum_dan) == 1:
        datum_dan = "0" + datum_dan

    if len(datum_mesec) == 1:
        datum_mesec = "0" + datum_mesec

    datum = datum_leto + "-" + datum_mesec + "-" + datum_dan

    if datum == "--":
        tekme_meni()
    
    return datum

def datum(prihod):
    '''Povpraša po datumu.'''
    print("=" * 50)
    print("Vpiši datum:")
    datum_dan = input("Od: (Dan) --> ")
    datum_mesec = input("Od: (Mesec) --> ")
    datum_leto = input("Od: (Leto) --> ")
    if len(datum_dan) == 1:
        datum_dan = "0" + datum_dan

    if len(datum_mesec) == 1:
        datum_mesec = "0" + datum_mesec

    datum = datum_leto + "-" + datum_mesec + "-" + datum_dan

    if datum == "--":
        prihod()
    
    return datum


#  ========== MENIJI ====================================
def osnovni_meni():
    """Meni, ki ga bomo zagledali ob zagonu vmesnika."""
    
    izpis = meni("Izberi možnost:", ["Podatki o igralcih", "Podatki o tekmah", "Podatko o sezonah", "Lestvice"], False, False)
    izpis += "0 - Izhod"
    print(izpis)

    izbira = input("--> ")

    if izbira == "1":
        meni_igralec()
        pass
        
    
    if izbira == "2":
        tekme_meni()
        pass

    if izbira == "3":
        sezona_meni()
        pass

    if izbira == "4":
        lestvice_meni()
        pass

    if izbira == "0":
        izhod()
        return None
    
    else:
        napaka(osnovni_meni)


def meni_igralec():
    '''Vodi uporabnika skozi meni iskanja podatkov o igralcu.'''

    izpis = meni("Izberi način iskanja", 
                ["Iskanje po ID", 
                 "Iskanje po imeu / priimku / vzdevku"
                 ], False)

    print(izpis)

    izbira = input("--> ")

    if izbira == "1":
        igralec = id_igralca(meni_igralec)
        print("")
        print(igralec)
        nadaljuj()
        natancnejsi_podatki_igralec(igralec, meni_igralec)
        

    if izbira == "2":
        igralec = id_iz_imena(meni_igralec)
        print("")
        print(igralec)
        nadaljuj()
        natancnejsi_podatki_igralec(igralec, meni_igralec)

    if izbira == "0":
        osnovni_meni()

    else:
        napaka(meni_igralec)

def natancnejsi_podatki_igralec(igralec, prihod):
    '''Uporabniku ponudi natančnejše inforamcije o igralcu z ID-jem id.'''

    izpis = meni("Želite pridobiti natančnejše informacije o igralcu?",
                 [
                 "Natančnejše informacije o igralcu"    
                 ])
    print(izpis)

    izbira = input("--> ")

    if izbira == "1":
        opozorilo_cakanje(meni_igralec)
        igralec.razsirjena_statistika(igralec)
        print(igralec)

        print("=" * 50)
        na_osnovni_meni()       
                
    
    if izbira == "2":
        prihod()

    if izbira == "0":
        osnovni_meni()

    else:
        napaka(natancnejsi_podatki_igralec(id, prihod))


def tekme_meni():
    '''Uporabnika vodi skozi možnosti za tekme.'''

    izpis = meni("Izberi način iskanja", [
            "Iskanje po ID", "Iskanje po datumu", "Iskanje po obdobju"
    ], False)

    print(izpis)
    izbira = input("--> ")

    if izbira == "1":
        tekma = tekma_id(tekme_meni)
        print(tekma)
        nadaljuj()
        natancnejsi_podatki_tekma(tekma)

    if izbira == "2":
        datum = tekma_datum(tekme_meni)
        tekma = model.Tekma.najdi_tekmo(datum)
        print(tekma)
        nadaljuj()
        natancnejsi_podatki_tekma(tekma)

    if izbira == "3":
        obdobje = casovno_obdobje(tekme_meni)
        seznam_tekem = model.Tekma.vse_tekme(obdobje[0], obdobje[1])
        for tekma in seznam_tekem:
            print(model.Tekma.eno_vrsticni_izpis(tekma))
        tekma = tekma_id(tekme_meni)
        print(tekma)
        nadaljuj()
        natancnejsi_podatki_tekma(tekma)

    if izbira == "0":
        osnovni_meni()

    else:
        napaka(tekme_meni)
    return None

def natancnejsi_podatki_tekma(tekma):
    '''Ponudi natančnejse podatke o tekmi in podatke o posameznih igralcih.'''
    izpis = meni("Želite natančnejše podatke o tekmi ali igralcih tekme?", 
                 [
                "Natančnejši podatki tekme",
                "Podatki o igralcu"])
    print(izpis)

    izbira = input("--> ")
    if izbira == "1":
        print(model.Tekma.izpisi_tekmo_dodatno(tekma))
        nadaljuj()
        na_osnovni_meni()

    if izbira == "2":
        id_igralca(tekme_meni)

    if izbira == "0":
        osnovni_meni()

    else:
        napaka(natancnejsi_podatki_tekma(tekma))
    return None


def sezona_meni():
    '''Uporabnika vodi skozi podatke o sezonah.'''
    sezone = model.Sezona.vse_sezone()
    izbire = [str(sezona) for sezona in sezone.values()]
    izpis = meni("Izberite sezono, ki vas zanima.", izbire, False)
    print(izpis)
    izbira = input("--> ")
    
    if izbira == "0":
        osnovni_meni()

    try:
        x = int(izbira)
    except:
        napaka(sezona_meni)    

    if int(izbira) in sezone:
        izberi_sezono(sezona_meni, sezone[int(izbira)])

    else:
        napaka(sezona_meni)        

def izberi_sezono(prihod, sezona):
    '''Uporabniku ponudi možnosti po izbrani sezoni.'''
    izpis = meni("Kaj več vas zanima o izbrani sezoni?", ["Splošni podatki", "Lestvice"])
    print(izpis)
    izbira = input("--> ")

    if izbira == "0":
        osnovni_meni()
    
    if izbira == "3":
        prihod()
    
    if izbira == "1":
        sezona.pridobi_podatke(sezona)
        print(sezona)
        nadaljuj()
        osnovni_meni()
    
    if izbira == "2":
        izbira_kateogirje(izberi_sezono, sezona.konec, sezona.zacetek)

    else:
        napaka(izberi_sezono(prihod, sezona))


def lestvice_meni():
    '''Uporabnika vodi skozi iskanje lestvic.'''
    izpis = meni("Izberite kakšne lestvice vas zanimajo.", ["Splošne lestvice", "Za izbrano obdobje"], False)
    print(izpis)
    izbira = input("--> ")

    if izbira == "0":
        osnovni_meni()

    if izbira == "1":
        izbira_kateogirje(lestvice_meni)

    if izbira == "2":
        obdobje = casovno_obdobje(lestvice_meni)
        izbira_kateogirje(lestvice_meni, obdobje[1], obdobje[0])

    

def izbira_kateogirje(prihod, datum=DANES, zacetek = PRVIC):
    '''Uporabniku ponudi možne kategorije lestvic.'''
    izbire = ["Prisotnost", "Zmage", "Porazi", "Neodločenosti", "Goli", "Asistence", "Avtogoli", "MMR", "Winrate", "Lossrate", "Tierate", "Goalrate", "Assistencerate", "AGrate", "SR"]
    izpis = meni("Izberite kategorijo", izbire)
    print(izpis)
    izbira = input("--> ")

    if izbira == "0":
        osnovni_meni()

    
    try:
        x = int(izbira)
    except:
        napaka(izbira_kateogirje)
    
    if x <= len(izbire):
        stevilo = izbira_dolzine()
        if x == 1:
            lestvica = model.Lestvica.pridobi_lestvico_prisotnost(datum, stevilo, zacetek)
            
        if x in [5,6,7]:
            lestvica = model.Lestvica.pridobi_lestvico_g_a_ag(izbire[x-1], datum, stevilo, zacetek)

        if x == len(izbire):
            lestvica = model.Lestvica.pridobi_lestvico_SR(datum, stevilo, zacetek)

        else:
            lestvica = model.Lestvica.pridobi_lestvico_razno(izbire[x-1], datum, stevilo, zacetek)

        print(lestvica)
        nadaljuj()
        osnovni_meni()
        
    if x == len(izbire) + 1:
        prihod()

    else:
        napaka(izbira_kateogirje)

def izbira_dolzine():
    '''Uporabniku ponudi dolzino lestvice.'''
    izpis = "S številko zapišite koliko igralec želite izpisanih. Če želite izpisati vse, pustite prazno (enter)."
    print(izpis)
    stevilo = input("--> ")
    try: 
        x = int(stevilo)
    except:
        x = 0

    return x


osnovni_meni()
