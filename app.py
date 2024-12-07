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
import time
import schedule
from gmail_service import fetch_mails, send_response, mark_as_read

def process_emails():
    """
    Processus principal pour lire et répondre aux emails.
    """
    # Étape 1 : Récupérer les emails non lus
    emails = fetch_mails()

    # Étape 2 : Filtrer les emails pertinents
    relevant_emails = [
        email for email in emails if "Demande de certificat de scolarite" in email.get("subject", "")
    ]

    # Étape 3 : Répondre aux emails pertinents
    for email in relevant_emails:
        thread_id = email["threadId"]
        sender_email = email["sender"]
        send_response(thread_id, sender_email)

        # Marquer l'email comme lu
        mark_as_read(email["id"])

    print(f"Réponses envoyées à {len(relevant_emails)} emails pertinents.")

# Planifier le processus toutes les 2 minutes
schedule.every(2).minutes.do(process_emails)

# Boucle continue pour exécuter les tâches planifiées
print("Agent en cours d'exécution...")
while True:
    schedule.run_pending()
    time.sleep(1)
