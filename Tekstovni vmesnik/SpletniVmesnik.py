import bottle
from model import conn, Igralec, Tekma, Sezona, Lestvica, PRVIC, DANES


# Osnovni meni =======================================================================================================================
@bottle.route('/')
def osnovni_meni():
    '''Vrne začetni meni aplikacije.'''
    return bottle.template("osnovni_meni")


# Meni igralec =======================================================================================================================
@bottle.route('/igralec/meni')
def meni_igralec():
    '''Vrne začetni meni za igralce.'''
    return bottle.template("meni_igralec", prikazi="meni")


@bottle.route('/igralec/id')
def igralec_id():
    '''Vrne obrazec za iskanje igralca po ID.'''
    return bottle.template("meni_igralec", prikazi="id")

@bottle.route('/igralec/id/<id:int>')
def igralec_po_id(id):
    '''Preusmeri na izbiro obdobja za podatke o igralcu.'''
    return bottle.redirect(f'/igralec/{id}/obdobje')


@bottle.route('/igralec/ime')
def igralec_ime():
    '''Vrne obrazec za iskanje igralca po imenu.'''
    return bottle.template("meni_igralec", prikazi="ime")

@bottle.post('/igralec/iskanje')
def iskanje_po_imenu():
    '''Vrne rezultate iskanja igralca po imenu.'''
    niz = bottle.request.forms.get('ime')
    igralci = Igralec.najdi_igralca(niz)

    if not igralci:
        return bottle.template("napaka", sporocilo="Ni zadetkov za vnešeno ime."), 404

    if len(igralci) == 1:
        return bottle.redirect(f"/igralec/id/{igralci[0].id}/sezona")

    return bottle.template("meni_igralec", prikazi="rezultati_iskanja", igralci=igralci)


@bottle.route("/igralec/<id:int>/obdobje")
def izberi_obdobje(id):
    '''Vrne obrazec za izbiro obdobja za statistiko igralca.'''
    sezone_obj = Sezona.vse_sezone()
    sezone = [(id, sez.zacetek, sez.konec) for id, sez in sezone_obj.items()]
    return bottle.template("meni_igralec", prikazi='obdobje', id=id, sezone=sezone)

@bottle.route("/igralec/<id:int>/statistika", method="POST")
def prikazi_statistiko(id):
    '''Vrne statistiko igralca glede na izbrano obdobje.'''
    izbira = bottle.request.forms.get("izbira")

    if izbira == "7":
        stat = Igralec.pridobi_statistiko(id)
    elif izbira == "8":
        zacetek = bottle.request.forms.get("zacetek")
        konec = bottle.request.forms.get("konec")
        stat = Igralec.pridobi_statistiko(id, zacetek, konec)
    else:
        sezona = int(izbira)
        zacetek = Sezona.sezona_zacetek(sezona)
        konec = Sezona.sezona_konec(sezona)
        stat = Igralec.pridobi_statistiko(id, zacetek, konec)

    igralec = Igralec.najdi_igralca(id)
    return bottle.template("meni_igralec", prikazi="statistika", stat=stat)

@bottle.route('/igralec/<id:int>/natančno')
def prikazi_natancno(id):
    '''Vrne natančnejše podatke o igralcu.'''
    igralec = Igralec.najdi_igralca(id)
    if not igralec:
        return bottle.template("napaka", sporocilo="Igralec ne obstaja."), 404

    sezonski_SR = Igralec.natančna_statistika(id)
    return bottle.template("meni_igralec", prikazi="natančno", igralec=igralec, sezonski_SR=sezonski_SR)



# Meni tekme =========================================================================================================================
@bottle.route('/tekme')
def meni_tekme():
    '''Vrne začetni meni za tekme.'''
    return bottle.template("meni_tekme", prikazi="meni")


@bottle.route('/tekma/id')
def tekma_id():
    '''Vrne obrazec za iskanje tekme po ID.'''
    return bottle.template("meni_tekme", prikazi="id", tekma=None)

def najdi_tekmo_po_id(id):
    '''Vrne podatke o tekmi z danim ID-jem.'''
    poizvedba = """
        SELECT id, goli_a, goli_b, datum FROM tekma WHERE id = ?
    """
    rezultat = conn.execute(poizvedba, (id,)).fetchone()

    if not rezultat:
        return None

    id_tekme, goli_a, goli_b, datum = rezultat

    poizvedba = """
        SELECT igralec.id, igralec.ime, igralec.priimek, prisotnost.ekipa
        FROM prisotnost
        JOIN igralec ON prisotnost.igralec_id = igralec.id
        WHERE prisotnost.tekma_id = ?
    """
    rezultat = conn.execute(poizvedba, (id_tekme,)).fetchall()

    ekipa_a = []
    ekipa_b = []

    for id_igralca, ime, priimek, ekipa in rezultat:
        opis = f"ID:{id_igralca} > {ime} {priimek}"
        if ekipa == 0:
            ekipa_a.append(opis)
        else:
            ekipa_b.append(opis)

    return {
        "id": id_tekme,
        "goli_a": goli_a,
        "goli_b": goli_b,
        "datum": datum,
        "ekipa_a": ekipa_a,
        "ekipa_b": ekipa_b,
    }

@bottle.route('/tekma/id/<id:int>')
def tekma_po_id(id):
    '''Vrne stran s podatki o tekmi z danim ID-jem.'''
    tekma = najdi_tekmo_po_id(id)
    if tekma:
        return bottle.template("meni_tekme", prikazi="id", tekma=tekma)
    else:
        return bottle.template("napaka", sporocilo="Tekma s tem ID-jem ne obstaja."), 404

@bottle.route('/tekma/<id:int>/natančno')
def natancno_tekma(id):
    '''Vrne natančnejše podatke o tekmi z danim ID-jem.'''
    tekma = Tekma.najdi_tekmo_id(id)
    if tekma.id == 0:
        return bottle.template("napaka", sporocilo="Tekma s tem ID-jem ne obstaja.")
    podatki = Tekma.izpisi_tekmo_dodatno(tekma)
    return bottle.template("meni_tekme", prikazi="natančno", izpis=podatki)

@bottle.route('/tekma/<id:int>/moznosti')
def izberi_moznost_za_tekmo(id):
    '''Vrne meni z dodatnimi možnostmi za prikaz podatkov tekme.'''
    tekma = najdi_tekmo_po_id(id)
    if tekma is None:
        return bottle.template("napaka", sporocilo="Tekma s tem ID-jem ne obstaja.")
    return bottle.template("meni_tekme", prikazi="moznosti", tekma=tekma)


@bottle.route('/tekma/datum')
def tekma_datum():
    '''Vrne seznam tekem, odigranih na določen datum.'''
    datum = bottle.request.query.get("datum")
    if datum:
        poizvedba = "SELECT id FROM tekma WHERE datum = ?"
        rezultat = conn.execute(poizvedba, (datum,)).fetchall()

        if rezultat:
            if len(rezultat) == 1:
                return bottle.redirect(f"/tekma/id/{rezultat[0][0]}")
            else:
                tekme = []
                for row in rezultat:
                    podrobnosti = najdi_tekmo_po_id(row[0])
                    if podrobnosti:
                        tekme.append(podrobnosti)
                return bottle.template("meni_tekme", prikazi="datum", tekme=tekme, datum=datum)
        else:
            return bottle.template("meni_tekme", prikazi="datum", tekme=[], datum=datum)
    return bottle.template("meni_tekme", prikazi="datum", tekme=None, datum=None)


@bottle.route('/tekma/obdobje')
def tekma_obdobje():
    '''Vrne obrazec za izbiro obdobja tekem.'''
    sezone_obj = Sezona.vse_sezone()
    sezone = {}

    for id, sez in sezone_obj.items():
        sezone[id] = {"zacetek": sez.zacetek, "konec": sez.konec}

    sezone[7] = {"zacetek": "vse", "konec": "statistike"}
    sezone[8] = {"zacetek": "po", "konec": "meri"}
    return bottle.template("meni_tekme", prikazi="obdobje", sezone=sezone, tekme=None, zacetek=None, konec=None)

def najdi_tekme_po_obdobju(zacetek, konec):
    '''Vrne vse tekme znotraj danega obdobja.'''
    poizvedba = "SELECT id, goli_a, goli_b, datum FROM tekma WHERE datum BETWEEN ? AND ?"
    rezultat = conn.execute(poizvedba, (zacetek, konec)).fetchall()
    if rezultat:
        return [{"id": row[0], "goli_a": row[1], "goli_b": row[2], "datum": row[3]} for row in rezultat]
    return None

@bottle.route('/tekma/obdobje/<zacetek>/<konec>')
def tekma_po_obdobju(zacetek, konec):
    '''Vrne tekme, ki so bile odigrane v izbranem obdobju.'''
    tekme = najdi_tekme_po_obdobju(zacetek, konec)
    sezone_obj = Sezona.vse_sezone()
    sezone = {id: {"zacetek": sez.zacetek, "konec": sez.konec} for id, sez in sezone_obj.items()}
    sezone[7] = {"zacetek": "vse", "konec": "statistike"}
    sezone[8] = {"zacetek": "po", "konec": "meri"}

    if tekme:
        return bottle.template("meni_tekme", prikazi="obdobje", tekme=tekme, sezone=sezone, zacetek=zacetek, konec=konec)
    else:
        return bottle.template("napaka", sporocilo="V tem obdobju ni bilo nobene tekme."), 404

@bottle.post("/tekma/obdobje/izberi")
def obdelaj_obdobje_izbiro():
    '''Vrne tekme glede na izbrano obdobje.'''
    izbira = bottle.request.forms.get("izbira")

    sezone_obj = Sezona.vse_sezone()
    sezone = {id: {"zacetek": sez.zacetek, "konec": sez.konec} for id, sez in sezone_obj.items()}
    sezone[7] = {"zacetek": "vse", "konec": "statistike"}
    sezone[8] = {"zacetek": "po", "konec": "meri"}

    if izbira == "7":
        tekme = najdi_tekme_po_obdobju("0000-01-01", "9999-12-31")
        return bottle.template("meni_tekme", prikazi="obdobje", tekme=tekme, sezone=sezone, zacetek="0000-01-01", konec="9999-12-31")
    elif izbira == "8":
        zacetek = bottle.request.forms.get("zacetek")
        konec = bottle.request.forms.get("konec")
        tekme = najdi_tekme_po_obdobju(zacetek, konec)
        return bottle.template("meni_tekme", prikazi="obdobje", tekme=tekme, sezone=sezone, zacetek=zacetek, konec=konec)
    else:
        sezona = int(izbira)
        zacetek = Sezona.sezona_zacetek(sezona)
        konec = Sezona.sezona_konec(sezona)
        tekme = najdi_tekme_po_obdobju(zacetek, konec)
        return bottle.template("meni_tekme", prikazi="obdobje", tekme=tekme, sezone=sezone, zacetek=zacetek, konec=konec)


# Meni sezone ========================================================================================================================
@bottle.route('/sezone')
def sezone():
    '''Vrne začetni meni sezon.'''
    sezone = Sezona.vse_sezone()
    sezonski_podatki = []

    for id, sezona in sezone.items():
        sezonski_podatki.append({
            "id": id,
            "zacetek": Sezona.sezona_zacetek(id),
            "konec": Sezona.sezona_konec(id)
        })

    return bottle.template("meni_sezone", prikazi="izberi", sezone=sezonski_podatki)

@bottle.route("/sezona/<id:int>")
def meni_za_sezono(id):
    '''Vrne meni za izbrano sezono.'''
    zacetek = Sezona.sezona_zacetek(id)
    konec = Sezona.sezona_konec(id)
    return bottle.template("meni_sezone", prikazi="podrobnosti", sezona_id=id, zacetek=zacetek, konec=konec)

@bottle.route('/sezona/<id:int>/splosni')
def splosni_podatki_o_sezoni(id):
    '''Vrne splošne podatke o tekmah v izbrani sezoni.'''
    sezona = Sezona.vse_sezone()[id]
    sezona.pridobi_podatke(sezona)

    podatki = {
        "tekem": sezona.tekme,
        "golov": sezona.goli,
        "asistenc": sezona.asistence,
        "avtogolov": sezona.avto_goli,
        "tekme": []
    }

    poizvedba = """SELECT id, datum, goli_a, goli_b 
                   FROM tekma 
                   WHERE datum >= ? AND datum <= ? 
                   ORDER BY datum"""
    rezultat = conn.execute(poizvedba, [sezona.zacetek, sezona.konec]).fetchall()

    for vrstica in rezultat:
        podatki["tekme"].append({
            "id": vrstica[0],
            "datum": vrstica[1],
            "goli_a": vrstica[2],
            "goli_b": vrstica[3]
        })

    return bottle.template("meni_sezone", prikazi="splošni", id=id, zacetek=sezona.zacetek, konec=sezona.konec, podatki=podatki)

@bottle.route("/sezona/<id:int>/lestvice")
def lestvice_za_sezono(id):
    '''Vrne seznam kateogrij lestvic.'''
    zacetek = Sezona.sezona_zacetek(id)
    konec = Sezona.sezona_konec(id)
    kategorije = [
        "Prisotnost", "Zmage", "Porazi", "Neodločenosti", "Goli",
        "Asistence", "Avtogoli", "MMR", "Winrate", "Lossrate",
        "Tierate", "Goalrate", "Assistencerate", "AGrate", "SR"
    ]
    return bottle.template("meni_sezone", prikazi="kategorije_lestvic", sezona_id=id, zacetek=zacetek, konec=konec, kategorije=kategorije)

@bottle.route('/sezona/<id:int>/lestvice/<kategorija>')
def lestvica_za_sezono_in_kategorijo(id, kategorija):
    '''Vrne eno lestvico za izbrano kategorijo v izbrani sezoni.'''
    zacetek = Sezona.sezona_zacetek(id)
    konec = Sezona.sezona_konec(id)
    stevilo = 0

    if kategorija == "Prisotnost":
        lestvica = Lestvica.pridobi_lestvico_prisotnost(konec, stevilo, zacetek)
    elif kategorija in ["Goli", "Asistence", "Avtogoli"]:
        lestvica = Lestvica.pridobi_lestvico_g_a_ag(kategorija, konec, stevilo, zacetek)
    elif kategorija == "SR":
        lestvica = Lestvica.pridobi_lestvico_SR(konec, stevilo, zacetek)
    else:
        prava = Lestvica.prevedi_kategorijo(kategorija)
        lestvica = Lestvica.pridobi_lestvico_razno(prava, konec, stevilo, zacetek)

    return bottle.template("meni_sezone", prikazi="ena_lestvica", kategorija=kategorija, lestvica=lestvica.vsebina, atribut=Lestvica.prevedi_kategorijo(kategorija), id=id, zacetek=zacetek, konec=konec)


# Meni lestvice ======================================================================================================================
@bottle.route('/lestvice')
def lestvice_meni():
    '''Vrne začetni meni lestvic.'''
    return bottle.template("meni_lestvice", prikazi="meni")

@bottle.route('/lestvice/splosne')
def splosne_lestvice():
    '''Vrne seznam kategorij za lestvice.'''
    kategorije = [
        "Prisotnost", "Zmage", "Porazi", "Neodločenosti", "Goli",
        "Asistence", "Avtogoli", "MMR", "Winrate", "Lossrate",
        "Tierate", "Goalrate", "Assistencerate", "AGrate", "SR"
    ]
    return bottle.template("meni_lestvice", prikazi="seznam_kategorij", kategorije=kategorije)

@bottle.route('/lestvice/splosne/<kategorija>')
def prikazi_splosno_lestvico(kategorija):
    '''Vrne splošno lestvico za izbrano kategorijo.'''
    zacetek = PRVIC
    konec = DANES
    stevilo = 0

    if kategorija == "Prisotnost":
        lestvica = Lestvica.pridobi_lestvico_prisotnost(konec, stevilo, zacetek)
    elif kategorija in ["Goli", "Asistence", "Avtogoli"]:
        lestvica = Lestvica.pridobi_lestvico_g_a_ag(kategorija, konec, stevilo, zacetek)
    elif kategorija == "SR":
        lestvica = Lestvica.pridobi_lestvico_SR(konec, stevilo, zacetek)
    else:
        prava_kategorija = Lestvica.prevedi_kategorijo(kategorija)
        lestvica = Lestvica.pridobi_lestvico_razno(prava_kategorija, konec, stevilo, zacetek)

    return bottle.template("meni_lestvice", prikazi="ena_lestvica", kategorija=kategorija, lestvica=lestvica.vsebina, atribut=lestvica.kategorija)


@bottle.route('/lestvice/obdobje')
def lestvice_obdobje_obrazec():
    '''Vrne obrazec za izbiro obdobja.'''
    sezone_obj = Sezona.vse_sezone()
    sezone = {}
    for id, sez in sezone_obj.items():
        sezone[id] = {"zacetek": sez.zacetek, "konec": sez.konec}
    sezone[7] = {"zacetek": "vse", "konec": "statistike"}
    sezone[8] = {"zacetek": "po", "konec": "meri"}
    return bottle.template("meni_lestvice", prikazi="obdobje", sezone=sezone)

@bottle.route('/lestvice/obdobje/<zacetek>/<konec>')
def lestvice_obdobje(zacetek, konec):
    '''Vrne lestvice za obdobje v izbrani kategoriji.'''
    stevilo = 0  # 0 pomeni "vse"

    kategorije = [
        "Prisotnost", "Zmage", "Porazi", "Neodločenosti", "Goli",
        "Asistence", "Avtogoli", "MMR", "Winrate", "Lossrate",
        "Tierate", "Goalrate", "Assistencerate", "AGrate", "SR"
    ]

    lestvice = {}

    for kategorija in kategorije:
        if kategorija == "Prisotnost":
            lestvice[kategorija] = Lestvica.pridobi_lestvico_prisotnost(konec, stevilo, zacetek)
        elif kategorija in ["Goli", "Asistence", "Avtogoli"]:
            lestvice[kategorija] = Lestvica.pridobi_lestvico_g_a_ag(kategorija, konec, stevilo, zacetek)
        elif kategorija == "SR":
            lestvice[kategorija] = Lestvica.pridobi_lestvico_SR(konec, stevilo, zacetek)
        else:
            prava_kategorija = Lestvica.prevedi_kategorijo(kategorija)
            lestvice[kategorija] = Lestvica.pridobi_lestvico_razno(prava_kategorija, konec, stevilo, zacetek)

    return bottle.template("meni_lestvice", prikazi="rezultati", lestvice=lestvice, zacetek=zacetek, konec=konec)

@bottle.post("/lestvice/obdobje/izberi")
def obdelaj_obdobje_izbiro_lestvice():
    '''Preusmeri na seznam kategorij za izbrano obdobje.'''
    izbira = bottle.request.forms.get("izbira")
    if izbira == "7":
        return bottle.redirect("/lestvice/obdobje/0000-01-01/9999-12-31/seznam")
    elif izbira == "8":
        zacetek = bottle.request.forms.get("zacetek")
        konec = bottle.request.forms.get("konec")
        return bottle.redirect(f"/lestvice/obdobje/{zacetek}/{konec}/seznam")
    else:
        sezona = int(izbira)
        zacetek = Sezona.sezona_zacetek(sezona)
        konec = Sezona.sezona_konec(sezona)
        return bottle.redirect(f"/lestvice/obdobje/{zacetek}/{konec}/seznam")

@bottle.route("/lestvice/obdobje/<zacetek>/<konec>/seznam")
def izberi_kategorijo_lestvice(zacetek, konec):
    '''Vrne seznam kategorij za prikaz lestvice po obdobju.'''
    kategorije = [
        "Prisotnost", "Zmage", "Porazi", "Neodločenosti", "Goli",
        "Asistence", "Avtogoli", "MMR", "Winrate", "Lossrate",
        "Tierate", "Goalrate", "Assistencerate", "AGrate", "SR"
    ]
    return bottle.template("meni_lestvice", prikazi="seznam_kategorij_obdobje", zacetek=zacetek, konec=konec, kategorije=kategorije)

@bottle.route('/lestvice/obdobje/<zacetek>/<konec>/<kategorija>')
def prikazi_lestvico_po_obdobju_in_kategoriji(zacetek, konec, kategorija):
    '''Vrne lestvico za izbrano kategorijo in obdobje.'''
    stevilo = 0

    if kategorija == "Prisotnost":
        lestvica = Lestvica.pridobi_lestvico_prisotnost(konec, stevilo, zacetek)
    elif kategorija in ["Goli", "Asistence", "Avtogoli"]:
        lestvica = Lestvica.pridobi_lestvico_g_a_ag(kategorija, konec, stevilo, zacetek)
    elif kategorija == "SR":
        lestvica = Lestvica.pridobi_lestvico_SR(konec, stevilo, zacetek)
    else:
        prava = Lestvica.prevedi_kategorijo(kategorija)
        lestvica = Lestvica.pridobi_lestvico_razno(prava, konec, stevilo, zacetek)

    return bottle.template("meni_lestvice", prikazi="ena_lestvica", kategorija=kategorija, lestvica=lestvica.vsebina, atribut=lestvica.kategorija)


# Zagon strežnika ====================================================================================================================
if __name__ == "__main__":
    bottle.run(host='localhost', port=8080, debug=True, reloader=True)
