from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurant_menu/restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/hello") or self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                # Determine greeting based on path
                greeting = "Hello!" if "/hello" in self.path else "&#161 Hola !"
                
                output = "<html><body>"
                output += f"<h1>{greeting}</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'>
                             <h2>What would you like me to say?</h2>
                             <input name="message" type="text" >
                             <input type="submit" value="Submit"> 
                             </form>'''
                output += "</body></html>"
                
                self.wfile.write(output.encode())
                return
            
            if self.path.endswith("/restaurants") or self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                output = "<html><body>"

                for restaurant_item in session.query(Restaurant):
                    output += f"{restaurant_item.name}</br>"
                    output += "<a href ='#' >Edit </a> "
                    output += "</br>"
                    output += "<a href =' #'> Delete </a>"
                    output += "</br></br>"
                output += "</body></html>"

                self.wfile.write(output.encode())
                return
            
            if self.path.endswith("/restaurants/new") or self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                output = "<html><body>"
                greeting = "Create a New Restaurant"
                output += f"<h1>{greeting}</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'>
                             <h2>What would you like me to say?</h2>
                             <input name="message" type="text" >
                             <input type="submit" value="Submit"> 
                             </form>'''
                output += "</body></html>"

                self.wfile.write(output.encode())
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            
            # CRITICAL: Key must be 'CONTENT-LENGTH' in all caps for Python 3.7+
            content_len = self.headers.get('Content-Length')
            if content_len:
                pdict['CONTENT-LENGTH'] = int(content_len)
            
            # Ensure boundary is bytes
            if 'boundary' in pdict:
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')

            output = "<html><body>"
            output += " <h2> Okay, how about this: </h2>"
            
            # Safeguard in case messagecontent is empty
            if messagecontent:
                # Get the first item from the list
                data = messagecontent[0]
                
                # If it's bytes, decode it. If it's already a string, just use it.
                if isinstance(data, bytes):
                    display_text = data.decode()
                else:
                    display_text = data
                
                output += f"<h1> {display_text} </h1>"
            else:
                output += "<h1> (No message received) </h1>"
                
            output += '''<form method='POST' enctype='multipart/form-data' action='/hello'>
                         <h2>What would you like me to say?</h2>
                         <input name="message" type="text" >
                         <input type="submit" value="Submit"> 
                         </form>'''
            output += "</body></html>"
            
            self.wfile.write(output.encode())
        except Exception as e:
            print(f"Error in POST: {e}")

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print(f"Web Server running on http://localhost:{port}/hello")
        server.serve_forever()
    except KeyboardInterrupt:
        print(" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()