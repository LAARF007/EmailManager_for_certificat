import os
import time
import schedule
from gmail_service import (
    fetch_mails,
    remplir_template_docx,
    send_response_with_attachment,
    load_students_data,
    extract_code_massar_with_gemini,
    send_response,
    mark_as_read,
    is_request_for_certificat,
)

def process_emails():
    """
    Processus principal pour traiter les emails entrants et répondre en fonction du contenu.
    """
    try:
        emails = fetch_mails()  # Étape 1 : Récupérer les emails non lus
        students = load_students_data()  # Charger les données des étudiants
    except Exception as e:
        print(f"Erreur lors du chargement des emails ou des données des étudiants : {e}")
        return

    for email in emails:
        try:
            thread_id = email["threadId"]
            sender_email = email["sender"]
            snippet = email["snippet"]
            subject = email.get("subject", "")

            # Vérification si le sujet correspond à une demande de certificat
            if not is_request_for_certificat(subject):
                print(f"Email ignoré (sujet non valide) : {subject}")
                continue

            # Extraire le code Massar
            code_massar = extract_code_massar_with_gemini(snippet)
            if code_massar:
                # Rechercher le code Massar dans les données des étudiants
                student_data = next((s for s in students if s["code_massar"] == code_massar), None)

                if student_data:
                    # Générer un certificat
                    try:
                        output_file = remplir_template_docx(
                            code_massar=student_data["code_massar"],
                            ville=student_data["ville"],
                            nom_complet=student_data["nom"],
                            cycle_d_etudes=student_data["cycle_d_etudes"],
                            filiere=student_data["filiere"]
                        )
                        # Vérifier que le fichier a été généré
                        if os.path.exists(output_file):
                            # Envoyer l'email avec le certificat
                            subject = "Votre certificat de scolarité"
                            body = f"Bonjour {student_data['nom']},\n\nVeuillez trouver ci-joint votre certificat de scolarité."
                            send_response_with_attachment(thread_id, sender_email, subject, body, output_file)
                        else:
                            raise FileNotFoundError(f"Le fichier {output_file} n'a pas été trouvé après génération.")
                    except Exception as e:
                        # En cas d'erreur, envoyer un email pour informer de l'échec
                        subject = "Erreur de génération du certificat"
                        body = (
                            f"Bonjour {student_data['nom']},\n\nUne erreur est survenue lors de la génération de votre certificat "
                            f"de scolarité. Veuillez réessayer plus tard.\n\nErreur : {e}"
                        )
                        send_response(thread_id, sender_email, subject, body)
                else:
                    # Répondre que le code Massar est inconnu
                    subject = "Code Massar inconnu"
                    body = (
                        f"Bonjour,\n\nNous avons trouvé un code Massar dans votre email ({code_massar}), "
                        "mais il n'est pas enregistré dans notre base de données."
                    )
                    send_response(thread_id, sender_email, subject, body)
            else:
                # Répondre que le code Massar est manquant
                subject = "Code Massar manquant"
                body = (
                    "Bonjour,\n\nNous n'avons pas trouvé de code Massar dans votre email. "
                    "Veuillez nous envoyer un email avec un code Massar valide pour recevoir votre certificat."
                )
                send_response(thread_id, sender_email, subject, body)

            # Marquer l'email comme lu
            mark_as_read(email["id"])

        except Exception as e:
            print(f"Erreur lors du traitement de l'email : {e}")

    print("Traitement des emails terminé.")

# Planifier le processus toutes les 2 minutes
schedule.every(1).minutes.do(process_emails)

# Boucle continue pour exécuter les tâches planifiées
print("Agent en cours d'exécution...")
while True:
    schedule.run_pending()
    time.sleep(1)
