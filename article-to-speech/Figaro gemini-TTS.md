# **Figaro TTS**

Context:  
Mise en voix des articles du journal le Figaro. 

* Nombre de contenus publiés depuis le 5 février : 2874 (\~410/j)  
* Nombre moyen de caractères moyen par article : 3223.88 (calculé sur les 200 derniers articles/flash de [www.Lefigaro.fr](http://www.lefigaro.fr/))  
* Environ 20% de texte est modifié lors des republications

Le périmètre de traitement (Titre, Chapeau, Corps).  
Les problèmes techniques à résoudre (troncations, qualité robotique).  
Les ambitions futures (podcasts personnalisés, enrichissement des médias).

**Objet :** Synthèse Workshop & Débrief : Solutions Voice AI et prochaines étapes pour Le Figaro

Bonjour à toutes et à tous,

Je tenais à vous remercier pour notre workshop technique d'hier, ainsi que pour nos échanges informels qui ont suivi. C'était très riche d’enseignements pour bien cerner vos enjeux de modernisation audio pour Le Figaro et Figaro TV.

Afin de vous accompagner au mieux dans votre benchmark de ce premier trimestre, voici la synthèse de nos échanges et les actions que nous mettons en place.

### **1\. Qualité vocale et Prononciation (Le cœur du réacteur)**

L'objectif est de dépasser le rendu "robotique" de votre solution actuelle (ETX) et de sécuriser la prononciation des noms propres et acronymes.

* **Le modèle :** Nous recommandons l'utilisation de **Gemini 2.5 PRO TTS**, conçu spécifiquement pour une prosodie naturelle, capable d'adapter son ton au contexte (ex: sérieux pour la géopolitique, plus léger pour le lifestyle).  
* **Pilotage en langage naturel :** Gemini se contrôle par **"Style Prompting"**. Vous lui donnez simplement des directives claires (ex: *"Prononce 'Fillon' comme 'Fi-yon', adopte un ton journalistique neutre"*).  
* **Didascalies & Expressivité :** Vous pouvez insérer des indications directement dans le texte pour varier le rythme et l'émotion, par exemple : *"Non...[long pause]..., c'est pas vrai! [surprised]"*. Le modèle adapte sa prosodie "out of the box" selon ces suggestions.
* **Feedback Loop :** Pour les cas très spécifiques (marques, nouveaux noms), nous travaillerons sur une logique de dictionnaire / boucles de feedback pour alerter en cas de doute du modèle avant publication.

### **2\. Identité sonore, Citations et Mixage**

* **Dynamique de lecture :** L'API permet d'alterner les identités vocales (Speaker IDs). C'est idéal pour différencier la voix du journaliste de celle utilisée pour une citation ou un encadré.  
* **Habillage sonore :** Gemini générant la piste vocale pure, l'ajout de jingles ou de fonds sonores (votre "habillage") s'effectue facilement en post-production via votre code d'assemblage, garantissant un contrôle total sur le mixage.

### **3\. Clonage de Voix (Voice Cloning / Instant Custom Voice)**

Comme évoqué lors de notre débrief, la technologie a considérablement évolué, faisant chuter les barrières à l'entrée (coûts et temps) :

* **Agilité :** Il n'est plus nécessaire de faire des heures de studio. Un extrait audio de qualité de **30 secondes** suffit pour créer une "surcouche" (adaptation fine) de nos modèles de base pour répliquer un timbre vocal.  
* **Accès :** Cette fonctionnalité est actuellement en *Private Preview*.

### **4\. Prochaines étapes et Actions**

**Du côté Google Cloud :**

* **Private Preview :** Je lance dès aujourd'hui la demande d'accès ("allowlisting") pour vos équipes concernant l'Instant Custom Voice.  
* **Environnement de test :** J'ai mis à jour le repository GitHub (démo Streamlit). Vous pouvez désormais le tester sereinement en local pour valider vos propres prompts.

**Du côté Figaro :**

* **Cas d'usage :** Pour appuyer notre dossier de Private Preview, pourriez-vous me faire un retour sur l'estimation des volumes envisagés et les premières voix "cibles" que vous souhaiteriez cloner ?  
* **Benchmark :** N'hésitez pas à compiler vos listes de "mots pièges" (noms propres, anglicismes) pour que nous testions ensemble les prompts les plus efficaces.

Je reste à votre entière disposition pour vous accompagner dans vos tests sur l'API.

Très bonne journée,

**Julien MIQUEL**

Customer Engineer \- Google Cloud

