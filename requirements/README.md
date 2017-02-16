These are the tested versions of install and test dependencies in case users
want to test against a known working environment, e.g.:

```
$ git clone https://github.com/jtriley/gpucrate.git
$ virtualenv gpucrate/env
$ source gpucrate/env/bin/activate
$ pip install -r requirements/install.txt
$ pip install -r requirements/test.txt
$ python setup.py develop
$ python setup.py test
```

Using pip or setup.py to install will pull in the latest versions of these
dependencies from PyPI.
