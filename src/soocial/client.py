import base64
import cookielib
import httplib2
import re
import socket
import urllib2
import vobject

from elementtree import ElementTree
from urllib import quote, urlencode

try:
    import json # Python 2.6
except ImportError:
    import simplejson as json

from xml2dict import XmlDictParser, XmlListParser

DEFAULT_URI = u'https://www.soocial.com'


class Soocial(object):
    """
      
      Python wrapper for the Soocial developer API.
      
          >>> myemail = 'me@foo.com'
          >>> mypassword = '***'
          >>> soo = Soocial(myemail, mypassword)
      
      Let's start with an empty account::
      
          >>> len(soo)
          0
      
      Now let's add a contact::
      
          >>> id = soo.add({'first_name': 'Buddy', 'last_name': 'Holly'})
      
      The contact id is a string representing an integer::
      
          >>> str(int(id)) == id
          True
      
      This can now be used to lookup the contact::
      
          >>> buddy = soo[id]
          >>> buddy['family-name']
          'Holly'
          >>> buddy.keys()
          ['addresses', 'urls', 'family-name', 'deleted', 'organisations', 'updated-at', 'created-at', 'emails', 'id', 'given-name', 'parents', 'telephones', 'vcard', 'similarity-matrix', 'user-id', 'created-by', 'g-name-for-sorting', 'latest']
      
      You can iterate through all the contacts::
      
          >>> for item in soo:
          ...     item['given-name']
          'Buddy'
      
      Edit name information directly::
      
          >>> soo[id] = {'first_name': 'Charles Hardin', 'last_name': 'Holley'}
          >>> buddy = soo[id]
          >>> buddy['given-name']
          'Charles Hardin'
      
      You can also get data in vcard format.  Either parsed into a
      Python representation using the vobject library::
      
          >>> soo.get_all_vcards()
          [<VCARD| [<VERSION{}3.0>, <FN{u'CHARSET': [u'UTF-8']}Charles Hardin Holley>, <N{u'CHARSET': [u'UTF-8']} Charles Hardin  Holley >]>]
          >>> soo.get_vcard(id)
          <VCARD| [<VERSION{}3.0>, <FN{u'CHARSET': [u'UTF-8']}Charles Hardin Holley>, <N{u'CHARSET': [u'UTF-8']} Charles Hardin  Holley >]>
      
      Or as raw text::
      
          >>> soo.get_all_vcards(parse=False) #doctest: +ELLIPSIS
          ['BEGIN:VCARD...END:VCARD']
          
          >>> soo.get_vcard(id, parse=False) #doctest: +ELLIPSIS
          'BEGIN:VCARD...END:VCARD'
      
      Contacts contain ``phone_numbers``, ``email_addresses``,
      ``organisations``, ``urls`` and ``street_addresses``::
      
          >>> soo.get_phones(id)
          []
          
          >>> soo.get_emails(id)
          []
          
          >>> soo.get_urls(id)
          []
          
          >>> soo.get_addresses(id)
          []
          
          >>> soo.get_organisations(id)
          []
      
      Plus there's support to get a small set of data on the existing
      user and, presumably, the phone numbers of people the user
      is connected with (?)::
      
          >>> user = soo.get_user()
          >>> user.keys()
          ['username', 'name', 'number-of-contacts', 'updated-at', 'created-at', 'allow-newsletters', 'invites-available']
          
          >>> soo.get_connection_phones()
          []
      
      Atm, these are read only, until perhaps I get a little more
      info on the API, which atm doesn't work as documented
      
      
    """
    
    def __init__(self, email, password, uri=DEFAULT_URI, cache=None, timeout=None):
        """
          
          Initialize the Soocial account.
          
          :param uri: the URI of the server (for example
          ``https://www.soocial.com/contacts.xml``)
          :param cache: either a cache directory path (as a string)
          or an object compatible with the ``httplib2.FileCache``
          interface. If `None` (the default), no caching is performed.
          :param timeout: socket timeout in number of seconds, or
          `None` for no timeout
          
          
        """
        
        h = httplib2.Http(cache=cache, timeout=timeout)
        h.add_credentials(email, password)
        h.force_exception_to_status_code = False
        self.conn = Connection(h, uri)
        self.email = email
        self.password = password
    
    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.conn.uri)
    
    def __contains__(self, id):
        """
          
          Return whether the account contains a contact with the
          specified id.
          
          :param id: the contact id
          :return: `True` if a database with the name exists, `False` otherwise
          
          Would be nice if the HEAD method was supported...
          
          
        """
        
        path = 'contacts/%s.xml' % validate_id(id)
        try:
            self.conn.get(path)
            return True
        except ResourceNotFound:
            return False
        
    
    def __iter__(self):
        """
          
          Iterate over contacts list.
          
          
        """
        
        resp, data = self.conn.get('contacts.xml')
        try:
            return iter(data) # ['contacts']['contact'])
        except KeyError:
            return iter({})
    
    def __len__(self):
        """
          
          Return the number of contacts.
          
          
        """
        
        resp, data = self.conn.get('contacts.xml')
        try:
            return len(data)
        except KeyError:
            return 0
        
    
    def __nonzero__(self):
        """
          
          Return whether soocial.com is alive.
          
          Would be nice if the HEAD method was supported...
          
          
        """
        
        try:
            self.conn.get('contacts.xml')
            return True
        except:
            return False
        
    
    def __getitem__(self, id):
        """
          
          Return a dict representing the contact with the
          specified id.
          
          :param id: the id of the contact
          :return: a dict representing the contact
          :rtype: dict
          :raise ResourceNotFound: if no contact with that id exists
          
          
        """
        
        path = 'contacts/%s.xml' % validate_id(id)
        resp, data = self.conn.get(path)
        return data
        
    
    def __setitem__(self, id, postdata):
        """
          
          Update the contact with the specified data.
          
          :param id: the id of the contact
          :param postdata: the data to update the contact with
          :return: a dict representing the contact
          :rtype: dict
          :raise ResourceNotFound: if no contact with that id exists
          
          
        """
        
        path = 'contacts/%s.xml' % validate_id(id)
        data = {}
        for item in postdata:
            data['contact[%s]' % item] = postdata[item]
        postdata = urlencode(data, True)
        resp, data = self.conn.put(path, content=postdata)
        return data
    
    def __delitem__(self, id):
        """
          
          Remove the contact with the specified id.
          
          :param id: the id of the contact
          :raise ResourceNotFound: if no contact with that id exists
          
          
        """
        
        path = 'contacts/%s.xml' % validate_id(id)
        self.conn.delete(path)
    
    def add(self, postdata):
        """
          
          Create a new contact.
          
          :param postdata: the data to create the new contact with
          :return: id of the created contact
          :rtype: string
          
          
        """
        
        path = 'contacts.xml'
        data = {}
        for item in postdata:
            data['contact[%s]' % item] = postdata[item]
        postdata = urlencode(data, True)
        resp, data = self.conn.post(path, content=postdata)
        return data
    
    def get_phones(self, id):
        path = 'contacts/%s/telephones.xml' % id
        resp, data = self.conn.get(path)
        return data
    
    def get_emails(self, id):
        path = 'contacts/%s/emails.xml' % id
        resp, data = self.conn.get(path)
        return data
    
    def get_urls(self, id):
        path = 'contacts/%s/urls.xml' % id
        resp, data = self.conn.get(path)
        return data
    
    def get_addresses(self, id):
        path = 'contacts/%s/addresses.xml' % id
        resp, data = self.conn.get(path)
        return data
    
    def get_organisations(self, id):
        path = 'contacts/%s/organisations.xml' % id
        resp, data = self.conn.get(path)
        return data
    
    def get_user(self):
        """
          
          Special case: requires cookie based authentication.
          
          
        """
        
        raw = "%s:%s" % (self.email, self.password)
        auth = base64.encodestring(raw).strip()
        headers = {'AUTHORIZATION': 'Basic %s' % auth}
        opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(
                cookielib.LWPCookieJar()
            )
        )
        url = '%s/user.xml' % DEFAULT_URI
        request = urllib2.Request(url, headers=headers)
        sock = opener.open(request)
        xml = ElementTree.fromstring(sock.read())
        return XmlDictParser(xml)
    
    def get_connection_phones(self):
        resp, data = self.conn.get('/connections/phones.xml')
        return data
    
    def get_all_vcards(self, parse=True):
        """
          
          Get all the contacts as a list of vcards.
          
          The vcards are parsed from plain text into vobject.vCard
          form (a python wrapper class) by default.
          
          :param parse: set this to False to return just the raw text
          :return: list of vcards
          :rtype: list
          
          
        """
        
        resp, data = self.conn.get('contacts.vcf')
        data = data.replace('END:VCARDBEGIN:VCARD', 'END:VCARD\nBEGIN:VCARD')
        data = data.strip()
        vcards = []
        while True:
            i = data.find('END:VCARD')
            if i > -1:
                i += len('END:VCARD')
                text = data[:i]
                data = data[i:]
                if parse:
                    vcard = vobject.readOne(text.strip())
                    vcards.append(vcard)
                else:
                    vcards.append(text.strip())
            else: # no more left, we're done
                break
        return vcards
    
    def get_vcard(self, id, parse=True):
        """
          
          Get contact vcard.
          
          :param id: contact id
          :param parse: set this to False to return just the raw text
          :return: vcard
          :rtype: vobject.vCard or string
          
          
        """
        
        path = 'contacts/%s.vcf' % validate_id(id)
        resp, data = self.conn.get(path)
        if parse:
            vcard = vobject.readOne(data)
        else:
            vcard = data
        return vcard
    


class Connection(object):
    def __init__(self, http, uri):
        if http is None:
            http = httplib2.Http()
            http.force_exception_to_status_code = False
        self.http = http
        self.uri = uri
    
    def get(self, path, headers=None, **params):
        return self._request('GET', path, headers=headers, **params)
    
    def post(self, path, content=None, headers=None, **params):
        return self._request(
            'POST', path, content=content, headers=headers, **params
        )
    
    def put(self, path, content=None, headers=None, **params):
        return self._request(
            'PUT', path, content=content, headers=headers, **params
        )
    
    def head(self, path, headers=None, **params):
        return self._request('HEAD', path, headers=headers, **params)
    
    def delete(self, path, headers=None, **params):
        return self._request('DELETE', path, headers=headers, **params)
    
    def _request(self, method, path, content=None, headers=None, **params):
        headers = headers or {}
        headers.setdefault('Accept', '*/*')
        headers.setdefault('User-Agent', 'py-soocial')
        body = None
        if content is not None:
            body = content
            headers.setdefault('Content-Type', 'application/x-www-form-urlencoded')
            headers.setdefault('Content-Length', str(len(body)))
        def _make_request(retry=1):
            try:
                url = uri(
                    self.uri, 
                    path, 
                    **params
                )
                return self.http.request(
                    url,
                    method,
                    body = body, 
                    headers = headers
                )
            except socket.error, e:
                if retry > 0 and e.args[0] == 54: # reset by peer
                    return _make_request(retry - 1)
                raise
        resp, data = _make_request()
        code = int(resp.status)
        if data:
            if code == 200 and resp.get('content-type').startswith('application/xml'):
                xml = ElementTree.fromstring(data)
                # hack logic to differentiate between the two types of
                # response from soocial
                # one day it would be nice to have a *proper*
                # xml <-> py dict <-> xml convertor
                tagname = u''
                config = XmlListParser
                for item in xml.getchildren():
                    if not tagname:
                        tagname = item.tag
                    else:
                        if not item.tag == tagname:
                            config = XmlDictParser
                            break
                data = config(xml)
            elif code == 201:
                data = resp['location'].split('/')[-1]
        if code >= 400:
            if type(data) is dict:
                error = (data.get('error'), data.get('reason'))
            else:
                error = data
            if code == 404:
                raise ResourceNotFound(error)
            elif code == 409:
                raise ResourceConflict(error)
            elif code == 412:
                raise PreconditionFailed(error)
            else:
                raise ServerError((code, error))
        return resp, data
    


class PreconditionFailed(Exception):
    """412"""

class ResourceNotFound(Exception):
    """404"""

class ResourceConflict(Exception):
    """409"""

class ServerError(Exception):
    """Unexpected HTTP error"""


def uri(base, *path, **query):
    """
      
      Assemble a uri based on a base, any number of path segments,
      and query string parameters.
      
          >>> uri('http://example.org/', '/_all_dbs')
          'http://example.org/_all_dbs'
      
      
    """
    
    if base and base.endswith('/'):
        base = base[:-1]
    retval = [base]
    
    # build the path
    path = '/'.join([''] +
                    [s.strip('/') for s in path
                     if s is not None])
    if path:
        retval.append(path)
    
    # build the query string
    params = []
    for name, value in query.items():
        if type(value) in (list, tuple):
            params.extend([(name, i) for i in value if i is not None])
        elif value is not None:
            if value is True:
                value = 'true'
            elif value is False:
                value = 'false'
            params.append((name, value))
    if params:
        retval.extend(['?', unicode_urlencode(params)])
    return ''.join(retval)

def unicode_quote(string, safe=''):
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    return quote(string, safe)

def unicode_urlencode(data, doseq=None):
    if isinstance(data, dict):
        data = data.items()
    params = []
    for name, value in data:
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        params.append((name, value))
    return urlencode(params, doseq)


VALID_ID = re.compile(r'^[0-9]+$')
def validate_id(id):
    if not VALID_ID.match(id):
        raise ValueError('Invalid contact ID')
    return id


if __name__ == '__main__':
    import sys
    email = sys.args[0]
    password = sys.args[1]
    soo = Soocial(email, password)
    for item in soo:
        print item
    

