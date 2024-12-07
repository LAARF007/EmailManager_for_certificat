# from langchain_community.agent_toolkits import GmailToolkit
# from langchain_community.tools.gmail.search import GmailSearch
# from langchain_community.tools.gmail.send_message import GmailSendMessage
#
# from langchain_community.tools.gmail.utils import (
#     build_resource_service,
#     get_gmail_credentials,
# )
#
# credentials = get_gmail_credentials(
#     token_file="token.json",
#     scopes=["https://mail.google.com/"],
#     client_secrets_file="credentials.json"
# )
# api_resource = build_resource_service(credentials=credentials)
#
# def fetch_mails():
#     search = GmailSearch(api_resource=api_resource)
#     emails = search.invoke("in:inbox")  # Utilisation de invoke au lieu de __call__
#
#     mails = []
#
#     for email in emails:
#         mails.append(
#             {
#                 "id": email["id"],
#                 "threadId": email["threadId"],
#                 "snippet": email["snippet"],
#                 "sender": email["sender"],
#             }
#         )
#
#     return mails
#     # search = GmailSearch(api_resource=api_resource)
#     # emails = search("in:inbox")
#     #
#     # mails = []
#     #
#     # for email in emails:
#     #     mails.append(
#     #         {
#     #             "id": email["id"],
#     #             "threadId": email["threadId"],
#     #             "snippet": email["snippet"],
#     #             "sender": email["sender"],
#     #         }
#     #     )
#     #
#     # return mails
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
#     # Préparer et envoyer l'email
#     try:
#         response = send_tool.run(
#             message=body,
#             to=to_email,
#             subject=subject
#         )
#         print(f"Message envoyé : {response}")
#     except Exception as e:
#         print(f"Erreur lors de l'envoi de l'email : {e}")

from langchain_community.tools.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)
from langchain_community.tools.gmail.search import GmailSearch
from langchain_community.tools.gmail.send_message import GmailSendMessage
import re
import json
from typing import Any
import spacy

# Initialiser les services Gmail API
credentials = get_gmail_credentials(
    token_file="token.json",
    scopes=["https://mail.google.com/"],
    client_secrets_file="credentials.json"
)
api_resource = build_resource_service(credentials=credentials)


def fetch_mails():
    """
    Récupère les emails depuis la boîte de réception Gmail.

    Returns:
        list: Une liste d'emails contenant leur ID, threadId, snippet et expéditeur.
    """
    search = GmailSearch(api_resource=api_resource)
    emails = search.invoke("in:inbox")

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


#extract details
nlp = spacy.load("fr_core_news_sm")  # Modèle français de spaCy


def extract_email_details_nlp(snippet):
    doc = nlp(snippet)
    details = {"code_massar": None, "name": None, "city": None}

    for ent in doc.ents:
        if ent.label_ == "MISC":  # Ajustez les labels selon vos besoins
            if "massar" in ent.text.lower():
                details["code_massar"] = ent.text
        elif ent.label_ == "PER":
            details["name"] = ent.text
        elif ent.label_ == "LOC":
            details["city"] = ent.text

    return details


def extract_email_details(snippet):
    """
    Extrait les détails (code Massar, nom et prénom, ville) du snippet.

    Args:
        snippet (str): Le contenu de l'email.

    Returns:
        dict: Un dictionnaire contenant les informations extraites.
    """
    # Expressions régulières pour chaque champ
    massar_regex = r"code\s*massar\s*:\s*([A-Z]\d+)"
    name_regex = r"nom\s*et\s*prenom\s*:\s*([a-zA-Z\s]+)"
    city_regex = r"ville\s*:\s*([a-zA-Z\s]+)"

    # Extraction des valeurs
    code_massar = re.search(massar_regex, snippet, re.IGNORECASE)
    name = re.search(name_regex, snippet, re.IGNORECASE)
    city = re.search(city_regex, snippet, re.IGNORECASE)

    # Retourner les résultats extraits
    return {
        "code_massar": code_massar.group(1).strip() if code_massar else None,
        "name": name.group(1).strip() if name else None,
        "city": city.group(1).strip() if city else None,
    }


def save_to_json(data: Any, filename: str = "data.json") -> None:
    """
    Sauvegarde les données dans un fichier JSON de manière sécurisée.

    Args:
        data (Any): Les données à enregistrer.
        filename (str): Le nom du fichier JSON.
    """
    try:
        # Charger les données existantes
        try:
            with open(filename, "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        # Ajouter les nouvelles données
        if not isinstance(existing_data, list):
            existing_data = []
        existing_data.append(data)

        # Sauvegarder dans le fichier
        with open(filename, "w", encoding="utf-8") as file:
            file.write(json.dumps(existing_data, indent=4, ensure_ascii=False))

        print(f"Les données ont été enregistrées avec succès dans {filename}.")

    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données : {e}")
