import imaplib
import email
from django.conf import settings


def obtener_correos(limit=20):
    """
    Lee correos desde el servidor IMAP y los devuelve en lista.
    No guarda nada en la base de datos.
    """

    correos = []

    try:
        # conexión IMAP
        if settings.IMAP_USE_SSL:
            mail = imaplib.IMAP4_SSL(settings.IMAP_HOST, settings.IMAP_PORT)
        else:
            mail = imaplib.IMAP4(settings.IMAP_HOST, settings.IMAP_PORT)

        # login
        mail.login(settings.IMAP_USER, settings.IMAP_PASSWORD)

        # seleccionar bandeja
        mail.select("INBOX")

        # buscar correos
        status, data = mail.search(None, "ALL")

        if status != "OK":
            return correos

        ids = data[0].split()[-limit:]

        # recorrer correos
        for mail_id in reversed(ids):
            status, msg_data = mail.fetch(mail_id, "(RFC822)")

            if status != "OK":
                continue

            for response in msg_data:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])

                    asunto = msg.get("subject", "")
                    remitente = msg.get("from", "")
                    fecha = msg.get("date", "")

                    cuerpo = extraer_cuerpo(msg)

                    correos.append({
                        "id": mail_id.decode(),
                        "asunto": asunto,
                        "remitente": remitente,
                        "fecha": fecha,
                        "cuerpo": cuerpo[:300],  # preview
                    })

        mail.logout()

    except Exception as e:
        print("Error leyendo correos:", e)

    return correos


def extraer_cuerpo(msg):
    """
    Extrae el texto plano del correo.
    """

    cuerpo = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()

            if content_type == "text/plain":
                try:
                    cuerpo = part.get_payload(decode=True).decode(errors="ignore")
                    break
                except:
                    pass
    else:
        try:
            cuerpo = msg.get_payload(decode=True).decode(errors="ignore")
        except:
            pass

    return cuerpo
