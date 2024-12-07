# from crewai import Task
# from textwrap import dedent
#
# class Tasks():
#     def filter_emails_task(agent, emails):
#         # Filtrer les emails pertinents
#         relevant_emails = [
#             email for email in emails if "Demande de certificat de scolarité" in email.get("snippet", "")
#         ]
#         # Description pour la tâche
#         description = dedent(f"""
#                From the given emails, filter only those related to school certificate requests.
#
#                Relevant Emails:
#                {relevant_emails}
#
#                Your final answer MUST include the relevant thread_ids and the sender, formatted as bullet points.
#            """)
#         # Résultat attendu
#         expected_output = "List of relevant thread_ids and senders, formatted as bullet points."
#
#         # Créer la tâche
#         return Task(
#             description=description,
#             expected_output=expected_output,
#             agent=agent
#         ), relevant_emails
#
#
# # add
# def filter_emails_task(agent, emails):
#     """
#     Filtre les emails pertinents ayant pour objet 'Demande de certificat de scolarité'.
#
#     Args:
#         agent (Agent): L'agent responsable de la tâche.
#         emails (list): Liste des emails récupérés depuis Gmail.
#
#     Returns:
#         Task: Une instance de Task configurée avec la description et les emails pertinents.
#     """
#     # Filtrer les emails contenant "Demande de certificat de scolarité" dans le snippet
#     relevant_emails = [
#         email for email in emails if "Demande de certificat de scolarité" in email.get("snippet", "")
#     ]
#
#     # Ajouter les informations importantes des emails pertinents
#     relevant_email_details = "\n".join(
#         f"- Thread ID: {email['threadId']}, Sender: {email['sender']}"
#         for email in relevant_emails
#     )
#
#     return Task(
#         description=dedent(f"""
#             From the given emails, filter only those related to school certificate requests.
#
#             Relevant Emails:
#             {relevant_email_details}
#
#             Your final answer MUST include the relevant thread_ids and the sender, formatted as bullet points.
#         """),
#         agent=agent,
#         context=None,  # Vous pouvez ajouter d'autres tâches liées si nécessaire
#     ), relevant_emails
#
#
