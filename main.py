import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime

# Configurações
IMAP_SERVER = ""
EMAIL_ADDRESS = ""
PASSWORD = ""
OUTPUT_DIR = "output"

# Criar diretório de saída se não existir
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def decode_subject(subject):
    # Decodifica o assunto do e-mail
    decoded = decode_header(subject)
    first_part = decoded[0]
    subject_part = first_part[0]
    encoding = first_part[1]

    if isinstance(subject_part, bytes):
        if encoding is not None:
            subject_part = subject_part.decode(encoding)
        else:
            subject_part = subject_part.decode("utf-8")
    return subject_part


def save_attachment(part, email_id):
    # Salva anexos no disco
    filename = part.get_filename()
    if filename is not None:
        decoded_filename_tuple = decode_header(filename)[0]
        decoded_filename = decoded_filename_tuple[0]
        if isinstance(decoded_filename, bytes):
            decoded_filename = decoded_filename.decode()

        safe_filename = ""
        for c in decoded_filename:
            if c.isalnum() or c in ('.', '_', '-'):
                safe_filename += c

        filepath = os.path.join(OUTPUT_DIR, str(email_id) + "_" + safe_filename)

        with open(filepath, "wb") as f:
            f.write(part.get_payload(decode=True))

        print("Anexo salvo:", filepath)


def process_email():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, PASSWORD)
        mail.select("INBOX")

        status, messages = mail.search(None, "ALL")
        if status != "OK":
            print("Erro ao buscar e-mails.")
            return

        message_ids = messages[0].split()

        for mail_id in message_ids:
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            if status != "OK":
                print("Erro ao buscar e-mail ID", mail_id)
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = decode_subject(msg["subject"])
            from_ = msg.get("from")

            print("")
            print("E-mail ID:", mail_id.decode())
            print("Assunto:", subject)
            print("De:", from_)

            html_content = None

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    disposition = part.get("Content-Disposition")

                    if content_type == "text/html":
                        payload = part.get_payload(decode=True)
                        try:
                            html_content = payload.decode()
                        except UnicodeDecodeError:
                            html_content = payload.decode("latin-1", errors="replace")

                    elif disposition is not None and part.get_filename() is not None:
                        save_attachment(part, mail_id.decode())

            else:
                content_type = msg.get_content_type()
                if content_type == "text/html":
                    payload = msg.get_payload(decode=True)
                    try:
                        html_content = payload.decode()
                    except UnicodeDecodeError:
                        html_content = payload.decode("latin-1", errors="replace")

            if html_content is not None:
                html_filename = os.path.join(OUTPUT_DIR, "email_" + mail_id.decode() + ".html")
                with open(html_filename, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("HTML salvo:", html_filename)

        mail.logout()

    except imaplib.IMAP4.error as e:
        print("Erro ao conectar ou autenticar:", e)
    except Exception as e:
        print("Erro inesperado:", e)


if __name__ == "__main__":
    process_email()
