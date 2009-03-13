
Introduction
------------

This package provides a python wrapper to the `Soocial developer API <http://www.soocial.com/support/developers>`_.  `Soocial <http://www.soocial.com>`_ is a web
service that facilitates contact management by syncing across mutliple devices.


Basic Usage
-----------

Import Soocial and provide it with your Soocial email and password::

    >>> from soocial import Soocial
    >>> myemail = 'me@foo.com'
    >>> mypassword '***'
    >>> soo = Soocial(myemail, mypassword)

You have the following API available:

- ``def __contains__(id)``: does the contact with id ``id`` exist?
- ``def __iter__()``: for contact in soo: # do stuff with contact
- ``def __len__()``: no_of_contacts = len(soo)
- ``def __nonzero__()``: if soo: # do stuff
- ``def __getitem__(id)``: mycontact = soo[id]
- ``def __setitem__(id, postdata)``: soo[id] = {...} # n.b. rather limited atm
- ``def __delitem__(id)``: del soo[id]
- ``def add(postdata)``: soo.add({...}) # ltd
- ``def get_all_vcards(parse=True)``: get all contacts as a list of vcards
- ``def get_vcard(id, parse=True)``: get contact as vcard
- ``def get_phones(id)``: get list of contact's telephone numbers
- ``def get_emails(id)``: get list of contacts's emails
- ``def get_urls(id)``: get list of contacts's urls
- ``def get_addresses(id)``: get list of contacts's addresses
- ``def get_organisations(id)``: get list of contacts's organisations
- ``def get_user()``: get small set of user data
- ``def get_connection_phones()``: get phone number of user's connections


Example Usage
-------------

See ``soocial.client.Soocial.__doc__``.


Tests
-----

To run the tests create an empty soocial account, temporarily hack your email
and password into .client.Soocial's doc string and run::

    $ python setup.py nosetests --with-doctest

Then perhaps remove your email and password from the doc string ;)


Notes
-----

- the API doesn't support ``HEAD`` requests, which would be handy for checking
  existence without incurring extra request size overhead of ``GET``
  
- the ``/contact*`` REST seems the wrong way round: using ``POST`` for add and ``PUT`` for edit
  
- parameter names don't correspond to returned XML element names (i.e.: ``first_name``
  becomes ``given-name``
  
- write access to the elements contained by a contact (email, url, phone, etc.)
  seems not to be working as documented; in fact, it would be nice to have some
  documentation on the right URLs and the right parameters
  

