# 07 – Pregled projekta

## Pregled implementiranih funkcionalnosti za MVP

V okviru prve delujoče različice (MVP) je bilo uspešno implementiranih vseh 6 predvidenih funkcionalnosti (**F1–F6**):

- **F1 – Prijava in dostop glede na vlogo:** Avtentikacija z e-pošto in geslom (JWT, bcrypt), preusmeritev na stran pripadajoče vloge (`administrator`, `organizator`, `ucitelj`, `dijak`), zavrnitev neaktivnih uporabnikov ter blokada dostopa do strani drugih vlog.
- **F2 – Vnos oddelkov, predmetov, učiteljev in urnika:** CRUD operacije za oddelke, predmete in učitelje ter dodajanje ur v tedenski urnik oddelka s preverjanjem prekrivanja (zasedenost učitelja ali oddelka).
- **F3 – Vnos odsotnosti in samodejni izračun izpadlih ur iz urnika:** Vnos odsotnosti učitelja v obdobju od–do z razlogom in navodili, preverjanje prekrivanja odsotnosti, upoštevanje prostih dni (`prost_dan`) ter samodejno generiranje nepokritih nadomeščanj.
- **F4 – Predlog razvrščenih kandidatov za izpadlo uro:** Izločanje odsotnih in zasedenih učiteljev, upoštevanje odsotnih oddelkov (`odsotnost_oddelka`), določitev vrste suplence (*strokovno* / *po navodilih*), izračun plačljivosti in števila suplenc v tekočem tednu ter razvrščanje kandidatov po pravilih šole (možnost tudi označitve »Ura odpade«).
- **F5 – Potrditev suplence:** Dodelitev nadomeščanja izbranemu učitelju s preverjanjem, da ob isti uri še nima potrjene druge suplence, ter zapisom vrste in plačljivosti (plačana ura izven rednega pouka učitelja oz. ura za fond).
- **F6 – Dnevni pregled sprememb za učitelja in oddelek:** Prikaz potrjenih suplenc in navodil za prijavljenega učitelja ter prikaz sprememb urnika (nadomeščanja in odpadle ure brez prikaza razloga odsotnosti) za dijakov oddelek za danes in jutri.

Funkcionalnosti izven MVP (**F7–F12**: potrditev izvedbe s snovjo, nerazpoložljivost vnaprej, odklonitev suplence, realizacija ur in izvozi CSV) v trenutni različici še niso implementirane.

---

## Ustreznost glede na uporabniške zgodbe (MVP)

V projektu je za MVP definiranih 7 uporabniških zgodb (**US-01 do US-07**), ki pokrivajo funkcionalnosti F1–F6. Spodaj je pregled izpolnjevanja pogojev sprejemljivosti:

| Uporabniška zgodba | Status | Opombe / izpolnjevanje pogojev sprejemljivosti |
|---|---|---|
| **US-01 – Prijava in dostop glede na vlogo** (F1) | ✔ Izpolnjena | Vsi pogoji sprejemljivosti so izpolnjeni: preusmeritev glede na vlogo, sporočilo »Napačna e-pošta ali geslo«, blokada deaktiviranih uporabnikov (`aktiven = False`) in prikaz »Nimate dostopa« ob obisku nedovoljene poti. |
| **US-02 – Vnos urnika** (F2) | ✔ Izpolnjena | Administrator lahko dodaja, ureja in briše oddelke, predmete in učitelje. Pri vnosu ure v urnik sistem preveri zasedenost učitelja in oddelka ter prikaže urnik kot tedensko tabelo (dnevi × šolske ure). |
| **US-03 – Vnos odsotnosti in izpadle ure** (F3) | ✔ Izpolnjena | Ob shranjevanju odsotnosti sistem preveri prekrivanje z obstoječimi odsotnostmi, preskoči proste dneve (`prost_dan`) in samodejno ustvari ter prikaže izpadle ure s statusom `nepokrita`. |
| **US-04 – Predlog kandidatov** (F4) | ✔ Izpolnjena | Sistem filtrira proste in prisotne učitelje ter jih pravilno razvrsti (isti predmet → odpadla ura oddelka → manj suplenc v tekočem tednu). Prikazani so vrsta, plačljivost in število suplenc, ob praznem seznamu pa sporočilo »Ni prostega učitelja« in gumb »Ura odpade«. *(Opomba: nerazpoložljivost učiteljev F8 še ni del MVP).* |
| **US-05 – Potrditev suplence** (F5) | ✔ Izpolnjena | Status ure se spremeni v `potrjena`, shrani se izračunana plačljivost (pred prvo ali po zadnji uri učitelja tisti dan = plačana, sicer fond), sistem prepreči dvojno dodelitev suplence v isti uri, sprememba pa je takoj vidna učitelju in dijaku. |
| **US-06 – Moje suplence** (F6) | ✔ Izpolnjena | Učitelj vidi le svoje potrjene suplence od danes naprej, urejene po datumu in uri, skupaj z navodili odsotnega učitelja oz. sporočilom »Ta teden nimate suplenc«. |
| **US-07 – Spremembe urnika oddelka** (F6) | ✔ Izpolnjena | Dijak vidi spremembe samo za svoj oddelek za danes in jutri (nadomeščajoči učitelj ali oznaka »Ura odpade«), brez razloga odsotnosti, oz. sporočilo »Danes/Jutri ni sprememb urnika«. |

### Zaključek
Implementirane funkcionalnosti **v celoti zadoščajo** vsem uporabniškim zgodbam, predvidenim za MVP (**US-01 do US-07**).
