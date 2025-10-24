import imaplib
import email
from email.header import decode_header

# Configurações
IMAP_SERVER = ""
EMAIL_ADDRESS = ""
PASSWORD = ""

def decode_subject(subject):
    # Decodifica o assunto do e-mail
    decoded = decode_header(subject)[0]
    subject_part, encoding = decoded
    if isinstance(subject_part, bytes):
        return subject_part.decode(encoding or "utf-8")
    return subject_part

def get_email_content(msg):
    # Extrai o conteúdo de texto do e-mail
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                try:
                    return payload.decode("utf-8")
                except UnicodeDecodeError:
                    return payload.decode("latin-1", errors="replace")
    else:
        if msg.get_content_type() == "text/plain":
            payload = msg.get_payload(decode=True)
            try:
                return payload.decode("utf-8")
            except UnicodeDecodeError:
                return payload.decode("latin-1", errors="replace")
    return "Nenhum conteúdo de texto encontrado."

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

        for mail_id in message_ids:
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            if status != "OK":
                print(f"Erro ao buscar e-mail ID {mail_id.decode()}")
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = decode_subject(msg["subject"])
            from_ = msg.get("from")
            content = get_email_content(msg)

            print("\nE-mail ID:", mail_id.decode())
            print("Assunto:", subject)
            print("Remetente:", from_)
            print("Conteúdo:", content)
            print("-" * 50)
            
        mail.logout()

    except imaplib.IMAP4.error as e:
        print("Erro ao conectar ou autenticar:", e)
    except Exception as e:
        print("Erro inesperado:", e)

if __name__ == "__main__":
    process_email()