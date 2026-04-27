import base64
import tenseal as ts
from src.utils.key_manager import KeyManager

class PrivacyTool:
    @staticmethod
    def encrypt(score: float) -> str:
        context = KeyManager.get_context(is_private=False)
        enc_vec = ts.ckks_vector(context, [score])
        return base64.b64encode(enc_vec.serialize()).decode('utf-8')

    @staticmethod
    def decrypt(b64_str: str) -> float:
        context = KeyManager.get_context(is_private=True)
        enc_vec = ts.ckks_vector_from(context, base64.b64decode(b64_str.encode('utf-8')))
        return enc_vec.decrypt()[0]
