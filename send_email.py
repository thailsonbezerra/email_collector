from email.message import EmailMessage
import smtplib

msg = EmailMessage()
msg['From'] = ''
msg['To'] = ''
msg['Subject'] = ''

# Adicionando metadados personalizados
msg.add_header('X-Session-ID', 'blablabla')
msg.add_header('X-Ticket-ID', '2')

msg.set_content('Teste com metadados no email.')

# Envio
with smtplib.SMTP('smtp.gmail.com', 587) as server:
    server.starttls()
    server.login('', '')
    server.send_message(msg)

print("E-mail enviado com metadados!")