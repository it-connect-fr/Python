#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Auteur : Mickael Dorigny @ IT-Connect.fr

# Importation des modules nécessaires
# Module pour interagir avec le système d'exploitation
import os
# Importation de la classe Mistral du module mistralai
from mistralai import Mistral

# Récupération de la clé API à partir des variables d'environnement
api_key = os.environ["MISTRAL_API_KEY"]
# Définition du modèle à utiliser pour la requête
model = "mistral-large-latest"

# Création d'une instance de la classe Mistral avec la clé API
client = Mistral(api_key=api_key)

# Envoi d'une requête de complétion de chat au modèle spécifié
chat_response = client.chat.complete(
    model=model,                   # Spécification du modèle à utiliser
    messages=[                     # Liste des messages pour la conversation
        {
            "role": "user",       # Rôle de l'expéditeur du message
            "content": "D'où vient la popularité du nombre 42 ?",  # Contenu du message
        },
    ]
)

# Affichage de la réponse générée par le modèle
print(chat_response.choices[0].message.content)