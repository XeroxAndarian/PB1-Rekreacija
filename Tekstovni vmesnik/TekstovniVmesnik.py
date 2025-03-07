import model
import datetime


danes = datetime.datetime.today().strftime('%Y-%m-%d')

def napaka(f):
    '''Kadarkoli pritisnemo napačno izbiro želimo izpisati stalno sporočilo in vrniti meni f.'''
    print("Vpisali ste neveljavno izbiro. Prosim, da izberete eno izmed navedenih možnosti.")
    return f()

def meni_casovno_obdobje(prihod):
    '''Funkcija od od uporabnika pridobi informacije o začetku in koncu obdobja, ki ga zanima za igralca in vrne podatke o igralcu iz tega obdobja.'''
    print("=" * 50)
    print("Od kdaj do kdaj te zanima statistika?")
    print("0 - Celotna statistika")

    sezone = []
    i = 1
    while i <= len(model.Sezona.vse_sezone()):
        print(f"{i} - Sezona {i} [{model.Sezona.sezona_zacetek(i)} - {model.Sezona.sezona_konec(i)}]")
        sezone.append(i)
        i+=1

    print(f"{i} - Po Meri")
    j = i + 1
    print(f"{j} - Nazaj")
    print(f"{j + 1} - Nazaj na začetni zaslon")

    izbira = input("--> ")
    
    if izbira == "0":
        return ('2000-01-01', '2099-12-31')
    
    if izbira == f"{j}":
        prihod
        return None
    
    if izbira == f"{j+1}":
        osnovni_meni()
        return None
    
    if izbira == f"{i}":
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
            zacetek = "2000-01-01"
        
        if konec == "--":
            konec = "2099-12-31"

        return (zacetek, konec)
    
    if int(izbira) in sezone:
        zacetek = model.Sezona.sezona_zacetek(izbira)
        konec = model.Sezona.sezona_konec(izbira)
        return(zacetek, konec)
    
    else:
        napaka(meni_casovno_obdobje(meni_casovno_obdobje))



def osnovni_meni():
    """Meni, ki ga bomo zagledali ob zagonu vmesnika."""
    

    print("=" * 50,
            "Izberi možnost:",
              "1 - Podatki o igralcih",
              "2 - Podatki o sezonah",
              "3 - Podatki o tekmah ",
              "4 - Lestvice",
              "5 - Izhod",
              sep = "\n")
    
    izbira = input("--> ")

    if izbira == "1":
        igralec_meni()
        
    
    if izbira == "2":
        sezona_meni()
        pass

    if izbira == "3":
        tekme_meni()
        pass

    if izbira == "4":
        # lestvice_meni()
        pass

    if izbira == "5":
        print("Do prihodnjič!")
        return None
    
    else:
        napaka(osnovni_meni)

def izpis_igralca():
    '''Funkcija sprejme ID igralca in v primeru, da igralec obstaja, vrne podatke o igralcu v danem obdobju. Tekom izvajanja poklice funkcijo meni_casovno_obdobje.'''
    print("=" * 50)
    print("Vpiši ID igralca, za katerega te zanima statistika:")
    igralec_id = input("ID igralca: --> ")
    rezultat = model.Igralec.pridobi_statistiko(igralec_id)
    if rezultat.ime == '':
        print("Igralec s tem ID-jem ne obstaja. Preveri, če si se slučajno zatipkal. Sicer poskusi poiskati drugega igralca.")
        izpis_igralca()
    else: 
        obdobje = meni_casovno_obdobje(izpis_igralca)
        rezultat = model.Igralec.pridobi_statistiko(igralec_id, obdobje[0], obdobje[1])
        print(rezultat)
        input("Pritisnite tipko enter za vrnitev na osnovni meni: --> ")
        osnovni_meni()
    
    
def igralec_meni():
    '''Funkcija, ki nas vodi skozi meni, ki je namenjen za navigacijo po iskanuju igralcev.'''

    print("=" * 50,
        "Izberi način iskanja:",
        "1 - Iskanje po ID",
        "2 - Iskanje po imenu / priimku / vzdevku",
        "3 - Nazaj na začetni zaslon",
        sep = "\n")
    izbira = input("--> ")

    
    if izbira == "1":
        izpis_igralca()
    

    if izbira == "2":
        while True:
            print("=" * 50)
            print("Vpiši ime, priimek ali vzdevek igralca, ki te zanima:")
            igralec = input("Igralec: --> ") 
            moznosti = model.Igralec.najdi_igralca(igralec)
            if moznosti != []:
                break
            else:
                print("Igralec s tem imenom, vzdevkom ali priimkom ne obstaja. Preveri, če si se slučajno zatipkal. Sicer poskusi poiskati drugega igralca.")
        print("=" * 50)
        print("Rezultati iskanja: ")
        for igralec in moznosti:
            print(f"ID:{str(igralec.id)} > {igralec.ime} {igralec.priimek}")
        izpis_igralca()
    
    if izbira == "3":
        osnovni_meni()

    else:
        napaka(igralec_meni)

    
def sezona_meni():
    '''Funkcija nas vodi po meniju do informacij o posamezni sezoni.'''
    print("=" * 50,
        "Statistika sezon:",
        "1 - Trajanje sezon",
        "2 - Nazaj na začetni zaslon",
        sep = "\n")
    izbira = input("--> ")

    if izbira == "1":
        sezone = model.Sezona.vse_sezone()

        i = 0
        while i < len(sezone):
            i+=1
            print(f"{sezone[i]}")

        print("To je sezanm vseh sezone in njihovih trajanj.")
        input("Pritisnite tipko enter za vrnitev na osnovni meni: --> ")
        osnovni_meni()


def tekme_meni():
    '''Vodi nas po meniju za tekme.'''

    print("=" * 50,
        "Izberi način iskanja:",
        "1 - Iskanje po ID",
        "2 - Iskanje po datumu",
        "3 - Seznam tekem",
        "4 - Seznam tekem v časovnem obdobju",
        "5 - Seznam tekem po igralcu",
        "0 - Nazaj na začetni zaslon",
        sep = "\n")
    izbira = input("--> ")

    if izbira == "1":
        izpis_tekme_id()

    if izbira == "2":
        izpis_tekme_datum()

    if izbira == "3":
        tekme = model.Tekma.vse_tekme()
        i = 1
        for tekma in tekme:
            if i % 10 == 0:
                print("-" * 50)
            print(model.Tekma.eno_vrsticni_izpis(tekma))
            i+=1
        izpis_tekme_id()

    if izbira == "4":
        obdobje = meni_casovno_obdobje(tekme_meni)
        tekme = model.Tekma.vse_tekme(obdobje[0], obdobje[1])
        
        izpis_tekme_id()

    if izbira == "5":
        obdobje = meni_casovno_obdobje(tekme_meni)
        tekme = model.Tekma.tekme_igralca()
        

    if izbira == "0":
        osnovni_meni()

    else:
        napaka(tekme_meni)

def izpis_seznama_tekem(tekme):
    i = 1
    for tekma in tekme:
        if i % 10 == 0:
            print("-" * 50)
        print(model.Tekma.eno_vrsticni_izpis(tekma))
        i+=1
    return None
        
def izpis_tekme_id():
    '''Funkcija sprejme ID tekme in v primeru, da tekma obstaja, vrne podatke o tekmi.'''
    print("=" * 50)
    print("Vpiši ID tekme, za katero te zanima statistika:")
    tekma_id = input("ID tekme: --> ")
    rezultat = model.Tekma.najdi_tekmo_id(tekma_id)
    if rezultat.datum == '':
        print("Tekma s tem ID-jem ne obstaja. Preveri, če si se slučajno zatipkal. Sicer poskusi poiskati drugo tekmo.")
        izpis_tekme_id()
    else: 
        print(rezultat)
        input("Pritisnite tipko enter za vrnitev na osnovni meni: --> ")
        osnovni_meni()


def izpis_tekme_datum():
    '''Funkcija sprejme ID tekme in v primeru, da tekma obstaja, vrne podatke o tekmi.'''
    print("=" * 50)
    print(f"Navedi datum tekme, za katero te zanima statistika:")
    datum_dan = input("Od: (Dan) --> ")
    datum_mesec = input("Od: (Mesec) --> ")
    datum_leto = input("Od: (Leto) --> ")
    if len(datum_dan) == 1:
            datum_dan = "0" + datum_dan

    if len(datum_mesec) == 1:
            datum_mesec = "0" + datum_mesec

    datum = datum_leto + "-" + datum_mesec + "-" + datum_dan

    rezultat = model.Tekma.najdi_tekmo(datum)
    if rezultat.datum == '':
        print("Preveri, če si se slučajno zatipkal. Sicer poskusi poiskati drugo tekmo.")
        tekme_meni()
    else: 
        print(rezultat)
        input("Pritisnite tipko enter za vrnitev na osnovni meni: --> ")
        osnovni_meni()

# zaženi
print("Pozdravljeni v brskalniku statistike rekreacijskega nogometa! Sledite vmesniku, ki vas bo vodil do vaše željene statistike.")
osnovni_meni()
