import os, hashlib, hmac

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    iterations = 220_000
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        algo, it_s, salt_hex, digest_hex = encoded.split("$")
        if algo != "pbkdf2_sha256":
            return False
        dk = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(it_s)
        )
        return hmac.compare_digest(dk.hex(), digest_hex)
    except Exception:
        return False
