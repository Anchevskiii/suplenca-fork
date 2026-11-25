# baza.py – povezava s podatkovno bazo MySQL prek SQLAlchemy

import os
import sys
from sqlalchemy import create_engine   # funkcija, ki pripravi povezavo z bazo
from sqlalchemy.orm import sessionmaker, declarative_base

# naslov baze: privzeto MySQL v docker-compose, pri testiranju pa lahko prek NASLOV_BAZE uporabimo SQLite
NASLOV_BAZE = os.getenv("NASLOV_BAZE", "mysql+pymysql://suplenca:test123@baza:3306/suplenca")

# objekt, prek katerega se bo backend pogovarjal z bazo
povezava = create_engine(NASLOV_BAZE)

# Seja: z njo beremo in pišemo podatke (ena seja = en pogovor z bazo)
Seja = sessionmaker(bind=povezava)

# Osnova: iz nje izpeljemo vse tabele (modele)
Osnova = declarative_base()