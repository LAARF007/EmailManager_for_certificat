# from agents import Agents
# from tasks import Tasks
# from gmail_service import fetch_mails, send_response
# from crewai import Crew
#
# # Étape 1 : Récupérer les emails depuis Gmail
# emails = fetch_mails()
#
# # Étape 2 : Créer un agent de filtrage
# filter_agent = Agents.email_filter_agent()
#
# # Étape 3 : Appliquer la tâche de filtrage et récupérer les emails pertinents
# filter_task, relevant_emails = Tasks.filter_emails_task(filter_agent, emails)
#
# # Étape 4 : Répondre automatiquement aux emails pertinents
# for email in relevant_emails:
#     thread_id = email["threadId"]
#     sender_email = email["sender"]
#     send_response(thread_id, sender_email)
#
# # Étape 5 : Assembler les agents et les tâches pour la gestion globale (Crew)
# crew = Crew(
#     agents=[filter_agent],
#     tasks=[filter_task]
# )
#
# # Étape 6 : Lancer le processus et afficher les résultats
# result = crew.kickoff()
# print("Processus terminé avec les résultats suivants :")
# print(result)
from gmail_service import fetch_mails, send_response

# Étape 1 : Récupérer les emails
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

print(f"Réponses envoyées à {len(relevant_emails)} emails pertinents.")
