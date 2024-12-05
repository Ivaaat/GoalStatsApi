import ssl
from dotenv import load_dotenv
import os


load_dotenv()


SSL_ROOT_CERTFILE  = os.getenv("SSL_ROOT_CERTFILE")
SSL_CERTFILE = os.getenv("SSL_CERTFILE")
SSL_KEYFILE = os.getenv("SSL_KEYFILE")


def get_ssl_context() -> ssl.SSLContext:
    ssl_context = ssl._create_unverified_context()
    ssl_context.load_verify_locations(cafile=SSL_ROOT_CERTFILE) 
    ssl_context.load_cert_chain(certfile=SSL_CERTFILE, keyfile=SSL_KEYFILE)
    return ssl_context