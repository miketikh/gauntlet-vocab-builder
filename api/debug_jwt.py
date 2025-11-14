"""
Quick script to decode JWT header and payload without verification
This helps us determine what algorithm Supabase is using
"""
import json
import base64
import sys

def decode_jwt_header(token: str):
    """Decode JWT header without verification"""
    try:
        # Split the token
        parts = token.split('.')
        if len(parts) != 3:
            print("Invalid JWT format")
            return

        # Decode header
        header = parts[0]
        # Add padding if needed
        header += '=' * (4 - len(header) % 4)
        header_decoded = base64.urlsafe_b64decode(header)
        header_json = json.loads(header_decoded)

        # Decode payload (just to see it)
        payload = parts[1]
        payload += '=' * (4 - len(payload) % 4)
        payload_decoded = base64.urlsafe_b64decode(payload)
        payload_json = json.loads(payload_decoded)

        print("JWT Header:")
        print(json.dumps(header_json, indent=2))
        print("\nJWT Payload (partial):")
        # Print only non-sensitive fields
        safe_fields = {k: v for k, v in payload_json.items()
                      if k in ['aud', 'exp', 'iat', 'iss', 'sub', 'role']}
        print(json.dumps(safe_fields, indent=2))

    except Exception as e:
        print(f"Error decoding JWT: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        decode_jwt_header(sys.argv[1])
    else:
        print("Usage: python debug_jwt.py <JWT_TOKEN>")
        print("\nOr paste token when prompted:")
        token = input("JWT Token: ").strip()
        if token:
            decode_jwt_header(token)
