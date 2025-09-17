from cryptography.fernet import Fernet
import os
import base64
import json
from typing import Dict, Any

class CredentialManager:
    """Менеджер для безпечного зберігання та шифрування чутливих даних"""
    
    def __init__(self):
        encryption_key = os.getenv('ENCRYPTION_KEY')
        
        if not encryption_key:
            # Генерація ключа для розробки (НЕ використовувати в продакшені!)
            encryption_key = Fernet.generate_key().decode()
            print(f"⚠️ Використовується тимчасовий ключ шифрування: {encryption_key}")
            print("⚠️ ВСТАНОВІТЬ ENCRYPTION_KEY в змінні середовища для продакшену!")
        
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
            
        self.cipher_suite = Fernet(encryption_key)
    
    def encrypt_facebook_cookies(self, cookies: Dict[str, Any]) -> str:
        """Шифрування Facebook куків"""
        try:
            json_data = json.dumps(cookies, ensure_ascii=False)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode('utf-8'))
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Помилка шифрування куків: {e}")
    
    def decrypt_facebook_cookies(self, encrypted_cookies: str) -> Dict[str, Any]:
        """Розшифровка Facebook куків"""
        try:
            encrypted_data = base64.b64decode(encrypted_cookies.encode('utf-8'))
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Помилка розшифровки куків: {e}")
    
    def encrypt_access_token(self, token: str) -> str:
        """Шифрування Facebook токена доступу"""
        try:
            encrypted_data = self.cipher_suite.encrypt(token.encode('utf-8'))
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Помилка шифрування токена: {e}")
    
    def decrypt_access_token(self, encrypted_token: str) -> str:
        """Розшифровка Facebook токена доступу"""
        try:
            encrypted_data = base64.b64decode(encrypted_token.encode('utf-8'))
            return self.cipher_suite.decrypt(encrypted_data).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Помилка розшифровки токена: {e}")
    
    def encrypt_proxy_info(self, proxy_info: Dict[str, Any]) -> str:
        """Шифрування інформації про проксі"""
        try:
            json_data = json.dumps(proxy_info, ensure_ascii=False)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode('utf-8'))
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Помилка шифрування проксі: {e}")
    
    def decrypt_proxy_info(self, encrypted_proxy: str) -> Dict[str, Any]:
        """Розшифровка інформації про проксі"""
        try:
            encrypted_data = base64.b64decode(encrypted_proxy.encode('utf-8'))
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Помилка розшифровки проксі: {e}")

# Глобальний екземпляр менеджера
credential_manager = CredentialManager()