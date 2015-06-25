########################################################################
#
# File:   xmlrpc_cookie.py
# Author: Vaibhav Bhatia
# Revised:Syed Shahrukh Hussain
# Date:   2013-09-20
#
########################################################################
########################################################################
# --Usage-
# server = xmlrpclib.ServerProxy('http://localhost',transport=CookieAuthXMLRPCTransport(),verbose=False)
# server.login({'username':'<username>','password':'<password>'}) 
########################################################################
########################################################################
# Imports
########################################################################
import xmlrpclib
import os
import sys
import xmlrpclib
import urllib2
import logging
import cookielib

def create_user_agent():
    ma, mi, rel = sys.version_info[:3]
    return "xmlrpclib - Python-%s.%s.%s"%(ma, mi, rel)

class CookieAuthXMLRPCTransport(xmlrpclib.SafeTransport):
    """
xmlrpclib.Transport that caches authentication cookies in a
local cookie jar and reuses them.

Based off `this recipe
<http://code.activestate.com/recipes/501148-xmlrpc-serverclient-which-does-cookie-handling-and/>`_

"""

    def __init__(self, cookiefile = None, user_agent = None):
        self.cookiefile = cookiefile or "cookies.txt"
        self.user_agent = user_agent or create_user_agent()
        xmlrpclib.SafeTransport.__init__(self)
        
    def send_cookie_auth(self, connection):
        """Include Cookie Authentication data in a header"""
        logging.debug("Sending cookie")
        cj = cookielib.LWPCookieJar()
        cj.load(self.cookiefile,ignore_discard=True, ignore_expires=True)
        #print self.cookiefile
        for cookie in cj:
            connection.putheader("Cookie", "%s=%s" % (cookie.name,cookie.value))
            #print cookie.name, cookie.value

    ## override the send_host hook to also send authentication info
    def send_host(self, connection, host):
        xmlrpclib.Transport.send_host(self, connection, host)
        if os.path.exists(self.cookiefile):
            logging.debug(" Sending back cookie header")
            self.send_cookie_auth(connection)

    def request(self, host, handler, request_body, verbose=0):
        # dummy request class for extracting cookies
        class CookieRequest(urllib2.Request):
            pass
        # dummy response class for extracting cookies
        class CookieResponse():
            def __init__(self, headers):
                self.headers = headers
            def info(self):
                return self
            def getheaders(self,header=None):
                h=self.headers.getheaders()
                return [h[1][1]]
        
        crequest = CookieRequest('https://'+host+'/')
        # issue XML-RPC request
        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)
        self.send_request(h, handler, request_body)
        self.send_host(h, host)
        self.send_user_agent(h)
        # creating a cookie jar for my cookies
        cj = cookielib.LWPCookieJar()
        self.send_content(h, request_body)
        errcode =200 
        errmsg = 0 
        headers = h.getresponse()
       
        cresponse = CookieResponse(headers)
        print cresponse.getheaders()
        cj.extract_cookies(cresponse, crequest)
       
        if len(cj) >0 and not os.path.exists(self.cookiefile):
            logging.debug("Saving cookies in cookie jar")
            cj.save(self.cookiefile,ignore_discard=True, ignore_expires=True)
        if errcode != 200:
            raise xmlrpclib.ProtocolError(host + handler,
                                          errcode, errmsg,headers)
        self.verbose = verbose
        try:
            sock = h._conn.sock
        except AttributeError:
            sock = None
        return self.parse_response(headers)
