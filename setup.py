from setuptools import setup, find_packages

sock = open('src/soocial/README.rst')
long_description = sock.read()
sock.close()

setup(
    name = 'py-soocial',
    version = '0.2',
    description = "Python bindings for the http://www.soocial.com developer API",
    long_description = long_description,
    author = 'thruflo',
    author_email = 'thruflo@googlemail.com',
    url = 'http://github.com/thruflo/py-soocial/tree/master',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Programming Language :: Python'
    ],
    license = 'Public Domain',
    packages = find_packages('src'),
    package_dir = {
        '': 'src'
    },
    include_package_data = True,
    zip_safe = True,
    dependency_links = [
        'http://pypi.python.org/simple'
    ],
    install_requires = [
        'ElementTree',
        'httplib2',
        'nose',
        'simplejson',
        'vobject'
    ],
    test_suite = 'nose.collector',
    entry_points = {}
)