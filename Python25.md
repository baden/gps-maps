# Introduction #

See here:
http://code.google.com/p/googleappengine/issues/detail?id=757



Just to complete Emilien's post, here is what I did, starting from a vanilla Ubuntu
10.04 (Lucid) installation.  A few differences:
- Python 2.5 is compiled with SSL support, instead of installing it afterward;
- Python 2.5 is installed without replacing the default python for Lucid (2.6).

apt-get install the following packages:
- libfreetype6-dev
- libjpeg62-dev
- liblcms1-dev
- libsqlite3-dev
- libssl-dev
- zlib1g-dev

Download Python 2.5.5 from http://python.org/download/releases/2.5.5
Download Imaging 1.1.7 from http://www.pythonware.com/products/pil/

$ tar -xvjf Python-2.5.5.tar.bz2
$ tar -xvzf Imaging-1.1.7.tar.gz

cd Python-2.5.5/

Edit Modules/Setup.dist, uncommenting _socket and ssl lines as shown below:
(...)
# Socket module helper for socket(2)_socket socketmodule.c

# Socket module helper for SSL support; you must comment out the other
# socket line above, and possibly edit the SSL variable:
SSL=/usr/bin/openssl
_ssl_ssl.c \
> -DUSE\_SSL -I$(SSL)/include -I$(SSL)/include/openssl \
> -L$(SSL)/lib -lssl -lcrypto
(...)

$ cp Modules/Setup.dist Modules/Setup

Compile Python with SSL support:
$ ./configure
$ make

Install without replacing /usr/bin/python:
$ sudo make altinstall
$ python --version
Python 2.6.5
$ python2.5 --version
Python 2.5.5

Compile and install Python Imaging Library (PIL):
$ cd ../Imaging-1.1.7/
$ sudo python2.5 setup.py install

At this point it is possible to run the GAE tutorial project:
$ python2.5 google\_appengine/dev\_appserver.py helloworld/