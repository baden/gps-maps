import logging
import wsgiref.handlers

#
# Use ../pywebsocket/PyAMF-0.5.1/tryit.bat for testing service.
#

from pyamf.remoting.gateway.wsgi import WSGIGateway


def echo(data):
    return data


services = {
    'myservice.echo': echo,
}


def main():
    gateway = WSGIGateway(services, logger=logging, debug=True)
    wsgiref.handlers.CGIHandler().run(gateway)


if __name__ == '__main__':
    main()
