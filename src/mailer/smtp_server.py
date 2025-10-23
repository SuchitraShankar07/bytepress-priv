# debug_smtp.py
import smtpd
import asyncore
from email import message_from_bytes

class DecodingDebugServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        print(f"--- Received email from {mailfrom} ---")
        msg = message_from_bytes(data)
        print(f"Subject: {msg.get('Subject')}")
        print(f"To: {msg.get('To')}")
        print("Body:")
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain" or content_type == "text/html":
                    print(part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8"))
        else:
            print(msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8"))
        print("--- End of email ---\n")

server = DecodingDebugServer(("localhost", 1025), None)
print("Decoding Debug SMTP server running on localhost:1025 ...")
asyncore.loop()

