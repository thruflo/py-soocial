from setuptools import setup, find_packages

setup(
    name = 'py-soocial',
    version = '0.1',
    description = "Python bindings for the http://www.soocial.com developer API",
    author = 'thruflo',
    author_email = 'thruflo@googlemail.com',
    url = 'http://thruflo.github.com',
    packages = find_packages('src'),
    package_dir = {
        '': 'src'
    },
    include_package_data = True,
    zip_safe = False,
    dependency_links = [
        'http://pypi.python.org/simple'
    ],
    install_requires = [
        'simplejson',
        'httplib2',
        'ElementTree'
    ],
    entry_points = {}
)