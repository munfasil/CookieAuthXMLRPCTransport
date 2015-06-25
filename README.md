# CookieAuthXMLRPCTransport
Implements XMLRPC cookie based authentication

##Usage

server = xmlrpclib.ServerProxy('http://localhost',transport=CookieAuthXMLRPCTransport(),verbose=False)
server.login({'username':'USERNAME','password':'PASSWORD'}) 
