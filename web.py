import argparse
from fridge.app import app
from fridge import routes


if __name__ == '__main__':
    ARGS = argparse.ArgumentParser(description="Run http server.")
    ARGS.add_argument(
        '--host', action="store", dest='host',
        default='127.0.0.1', help='Bind address in format: host[:port]')

    args = ARGS.parse_args()
    port = 5000
    if ':' in args.host:
        args.host, port = args.host.split(':', 1)
        port = int(port)

    app.run(args.host, port)
