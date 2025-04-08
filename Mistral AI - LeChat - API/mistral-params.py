#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Auteur : Mickael Dorigny @ IT-Connect.fr

# Importation des modules nécessaires
# Module pour interagir avec le système d'exploitation
import os
# Importation de la classe Mistral du module mistralai 
from mistralai import Mistral
# Module pour analyser les arguments de la ligne de commande
import argparse

def main(args) -> None:
    """
    Fonction principale qui utilise l'API de Mistral AI pour générer une réponse
    à partir d'un prompt fourni en argument.
    """

    # Récupération de la clé API à partir des variables d'environnement
    api_key = os.environ["MISTRAL_API_KEY"]
    # Définition du modèle à utiliser pour la requête
    model = "mistral-small-latest"

    # Création d'une instance de la classe Mistral avec la clé API
    client = Mistral(api_key=api_key)

    # Boucle infinie pour permettre une interaction continue avec l'utilisateur
    while True:
        # Envoi d'une requête de complétion de chat au modèle spécifié
        chat_response = client.chat.complete(
            model=model,                   # Spécification du modèle à utiliser
            messages=[                     # Liste des messages pour la conversation
                {
                    "role": "user",       # Rôle de l'expéditeur du message (ici, l'utilisateur)
                    "content": args.prompt, # Contenu du message, basé sur l'argument fourni
                },
            ]
        )
        # Affichage de la réponse générée par le modèle
        print(chat_response.choices[0].message.content)

if __name__ == '__main__':
    # Création du parseur d'arguments pour la ligne de commande
    parser = argparse.ArgumentParser(prog='mistral-params')
    # Ajout d'un argument pour le prompt avec une aide et une exigence de saisie
    parser.add_argument("-p", '--prompt', help='Your prompt, between quotes if you have space', required=True)
    # Analyse des arguments fournis en ligne de commande
    args = parser.parse_args()
    # Appel de la fonction principale avec les arguments analysés
    main(args)
