import os
import tenseal as ts

SECRET_KEY_PATH = os.path.join(os.path.dirname(__file__), '../workflows/secret_context.bytes')
PUBLIC_KEY_PATH = os.path.join(os.path.dirname(__file__), '../workflows/public_context.bytes')

class KeyManager:
    @staticmethod
    def get_context(is_private: bool = False):
        path = SECRET_KEY_PATH if is_private else PUBLIC_KEY_PATH
        if not os.path.exists(path):
            context = ts.context(ts.SCHEME_TYPE.CKKS, 8192, [60, 40, 40, 60])
            context.global_scale = 2**40
            context.generate_galois_keys()
            # Ensure the directory exists
            os.makedirs(os.path.dirname(SECRET_KEY_PATH), exist_ok=True)
            with open(SECRET_KEY_PATH, 'wb') as f: f.write(context.serialize(save_secret_key=True))
            context.make_context_public()
            with open(PUBLIC_KEY_PATH, 'wb') as f: f.write(context.serialize())
            return context if is_private else context
        with open(path, 'rb') as f: return ts.context_from(f.read())
