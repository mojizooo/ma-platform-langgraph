import base64
import tenseal as ts
from src.utils.key_manager import KeyManager

def coordinator_agent(state):
    context = KeyManager.get_context(is_private=False)
    def decode(b64): 
        if not b64:
            return ts.ckks_vector(context, [0.0])
        return ts.ckks_vector_from(context, base64.b64decode(b64.encode('utf-8')))
    
    a_vec = decode(state.get("enc_academic_b64"))
    f_vec = decode(state.get("enc_financial_b64"))
    p_vec = decode(state.get("enc_psych_b64"))
    
    # Weighted average: 0.4*A + 0.3*F + 0.3*P
    total = a_vec * 0.4 + f_vec * 0.3 + p_vec * 0.3
    return {"enc_total_b64": base64.b64encode(total.serialize()).decode('utf-8')}
