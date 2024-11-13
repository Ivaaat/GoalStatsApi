import hvac
import os

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv('VAULT_ADDR'),  # Адрес вашего Vault сервера
            token=os.getenv('VAULT_TOKEN') # Токен для доступа к Vault
        )
        
        if not self.client.is_authenticated():
            raise Exception("Vault authentication failed.")

    def get_secret(self, path: str):
        secret_response = self.client.secrets.kv.read_secret_version(path=path)
        return secret_response['data']['data']

    def get_ssl_certificates(self):
        return self.get_secret('path/to/ssl_certificates')  # Замените путь на ваш