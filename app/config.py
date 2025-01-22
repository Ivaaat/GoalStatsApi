import ssl
from models import SSL, DB, Settings
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    ssl: SSL = Field(default_factory=SSL)
    db: DB = Field(default_factory=DB)
    setting: Settings = Field(default_factory=Settings)

    @classmethod
    def load(cls) -> "Config":
        return cls()

config = Config.load()

def get_ssl_context() -> ssl.SSLContext:
    ssl_context = ssl._create_unverified_context()
    ssl_context.load_verify_locations(cafile=config.ssl.root_certfile) 
    ssl_context.load_cert_chain(certfile=config.ssl.certfile, keyfile=config.ssl.keyfile)
    return ssl_context