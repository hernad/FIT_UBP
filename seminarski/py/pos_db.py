#!/usr/bin/python

# author hernad@bring.out.ba
# licenca: GPLv2: http://www.gnu.org/licenses/gpl-2.0.html

import sqlite3
import os.path
from datetime import date


VER="0.9.1"
DATE="26.02.2011"
APP="UBP POS app"
AUTHOR="hernad@bring.out.ba"


PDV_STOPA=17
 
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
     
     def get_next_broj_racuna(self, datum):
        # nadji najveci za ovaj datum pa dodaj +1
        print "datum=", datum 
        ret = self.cursor.execute("select max(broj) from racuni where datum=:datum", {'datum': datum} ).fetchone()[0]
        if not ret: 
           print "na datum ", datum, "nema racuna, krecemo od 1"
           return 1
        else:
           print "max broj racuna je", ret, " za datum ", date 
           return ret+1

     # ------------------ find sekcija -------------------------------------------------------

     def find_parametar_by_svrha(self, svrha):
        c_op = self.cursor.execute("select opis from parametri where svrha=:svrha", { 'svrha': svrha })
        try:
          return c_op.fetchone()[0]
        except:
          print "nepostoji parametar sa svrhom:", svrha
          return None        
  
     def find_operater_by_naziv(self, naziv):
        c_op = self.cursor.execute("select id from operateri where naziv = :naziv", {'naziv': naziv} )
        try:
          return c_op.fetchone()[0]
        except:
          print "nepostoji operater imena:", naziv
          return None

     def find_artikal_by_kod(self, kod):
         row_artikal = self.cursor.execute("select id, cijena from artikli where kod=:kod", {'kod': kod}).fetchone()
         if row_artikal:
           return { 'id': row_artikal[0], 'cijena': row_artikal[1] }
         else: 
           return None 

     def find_racun_by_id(self, id):
         c_op = self.cursor.execute("select broj, datum, tip, ukupno_s_pdv from racuni where id=:id", {'id': id})
         try:
           tpl = c_op.fetchone()
           return { 'broj': tpl[0], 'datum': tpl[1], 'tip': tpl[2], 'ukupno_s_pdv': tpl[3] }
         except:
           print "nepostoji racun id-a:", id
           return None

     def find_racun_by_broj_datum(self, broj, datum):
         c_op = self.cursor.execute("select id, tip, ukupno_s_pdv from racuni where broj=:broj and datum=:datum", {'broj': broj, 'datum': datum})
         try:
           tpl = c_op.fetchone()
           return { 'id': tpl[0], 'tip': tpl[1], 'ukupno_s_pdv': tpl[2] }
         except:
           print "nepostoji racun sa broj, datum:", broj, datum
           return None

     # --- kraj find sekcije -------------------------------------------------------------------------------
                
     def add_racun(self, racun, rn_stavke):
        # nije proslijedjen broj racuna, automatski ga odredi 
        if not 'broj' in racun:
          racun['broj'] = self.get_next_broj_racuna(racun['datum'])

        racun['operater_id'] = self.find_operater_by_naziv(racun['operater'])
        print racun['operater_id']
        self.cursor.execute("insert into racuni(tip, broj, datum, operater_id, ukupno_s_pdv) values(:tip, :broj, :datum, :operater_id, 0)", racun)
        r_racun = self.cursor.execute("select id from racuni where broj = :broj and datum = :datum", racun)
        racun['id'] = r_racun.fetchone()[0]
        print "racun", r_racun, r_racun.fetchone()
        for rn_stavka in rn_stavke:
           d_artikal = self.find_artikal_by_kod( rn_stavka['artikal_kod'] )
           rn_stavka['racun_id'] = racun['id']
           rn_stavka['artikal_id'] = d_artikal['id']
           rn_stavka['cijena'] = d_artikal['cijena']    
           self.cursor.execute("insert into rn_stavke(racun_id, artikal_id, kolicina, cijena) values(:racun_id, :artikal_id, :kolicina, :cijena)", rn_stavka)
        self.connection.commit()
        return {'id': racun['id'], 'broj': racun['broj'], 'datum': racun['datum'] }
 
      



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

    def artikli(self, to_str=None):
        result = self.pos.cursor.execute("select kod, naziv, jmj, barkod, cijena from artikli")
        out = ""
        # izlistaj parametre 
        for row in result:
           if to_str:
              str = '<a href=/report/kartica_prodaje/{kod}>{kod:<10}</a>'.format(kod=row[0])
           else:
              str = '{kod:<10}'.format(kod=row[0])
           str += ' - {naziv:<40} ({jmj:<3}) : barkod: {barkod:<13}, cijena = {cijena:8.2f} '.format(naziv=row[1], jmj=row[2], barkod=row[3], cijena=row[4])
           if to_str:
              out += str + '\n'
           else:
              print str

        if to_str:
           return out

    def kartica_prodaje(self, artikal_kod):
        c_stavke = self.pos.cursor.execute("""SELECT racuni.datum, racuni.broj, artikli.kod, artikli.naziv, artikli.jmj, artikli.barkod, rn_stavke.cijena, case racuni.tip when 1 then kolicina else -kolicina end as kol
FROM rn_stavke 
LEFT OUTER JOIN artikli ON rn_stavke.artikal_id = artikli.id 
LEFT OUTER JOIN racuni  ON rn_stavke.racun_id = racuni.id
WHERE artikli.kod=:kod """, {'kod': artikal_kod})

        s_out = "Izvjestaj: Kartica prodaje artikla\n\n"
        ciza = "----- ---------- ---------- ------------ ---------- ---------- ----------"
        hdr  = "  r.br   datum   racun broj        cijena     kolicina   stanje   ukupno\n"
        s_out += "{ciza}\n".format(ciza=ciza)
        ukupno_t = 0
        kolicina_t = 0  
        r_br = 0
        for stavka in c_stavke:
           datum, broj, kod, naziv, jmj, barkod, cijena, kolicina = stavka
           if r_br == 0: 
              s_out += "Artikal: {kod} {naziv}\n".format(kod=kod, naziv=naziv)
              s_out +="{ciza}\n".format(ciza=ciza)
              s_out +="{hdr}\n".format(hdr=hdr)
              s_out +="{ciza}\n".format(ciza=ciza)
           r_br += 1     
           ukupno = kolicina*cijena
           ukupno_t += ukupno
           kolicina_t += kolicina
           s_out += "{r_br:4}. {datum:10}   {broj:>8}   {cijena:10} {kolicina:10} {kolicina_t:10} {ukupno:10}\n".format(r_br=r_br, datum=datum, broj=broj, cijena=cijena, kolicina=kolicina, kolicina_t=kolicina_t, ukupno=ukupno_t)
        
        s_out +="{ciza}\n".format(ciza=ciza)
        s_out +="{kolicina_t:62} {ukupno_t:10}\n".format(kolicina_t=kolicina_t, ukupno_t=ukupno_t)
        s_out +="{ciza}\n".format(ciza=ciza)
        
        print s_out
        return s_out   
           


    def racun(self, id):
       rn = self.pos.find_racun_by_id(id)
       if not rn:
          return "nema racuna id={0}".format(id) 
       header = {
          'naziv_firme': self.pos.find_parametar_by_svrha("F"),
          'pdv_broj':  self.pos.find_parametar_by_svrha("P"),
          'naziv_p': self.pos.find_parametar_by_svrha("N"),
          'adresa_p': self.pos.find_parametar_by_svrha("A"),
          'telefon': self.pos.find_parametar_by_svrha("T"),
          'fax': self.pos.find_parametar_by_svrha("U"),
          'broj': rn['broj'],
          'datum': rn['datum'],
          'tip': rn['tip']
       }

       ciza = "-" * 35
       if rn['tip'] == 1:
           tip_rn = "REDOVAN"
       else:
           tip_rn = "REKLAMIRANI"
       s_out = """{naziv_firme}
PDV Broj: {pdv_broj}
{naziv_p}
{adresa_p}
tel: {telefon}
fax: {fax}
{tip_rn} Racun br. {broj}
Sarajevo, {datum}

{ciza}
R.br Sifra       Naziv(jmj)
              kol.    cij. ukupno
{ciza}\n""".format(naziv_firme=header['naziv_firme'], pdv_broj=header['pdv_broj'], naziv_p=header['naziv_p'], adresa_p=header['adresa_p'], telefon=header['telefon'], fax=header['fax'], broj=header['broj'], datum=header['datum'], ciza=ciza, tip_rn=tip_rn)       
        

       c_stavke = self.pos.cursor.execute("select artikli.kod, artikli.naziv, artikli.jmj, artikli.barkod, rn_stavke.cijena, rn_stavke.kolicina from rn_stavke LEFT OUTER JOIN artikli ON rn_stavke.artikal_id = artikli.id WHERE racun_id=:id ", {'id': id})
 
       rbr = 0
       ukupno_t = 0
       for st in c_stavke:
           rbr += 1
           artikal_kod = st[0]
           naziv_art = st[1] + '(' + st[2] + ')' 
           barkod =st[3] 
           cijena = st[4]
           kolicina = st[5]
           ukupno = kolicina * cijena
           ukupno_t += ukupno
           s_out = s_out + """{rbr:3}. {naziv_art:20}
{kod:10} {kolicina:6} {cijena:7} {ukupno:9}\n""".format(rbr=rbr, naziv_art=naziv_art, kolicina=kolicina, cijena=cijena, ukupno=ukupno, kod=artikal_kod)

       ukupno_bez_pdv_t = ukupno_t / ((100.00 + PDV_STOPA)/100.00)
       ukupno_pdv_t = ukupno_bez_pdv_t * (PDV_STOPA/100.00)
       # ukupno sa pdv ne smijemo dirati zato cemo gresku u zaokruzenju prebaciti na ukupno bez pdv
       ukupno_pdv_t = round(ukupno_pdv_t, 2)
       ukupno_t = round(ukupno_t, 2)
       ukupno_bez_pdv_t = ukupno_t - ukupno_pdv_t

       s_out = s_out + """{ciza}
Ukupno bez PDV         {uk_bez:12}
iznos   PDV            {uk_pdv:12}
{ciza}
Ukupno sa PDV          {uk_s_pdv:12}
{ciza}""".format(uk_bez=ukupno_bez_pdv_t, uk_pdv=ukupno_pdv_t, uk_s_pdv=ukupno_t, ciza=ciza)
       print s_out
       return s_out
 

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

    for i in range(1, 0):
      racun = { 'tip':1, 'datum': date.today(), 'operater': 'hernad' }
      rn_stavke = [ { 'artikal_kod': 'USB5', 'kolicina': 1+i },
                    { 'artikal_kod': 'SP9', 'kolicina': 2+i }
                  ]
      p.add_racun(racun, rn_stavke)
  
      #print racun
      #print rn_stavke

    #result = p.cursor.execute("select * from parametri")
    #print (result.fetchall())
    #p2 = Pos("ubp_pos_2.db")
    #print p2.cursor

    print_pos.racun(5)
    print_pos.kartica_prodaje("POS")



