import httplib2
import re
import socket

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
      
      Provides the Soocial developer API.
      
      Requires your Soocial email and password (the class takes
      care of quoting them, so you can pass user@domain.com, instead
      of user%40domain.com)::
          
          >>> email = 'user@domain.com'
          >>> password '******'
          >>> soo = Soocial(email, password)
      
      Imagine we have a new account::
      
          >>> len(soo)
          0
      
      Let's add a contact::
          
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
          
          >>> for item in contacts:
          ...     item['given-name']
          'Buddy'
      
      You can edit name information directly::
      
          >>> soo[id] = {'given-name': 'Charles Hardin', 'family-name': 'Holley'}
          >>> buddy = soo[id]
          >>> buddy['given-name']
          'Charles Hardin'
      
      Atm I'm not sure what other attributes are allowable on a contact.
      However, contents can *contain* ``phone_numbers``, ``email_addresses``,
      ``organisations``, ``urls`` and ``street_addresses``.
      
      TODO: MORE!
      
      
      
      
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
            return len(data.contacts.contact)
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
        
    
    
    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.conn.uri)
    
    
    def __delitem__(self, id):
        """
        
          Remove the contact with the specified id.
          
          :param id: the id of the contact
          :raise ResourceNotFound: if no contact with that id exists
          
        
        """
        
        path = 'contacts/%s.xml' % validate_id(id)
        self.conn.delete(path)
    
    
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
          :param id: the data to update the contact with
          :return: a dict representing the contact
          :rtype: dict
          :raise ResourceNotFound: if no contact with that id exists
          
          
        """
        
        print id
        print postdata
        path = 'contacts/%s.xml' % validate_id(id)
        data = {}
        for item in postdata:
            data['contact[%s]' % item] = postdata[item]
        postdata = urlencode(data, True)
        print postdata
        resp, data = self.conn.put(path, content=postdata)
        return data
    
    
    def add(self, postdata):
        """
          
          Create a new contact.
          
          :param postdata: the data to create the new contact with
          :return: id of the created contact
          :rtype: id
          
          
        """
        
        path = 'contacts.xml'
        data = {}
        for item in postdata:
            data['contact[%s]' % item] = postdata[item]
        postdata = urlencode(data, True)
        resp, data = self.conn.post(path, content=postdata)
        return data
    


class Connection(object):
    def __init__(self, http, uri):
        if http is None:
            http = httplib2.Http()
            http.force_exception_to_status_code = False
        self.http = http
        self.uri = uri
    
    def get(self, path, headers=None, **params):
        print 'get'
        print 'path: %s' % path
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
                print url
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
    email = 'james.arthur@largeblue.com'
    password = 'letme1n'
    soo = Soocial(email, password)
    print soo.items()
    # print soo['24276485']
    #for item in soo:
    #    print item
    #print soo.add({
    #        'first_name': 'Buddy',
    #        'last_name': 'Holly'
    #    }
    #)

