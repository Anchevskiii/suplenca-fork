# test_main.py – enotski in integracijski testi za backend (FastAPI + SQLite)

import os
from datetime import date

# pred uvozom main.py nastavimo testno SQLite bazo, da testi ne potrebujejo MySQL strežnika
os.environ["NASLOV_BAZE"] = "sqlite:///./test.db"

import bcrypt
from fastapi.testclient import TestClient
from baza import Osnova, povezava, Seja
from modeli import Uporabnik, ProstDan
from main import aplikacija

odjemalec = TestClient(aplikacija)


# pred vsakim zagonom pripravimo čisto bazo z osnovnimi testnimi uporabniki
def setup_module():
    Osnova.metadata.drop_all(povezava)
    Osnova.metadata.create_all(povezava)

    geslo_hash = bcrypt.hashpw("test123".encode(), bcrypt.gensalt()).decode()
    seja = Seja()
    seja.add_all([
        Uporabnik(id=1, ime="Ana", priimek="Admin", email="admin@sola.si",
                  geslo_hash=geslo_hash, vloga="administrator", aktiven=True),
        Uporabnik(id=2, ime="Olga", priimek="Organizator", email="organizator@sola.si",
                  geslo_hash=geslo_hash, vloga="organizator", aktiven=True),
        Uporabnik(id=3, ime="Janez", priimek="Novak", email="novak@sola.si",
                  geslo_hash=geslo_hash, vloga="ucitelj", aktiven=True),
        Uporabnik(id=4, ime="Dejan", priimek="Dijak", email="dijak@sola.si",
                  geslo_hash=geslo_hash, vloga="dijak", aktiven=True, oddelek_id=1),
        Uporabnik(id=5, ime="Bojan", priimek="Bivsi", email="bivsi@sola.si",
                  geslo_hash=geslo_hash, vloga="ucitelj", aktiven=False),
        ProstDan(datum=date(2026, 12, 25), opis="Božič"),
    ])
    seja.commit()
    seja.close()


def teardown_module():
    povezava.dispose()
    if os.path.exists("test.db"):
        os.remove("test.db")


# pomožna funkcija: prijavi uporabnika in vrne glavo z JWT žetonom
def glava_za(email):
    odgovor = odjemalec.post("/prijava", json={"email": email, "geslo": "test123"})
    zeton = odgovor.json()["zeton"]
    return {"Authorization": "Bearer " + zeton}


# 1. Test delovanja backenda in povezave z bazo
def test_preveri_bazo():
    odgovor = odjemalec.get("/")
    assert odgovor.status_code == 200
    assert odgovor.json()["stanje"] == "backend deluje, baza dosegljiva"


# 2. Test uspešne prijave (US-01)
def test_prijava_uspesna():
    odgovor = odjemalec.post("/prijava", json={"email": "admin@sola.si", "geslo": "test123"})
    assert odgovor.status_code == 200
    assert odgovor.json()["vloga"] == "administrator"
    assert "zeton" in odgovor.json()


# 3. Test prijave z napačnim geslom (US-01)
def test_prijava_napacno_geslo():
    odgovor = odjemalec.post("/prijava", json={"email": "admin@sola.si", "geslo": "narobe"})
    assert odgovor.status_code == 401
    assert odgovor.json()["detail"] == "Napačna e-pošta ali geslo"


# 4. Test prijave deaktiviranega uporabnika (US-01)
def test_prijava_deaktiviran_uporabnik():
    odgovor = odjemalec.post("/prijava", json={"email": "bivsi@sola.si", "geslo": "test123"})
    assert odgovor.status_code == 403
    assert odgovor.json()["detail"] == "Uporabnik je deaktiviran"


# 5. Test preverjanja dostopa glede na vlogo (US-01)
def test_preveri_dostop_vloge():
    glava = glava_za("admin@sola.si")
    dovoljeno = odjemalec.get("/dostop/administrator", headers=glava)
    zavrnjeno = odjemalec.get("/dostop/organizator", headers=glava)
    assert dovoljeno.status_code == 200
    assert zavrnjeno.status_code == 403


# 6. Test dodajanja in branja oddelkov (US-02)
def test_dodaj_in_preberi_oddelke():
    glava = glava_za("admin@sola.si")
    dodaj = odjemalec.post("/oddelki", json={"oznaka": "3. b"}, headers=glava)
    seznam = odjemalec.get("/oddelki", headers=glava)
    assert dodaj.status_code == 200
    assert len(seznam.json()) == 1
    assert seznam.json()[0]["oznaka"] == "3. b"


# 7. Test dodajanja in urejanja predmeta (US-02)
def test_dodaj_in_uredi_predmet():
    glava = glava_za("admin@sola.si")
    odjemalec.post("/predmeti", json={"kratica": "MAT", "naziv": "Matematika"}, headers=glava)
    uredi = odjemalec.put("/predmeti/1", json={"kratica": "PRO", "naziv": "Programiranje"}, headers=glava)
    seznam = odjemalec.get("/predmeti", headers=glava)
    assert uredi.status_code == 200
    assert seznam.json()[0]["naziv"] == "Programiranje"


# 8. Test dodajanja novega učitelja (US-02)
def test_dodaj_ucitelja():
    glava = glava_za("admin@sola.si")
    dodaj = odjemalec.post("/ucitelji", json={
        "ime": "Maja", "priimek": "Kovač", "email": "kovac@sola.si", "geslo": "test123"
    }, headers=glava)
    seznam = odjemalec.get("/ucitelji", headers=glava)
    assert dodaj.status_code == 200
    assert any(u["email"] == "kovac@sola.si" for u in seznam.json())


# 9. Test dodajanja ure v urnik in zavrnitve ob prekrivanju (US-02)
def test_dodaj_uro_in_prekrivanje():
    glava = glava_za("admin@sola.si")
    ura = {"oddelek_id": 1, "predmet_id": 1, "ucitelj_id": 3, "dan_v_tednu": 1, "solska_ura": 2, "ucilnica": "R12"}
    prvi_vnos = odjemalec.post("/urnik", json=ura, headers=glava)
    podvojen_vnos = odjemalec.post("/urnik", json=ura, headers=glava)
    urnik = odjemalec.get("/urnik/1", headers=glava)
    assert prvi_vnos.status_code == 200
    assert podvojen_vnos.status_code == 400
    assert len(urnik.json()) == 1


# 10. Test vnosa odsotnosti, izračuna izpadlih ur in prekrivanja odsotnosti (US-03)
def test_dodaj_odsotnost_in_izpadle_ure():
    glava = glava_za("organizator@sola.si")
    # 2026-11-30 je ponedeljek (dan_v_tednu = 1), ko ima učitelj 3 pouk
    podatki = {
        "ucitelj_id": 3,
        "datum_od": "2026-11-30",
        "datum_do": "2026-11-30",
        "razlog": "Bolniška",
        "navodila": "Rešite naloge na strani 42.",
    }
    odgovor = odjemalec.post("/odsotnosti", json=podatki, headers=glava)
    prekrivanje = odjemalec.post("/odsotnosti", json=podatki, headers=glava)
    assert odgovor.status_code == 200
    assert len(odgovor.json()["izpadle_ure"]) == 1
    assert odgovor.json()["izpadle_ure"][0]["status"] == "nepokrita"
    assert prekrivanje.status_code == 400


# 11. Test predloga kandidatov za izpadlo uro (US-04)
def test_predlog_kandidatov():
    glava = glava_za("organizator@sola.si")
    pregled = odjemalec.get("/dnevni-pregled/2026-11-30", headers=glava)
    nadomescanje_id = pregled.json()[0]["id"]
    kandidati = odjemalec.get(f"/kandidati/{nadomescanje_id}", headers=glava)
    assert pregled.status_code == 200
    assert kandidati.status_code == 200
    # Maja Kovač je edina aktivna in prosta učiteljica
    assert len(kandidati.json()) == 1
    assert "Kovač" in kandidati.json()[0]["ucitelj"]


# 12. Test potrditve suplence in sprememb urnika za dijaka (US-05, US-07)
def test_potrdi_suplenco_in_spremembe_dijaka():
    glava_org = glava_za("organizator@sola.si")
    kandidat = odjemalec.get("/kandidati/1", headers=glava_org).json()[0]
    potrditev = odjemalec.put("/nadomescanja/1/potrdi", json={
        "ucitelj_id": kandidat["id"],
        "vrsta": kandidat["vrsta"],
        "placana": kandidat["placana"],
    }, headers=glava_org)
    assert potrditev.status_code == 200

    # dijak preveri spremembe za ta datum
    glava_dijak = glava_za("dijak@sola.si")
    spremembe = odjemalec.get("/spremembe/2026-11-30", headers=glava_dijak)
    assert spremembe.status_code == 200
    assert len(spremembe.json()) == 1
    assert spremembe.json()[0]["nadomesca"] == "Kovač"
    assert spremembe.json()[0]["odpade"] is False
