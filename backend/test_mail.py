import sys

print(sys.executable)
try:
    import aiosmtplib

    print("AIOSMTPLIB IMPORTED")
except ImportError as e:
    print(f"FAILED TO IMPORT AIOSMTPLIB: {e}")

try:
    from commons.mail import send_email

    print("MAIL MODULE IMPORTED")
except ImportError as e:
    print(f"FAILED TO IMPORT MAIL MODULE: {e}")
