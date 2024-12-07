from langchain_community.tools.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)
from langchain_community.tools.gmail.search import GmailSearch
from langchain_community.tools.gmail.send_message import GmailSendMessage
import re

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
    search = GmailSearch(api_resource=api_resource)
    # Récupérer uniquement les emails non lus
    emails = search.invoke("in:inbox is:unread")

    def extract_email(sender):
        match = re.search(r"<(.+?)>", sender)
        return match.group(1) if match else sender

    return [
        {
            "id": email["id"],
            "threadId": email["threadId"],
            "subject": email["subject"],
            "snippet": email["snippet"],
            "sender": extract_email(email["sender"]),
        }
        for email in emails
    ]

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

# from langchain_community.tools.gmail.utils import (
#     build_resource_service,
#     get_gmail_credentials,
# )
# from langchain_community.tools.gmail.search import GmailSearch
# from langchain_community.tools.gmail.send_message import GmailSendMessage
# import re
# # Initialiser les services Gmail API
# credentials = get_gmail_credentials(
#     token_file="token.json",
#     scopes=["https://mail.google.com/"],
#     client_secrets_file="credentials.json"
# )
# api_resource = build_resource_service(credentials=credentials)
#
# def fetch_mails():
#     """
#     Récupère les emails depuis la boîte de réception Gmail.
#
#     Returns:
#         list: Une liste d'emails contenant leur ID, threadId, snippet et expéditeur.
#     """
#     search = GmailSearch(api_resource=api_resource)
#     emails = search.invoke("in:inbox")
#
#     def extract_email(sender):
#         match = re.search(r"<(.+?)>", sender)
#         return match.group(1) if match else sender
#
#     return [
#         {
#             "id": email["id"],
#             "threadId": email["threadId"],
#             "subject":email["subject"],
#             "snippet": email["snippet"],
#             "sender": extract_email(email["sender"]),
#         }
#         for email in emails
#     ]
#
#
# def send_response(thread_id, to_email):
#     """
#     Envoie une réponse automatique à l'adresse fournie.
#
#     Args:
#         thread_id (str): L'identifiant du fil de discussion de l'email.
#         to_email (str): L'adresse email de l'expéditeur (demandeur).
#     """
#     # Sujet et contenu du message
#     subject = "Réponse à votre demande de certificat de scolarité"
#     body = "Votre demande a bien été reçue. Nous reviendrons vers vous bientôt."
#
#     # Initialiser l'outil d'envoi d'email
#     send_tool = GmailSendMessage(api_resource=api_resource)
#
#     # Construire l'entrée pour le tool
#     tool_input = {
#         "message": body,
#         "to": to_email,
#         "subject": subject,
#     }
#
#     # Préparer et envoyer l'email
#     try:
#         response = send_tool.run(tool_input=tool_input)
#         print(f"Message envoyé : {response}")
#     except Exception as e:
#         print(f"Erreur lors de l'envoi de l'email : {e}")
#
#
#
