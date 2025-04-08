#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Auteur : Mickael Dorigny @ IT-Connect.fr

# Importation des modules nécessaires
import os                          # Module pour interagir avec le système d'exploitation
from mistralai import Mistral     # Importation de la classe Mistral du module mistralai

# Récupération de la clé API à partir des variables d'environnement
api_key = os.environ["MISTRAL_API_KEY"]
# Définition du modèle à utiliser pour la requête
model = "mistral-small-latest"

# Création d'une instance de la classe Mistral avec la clé API
client = Mistral(api_key=api_key)

# Boucle infinie pour permettre une interaction continue avec l'utilisateur
while True:

    # Demande à l'utilisateur d'entrer un prompt
    prompt = input("\n=> Enter your prompt : ")

    # Vérifie si l'utilisateur souhaite quitter la boucle
    if prompt in ["bye", "quit"]:
        break  # Sort de la boucle si l'utilisateur entre "bye" ou "quit"

    # Envoi d'une requête de complétion de chat au modèle spécifié
    chat_response = client.chat.complete(
        model=model,                   # Spécification du modèle à utiliser
        messages=[                     # Liste des messages pour la conversation
            {
                "role": "user",       # Rôle de l'expéditeur du message (ici, l'utilisateur)
                "content": prompt,     # Contenu du message, basé sur l'entrée de l'utilisateur
            },
        ]
    )

    # Affichage de la réponse générée par le modèle
    print(chat_response.choices[0].message.content)
