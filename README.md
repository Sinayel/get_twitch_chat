# Twitch Chat Bot avec Interface Tkinter

Une application Python simple pour connecter des bots à des chaînes Twitch, récupérer les messages du chat, et sauvegarder les conversations automatiquement.

---

## Fonctionnalités principales

- Connexion à plusieurs chaînes Twitch via IRC.
- Interface graphique avec Tkinter pour gérer les chaînes.
- Ajout / suppression de chaînes Twitch à écouter.
- Démarrage / arrêt des bots par un double-clic.
- Sauvegarde automatique des messages toutes les 15 minutes dans des fichiers CSV.
- Vérification que le pseudo Twitch existe avant de lancer le bot.
- Affichage du statut de connexion (vert = connecté, rouge = déconnecté).

---

## Installation

1. Clone ce dépôt :  
   ```bash
   git clone https://github.com/tonpseudo/get_twitch_chat.git
   ```
2. Place-toi dans le dossier cloné :  
   ```bash
   cd get_twitch_chat
   ```
3. Installe les dépendances Python (requests, tkinter est inclus par défaut) :  
   ```bash
   pip install requests
   ```
4. Modifie le fichier Python pour renseigner tes identifiants Twitch (`NICKNAME`, `TOKEN`, `CLIENT_ID`, `CLIENT_SECRET`).

---

## Usage

1. Lance le script Python :  
   ```bash
   python3 get_chat.py
   ```
2. Dans la fenêtre qui s’ouvre :  
   1. Entre un nom de chaîne Twitch dans la zone de texte.  
   2. Clique sur **Ajouter** pour l’ajouter à la liste.  
   3. Double-clique sur une chaîne dans la liste pour démarrer ou arrêter le bot.  
   4. Les messages du chat s’affichent dans la console et sont sauvegardés automatiquement.

---

## Organisation du code

- **Connexion IRC** : gestion du protocole IRC Twitch avec des sockets.  
- **Interface Tkinter** : gestion de l’affichage et des interactions utilisateur.  
- **Multithreading** : chaque bot fonctionne dans un thread indépendant.  
- **API Twitch** : validation des noms de chaînes via l’API officielle.  
- **Sauvegarde** : messages enregistrés dans des fichiers CSV horodatés.

---

## Personnalisation

- Change le délai de sauvegarde en modifiant la variable `SAVE_INTERVAL` (en secondes).  
- Personnalise le nom des fichiers de sauvegarde dans la fonction `save_messages`.  
- Améliore la gestion des erreurs ou l’interface selon tes besoins.

---

## Notes importantes

- Assure-toi d’avoir un token OAuth valide pour Twitch (à récupérer [ici](https://dev.twitch.tv/console/apps)).  
- Le bot répond automatiquement aux pings Twitch pour rester connecté.  
- L’historique des chaînes est conservé dans le fichier `channels_history.txt`.  
- Le script utilise un pseudo Twitch sans majuscules.  
- Pour obtenir le `TOKEN`, tu peux utiliser un outil comme [Twitch Token Generator](https://twitchtokengenerator.com/).

---

## Contributions

Les contributions sont les bienvenues !  
N’hésite pas à proposer des améliorations ou corriger des bugs via des pull requests.

---

## Licence

Ce projet est sous licence MIT.  
Voir le fichier LICENSE pour plus d’informations.

---

## Remerciements

Merci à Twitch pour son API et sa documentation.  
Merci à la communauté Python pour les outils.

---

**Amuse-toi bien avec ton bot Twitch ! 🚀**
