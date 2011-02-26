#!/usr/bin/python

import sqlite3
import os.path

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
           print "radim update artikla", artikal['kod']
           self.cursor.execute("update artikli set barkod=:barkod, jmj=:jmj, cijena=:cijena, naziv=:naziv where kod=:kod", artikal)
            
     def add_artikal(self, artikal):
        # http://www.doughellmann.com/articles/how-tos/python-exception-handling/
        # http://docs.python.org/library/sqlite3.html#module-functions-and-constants

        try:
           self.cursor.execute("insert into artikli(kod, barkod, jmj, cijena, naziv) values(:kod, :barkod, :jmj, :cijena, :naziv)", artikal)
        except sqlite3.Error, e:
            print "desila se greska", e.args[0]
      
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
    p.add_update_artikal ({ 'kod': "USB1", 'barkod': '387332930212', 'naziv': "USB flash 4GB", 'jmj': "kom", 'cijena': 15.5})

    p.add_update_artikal ({ 'kod': "USB2", 'barkod': '387332930225', 'naziv': "USB flash 8GB", 'jmj': "kom", 'cijena': 19.95})

    p.add_update_artikal ({ 'kod': "USB4", 'barkod': '387332930201', 'naziv': "USB flash 16GB", 'jmj': "kom", 'cijena': 35})

    p.add_update_artikal ({ 'kod': "USB5", 'barkod': '991332930201', 'naziv': "USB flash 32GB", 'jmj': "kom", 'cijena': 49.25})
    # promjena cijene i barkoda
    p.add_update_artikal ({ 'kod': "USB5", 'barkod': '991330030299', 'naziv': "USB flash 32GB", 'jmj': "kom", 'cijena': 44.55})

    print_pos = PosPrint(p)
    print_pos.parametri()

    print("-"*80)
    print_pos.artikli()

    #result = p.cursor.execute("select * from parametri")
    #print (result.fetchall())
    #p2 = Pos("ubp_pos_2.db")
    #print p2.cursor


