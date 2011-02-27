#!/usr/bin/python

# author hernad@bring.out.ba
# licenca: AGPL: http://www.gnu.org/licenses/agpl.html

import StringIO
import datetime
import pos_db
import cgi
from datetime import date

from wsgiref.simple_server import make_server
from urllib import unquote_plus

PORT=3000
VER="0.5.0"
AUTHOR="hernad@bring.out.ba"

class PosWeb:

   pos = None
   port = 0
   # racun { tip, operater, datum }
   racun = {}
   # rn_stavka - dict { artikal_kod, kolicina }
   rn_stavke = []
   err_msg = None
   # napravljen je ovaj racun
   print_rn_id = None


   def __init__(self, port):
      self.port = port
      self.pos = pos_db.Pos("ubp_pos.db")

   def get_form_vals(self, post_str):

      print "-" * 80
      print "post_str=", post_str
      print "-" * 80
      form_vals = {}
      for item in post_str.split("&"):
         form_vals[item.split("=")[0]] = item.split("=")[1]

      print form_vals
      return form_vals

   def html_start(self, output):
      output.write("""
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
        """)

   def html_head_start(self, output):
      output.write("""<head>""")
       
   def html_head_end(self, output):
      output.write("""</head>
      <body>""")

   def html_footer(self, output):
      # http://wiki.python.org/moin/EscapingHtml
      output.write("<p/></p>" + cgi.escape(AUTHOR + ", ver: " + VER))


   def html_rn_stavke(self, output):
       print >>output, "<table>\n"
       tbl_row = "<tr><td>{0}</td><td>{1}</td></tr>\n"
       
       print >>output, tbl_row.format("-------", "------------")
       print >>output, tbl_row.format("artikal", "kolicina")
       for stavka in self.rn_stavke:
           print >>output, tbl_row.format(stavka['artikal_kod'], stavka['kolicina'])
       print >>output, tbl_row.format("-------", "------------")

       print >>output, "</table>\n"
       
   def html_error(self, output):
       if self.err_msg:
          print self.err_msg
          output.write("<b>{0}</b><p/><p/>".format(cgi.escape(self.err_msg)))
       
          if self.print_rn_id:
             #odstampaj racun
             pos_print = pos_db.PosPrint(self.pos)
             str_racun = cgi.escape(pos_print.racun(self.print_rn_id))
             output.write("<pre>{0}</pre><p>".format(str_racun) )
             self.print_rn_id = None
          else:
             #odstampaj artikle
             output.write("Lista postojecih artikala:<p><p>")
             pos_print = pos_db.PosPrint(self.pos)
             str_artikli = cgi.escape(pos_print.artikli(True))
             output.write("<pre>{0}</pre><p>".format(str_artikli) )
          self.err_msg = None

   def html_end(self, output):
      output.write("""
        </body>
        </html>""")

   def html_form_racun(self, output):
      # http://stackoverflow.com/questions/991922/how-does-a-html-form-identify-itself-in-post-header
      # http://www.htmlcodetutorial.com/forms/_INPUT_TYPE_RADIO.html

      # setuj button na osnovu stanja racun['tip']
      if 'tip' in self.racun:
         if self.racun['tip'] == 1:
            s_0 = 'checked'
            s_1 = ''
         else:
            s_0 = ''
            s_1 = 'checked'
      else:
         s_0 = 'checked'
         s_1 = ''

      if 'operater' in self.racun:
          s_op = '"' + self.racun['operater'] + '"'
      else:
          s_op = '""'

      print >>output,  """<form method="POST" onsubmit="return true" id="zakljuci_rn" >
           Tip racuna:
            <INPUT TYPE=RADIO NAME="tip" VALUE="1" {0}>redovni
            <INPUT TYPE=RADIO NAME="tip" VALUE="2"  {1}>reklamirani
           operater: <input type="text" name="operater" id="operater" value={2} />
           <input type="submit" value="Zakljuci racun" name="form_racun" /> 
           </form>""".format(s_0, s_1, s_op)


   def html_form_artikli(self, output):
      print >>output,  """<form method="POST" onsubmit="return validate_unos()" id="dodaj_stavku" >
           Artikal: <input type="text" name="artikal" id="artikal" />
           kolicina: <input type="text" name="kolicina" id="kolicina" /> 
           <input type="submit" value="Dodaj stavku" name="form_stavke" />
           </form>"""


   def html_report_racun(self, output, broj):
        #odstampaj racun
        print "report 1 / stampa danasnjeg racuna broj:", broj
        pos_print = pos_db.PosPrint(self.pos)
        rn = self.pos.find_racun_by_broj_datum(broj, date.today())
        str_racun = cgi.escape(pos_print.racun(rn['id']))
        output.write("<pre>{0}</pre><p>".format(str_racun) )


   # javascript validation
   def js_validate(self, output):

      output.write("""
      <script type="text/javascript">
      function validate_fields() {
         artikal = document.getElementById('artikal');
         artikal = artikal.value;

         kolicina = document.getElementById('kolicina');
         kolicina = kolicina.value;

         ret = true;
         err = '';

         //alert('artikal =" + artikal);
         if( artikal.length == 0 ) {
            err = err + ' (1) artikal ne moze biti prazan !';
            ret = false;
         } 

         if( kolicina.length == 0 ) {
            err = err + ' (2) polje kolicina ne moze biti prazno !';
            ret = false;
         } 

         var reNum = new RegExp('[a-zA-Z]+', 'mig');
         if (reNum.test(kolicina)) {
           err = err + " (3) kolicina mora biti broj (formata 999.99) !";
           ret = false;
         }

         if (!ret)
             alert(err);

         return ret;
      }
        
      function validate_unos() {
          ret = true;
          ret = ret && validate_fields();
          //if (!ret) {
          //  alert("validacija neuspjesna!");
          //}
          return ret;
      }

      </script>
        """)
    
   def process(self, environ, response):
      
      output = StringIO.StringIO()
      # HTTP ok
      status = b'200 OK'
      # HTTP header
      headers = [ (b'Content-type', b'text/html; charset=utf-8') ]
   
      response(status, headers)

      self.html_start(output)
      self.html_head_start(output)
      self.js_validate(output)
      self.html_head_end(output)

      print >>output, "<h1>UBP seminarski POS app web klijent</h1>"

      path_vals = environ['PATH_INFO'][1:].split("/")
      print path_vals

      
      if path_vals[0] == 'report' and path_vals[1] and path_vals[2]:
         print "procesiram report ..."
         process_rpt = True
         # report/1/broj_danasnjeg_racuna
         if path_vals[1] == "racun" and int(path_vals[2]) > 0:
            # stampa racuna na danasnji dan
            self.html_report_racun(output, int(path_vals[2]))
      else:
         process_rpt = False
               

      
      if environ['REQUEST_METHOD'] == 'POST':
         self.process_post(environ)

      if not process_rpt:
        self.html_form_racun(output)

        if not self.err_msg:
           # prikazi do sada unesene stavke
           self.html_rn_stavke(output)
        self.html_error(output)
        self.html_form_artikli(output)

      self.html_footer(output)
      self.html_end(output)

      return [output.getvalue()]

   def set_err_msg(self, err_msg):
       self.err_msg = err_msg

   # process HTTP POST 
   def process_post(self, environ):
      size = int(environ['CONTENT_LENGTH'])
      #print environ
      post_str = unquote_plus(environ['wsgi.input'].read(size).decode())
   
      form_vals = self.get_form_vals(post_str)
      print form_vals

      if 'form_racun' in form_vals:
          self.process_racun(form_vals)
      elif 'form_stavke' in form_vals:
          self.process_stavke(form_vals)
      else:
          print "KAKVA JE OVO FORMA ?!??"

   def zakljuci_racun(self):
      print "zakljucujem racun"
      self.racun['datum'] = date.today()
      rn = self.pos.add_racun(self.racun, self.rn_stavke)
      if rn['broj'] > 0:
         self.set_err_msg("Racun br. {0} datuma {1} AZURIRAN USPJESNO !".format(rn['broj'], rn['datum']))
         # treba ovaj racun odstampati
         self.print_rn_id = rn['id']

         # neka zapamti operatera, ostalo neka resetuje
         op = self.racun['operater']
         self.racun = { 'operater': op }
         
         self.rn_stavke = []


   def process_racun(self, form_vals):
      if form_vals['tip'] == "1":
          print "redovni racun"
          self.racun['tip'] = 1
      else:
          print "reklamirani racun"
          self.racun['tip'] = 2

      operater = self.pos.find_operater_by_naziv( form_vals['operater'])
      if not operater:
         self.set_err_msg("Operater " + form_vals['operater'] + " nepoznat !")
         return
      else:
         self.racun['operater'] = form_vals['operater']

      if len(self.rn_stavke) < 1:
         self.set_err_msg("Racun ne moze biti zakljucen ako nema stavki")
      else:
         self.zakljuci_racun()
         
   def process_stavke(self, form_vals):
      form_vals['timestamp'] = datetime.datetime.now()

      if form_vals['artikal']:
         d_artikal = self.pos.find_artikal_by_kod( form_vals['artikal'] )
         if d_artikal:
           self.rn_stavke.append( {'artikal_kod': form_vals['artikal'], 'kolicina':form_vals['kolicina']} )
         else:
           self.set_err_msg("Artikal kod: '" + form_vals['artikal'] + "' je nepostojeci !")

      print self.rn_stavke




   def serve(self):
      print("Server slusa na portu %s" % (self.port))
      httpd = make_server('', self.port, self.process)
      httpd.serve_forever()


pos_web = PosWeb(PORT)
pos_web.serve()

