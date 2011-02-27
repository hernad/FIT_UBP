import StringIO
import datetime
import pos_db


from wsgiref.simple_server import make_server
from urllib import unquote_plus


PORT=3000



def get_form_vals(post_str):

   print "-" * 80
   print "post_str=", post_str
   print "-" * 80
   form_vals = {}
   for item in post_str.split("&"):
      form_vals[item.split("=")[0]] = item.split("=")[1]

   print form_vals
   return form_vals


def pos_web_app(environ, response):
   #from io import StringIO
   output = StringIO.StringIO()


   # HTTP ok
   status = b'200 OK'
   # HTTP header
   headers = [ (b'Content-type', b'text/html; charset=utf-8') ]
   
   response(status, headers)

   print >>output, "<h1>UBP seminarski POS app web klijent</h1>"

   if environ['REQUEST_METHOD'] == 'POST':
      process_post(environ)

   path_vals = environ['PATH_INFO'][1:].split("/")

   #user, *tag = path_vals
   print "path_vals=", path_vals
   #print "user=", user
   #print "tag=", tag
   
   print >>output, """<form method="POST">
         Artikal: <input type="text" name="artikal">
         kolicina: <input type="text" name="kolicina"> 
         <input type="submit" value="Dodaj stavku">
         </form>"""

   return [output.getvalue()]

   
def process_post(environ):
   size = int(environ['CONTENT_LENGTH'])
   post_str = unquote_plus(environ['wsgi.input'].read(size).decode())
   
   form_vals = get_form_vals(post_str)
   form_vals['timestamp'] = datetime.datetime.now()

   print form_vals

   
print("Server slusa na portu %s" % (PORT))
httpd = make_server('', PORT, pos_web_app)
httpd.serve_forever()


