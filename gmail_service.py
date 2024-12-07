import base64
import re
import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from docx import Document
import os
from langchain_community.tools.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)
from langchain_community.tools.gmail.search import GmailSearch
from langchain_community.tools.gmail.send_message import GmailSendMessage

import mimetypes
from email.mime.base import MIMEBase
from email import encoders

# Initialiser les services Gmail API
credentials = get_gmail_credentials(
    token_file="token.json",
    scopes=["https://mail.google.com/"],
    client_secrets_file="credentials.json"
)
api_resource = build_resource_service(credentials=credentials)

def fetch_mails():
    """
    Récupère les emails non lus depuis la boîte de réception Gmail.

    Returns:
        list: Une liste d'emails contenant leur ID, threadId, snippet, expéditeur et sujet.
    """
    try:
        search = GmailSearch(api_resource=api_resource)
        emails = search.invoke("in:inbox is:unread")

        def extract_email(sender):
            match = re.search(r"<(.+?)>", sender)
            return match.group(1) if match else sender

        return [
            {
                "id": email["id"],
                "threadId": email["threadId"],
                "subject": email.get("subject", ""),
                "snippet": email.get("snippet", ""),
                "sender": extract_email(email.get("sender", "")),
            }
            for email in emails
        ]
    except Exception as e:
        print(f"Erreur lors de la récupération des emails : {e}")
        return []

def extract_code_massar(snippet):
    """
    Extrait le code Massar du corps ou snippet de l'email.

    Args:
        snippet (str): Le contenu de l'email.

    Returns:
        str: Le code Massar s'il est trouvé, sinon None.
    """
    try:
        match = re.search(r"code massar\s*:\s*([A-Za-z]\d+)", snippet, re.IGNORECASE)
        return match.group(1) if match else None
    except Exception as e:
        print(f"Erreur lors de l'extraction du code Massar : {e}")
        return None

def load_students_data():
    """
    Charge les données des étudiants depuis un fichier JSON.

    Returns:
        list: Liste d'étudiants avec leurs informations.
    """
    try:
        with open("etudiants.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des données des étudiants : {e}")
        return []

# def send_response_with_attachment(thread_id, to_email, subject, body, attachment_path):
#     """
#     Envoie une réponse avec une pièce jointe.
#
#     Args:
#         thread_id (str): L'identifiant du fil de discussion.
#         to_email (str): L'adresse email du destinataire.
#         subject (str): Le sujet de l'email.
#         body (str): Le corps de l'email.
#         attachment_path (str): Chemin de la pièce jointe.
#     """
#     send_tool = GmailSendMessage(api_resource=api_resource)
#     tool_input = {
#         "message": body,
#         "to": to_email,
#         "subject": subject,
#         "attachments": [attachment_path],
#     }
#     try:
#         response = send_tool.run(tool_input=tool_input)
#         print(f"Email avec pièce jointe envoyé : {response}")
#     except Exception as e:
#         print(f"Erreur lors de l'envoi de l'email : {e}")

def send_response_with_attachment(thread_id, to_email, subject, body, attachment_path):
    """
    Envoie une réponse avec une pièce jointe.

    Args:
        thread_id (str): L'identifiant du fil de discussion.
        to_email (str): L'adresse email du destinataire.
        subject (str): Le sujet de l'email.
        body (str): Le corps de l'email.
        attachment_path (str): Chemin de la pièce jointe.
    """
    try:
        # Créer un message MIME
        mime_message = MIMEMultipart()
        mime_message["To"] = to_email
        mime_message["Subject"] = subject

        # Ajouter le corps du message
        mime_message.attach(MIMEText(body, "plain"))

        # Ajouter la pièce jointe
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                mime_base = MIMEBase(*mimetypes.guess_type(attachment_path)[0].split("/"))
                mime_base.set_payload(attachment.read())
                encoders.encode_base64(mime_base)
                mime_base.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(attachment_path)}",
                )
                mime_message.attach(mime_base)
        else:
            raise FileNotFoundError(f"Le fichier '{attachment_path}' est introuvable.")

        # Encoder le message en Base64
        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

        # Envoyer le message via l'API Gmail
        create_message = {"raw": encoded_message}
        sent_message = (
            api_resource.users().messages().send(userId="me", body=create_message).execute()
        )
        print(f"Email envoyé avec succès : {sent_message['id']}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email avec pièce jointe : {e}")
def send_response(thread_id, to_email):
    """
    Envoie une réponse automatique à l'adresse fournie.

    Args:
        thread_id (str): L'identifiant du fil de discussion de l'email.
        to_email (str): L'adresse email de l'expéditeur (demandeur).
    """
    # Sujet et contenu du message
    subject = "Réponse à votre demande de certificat de scolarité"
    body = "Votre demande a bien été reçue. Nous reviendrons vers vous bientôt."

    # Initialiser l'outil d'envoi d'email
    send_tool = GmailSendMessage(api_resource=api_resource)

    # Construire l'entrée pour le tool
    tool_input = {
        "message": body,
        "to": to_email,
        "subject": subject,
    }

    # Préparer et envoyer l'email
    try:
        response = send_tool.run(tool_input=tool_input)
        print(f"Message envoyé : {response}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")

def mark_as_read(email_id):
    """
    Marque un email comme lu.

    Args:
        email_id (str): L'identifiant de l'email.
    """
    try:
        api_resource.users().messages().modify(
            userId="me",
            id=email_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        print(f"Email {email_id} marqué comme lu.")
    except Exception as e:
        print(f"Erreur lors du marquage comme lu : {e}")


def remplir_template_docx(code_massar, ville, nom_complet, output_folder="output", template_path="template.docx"):
    """
    Remplit un modèle Word avec les informations fournies et génère un fichier.

    :param code_massar: Code Massar de l'étudiant.
    :param ville: Ville de résidence.
    :param nom_complet: Nom complet de l'étudiant.
    :param output_folder: Dossier où enregistrer le fichier généré (par défaut 'output').
    :param template_path: Chemin vers le modèle Word (par défaut 'template.docx').
    :return: Chemin du fichier généré.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Le modèle Word '{template_path}' est introuvable.")

    # Vérifier si le dossier de sortie existe, sinon le créer
    os.makedirs(output_folder, exist_ok=True)

    # Charger le modèle Word
    doc = Document(template_path)
    output_path = os.path.join(output_folder, f"attestation_{code_massar}.docx")

    # Remplacer les champs dans le modèle
    placeholders = {
        "{{CODE_MASSAR}}": code_massar,
        "{{VILLE}}": ville,
        "{{NOM_COMPLET}}": nom_complet,
        "{{DATE}}": datetime.now().strftime("%d/%m/%Y"),
    }

    for paragraph in doc.paragraphs:
        for placeholder, value in placeholders.items():
            if placeholder in paragraph.text:
                paragraph.text = paragraph.text.replace(placeholder, value)

    # Sauvegarder le fichier Word généré
    doc.save(output_path)
    print(f"Certificat généré : {output_path}")
    return output_path