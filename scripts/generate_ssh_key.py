from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Save private key in PEM format
with open("digital-legacy-key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Generate public key
public_key = private_key.public_key()

# Save public key in OpenSSH format (required by AWS)
with open("digital-legacy-key.pub", "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    ))

print("SUCCESS: Key pair generated.")
print("- Private key: digital-legacy-key.pem")
print("- Public key: digital-legacy-key.pub")
