from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv
import os

load_dotenv()

IMAP_SERVER = os.getenv("IMAP_SERVER_COLLECTOR")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS_COLLECTOR")
PASSWORD = os.getenv("PASSWORD_COLLECTOR")

msg = EmailMessage()
msg['To'] = 'thailson.bezerra.119@ufrn.edu.br'
msg['Subject'] = 'Teste com metadados'

# Adicionando metadados personalizados
msg.add_header('X-Session-ID', 'blablabla')
msg.add_header('X-Ticket-ID', '2')

msg.set_content('Teste com metadados no email.')

# Envio
with smtplib.SMTP(IMAP_SERVER, 587) as server:
    server.starttls()
    server.login(EMAIL_ADDRESS, PASSWORD)
    server.send_message(msg)

print("E-mail enviado com metadados!")