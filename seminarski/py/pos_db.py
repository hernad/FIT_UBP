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

    print_pos = PosPrint(p)
    print_pos.parametri()

    #result = p.cursor.execute("select * from parametri")
    #print (result.fetchall())
    #p2 = Pos("ubp_pos_2.db")
    #print p2.cursor


