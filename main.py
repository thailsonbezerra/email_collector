import imaplib
import email
import requests
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime
from dotenv import load_dotenv
import os

load_dotenv()

IMAP_SERVER = os.getenv("IMAP_SERVER_COLLECTOR")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS_COLLECTOR")
PASSWORD = os.getenv("PASSWORD_COLLECTOR")
API_WEBHOOK_URL = f"http://localhost:80/api/webhook/tickets"

def parse_address(address_header):
    """Extrai nome e email do header From"""
    name, email_addr = parseaddr(address_header)
    return name, email_addr

def decode_subject(subject):
    """Decodifica o assunto do e-mail"""
    if subject is None:
        return ""
    
    decoded = decode_header(subject)[0]
    subject_part, encoding = decoded
    if isinstance(subject_part, bytes):
        return subject_part.decode(encoding or "utf-8", errors='ignore')
    return str(subject_part)

def extract_body(msg):
    """Extrai o corpo do email, priorizando texto simples"""
    body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Ignorar anexos
            if "attachment" in content_disposition:
                continue
                
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
                    break
            elif content_type == "text/html" and not body:
                payload = part.get_payload(decode=True)
                if payload:
                    # Fallback para HTML se não tiver texto simples
                    body = payload.decode('utf-8', errors='ignore')
    else:
        # Email não multipart
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode('utf-8', errors='ignore')
    
    return body

def parse_timestamp(date_header):
    """Converte o header Date para timestamp"""
    if not date_header:
        return ""
    
    try:
        # Converte a string de data para datetime object
        dt = parsedate_to_datetime(date_header)
        # Converte para timestamp (segundos desde epoch)
        timestamp = int(dt.timestamp())
        return timestamp
    except (ValueError, TypeError) as e:
        print(f"Erro ao converter data: {e}")
        return ""

def parse_email(msg):
    """Parse completo do email extraindo todas as informações"""
    # Extrair remetente
    from_header = msg.get('From', '')
    sender_name, sender_email = parse_address(from_header)
    
    # Extrair assunto
    subject = decode_subject(msg.get('Subject', ''))
    
    # Extrair data/hora e converter para timestamp
    date_header = msg.get('Date', '')
    timestamp = parse_timestamp(date_header)
    
    # Extrair corpo
    body = extract_body(msg)
    
    # Extrair informações de thread
    # message_id = msg.get('Message-ID', '')
    
    # Extrair metadados personalizados
    metadata_customizado = {
        'session_id': msg.get('X-Session-ID', ''),
        'ticket_id': msg.get('X-Ticket-ID', '')
    }

    return {
        'sender_name': sender_name,
        'sender': sender_email,
        'channel_message_id': metadata_customizado['session_id'],
        'timestamp': timestamp,
        'subject': subject,
        'body': body,
        'message_type': "message",
        "channel_type": "email",
        "reference_channel_message_id": "",
    }

def process_email():
    try:
        # Conectar ao servidor IMAP e fazer login
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, PASSWORD)
        mail.select("INBOX")

        # Buscar e-mails não lidos
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            print("Erro ao buscar e-mails.")
            return

        message_ids = messages[0].split()

        count = 3
        for mail_id in message_ids:
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            if status != "OK":
                print(f"Erro ao buscar e-mail ID {mail_id.decode()}")
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            result = parse_email(msg)
            
            result['ticket_id'] = str(count)

            response = requests.post(API_WEBHOOK_URL, json=result)

            # Verifica se a chamada para o API foi bem-sucedida
            if response.status_code == 200:
                print(f"Dados enviados com sucesso para o API. Resposta: {response.json()}")
            else:
                print(f"Falha ao enviar dados para o API. Status: {response.status_code}, Resposta: {response.text}")
            count += 1

        mail.logout()

    except imaplib.IMAP4.error as e:
        print("Erro ao conectar ou autenticar:", e)
    except Exception as e:
        print("Erro inesperado:", e)

if __name__ == "__main__":
    process_email()