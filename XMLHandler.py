from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class XMLHandler(ContentHandler):

    def __init__(self):
        self.diccionario = {}

    def startElement(self, etiqueta, attrs):

        if etiqueta == 'account':
            self.diccionario["username"] = attrs.get("username","")
            self.diccionario["passwd"] = attrs.get("passwd","")
        elif etiqueta == 'uaserver':
            self.diccionario["uasip"] = attrs.get("ip","")
            self.diccionario["uasport"] = attrs.get("puerto","")
        elif etiqueta == 'rtpaudio':
            self.diccionario["rtport"] = attrs.get("puerto","")
        elif etiqueta == 'regproxy':
            self.diccionario["proxyip"] = attrs.get("ip","")
            self.diccionario["proxyport"] = attrs.get("puerto","")
        elif etiqueta == 'log':
            self.diccionario["logpath"] = attrs.get("path","")
        elif etiqueta == 'audio':
            self.diccionario["mp3path"] = attrs.get("path","")
        elif etiqueta =='server':
            self.diccionario["servname"] = attrs.get("name","")
            self.diccionario["servip"] = attrs.get("ip","")
            self.diccionario["servport"] = attrs.get("puerto","")
        elif etiqueta == 'database':
            self.diccionario["datapath"] = attrs.get("path","")
            self.diccionario["datapass"] = attrs.get("passwdpath","")

    def get_tags(self):
        return self.diccionario

if __name__ == "__main__":

    parser = make_parser()
    cHandler = XMLHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open("ua1.xml"))

    listatotal = cHandler.get_tags()
    print(listatotal)
