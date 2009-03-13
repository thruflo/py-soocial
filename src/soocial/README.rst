
Introduction
------------

This package provides a python wrapper to the `Soocial developer API <http://www.soocial.com/support/developers>`_.  `Soocial <http://www.soocial.com>`_ is a web
service that facilitates contact management by syncing across mutliple devices.


Basic Usage
-----------

Import Soocial and provide it with your Soocial email and password::

    >>> from soocial import Soocial
    >>> myemail = 'user@domain.com'
    >>> mypassword '******'
    >>> soo = Soocial(myemail, mypassword)

You have the following API available:

- ``def __contains__(id)``: does the contact with id ``id`` exist?
- ``def __iter__()``: for contact in soo
- ``def __len__()``: no_of_contacts = len(soo)
- ``def __nonzero__()``: if soo
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


Notes
-----

- adding uses POST but editing uses PUT - isn't that the wrong way round?!
- why no HEAD?  would be handy to check existence etc.
- put and post to sub elements (emails etc.) doesn't seem to be working as
documented