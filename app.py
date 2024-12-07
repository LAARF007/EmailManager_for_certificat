#
# from gmail_service import fetch_mails, send_response
#
# # Étape 1 : Récupérer les emails
# emails = fetch_mails()
#
# # Étape 2 : Filtrer les emails pertinents
# relevant_emails = [
#     email for email in emails if "Demande de certificat de scolarite" in email.get("subject", "")
# ]
#
# # Étape 3 : Répondre aux emails pertinents
# for email in relevant_emails:
#     thread_id = email["threadId"]
#     sender_email = email["sender"]
#     send_response(thread_id, sender_email)
#
# print(f"Réponses envoyées à {len(relevant_emails)} emails pertinents.")
from gmail_service import fetch_mails, send_response, extract_email_details, save_to_json, extract_email_details_nlp

# Étape 1 : Récupérer les emails
emails = fetch_mails()

# Étape 2 : Filtrer les emails pertinents
relevant_emails = [
    email for email in emails if "Demande de certificat de scolarite" in email.get("subject", "")
]

# Étape 3 : Traiter chaque email pertinent
for email in relevant_emails:
    snippet = email.get("snippet", "")
    details = extract_email_details_nlp(snippet)

    # Vérifier que toutes les informations nécessaires sont présentes
    if all(details.values()):
        # Sauvegarder les détails dans un fichier JSON
        save_to_json(details)

        # Répondre à l'email
        thread_id = email["threadId"]
        sender_email = email["sender"]
        send_response(thread_id, sender_email)
    else:
        print(f"Informations manquantes pour l'email : {snippet}")

print(f"Réponses envoyées à {len(relevant_emails)} emails pertinents.")

