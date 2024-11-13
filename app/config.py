import ssl




def get_ssl_context() -> ssl.SSLContext:
    # ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_context.load_cert_chain(
    #     certfile=os.getenv("SSL_CERTFILE", "path/to/fullchain.pem"),
    #     keyfile=os.getenv("SSL_KEYFILE", "path/to/privkey.pem")
    # )
    ssl_context = ssl._create_unverified_context()
    # Если требуется клиентский сертификат и ключ, укажите их:
    ssl_context.load_verify_locations(cafile=r'C:\postr\rootCA.pem') 
    ssl_context.load_cert_chain(certfile=r'C:\postr\client.pem', keyfile=r'C:\postr\client.key')
    return ssl_context