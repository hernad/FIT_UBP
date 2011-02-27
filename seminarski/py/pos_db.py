#!/usr/bin/python

import sqlite3
import os.path
from datetime import date


VER="0.5.0"
DATE="26.02.2011"
APP="UBP POS app"
AUTHOR="hernad@bring.out.ba"
 
def header():
   print "=" * 80
   print AUTHOR, ",", APP, ",", VER, DATE
   print "=" * 80

class Pos:
     connection = None
     cursor = None

     # -----------------
     def __init__(self, db_name):
        print "... init begin ..."
        self.connect_db(db_name)
        if self.connection:
            self.cursor = self.connection.cursor()
        print "... init end ..."
        
     # --------------------
     def connect_db(self, db_name):

        if os.path.exists(db_name):
           print "imamo fajl", db_name
        else:
           print "nema baze !"
           return
        try:
           print "trying connect ...", db_name
  	   self.connection = sqlite3.connect(db_name)
           print "connected !"
        except:
	   print "nema baze ", db_name

     def add_operater(self, naziv):
        result = self.cursor.execute("select id from operateri where naziv = :naziv", {"naziv": naziv})
        if result.fetchone():
          print "vec postoji operater", naziv
        else:
         self.cursor.execute("insert into operateri(naziv) values(:naziv)", {'naziv': naziv})

     def parametar(self, svrha, opis):

         if not self.decode_svrhu_parametra(svrha):
             raise SystemExit("parametri nedozvoljena svrha !")

         # ako je postojao parametar izbrisi ga
         self.cursor.execute("delete from parametri where svrha = ?", svrha)
         # ubaci novi
         self.cursor.execute("insert into parametri(svrha, opis) values(?, ?)", (svrha, opis))


     def decode_svrhu_parametra(self, svrha):
         #svrha = svrha.encode('ascii','ignore')
         #print "svrha=", svrha

        if svrha == "F":
           return "Naziv Firme"
        elif svrha == "P":
           return "PDV broj"
        elif svrha == "N":
           return "Naziv prodavnice"
        elif svrha == "A":
           return "Adresa prodavnice"
        elif svrha == "T":
            return "Telefon"
        elif svrha == "U":
            return "Fax"
        else:
           return None


     def add_update_artikal(self, artikal):
        result = self.cursor.execute("select id from artikli where kod=:kod", artikal)
        # http://docs.python.org/library/sqlite3.html#sqlite3.Cursor
        if result.fetchone():
            print "vec postoji artikal sa kodom, radim update:", artikal['kod']
            self.update_artikal(artikal)
        else:
            print "nema artikla sa ovim kodom:", artikal['kod'], " ubacujem ga"
            self.add_artikal(artikal)

     def update_artikal(self, artikal):
        result = self.cursor.execute("select kod from artikli where kod=:kod", artikal)
        if result.fetchone():
           try:
             print "radim update artikla", artikal['kod']
             self.cursor.execute("update artikli set barkod=:barkod, jmj=:jmj, cijena=:cijena, naziv=:naziv where kod=:kod", artikal)
           except sqlite3.Error, e:
             print "Desila se greska >>>>>>>>>>", e.args[0]
            
     def add_artikal(self, artikal):
        # http://www.doughellmann.com/articles/how-tos/python-exception-handling/
        # http://docs.python.org/library/sqlite3.html#module-functions-and-constants
        try:
           self.cursor.execute("insert into artikli(kod, barkod, jmj, cijena, naziv) values(:kod, :barkod, :jmj, :cijena, :naziv)", artikal)
        except sqlite3.Error, e:
            print "Desila se greska >>>>>>>>>>", e.args[0]
     

     def add_racun(self, racun, rn_stavke):
         r_operater = self.cursor.execute("select id from operateri where naziv = :operater", racun)
          
         racun['operater_id'] = r_operater.fetchone()[0]
         print racun['operater_id']
         self.cursor.execute("insert into racuni(tip, broj, datum, operater_id, ukupno_s_pdv) values(:tip, :broj, :datum, :operater_id, 0)", racun)
         r_racun = self.cursor.execute("select id from racuni where broj = :broj and datum = :datum", racun)
         racun['id'] = r_racun.fetchone()[0]
         print "racun", r_racun, r_racun.fetchone()
         for rn_stavka in rn_stavke:
           row_artikal = self.cursor.execute("select id, cijena from artikli where kod=:artikal_kod", rn_stavka).fetchone()
           rn_stavka['racun_id'] = racun['id']
           rn_stavka['artikal_id'] = row_artikal[0]
           rn_stavka['cijena'] = row_artikal[1]    
           self.cursor.execute("insert into rn_stavke(racun_id, artikal_id, kolicina, cijena) values(:racun_id, :artikal_id, :kolicina, :cijena)", rn_stavka)
 
     def __del__(self):
         self.connection.commit()
         print "bye bye pos object ..."

class PosPrint:

    pos = None

    def __init__(self, pos):
        print type(pos)
        self.pos = pos 

    def parametri(self):
        result = self.pos.cursor.execute("select svrha, opis from parametri")
        # izlistaj parametre 
        for row in result:
           print row[0] , self.pos.decode_svrhu_parametra(row[0]), row[1]
        
    def operateri(self):
        result = self.pos.cursor.execute("select id, naziv from operateri")
        # izlistaj operatere
        for row in result:
           print row[0], row[1]

    def artikli(self):
        result = self.pos.cursor.execute("select kod, naziv, jmj, barkod, cijena from artikli")
        # izlistaj parametre 
        for row in result:
           #try:
           #http://docs.python.org/library/string.html
           print '{kod:<10} - {naziv:<40} ({jmj:<3}) : barkod: {barkod:<13}, cijena = {cijena:8.2f} '.format(kod=row[0], naziv=row[1], jmj=row[2], barkod=row[3], cijena=row[4])
           #except:
           #   print "ne mogu odstampati", row[0], "-", row[1] 




if __name__ == '__main__':

    header()

    p = Pos("ubp_pos.db")
    print p.cursor

    try:
       p.parametar("L", "lupetala lupetaljka parametar")
    except:
       print "error: L svrha ne prolazi !"
 
    p.parametar("F", "bring.out doo Sarajevo")
    p.parametar("P", "0123456789012")
    p.parametar("N", "Prodavnica 1")
    p.parametar("A", "Juraja Najtharta 6")
    p.parametar("T", "033/269-291")
    p.parametar("U", "033/269-292")

    p.add_update_artikal ({ 'kod': "POS", 'barkod': None, 'naziv': "bring.out POS software", 'jmj': "kom", 'cijena': 440})
    p.add_update_artikal ({ 'kod': "SP9", 'barkod': None, 'naziv': "bring.out instalacija POS", 'jmj': "kom", 'cijena': 100})
    p.add_update_artikal ({ 'kod': "USB1", 'barkod': '387332930212', 'naziv': "USB flash 4GB", 'jmj': "kom", 'cijena': 15.44})

    p.add_update_artikal ({ 'kod': "USB2", 'barkod': '387332930225', 'naziv': "USB flash 8GB", 'jmj': "kom", 'cijena': 19.95})

    p.add_update_artikal ({ 'kod': "USB4", 'barkod': '387332930201', 'naziv': "USB flash 16GB", 'jmj': "kom", 'cijena': 35.33})


    p.add_update_artikal ({ 'kod': "USB5", 'barkod': '991332930201', 'naziv': "USB flash 32GB", 'jmj': "kom", 'cijena': 49.25})
    # promjena cijene i barkoda
    p.add_update_artikal ({ 'kod': "USB5", 'barkod': '991330030299', 'naziv': "USB flash 32GB", 'jmj': "kom", 'cijena': 44.55})
    # raise 5pf err
    p.add_update_artikal ({ 'kod': "USB5", 'barkod': '991330030299', 'naziv': "USB flash 32GB", 'jmj': "kom", 'cijena': 44.33})
    # najnovija cijena
    p.add_update_artikal ({ 'kod': "USB5", 'barkod': '991330030299', 'naziv': "USB flash 32GB", 'jmj': "kom", 'cijena': 49.95})

    p.add_operater("hernad")
    p.add_operater("vsasa")
    p.add_operater("bjasko")


    print_pos = PosPrint(p)

    print("-" * 80)
    print_pos.parametri()

    print("-" * 80)
    print_pos.operateri()

    print("-" * 80)
    print_pos.artikli()

    for i in range(1, 11):
      racun = { 'tip':1, 'broj':i, 'datum': date.today(), 'operater': 'hernad' }
      rn_stavke = [ { 'artikal_kod': 'POS', 'kolicina': 1+i },
                    { 'artikal_kod': 'SP9', 'kolicina': 2+i }
                  ]
      p.add_racun(racun, rn_stavke)
  
      #print racun
      #print rn_stavke

    #result = p.cursor.execute("select * from parametri")
    #print (result.fetchall())
    #p2 = Pos("ubp_pos_2.db")
    #print p2.cursor


