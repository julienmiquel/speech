# 📝 notes

févr. 16, 2026

## Figaro \- workshop

Invité [Julien Miquel](mailto:julienmiquel@google.com) [Birame Fall](mailto:biramefall@google.com) [GHARIANI Houssem](mailto:hghariani@lefigaro.fr)

Pièces jointes [Figaro - workshop](https://calendar.google.com/calendar/event?eid=NnVlNjY0dXZpMjdiZDZhMWh0MTlnNXA1OGgganVsaWVubWlxdWVsQGdvb2dsZS5jb20)

Enregistrements de réunions [Transcription](https://docs.google.com/document/d/1rPltDq90KF_1QYTMnm4qgLlFNt6riL62l74iSSEExCc/edit?usp=drive_web&tab=t.s0752gcby17f) 

### Résumé

La réunion entre les participants et quelqu'un dans Aida (fr-par-25c) a porté sur les objectifs du projet, notamment l'évaluation comparative des solutions (benchmark) au T1 et l'amélioration de la qualité de la voix, jugée actuellement "un petit peu robotique". Il a été souligné l'importance de gérer la prononciation des termes techniques et d'intégrer des fonctionnalités avancées comme la double intervention pour les citations et la segmentation des voix par rubrique. La discussion a également couvert le workflow intégral utilisant des modèles Gemini pour structurer les données et adapter le ton à l'article, ainsi que les problèmes techniques récurrents de l'ancien système (ETX), notamment les coupures et les erreurs de longueur audio, tout en explorant le potentiel de nouveaux produits audio comme le "podcast podcastisé" et l'intégration de recommandations personnalisées. Le processus de génération audio-vidéo (Gemini TTS), qui prend en charge plus de 80 langues et permet de contrôler le style de la voix, a été démontré, et la fonctionnalité d'entraînement de voix personnalisée sur Gini TTS (actuellement en "private preview") a été abordée

### Étapes suivantes

- [ ] Quelqu'un dans Aida (fr-par-25c) devra s'assurer que Streamlit est dans les exigences et indiquer au groupe d'exécuter `streamlit run article_texte_speech` suivi de `app.py` après avoir créé un environnement virtuel (VENV).

- [ ] Quelqu'un dans Aida (fr-par-25c) va pousser le changement concernant le side (fixation de la voix) dans le code.

- [ ] Quelqu'un dans Aida (fr-par-25c) va fournir des exemples de composition et d'assemblage des fonds sonores.

### Détails

* **Réglages Initiaux et Objectifs de la Réunion**: La réunion a commencé par la vérification de l'équipement (écrans et caméras) et la clarification de l'agenda ([00:00:00](#00:00:00)). L'objectif principal de la session est de s'assurer que les participants partent avec une solution fonctionnelle, une bonne compréhension de l'API, et la capacité de reproduire les expérimentations en interne ([00:01:12](#00:01:12)).

* **Critères de Succès du Projet et Timing**: quelqu'un dans Aida (fr-par-25c) a exprimé le souhait de comprendre le calendrier du projet et les critères de succès pour le choix de la technologie ([00:03:18](#00:03:18)). Les participants ont convenu que le premier trimestre (Q1) sera consacré à l'évaluation comparative des solutions (benchmark) et à l'établissement d'une notion de coût ([00:09:06](#00:09:06)).

* **Critères de Qualité de la Voix et Double Intervention**: Les critères de succès incluent l'amélioration de la qualité de la voix, qui est actuellement perçue comme "un petit peu robotique". Il a été soulevé l'intérêt d'avoir deux intervenants pour les articles éditoriaux comportant des citations, ainsi que la possibilité de segmenter les voix par rubrique (comme les nouvelles politiques ou autres catégories) ([00:04:13](#00:04:13)).

* **Gestion des Termes Techniques et Prononciation**: Il est jugé crucial de s'assurer que le système gère correctement la prononciation des mots techniques, des mots anglais, et des noms de personnalités publiques, une difficulté souvent rencontrée avec d'autres fournisseurs. Des outils comme des dictionnaires de prononciation pourraient être nécessaires pour cette tâche ([00:05:40](#00:05:40)).

* **Intégration de la Monétisation (Ad Server)**: La question de l'intégration de la monétisation a été abordée, et il a été confirmé que les équipes utilisent déjà Google Ad Manager (GAM). La gestion du serveur publicitaire (ad server) est une discussion séparée qui ne relève pas de l'équipe Google Cloud et ne constitue pas un critère de réussite immédiat du projet ([00:07:43](#00:07:43)).

* **Évolution de la Technologie Google TTS**: Les solutions de synthèse vocale de Google ont beaucoup évolué depuis les derniers tests effectués il y a environ trois ans, où les fonctionnalités les plus intéressantes étaient expérimentales ou optimisées pour l'anglais ([00:09:50](#00:09:50)). Les nouveaux modèles à venir incluent le clonage de voix et la possibilité de définir l'intention (par exemple, être explicatif ou souriant) plutôt que d'utiliser uniquement le format SSML (Speech Synthesis Markup Language) ([00:10:27](#00:10:27)).

* **Workflow Intégral et Modèles Gemini**: L'approche actuelle ne repose pas sur un modèle TTS isolé, mais sur un flux de travail complet qui traite les données brutes, les structure, et permet d'intégrer des éléments tels que les pauses dramatiques, les tonalités (graves, souriantes, sérieuses), et même la musique ([00:12:04](#00:12:04)). Ce workflow utilise d'autres modèles Gemini pour la conversion et l'adaptation, garantissant un résultat final pertinent ([00:13:01](#00:13:01)).

* **Présentation Générale des Capacités d'IA Média (Overview)**: quelqu'un dans Aida (fr-par-25c) a rapidement présenté l'écosystème plus large des modèles Gen Media, y compris la génération d'images (Nano Banana), de vidéo, le modèle de musique (LIRIA), et la recherche sur les articles de presse ([00:15:12](#00:15:12)). Il a été souligné la capacité de lier l'information générée à des sources internes ou externes (grounding) pour garantir la validation des données ([00:17:43](#00:17:43)).

* **Démonstration de la Génération Audio-Vidéo (Gemini TTS)**: Gemini TTS, le modèle le plus avancé, gère plus de 80 langues et permet de contrôler le style de la voix via des mots-clés (par exemple, *sarcastique*, *giggle*, *whisper*). Il a été démontré comment le système peut gérer l'audio et la vidéo de manière cohérente, même si l'accent est mis sur l'audio pour ce projet ([00:21:07](#00:21:07)) ([00:28:38](#00:28:38)).

* **Détermination du Ton et Contrôle du Prompt**: La question de la détermination du ton approprié pour un article a été soulevée ([00:30:10](#00:30:10)). Il a été expliqué que le système utilise un workflow où le texte brut est analysé par un modèle de langage (NLM) pour déterminer le contexte et l'intention ([00:32:10](#00:32:10)). Ce processus permet d'adapter le ton en fonction de la catégorie de l'article (par exemple, être très factuel en géopolitique, ou utiliser un ton sarcastique si les directives l'autorisent) ([00:31:03](#00:31:03)) ([00:33:45](#00:33:45)).

* **Configuration de l'Autonomie de Génération**: Il est possible de définir une marge de confiance ou d'autonomie pour la génération, permettant de s'assurer que le ton reste approprié ou que les changements émotionnels ne sont intégrés qu'avec un niveau de certitude élevé ([00:36:12](#00:36:12)). Le client peut choisir de rester strictement fidèle au texte ou de permettre une légère déviation pour améliorer la qualité orale ([00:37:22](#00:37:22)).

* **Prochaines Étapes et Travail Pratique (Hands-on)**: quelqu'un dans Aida (fr-par-25c) a proposé une petite démo simple à installer sur l'environnement des participants pour qu'ils puissent commencer à travailler ([00:37:22](#00:37:22)). Les participants sont invités à se connecter au répertoire de Julien Miquel sur GitHub, où ils trouveront un outil Streamlit simple pour choisir les langues, extraire le texte et tester la conversion avec différentes voix (y compris la version Pro recommandée pour la clarté) ([00:46:39](#00:46:39)) ([00:52:31](#00:52:31)).

* **Problèmes de configuration initiaux et utilisation d'outils**: quelqu'un dans Aida (fr-par-25c) a commencé par mentionner de nouveaux chiffres concernant la Programmation Pluriannuelle de l'Énergie (PPE) ([00:59:20](#00:59:20)). La discussion a ensuite rapidement basculé sur des problèmes techniques et des préférences d'outils, quelqu'un dans Aida (fr-par-25c) préférant "team cursor" à "antigravity" ([01:01:07](#01:01:07)). Il y a eu des difficultés de configuration liées à l'activation d'un environnement virtuel et à la localisation, notamment la nécessité de se mettre en Europe pour certains droits d'accès au lieu de "US central" ([00:59:20](#00:59:20)) ([01:06:09](#01:06:09)).

* **Problèmes de localisation et d'accès aux données**: quelqu'un dans Aida (fr-par-25c) a signalé des problèmes de région et d'accès, mentionnant une possible interdiction sur "central 1" ([01:01:58](#01:01:58)). Il a été souligné qu'il fallait définir la localisation en "Europe Prestin" pour avoir les droits d'accès, sinon ils ne seraient pas accordés en "US central" ([01:06:09](#01:06:09)). Après correction, l'extraction a pu être lancée ([01:03:59](#01:03:59)).

* **Capacités de synthèse vocale et gestion des données**: Le potentiel de la synthèse vocale pour présenter des données a été abordé, citant un exemple de résultats d'élections municipales ([01:06:09](#01:06:09)). Quelqu'un dans Aida (fr-par-25c) a noté que la lecture était redondante dans un cas précis où le paragraphe et l'histogramme véhiculaient la même information ([01:08:13](#01:08:13)).

* **Gestion des infographies et de la redondance**: La question de savoir si l'audio devait lire les données des infographies a été soulevée, en particulier lorsque ces données ne sont pas entièrement racontées dans le texte ([01:07:29](#01:07:29)). Il a été convenu que si l'infographie présente des informations partiellement exclusives, il faudrait les détecter et les traduire en audio pour éviter une perte d'information essentielle ([01:08:55](#01:08:55)).

* **Intégration et différenciation des contenus additionnels**: Il a été suggéré d'introduire un changement de ton ou de voix pour différencier certains contenus, comme les encadrés ou les citations ([01:09:46](#01:09:46)). Cette approche est considérée comme importante pour les éléments enrichis comme les citations et les encadrés ([01:10:22](#01:10:22)).

* **Gestion des vidéos et des médias enrichis**: quelqu'un dans Aida (fr-par-25c) s'est interrogé sur la manière de gérer les vidéos qui enrichissent le texte, demandant si l'audio devait décrire les éléments visuels non couverts par l'article ([01:10:22](#01:10:22)). La question de la pertinence d'un média (vidéo, tweet, etc.) et de sa valeur pour la traduction audio a été soulevée ([01:12:42](#01:12:42)).

* **Stratégies de traduction des médias en audio**: Il a été proposé de traduire les médias en audio par description ou en intégrant des extraits audio de la vidéo elle-même, en se basant sur la pertinence du média par rapport au texte. Il a été mentionné que Gemini peut aider à définir le segment audio pertinent à extraire et assembler ([01:13:28](#01:13:28)).

* **Problèmes techniques et qualité de la voix actuelle**: quelqu'un dans Aida (fr-par-25c) a fait part de problèmes techniques rencontrés avec le système actuel (ETX), notamment des coupures, des erreurs de longueur d'audio et une voix au rendu jugé "un petit peu robotique" ([01:15:36](#01:15:36)). Il a été précisé que seul le titre, le chapeau et le corps des articles sont traités, et que la photo, la légende et les blocs de relance sont exclus ([01:16:32](#01:16:32)).

* **Gestion des limites de génération et de l'assemblage audio**: Il y a une limite de taille pour l'audio généré, nécessitant de découper l'article en plusieurs segments si nécessaire. Pour une production efficace, les segments générés (même s'ils proviennent du même locuteur) doivent être assemblés et gérés au niveau du code pour définir les délais entre les passages ([01:17:29](#01:17:29)) ([01:26:09](#01:26:09)).

* **Changement de voix pour le titre et le chapeau**: L'idée d'utiliser une voix différente pour le titre et le chapeau a été jugée pertinente, surtout pour les éditoriaux, afin de distinguer l'auteur ou l'interprétation du texte ([01:25:02](#01:25:02)). Pour l'identification des journalistes (signature), il est possible de le faire de manière déterministe ou de laisser Gemini l'intégrer en utilisant un modèle d'écriture ([01:24:06](#01:24:06)).

* **Exploitation des données utilisateur et de la personnalisation**: L'importance de l'AB testing sur les voix et les clics a été soulignée pour voir ce qui fonctionne en se basant sur la durée d'écoute plutôt que les clics ([01:28:27](#01:28:27)). Il a été suggéré de créer des radios de nouvelles basées sur des flux RSS pour enchaîner les lectures ([01:29:42](#01:29:42)).

* **Potentiel de nouveaux produits audio et recommandation**: La création d'un "podcast podcastisé" des articles sauvegardés et l'intégration de recommandations personnalisées (similaires à celles faites par Spotify) ont été envisagées ([01:30:32](#01:30:32)) ([01:33:39](#01:33:39)). Les données utilisateur (GA4 ou Piano) doivent être exploitées pour alimenter la recommandation ([01:35:02](#01:35:02)).

* **Intégration du fond sonore et de la musique d'ambiance**: L'ajout d'un fond sonore a été discuté; bien que Gemini ne gère pas directement le mixage texte/musique (une composition à faire par l'utilisateur ou avec une API externe comme Iliria, actuellement limitée) ([01:39:12](#01:39:12)). Il a été noté que la prochaine version d'Iliria pourrait permettre de générer un habillage pertinent à partir d'un prompt dérivé du segment audio ([01:41:03](#01:41:03)).

* **Personnalisation de la lecture par la température**: La "température" peut être utilisée comme un paramètre pour donner plus de liberté au modèle d'utiliser le contenu et d'adapter sa lecture de manière plus contextuelle ([01:49:08](#01:49:08)). Une température élevée augmente la liberté interprétative du modèle par rapport au contenu ([01:50:40](#01:50:40)).

* **Contrôle du contenu audio et accessibilité**: Il a été réaffirmé que l'utilisateur détermine quel contenu textuel est envoyé pour la génération audio ([01:51:57](#01:51:57)). Pour les médias, il est possible de demander à Gemini de générer une description ("captioning") dans le ton souhaité ([01:53:23](#01:53:23)).

* **Performance et comparaison des modèles**: En comparant les outils, quelqu'un dans Aida (fr-par-25c) a mentionné que "antigravity" était lent par rapport à "cursor" ([01:56:25](#01:56:25)). Les modèles "flash" ont été notés comme très rapides et moins chers, bien que de moindre qualité ([01:47:44](#01:47:44)) ([01:57:20](#01:57:20)).

* **Fonctionnement des puces (bullet points) dans le texte**: quelqu'un dans Aida (fr-par-25c) a confirmé que le fonctionnement des différentes puces ou "bullet points" est plutôt efficace au sein d'un texte. Ils ont noté qu'ils devaient vérifier le placement des puces en début ou en fin de phrase, comme avant les guillemets, pour s'assurer que l'interprétation est correcte ([01:58:13](#01:58:13)).

* **Processus de génération et extraction**: Le processus a rencontré un problème où, après avoir lancé l'extraction et la génération, il est revenu à l'étape d'extraction. Quelqu'un dans Aida (fr-par-25c) a mentionné qu'ils vérifiaient si c'était dû à une modification ou à un problème de surveillance ("watch") ([01:58:13](#01:58:13)).

* **Entraînement de voix personnalisée sur Gini TTS**: L'entraînement de voix personnalisée n'est pas basé sur CH ou Gini 2.5 Pro, mais est une fonctionnalité existante sur Gini TTS. Ce processus nécessite environ 30 secondes d'audio (des fragments), durant lesquelles un texte spécifique est lu pour capturer l'empreinte vocale et toutes les caractéristiques de la voix ([01:58:13](#01:58:13)).

* **Disponibilité de l'entraînement de voix personnalisée**: L'entraînement de la voix est actuellement en "private preview" (prévisualisation privée) et n'est pas accessible à tout le monde. Quelqu'un dans Aida (fr-par-25c) a indiqué qu'ils devront monter un dossier si quelqu'un souhaite utiliser cette fonctionnalité ([01:58:13](#01:58:13)).

*Nous vous conseillons d'examiner les notes de Gemini pour vérifier qu'elles ne contiennent pas d'erreur. [Profitez de nos astuces et découvrez comment Gemini prend des notes](https://support.google.com/meet/answer/14754931)*

*Merci de nous donner votre avis sur l'utilisation de Gemini pour la prise de notes en répondant à [cette courte enquête](https://google.qualtrics.com/jfe/form/SV_9vK3UZEaIQKKE7A?confid=FD6IHjSTpRB5Gzdw1KGCDxIcOBABMgUIigIgABgDCA&detailid=standard&screenshot=false).*

# 📖 Transcription

16 févr. 2026

## Figaro \- workshop \- Transcription

### 00:00:00 {#00:00:00}

   
**Aida (fr-par-25c):** que les chaises que les chaises vraiment les écrans on est pas mal les écrans on est bon franchement ça la caméra est un peu plus discrète on va dire s'il y a un truc sur pas trop mauvais c'est sur les écrans défaut du reste on est bon sur plein d'autres trucs du coup c'est ça après ce mid c'est clair prévu est loin. Donc si je me trompe pas, je avais prévu presse technique et démo, c'est ça ? Ouais, c'est ça. Et après vous faites l'atelier. Ouais, exactement. Moi, je vous quitte à l'atelier. OK. On va voir en fonction de l'organisation. Ouais. Euh qui manque juste Paul ou invit Guestou ça vous avez le code ou Ah non, j'ai pas de code.  
   
 

### 00:01:12 {#00:01:12}

   
**Aida (fr-par-25c):** C'est souvent alors bah on a un peu galéré là pour le coup. Alors le voici soit flash soit parfait merci beaucoup séance pas affiché c'est ça merci souvent je me suis pas connecté Ouais. Julien l'objectif du enfin je dis Julien c'est pas que pour Julien l'objectif du meeting aujourd'hui c'est quoi ? de se recaler sur les Alors, l'objectif l'objectif d'aujourd'hui, c'est c'est avant tout en fait qu'à la fin de la séance en fait, vous repartiez avec une solution qui soit fonctionnelle et sur lequel en fait vous essayz une compréhension de comment fonctionne la pay, de ce que vous allez pouvoir en fait travailler avec vous en interne parce qu'il y a énormément de configuration enfin de de choix en fait de possibilités de différentes voies, de manière de modulation, de manière dont vous allez vous prendre en fait le l'information que vous avez en source et que vous allez la transformer en pour l'animer à deux voix, pour aller construire quelque chose qui soit en fait dans le ton qui vous intéresse.  
   
 

### 00:03:18 {#00:03:18}

   
**Aida (fr-par-25c):** Moi, j'ai fait un certain nombre d'expérimentation que je vais vous présenter et l'idée c'est que en fait soyez capable de les reproduire chez vous, que vous compreniez la pays et vous posiez toutes vos questions et on sation de euh des mains sur le clavier et puis euh et de de génération et que vous vous disiez un petit peu ce que vous souhaitez euh les les points sur lesquels en fait vous avez besoin d'aide, les points sur lequels en fait c'est très clair et et vous avez juste besoin de retour d'utilisateur parce que peut-être que ça va être la manière dont vous allez vouloir fonctionner. Voilà. OK. Est-ce que c'est ça vous va comme agenda ? Est-ce qu'il y a des choses que vous vouliez rajouter ? Moi je dis bien une chose. Moi ce que j'aimerais c'est plutôt comprendre le timing de ce projet, comment il s'inscrit cette année et puis sur le sujet plus précisément, est-ce que vous avez des critères de sexués ?  
   
 

### 00:04:13 {#00:04:13}

   
**Aida (fr-par-25c):** Est-ce que c'est vous allez vous mettre autour d'une table écouter euh 3 15 50 générations et vous dire c'est plutôt ce modèle et et comment vous allez un peu un peu qualifier euh pour pouvoir faire un choix euh à viser pour pour le Figaro. Donc un peu le timing projet et puis c'est quoi vos critères de succès pour faire un choix sur cette techn c'est vous les Alors de mon côté premièrement c'est déjà la qualité aujourd'hui on a une voie un petit peu roboutique donc c'est voir déjà l'amélioration en terme de voix donc euh aussi cette alternance peut-être si on va entre par exemple si on est sur un article éditorial on a pas mal de citations donc c'est bien d'avoir aussi deux intervenants euh dans les gouttes euh aussi euh par rapport à la bibliothèque de voix. Donc je sais pas si c'est est-ce que pour un journal, est-ce qu'il y a des voix spécifiques pour euh pour mettre un temps plutôt euh sur la partie news politique, plutôt d'autres voix sur la partie euh donc est-ce que c'est un paramétrage qu'on va le faire une fois pour toutes pour tous les articles ou bien on peut segmenter sur différentes rubriques et différentes catégories euh voilà après tout le reste sur le player en lui-même et tout ça donc euh c'est pas les critères euh très important d'avoir par exemple les parce que ça c'est un  
   
 

### 00:05:40 {#00:05:40}

   
**Aida (fr-par-25c):** peu euh on peut le faire aussi de notre côté ou euh mais en terme de et surtout faire attention de notre côté sur des articles un petit peu où il y a par exemple des des mots techniques de mot en l'anglais pour voir comment la prononciation et c'est ça. Il y a beaucoup aussi euh de providers qui proposent des dictionnaires de prononciation ou des dictionnaires des dictionnaires en général et voir si on si on peut avoir quelque chose de similaire aussi sur cette partie-là, notamment sur des personnalités publiques où parfois on sait que certaines voix il respectent enfin ne respectent pas forcément la bonne prononciation d'un bon nom. On sait que ça va être assez important aussi cette partie-là. OK. Et donc ces éléments là vous les avez plutôt en tête ou vous les avez recensés quelque part ? pour pouvoir scorer. Ça c'est ma deuxème question. Et à un moment donné euh parce que vous faites partie de l'équipe tech, est-ce qu'il y a des vous avez des métiers en face qui vont venir euh un peu revalider ?  
   
 

### 00:06:40

   
**Aida (fr-par-25c):** Il a la partie métier qui est là à part le partie métier, la partie tech dans les équipes tech. Non, OK, donc toi tu représentes la partie métier qui va valider ça avant de faire un go live par exemple quoi. Ouais, on a une grille en tout cas lorsqu'on a essayé de préparer euh l'appel d'offre et tout. Donc on a une grille sur nos critères à nous. Qu'est-ce qu'on veut avoir sur tout ce qui est la partie tech aussi ? Ce qui est important c'est de pouvoir aussi avoir peut-être la partie euh monétisation aussi à voir comment on va euh comment on va l'intégrer euh monétisation comment vous vous allez OK. OK. qui concerne pas directement en tout cas là sur oui bah oui que propos je pense pas que pour le coup qu'il y a d'autres enfin il y a des éiteur qui propose des trucs là en main tu vois donc là il propose et la génération et le player et donc franchement avec serveur OK alors ce que je disais c'est que sur la partie ad server euh donc c'est quelque chose queon propose mais qui est pas couvert en fait par nous  
   
 

### 00:07:43 {#00:07:43}

   
**Aida (fr-par-25c):** équipe équipe Google Cloud Euh vous avez en fait certainement des contacts côté demander à Juliet ce que tu dis c'est un player qu'on propose nous aussi. C'est ça. C'est c'est pas pas forcément la partie player qui vous intéresse particulièrement. C'est surtout la partie ads manager dans le fait de pouvoir intégrer en fait les le bon contenu de publicitaire au bon moment pour les bonnes personnes dans le bon contexte. Voilà c'est c'est cet aspect là. demander à Juliette, on a des solutions aujourd'hui. Nous de toute façon, on utilise gamme déjà. Donc euh exactement donc c'est pour ça que le sujet sera si jamais on va vers un player qu'on fait nous-même, alors euh si on peut éviter à la régie de enfin si on peut pluguer ça dans ce qu'il disent déjà, c'est canon. Je corrige hein, mais je crois que c'est un peu d'idée quoi.  
   
 

### 00:08:30

   
**Aida (fr-par-25c):** Dans tous les cas, c'est une possibilité. Ouais. Là, il faudra qu'on fasse parce que nous on s'occupe pas de la serveur. C'est vraiment côté côté RI Media Figaro. Donc là, on discuter avec eux. C'est ça. C'est qu'on avait dit, c'est qu'en fait on excluait cette partie-là de de notre discussion pour le moment euh parce que en fait c'était c'est un sujet en fait qui allait pouvoir arriver en top. Euh vous utilisez déjà les solutions, vous utilisez déjà tout ça. Donc euh on va en fait ça va être intéressant de de rester dans l'écosystème mais dans tous les cas en fait c'est une discussion que vous pourrez avoir après. Oui. Oui. Oui. Puis c'est pas un critère de réussite du projet.  
   
 

### 00:09:06 {#00:09:06}

   
**Aida (fr-par-25c):** Enfin pour nous. OK. C'est du VUS là. Moi, il me semble que Q1, le but c'était euh euh benchmarker toutes les solutions, se faire un avis sur la enfin voilà qu'est-ce qui ressort dans les fameux critères que que vous avez déjà en tête. Euh et une notion de coût aussi qu'on puisse mettre ça en face d'un coup quand même, je pense. D'accord. Et une estimation que vous avez été partagée par Ouais, il y avait une estimation. Comment trop peu cher j'imagine euh cher ? Ouais. Moi je dis trop peu cher. Peut multiplier. On peut trouver un multiplicateur pour Fero. Si c'est trop peu cher. Non non, j'ai pas du tout en tête les enf j'ai en tête l'estimation, j'ai pas du tout en tête le les autres coups.  
   
 

### 00:09:50 {#00:09:50}

   
**Aida (fr-par-25c):** Donc du coup pas de OK merci beaucoup. Mais je pense l'idée en tout cas Q1 c'est quand même de se faire un avis sur les technos notamment parce que parce que ce qu'on a pas apprécié c'est qu'il y a 3 ans. Ouais. Il y a 3 ans. On avait déjà ou deux ou tr on a déjà testé des solutions Google comme ça complètement changé depuis. Voilà, on n'est pas du tout en sait ce que vous avez énormément évolué mais on n pas testé je crois récemment. Ouis. À l'époque, les parties les plus intéressantes étaient encore expérimentales. Ouais. Oui. Les meilleurs modèles étaient en anglais, pas forcément français. Ouais. Oui, tout à fait.  
   
 

### 00:10:27 {#00:10:27}

   
**Aida (fr-par-25c):** Et c'est encore évolué encore l'année dernière. Donc c'est ça va très très vite et en fait l'intérêt c'est que euh vous puissiez avoir accès en fait à des outils qui sont en évolution et qui sont en fait toujours en fait dans le bon sens et qui vont vont continuer à évoluer. Euh là, j'ai vu des previews là des prochains modèles text to switch euh donc ils vont arriver. Je peux pas vous dire quand, mais on passe encore à une étape supplémentaire euh qui a pour enfin je vais pas spoiler la présentation mais en fait euh il y a beaucoup de choses qui qui sont en train d'arriver, qui sont qui sont quasiment prêts, certaines qui sont privés de preview qui vont être en fait le clonage de voir qui est euh le fait de pouvoir en fait avoir sa son son sa voix qui est promptable dans le sens où en fait on déclare quelle est l'intention plutôt que de dire je vais définir on va dire le de manière très précise la prononciation le SSML le si le ça là en fait c'est expliquer quelle est l'intention que l'on va qu'on met sur chaque partie est-ce que en fait on veut être explicatif est-ce que on veut être Ah oui donc ça a beaucoup évolué par rapport à ce qu'on a testé c'était du SSML et clonage de voix je crois était relativement cher c un long process était long et la partie SSML  
   
 

### 00:12:04 {#00:12:04}

   
**Aida (fr-par-25c):** était aussi pas toujours en phase avec la doc ça marchait pas forcément toujours comme c'était assez en c'était dur à implémenter je pense. dur à implémenter je pense si on voulait gérer plein de cas h là où la partie prompting aujourd'hui quand on déclare des instructions si elles sont complètes naturelles exactement et en fait et en fait ce que je vais vous présenter aujourd'hui c'est en fait c'est c'est pas en fait un modèle qui est tout seul dans son coin en fait un un workflow qui passe de j'ai j'ai de la donnée source brute à j'ai de la donnée structurée donc avec différence les différents On voit les les différentes topologies. Est-ce que je fais je vais marquer une pause dramatique ? Est-ce que je vais en fait être grave dans mon ? Est-ce que je vais être être souriant ? Est-ce que je vais être être très sérieux ? Enfin, est-ce que je vais rire ?  
   
 

### 00:13:01 {#00:13:01}

   
**Aida (fr-par-25c):** Je sais pas si ça peut arriver dans vos cas, mais je suis pas sûr. Euh enfin voilà, il y a plein de possibilités d'intégrer en fait des sons mais que en fait on va c'est pas possible de vous demander en fait d'intégrer ça ça tout seul. C'est dans le workflow que en fait on met ça en place en fait qui va être alimenté par d'autres modèles géminiques qui vont faire les conversion qui vont en fait permettre de s'adapter en fait pour créer en fait un résultat final qui est pertinent qui intègre en fait même de la musique si vous vous le souhaitez parce que on a une gamme en fait de solutions qui aujourd'hui permettent en fait de fournir une solution vraiment complète et c'est là aujourd'hui, c'est pas un modèle tout seul dans son coin. Euh ça c'est bien, mais ce n'est qu'un qu'un tout petit bout en fait de ça serait regardé en fait vraiment sur un tout petit petit cas. Alors que euh là le l'idée c'est de partir en fait de vos données brutes peut-être qu'ils sont dans BQU déjà.  
   
 

### 00:14:08

   
**Aida (fr-par-25c):** Non, pas encore. Non non, je une perche. Voilà, sur lequel en fait on va pouvoir enf où est-ce qu'elles sont, mais en fait on va pouvoir les les convertir, les les transformer et et ainsi arriver à un produit final, un asset euh web, MP3 euh bineural. Enfin, on peut peut aller on peut aller très très loin dans ce dans ce que dans le résultat et la qualité que l'on veut avoir en terme de en terme de résultat. Et moi, je suis je suis là pour vous accompagner sur tout le process. OK. Nickel. OK. Donc c'est pour ça qu'en fait avant en fait de vous de focaliser sur Gini TTS, je voulais juste faire très très rapidement une overview de de tous les modèles dans la famille. gène gène média euh avant en fait de plonger sur le sur Gin TTS. Hop.  
   
 

### 00:15:12 {#00:15:12}

   
**Aida (fr-par-25c):** Donc euh voilà vous connaissez en fait euh ça fait très longtemps qu'on fait qu'on fait de l'I à l'échelle. Donc on sait faire euh nano bananana génération de génération d'images VO euh 3.1 génération de vidéo euh donc qui permet en fait de de générer de la voix et générer en fait du de la vidéo en même temps. Donc les deux en fait qui sont qui sont qui peuvent être assemblés et qui sont en fait qui vont se conc concorder. On fait tomber une on fait tomber en fait un ballon, on va entendre le le bruit du ballon qui va rebondir et qui est en ligne avec le avec le avec le son. Donc une manière en fait de d'avoir encore plus de contrôle sur le sur l'audio, c'est d'avoir la vidéo qui va avec. C'est c'est pas le même coup non plus, mais c'est c'est un un level, c'est le le l'étape d'après si vous voulez. Et donc pour tout ça en fait, on a une on a toute une plateforme euh donc de la sécurité, de l'infra, la data analytique, les tous les tous les modèles dont je vais je vais parler juste après.  
   
 

### 00:16:28

   
**Aida (fr-par-25c):** euh tout ce qui est gestion de protocoles de plateformes sur lequel on va très rapidement euh sauter. Et puis après tout ce qui est agent packagé, Géini Enterprise, on a beaucoup beaucoup parlé ce midi. Tout ce qui est recherche également, on a de la recherche sur étagère et je l'ai fait avec certains de vos confrères en fait, mettre en place en fait des solutions de recherche sur les articles, sur les images, les photos euh articles de presse, sur les des PDF, des de journaux pour pouvoir faire de la documentation ou même directement sur le site pour les utilisateurs. que c'est donc il y a vraiment en fait une palette de d'outils euh qui est qui est accessible et après tout ce qui est en fait centre de contact, je pense que je suis pas sûr ça vous je sais pas si vous avez un centre de contact chez vous. Oui, on a un service client. Service client. Euh donc on a une solution qui permet en fait de faire de la de l'aide à la résolution de ticket, de la formation de ça c'est c'est très efficace et et en fait c'est une solution SAS qui est qui est assez simple à mettre en place.  
   
 

### 00:17:43 {#00:17:43}

   
**Aida (fr-par-25c):** Donc voilà. Donc c'est donc sur l'image sur la génération d'images en fait, on voit qu'on est même capable de faire de de générer des textes qui sont qui sont cohérents et pertinents pour pouvoir en fait euh avoir le les résultats qui sont qui sont qui sont propres, qui sont affichés, qui sont grandés sur du texte sur du texte qui viendrait de recherche externe, c'estàd que euh dire que en fait afficher en fait cette image là, cette image là qui a été générée avec Nano Banana, ça vient ça vient en fait de de du texte d'entrée, mais aussi en fait d'aller rechercher de l'information sur internet pour confirmer en fait comment se formulent les différents les différents noms, comment ça se les typologie ou quoi que ce soit. Donc ça, on peut mixer en fait des choses ensemble et et lorsqu'en fait vous géini en fait vous pouvez toujours vous dire je peux le grander sur donc le grand c'est vraiment l'ancrer sur des données qui viennent d'internet ou ou le le cranter sur les ces données à soi qui sont dans dans mon environnement.  
   
 

### 00:19:01

   
**Aida (fr-par-25c):** Donc ma base de recherche que je j'expose à mes utilisateurs, elle peut me servir aussi en interne pour euh pour ancrer mes données et que m'assurer que lorsqu'en fait je fais une génération, bah ma génération, elle est elle s'appuie sur des données qui sont qui sont déjà en fait euh validées et vérifiées, programmé, c'est-à-dire si je prends l'exemple de la première photo, dire à chaque fin de grand prix, il récupère directement les résultats. Et moi en tant que journaliste, je trouve directement dans ma bibliothèque les images que Oui. En fait, ça va ce qui ce qui va se faire, c'est que de chaque grand prix euh au lieu d'avoir d'avoir en fait à les générer en fait dire "Bon bah voilà, il y a cette il y a il y a cette image là, cette image là, cette image là, ça il va le voir, il va le trouver dans votre bibliothèque. Donc il va l'intégrer en fait à l'image en fait. Enfin, tu on lui dit qu' qu'on veut voir le podium et donc cette image là, on peut la faire générer intégralement.  
   
 

### 00:20:03

   
**Aida (fr-par-25c):** La seule chose que qui va savoir qui va pas savoir, c'est qui est qui est le gagnant, qui les noms les noms du dessous. Euh donc on va avoir en fait les différentes informations de base, mais tout le reste après en fait tout le euh on va dire lui dire quel quel type de couleur on veut mettre ou ce genre de choses, mais que des informations relativement vagues pour aller créer systématiquement une image qui est qui est très qui est très bornée dans dans ce que l'on veut avoir et qui est toujours différente. Donc euh voilà. Euh voilà, ça c'est un autre exemple sur la partie image. Euh je donne toutes ces images là en fait toutes ces images là en fait en entrée. Je lui dis en fait que je veux en fait habiller la personne dans ce ce contexte là avec un chien et cetera et pou je vais avoir en fait cette image qui va qui va arriver. Le voice son de génération. Je vais hop là lancer.  
   
 

### 00:21:07 {#00:21:07}

   
**Présentation de Julien Miquel:** Hello. Is anybody here? What's going on?  
**Aida (fr-par-25c):** Vous az entendu le le son des pas ? Ouais, c'est donc ça c'est le même modèle. Euh le c'est le même modèle en fait que auquel vous allez euh avoir accès pour générer que de l'audio. Là, ça gère de l'audio et de la vidéo. Donc c'est en ça que ça dit aujourd'hui on se aujourd'hui on pense que à l'audio parce que c'est le sujet mais en fait si on va un peu plus loin en fait on peut dire pour aller générer en fait de la vidéo sur des sur des sur des séquences de ce type là qui soient auditivement pertinentes et visuellement pertinente. Donc voilà. Donc en fait en terme de modèle, on va avoir on a des modèles qui sont accessibles via la PI, donc génération d'images, génération en fait de génération et modification d'images. Chirp, c'est notre ancien modèle de génération d'audio qui a été remplacé par JMI manière voilà un level au-dessus encore.  
   
 

### 00:22:26

   
**Aida (fr-par-25c):** L'IRIA, c'est notre modèle pour générer en fait de euh de la musique. Donc musique, on va dire aujourd'hui relativement simple. Là, la version que l'on a aujourd'hui, elle est elle est bien. Elle est bien, mais on n'est pas sur un sono ou quoi que ce soit. On est on est juste bien bien. Je je vais pas dire rentrer plus là-dessus. Ça ça suffit pour entre guillemets pour pour euh se dire que on ça habille ça habille une écoute pas avoir quelque chose euh juste brut mais la version d'après, je sais pas s'ils vont la mettre tout de suite en ligne tellement elle est bien. C'est incroyable. C'est donc voilà. Après, on a des use cas, on a des en fait tous ces modèles là, ils permettent exactement ce que j'ai dit, c'est ils peuvent permettre en fait de créer des workflow, des workflow en fait pour aller faire virtual trion.  
   
 

### 00:23:21

   
**Aida (fr-par-25c):** C'est euh vous avez vu la la personne juste avant a dit "Habille-moi avec telle chose". Euh mais moi en génère en fait une cinématique à partir de trois trois images. Euh ça me génère une cinématique euh permet enfin voilà, je vais je vais pas rentrer plus là-dedans. Et euh et ce qui est intéressant c'est que comme tout ça c'est que de la PI, c'est intégration avec vos systèmes euh manière hyper simple. Je sais pas si vous l'avez vu là ces deux ces deux euh petites vidéos. Tiens, elle est pas euh Vous les avez vu ou pas ? Non non non. Je je vous les  
**Présentation de Julien Miquel:** Grâce aux nouvelles catégories vinted,  
**Aida (fr-par-25c):** passe.  
**Présentation de Julien Miquel:** vous pouvez vendre encore plus d'article. Vous n'utilisez pas, vendez-le.  
**Aida (fr-par-25c):** Je me je pose ça parce que j'ai pas mis le contexte.  
   
 

### 00:24:19

   
**Aida (fr-par-25c):** Cette vidéo là a été générée 100 % paria 100 % et elle a été passée au super ball de l'année dernière avec un vieux modèle. C'est ça que ça veut dire et elle était faite pour 2000 dollars. Le le coût de le coût d'en fait de de la mettre au Super Ball, c'est des c'est des millions et en terme d'impact c'est absolument  
**Présentation de Julien Miquel:** Put their money on.  
**Aida (fr-par-25c):** incroyable.  
**Présentation de Julien Miquel:** I'm all in on OKC. Indiana got that dog in him. Will egg prices go up this month? I think we'll hit $20. How many hurricanes do you think we'll have this year? Let you legally trade on anything anywhere in the US. Ok.  
**Aida (fr-par-25c):** précisé que c'était de l'IA quelque part hein. Ils avaient précisé quelque part que c'était fait 100 % il a ou c'était Oui.  
   
 

### 00:25:20

   
**Aida (fr-par-25c):** Oui. Non, je dire là dans parce que là moi je l'ai vu nulle part. Euh ils ont sûrement fait de la com pour Oui, ils ont fait de la com autour. Quand tu regardais le spot, tu tu avais nulle part l'info. Euh c'est vrai, c'est vrai. On a on a aussi celle celle-là qui est qui est aussi incroyable que je change d'écran.  
**Présentation de Julien Miquel:** This is Tom. Work has been weird lately. He's going to fly the coup and fast. Luckily, AI mode and Google search can help him hatch a plan. It's got to be quick and it's got to be Yeah, that should do it. Few things were getting dicey there for a moment, but now everything's gravy. Plenty a quick get.  
**Aida (fr-par-25c):** Bon voilà, donc vous avez compris euh on a ça ça s'excite juste avec la vidéo. Euh la vidéo, il y a toujours de l'audio et de l'image des images animées.  
   
 

### 00:26:37

   
**Aida (fr-par-25c):** Donc en fait, on est vraiment dans ce système là. Donc voilà. Donc vous avez compris en fait on a de l'image, de la vidéo et du speech. Aujourd'hui, je vais vous parler que de la partie Gini TTS euh parce que c'est le modèle le plus avancé et qui a le meilleur rendu. Je vous parlerai pas de CHRP 3 HD qui est notre vieux modèle entre guillemets qui qui est qui est qui est suffisamment qui est bien mais en fait qui est j'ai mis TTS et au-dessus donc je préfère vous présenter que ce qu'il y a le haut du panier et la partie debing debing c'est un c'est un produit qui est hyper particulier qui permet en fait de bah là aujourd'hui vous avez une vidéo en fait de d'une série qui est traduit intégralement dans une autre voie en avec la synchronisation labiale parce que on va modifier la vidéo pour pouvoir tout adapter. Donc c'est OK. Je sais pas si je pense je sais pas si je sais pas si c'est un un les doublures.  
   
 

### 00:27:49

   
**Aida (fr-par-25c):** Ou vous avez un métier là. Et c'est un c'est un cas d'utilisation chez vous ou pas du tout ? On s'était vraiment amusé à faire dubbing sur des émissions de du Figaro où on s'était dit bah tiens si un jour on veut les transformer en anglais ou quoi que ce soit et tu avais la voix de Trard qui parlait anglais et qui gardait exactement le même ton la même voix et c'était plutôt bien fait. Et ça vous l'avez fait avec qui aujourd'hui ? L'avait fait avec Eleven Labs à l'époque. Ça redate il y a 1 an et demi 2 ans d'accord. Donc voilà donc je vais je vais pas non plus aller euh aller trop loin là-dessus. Euh je vous enverrai les slides si vous si ça vous intéresse en fait sur la partie euh la partie vidéo euh vidéo euh voir un petit peu ce que ce que l'on peut faire.  
   
 

### 00:28:38 {#00:28:38}

   
**Aida (fr-par-25c):** Et ce qui est intéressant en fait, c'est surtout c'est surtout en fait cette premier niveau de compréhension euh que je voulais vous vous donner, c'est que en fait Gini TTS, c'est 80 langues. C'est c'est en fait une capacité à on va dire à intégrer en fait des du style contrôle on va dire juste par des mots clés sarcastique giggle whisper. Donc on va avoir en fait on va avoir en fait le prompt euh du euh global et on va avoir en fait euh les des informations qui vont être intégrées dans le texte dans le texte qui va être qui va être déclamé. C'estàd qu'en fait, on va pouvoir ajouter donc euh en plus du ton général des changements en fait de rythme euh directement. Et on a la possibilité aussi d'avoir d'avoir on va dire un double dialogue donc avec euh deux speakers. Donc on va choisir les deux voies et on va choisir en fait le les instructions pour chacune des voix. et et évidemment, on va pouvoir intégrer en fait le les mêmes les mêmes signaux euh dans le texte pour pouvoir en fait allez changer la manière dont don fait l'interaction.  
   
 

### 00:30:10 {#00:30:10}

   
**Aida (fr-par-25c):** Comment tu détermines ça justement le ton ? À quel moment tu à quel moment on arrive à nous à dire que sur tel texte à tel moment il faut tel ton et surtout pas tel autre ton ? Et c'est quoi ? C'est sur à ce niveau-là. C'est toi qui le définit du coup ? Non mais moi je peux pas définir tu vois. à moins de reposser sur chaque article et dire celui-ci là céit une blague mais j'imagine que vous avez quelque chose qui permet de le détecter. Oui ben en fait c'est son flow en fait tu vas me dire que ça fait il y a pas d'erreur évidemment mais est-ce que enfin je veux dire j'aimerais bien comprendre comment ça marche pour essayer de mesurer la marge d'erreur et que quelque chose de très sérieux soit dit avec un ton pas du tout sérieux. Tout à fait. En fait euh ce qu'on va faire c'est ce que je vous propose de faire c'est d'utiliser en fait le texte d'origine qui est le texte suivant mais sans les sans les petite chose ici et de venir en fait prompter prompter en fait  
   
 

### 00:31:03 {#00:31:03}

   
**Aida (fr-par-25c):** en disant je veux intégrer tel type de signaux. Je veux je veux intégrer en fait du sarcasme, je veux intégrer en fait euh des rires, je vais intégrer en fait euh des pauses, quelque chose qui soit pertinent par rapport en fait bah à l'article, par rapport au contexte de la phrase, par rapport en fait à la catégorie parce que je vais pas avoir faire la même chose euh sur la catégorie people que sur la catégorie géopolitique. Euh on est on a des il y a des des points sur lesquels on peut pas se permettre de pas être sérieux. Donc euh autant pour la météo, on peut on peut avoir un énorme sourire et puis en fait mettre de de l'émotion de l'émotion positive quand il fait un grand soleil ou quand il y a la guerre. Je on va rester très très factuel et très posé. Et ça les modèles les modèles Géminis, on peut le en fait leur leur leur demander euh justement d'avoir cette approche thématisée euh pour être pour coller au ton en fait que vous que vous souhaitez.  
   
 

### 00:32:10 {#00:32:10}

   
**Aida (fr-par-25c):** Alors est-ce que c'est à nous Figaro de dire que pour le Figaro c'est comme ça qu'il faut faire sur tel type de contenu ? Ouais. On lui donne à manger des articles, on dit cela, on veut ce type de ton. En fait, moi je comprends que dans son workflow euh tu prends le texte brut, tu le passes dans NLM pour analyser, c'est ça si je comprend pour analyser la le contexte de l'article, en sortir ce que tu veux faire pour l'audio et après tu reprompes, il apprend, il apprend avec ce et tu repromptes avec le prompte d'avant, enfin avec le résultat du prom d'avant quoi, tu vois, je pense c'est ça l'idée générale. Donc c'est là que tu dis euh les contenus politiques. Bon nous on a parfois actuou un qui en Suisse c'est un fait divers mais bon c'est quand même dramatique. C'est souvent dramatique les fait chez nous.  
   
 

### 00:32:52

   
**Aida (fr-par-25c):** Mais oui oui on est on est d'accord c'est je pense mon il a pas grandchose de réjouissant. Non, mais il peut y avoir des choses très sérieuses mais qui peuvent être déclamé avec un ton un peu sarcastique ou ironique parce que je prends un exemple, un totaliste très à droite va se moquer euh d'un mec à gauche. Tu vois, c'est un sujet très sérieux. il va peut-être dire un truc très sérieux, genre un mec s'est fait tuer hier, mais parce que lui il a envie de se moquer et ça peut être même pas un journaliste, ça peut être une tribune et donc quelqu'un d'extérieur et tu vois c'est même pas le Figaro qui parle, c'est juste donne la parole à quelqu'un et et là c'est vrai que c'est compliqué de savoir est-ce que je dois aller sur le ton ou est-ce que ben non, on prend pas de risque du coup zéro ton sur tous les articles sérieux ce qui ce qui ce qui perd un peu en saveur évidemment mais enfin je je pense que vous avez vraiment déjà réfléchi à tout ça mais moi c'est des choses sur lesquelles je Je vais être assez attentif.  
   
 

### 00:33:45 {#00:33:45}

   
**Aida (fr-par-25c):** Bah en fait, c'est très simple hein. Le l'article, il va être il potentiellement il peut être très sérieux mais en fait entre guillemets se moquer et donc ça en fait on va le détecter. Enfin, on va demander au prompt justement de de détecter en fait cette cette intention et donc si l'intention et que ça fait partie des guidelines que vous autorisez, vous pouvez l'être très bien intégrer. Donc en fait, moi j'aurais tendance à dire que niveau 1 en fait on le passe sans sans intégrer en fait de de changement émotionnel trop fort et après en fait se s'autoriser des des changements un peu plus un peu plus audacieux mais qui vont générer une connexion avec votre auditoire qui est beaucoup plus forte aussi parce que c'est c'est ça en fait le but l'audio, c'est c'est d'avoir en un ressenti qui est beaucoup plus beaucoup plus fort que ce que en fait on va pouvoir on va pouvoir lire et en fait on va pas le pour de la même manière non plus. Mais c'est comme en fait ce ce type de ce type de contenu c'est pour une euh c'est pour des personnes qui sont beaucoup plus premium.  
   
 

### 00:35:03

   
**Aida (fr-par-25c):** Euh vous savez en fait quel est le profil de la personne. Euh potentiellement en fait se dire tiens, je vais avoir deux catégories de personnes. Je vais avoir ceux en fait qui qui veulent un petit peu du sarcasme et en fait d'un peu chercher des choses un peu plus plus fortes. Et il y a ceux qui vont pas du tout apprécier ce genre de choses et poten pourquoi pas faire plusieurs versions. C'est c'est des choses qui sont possibles. C'est vous qui choisissez ce que vous voulez faire. Nous, on vous donne accès à des outils qui permettent en fait de mettre en œuvre en fait vos idées. Et donc en fait, moi ce que je moi je suis là pour vous accompagner à vous dire qu'est-ce qui est possible et et comment comment on le réalise. Et après, c'est vous qui me dites jusqu'où vous voulez aller ? Quelles sont les choses qui vous vous trouvez intéressantes et les choses pour lesquelles vous dites non là ça c'est ça c'est la c'est c'est une c'est une frontière qu'on veut pas qu'on veut pas dépasser et et elle elle existe.  
   
 

### 00:36:12 {#00:36:12}

   
**Aida (fr-par-25c):** Elle existe. Elle est à un certain niveau en fonction des clients. Elle est pas au même niveau partout. Donc moi ça je vais je vous laisse en fait me dire quelle est cette frontière et comment est-ce qu'en fait on fait pour la pour la la respecter et pour le prendre en lui-même, est-ce qu'il y a un indice de confiance par rapport son analyse sur l'article ? parce qu'on peut se tremper parfois sur est-ce que il y a quelqu'un qui se moque de quelqu'un par exemple qu'on peut se dire si tu es sûr à plus que 90 % du coup on peut utiliser ce temps-là sinon par défaut on fait un temps posé notre Oui. C'estàd queen fait quand on va faire la génération on va lui donner une marge de confiance une marge de euh d'autonomie. Donc on peut très bien et donc on peut choisir en fait de d'augmenter ou de diminuer cette autonomie en fait de de génération. Donc que ça soit sur la partie textuelle sur lequel en fait on veut on veut pas changer un seul mot sur la partie sur la partie audio.  
   
 

### 00:37:22 {#00:37:22}

   
**Aida (fr-par-25c):** Euh on veut lui donner en fait possibilité de changer un ou deux mots parce que ça fait plus joli à l'oral ou est-ce qu'on veut être strict vraiment strict. C'est c'est votre choix. L'outil permet en fait de changer ce curseur et de d'avoir de générer plus d'émotions euh en en s'éloignant peut-être un petit peu du texte d'origine, pas énormément, mais qui peut en fait potentiellement euh avoir un peu plus d'autonomie. C'est vous qui allez tester, c'est vous qui allez le définir et c'est tout. Et donc du coup tout ce donc préprunting pour créer le format qu'on va nourrir modèle TTS, ça c'est à nous de de le mettre en place de mettre en place chaque étape ou c'est quelque chose que en fait moi j'ai aujourd'hui j'ai j'ai préparé un petit une petite démo euh que je vais vous proposer d'installer sur vos environnements qui est qui est très simple. C'est c'est quelques promptes et quelques quelques promptes, une interface Streamlit.  
   
 

### 00:38:25

   
**Aida (fr-par-25c):** Enfin voilà, vraiment des choses très simples pour euh choisir les langues, choisir les aller scrapper en fait le texte parce que vous m'avez donné une liste de textes mais j'ai pas accès au fait au text. Donc je l' j'ai fait du scrapping dessus. Euh voilà, des choses de ce type là. Évidemment, vous en interne vaah vous l'intégrerez ça à votre CMS et donc en fait vous allez avoir en fait des une information de euh il est où le chapeau là il y a uncart. Euh donc l'encar je vais le jouer par une autre voix. Je vais le jouer là. Je ce que je ce que je propose c'est en fait une démonstration de qu'est-ce que ça pourrait être en terme de de découpage et si je veux l'animer à une voix de voix. Si je veux faire une ben dashmark sur 10 voix, sur 100 voix, enfin euh voilà, c'est vous qui allez qui allez pouvoir tester.  
   
 

### 00:39:22

   
**Aida (fr-par-25c):** C'est clair là-dessus ? OK. Euh après au-delà des critères de choix là que tu nous as présenté tout à l'heure, ça va être aussi un point euh vu que c'est un sujet qui va très vite, même les usages de demain euh tu vois même nous des fois on les connaît pas, tu vois. Nous tous les jours, on on découvre des nouveaux usages euh sur nos sur nos produits par nos clients et et les IT ou les structures techno de de nos clients les découvrent aussi eux-mêmes, tu vois. Une fois qu'ils ont euh qu'ils ont donné Gémini euh je même pas à des agriculteurs pour pouvoir analyser des sujets de plantes, bah les agriculteurs, ils vont aller prendre des photos euh sur leurs produits pour détecter des des maladies ou des choses comme ça. Tu vois, il y a toujours ce ce côté usage qui qui change et et donc nous là où on va avoir un vrai point fort, c'est ça, c'est de nous dire c'est pas prêt à l'emploi, c'est pas un truc clic bouton, claque, c'est parti.  
   
 

### 00:40:27

   
**Aida (fr-par-25c):** Par contre, demain, vous allez pouvoir démarrer peut-être très simplement avec une seule voix. euh 6 mois plus tard vous dire "On a une voix pour la politique euh les faits divers, les machins et peut-être dans 1 an même sur la politique, on commence à faire des choses, tu vois, un peu plus un peu plus sophistiqué, toujours en restant sur la même plateforme." Donc voilà, c'est cette c'est cette dimension qu'il faut intégrer à un moment donné euh pour voir comment vous projetez sur ce sujet-là. ou vous avez pas de retour d'expérience d'autres médias avec cet outil sur l'audio. Euh j'ai j'ai des des clients qui ont qui ont fait des qui ont fait des des tests qui ont qui ont déployé des choses. Moi, j'ai pas été intégré directement à ces à ces expérimentations. Donc je veux pas je vais pas inventer quelque chose que j'ai pas fait. Euh je préfère en fait parler exactement des sujets que j'ai pu mettre en place.  
   
 

### 00:41:23

   
**Aida (fr-par-25c):** Euh moi, j'ai fait beaucoup beaucoup d'expérimentations là sur la dernière année sur ce produit-là parce que ça m'intéresse plus euh personnellement. Euh j'ai benchmark marqué tous les outils du marché. Enfin, c'est c'est vraiment un sujet que je que personnellement je j'adore. Donc euh je pense qu'en fait euh on a j'ai assez en fait de de background pour vous vous expliquer en fait le retour d'expérience euh voilà sur le sur la préparation de la donnée, sur la modification, quoi que ce soit. Et là sur ce sujet là, vous êtes pas en retard, on va dire et on va pas vous dire ça fait 5 ans que on fait qu'est-ce qu'est-ce que vous faites les gars ? Donc c'est c'est pas du tout le sujet soit sur des sujets de pur tress ou même de sujets de on va dire de de d'expérience client ou c'est des bottes qui qui reprennent la main entre l'année dernière et cette année. Voilà, on voit vraiment cette accélération sur les choses qui se mettent en place comme d'habitude plus d'abord chez nos copains anglo-saxon qui se posent moins moins de questions tout de suite mais voilà mais c'est mais vous êtes pas en retard quoi.  
   
 

### 00:42:37

   
**Aida (fr-par-25c):** Et dans la bibliothèque de soi, est-ce que il y a des voies étrangères ? Par exemple, nous on a le Figaro in English. Du coup, lorsqu'on lance un lecteur audio dans un article Le Figaro in English, donc euh est-ce que on peut directement basculer sur un prononciation ? En fait, vous vous allez pouvoir choisir le la la voix euh la voix et la langue que vous pouvez choisir. Donc c'est le le point, c'est qu'en fait il faut fournir en fait la le l'article traduit. Donc évidemment, on est dans le process, on peut très bien dire qu'on intègre en fait cette fonction de traduction euh enfin j'imagine que vous avez déjà en fait une fonction de traduction anglais des articles sont déjà en anglais. Donc oui, donc si en fait c'est pas pour faire du multioueur, du multi euh c'est le faire en anglais, en français, en espagnol et cetera. Non non, c'est source. Voilà.  
   
 

### 00:43:36

   
**Aida (fr-par-25c):** Aucun problème. Aucun problème pour ça. Euh sur la partie euh multi multilingue multi, c'est qu'est-ce que c'est que c'est plus comment dire c'est toujours un peu plus costaud. Qu'est-ce que ça ? Qu'est-ce que Ah multioixie en fait donc avec deux voix ? Oui. Ou multilingue. Multilangue bah multilangue en fait c'est juste un paramètre. C'est au final, je vais vous présenter en fait le peut-être le là ce qu'on peut voir ce qu'on peut voir là sur le fichier en fait le euh donc ça c'est E Studio. et studio, je trouve je trouve assez intéressant en fait en terme de de présentation mais ce que je veux ce qui est important de comprendre c'est que donc on a Ei Studio, on a Vertex AI, AI Studio c'est la version entre guillemets grand public mais l'interface je la trouvais intéressante qui permet en fait de montrer la source euh le le builder avec les différents speakers la partie possibilité de choisir les différents speakers audio et évidemment le  
   
 

### 00:45:04

   
**Aida (fr-par-25c):** modèle et d'avoir également tout ce qui est tout ce qui est settings euh et donc qui permettent en fait d'aller construire en fait cette interaction cette cette interaction que ça soit en français en anglais, c'est vous qui choisissez en fait ces ces différents différents paramètres. Euh, je vous partage partage en fait le petit c'est à peu près la même chose. C'est le c'est c'est le un petit outil vraiment sans prétention permet en fait de choisir en fait le les différents les différents articles. Donc là, ça va extraire en fait le texte le texte de manière très très simple pour pouvoir en fait le convertir en avec les différentes parties. Donc là, on a le premier speaker et donc on va pouvoir choisir modifier cette cette ce jeu jeu d'acteur entre speaker 1 speaker 2\. On va avoir aussi la possibilité de pouvoir définir le prompt par pour chaque speaker. Donc on va lui dire qu'en fait on parle français de France si on veut pas avoir des 98 ou des choses comme ça. C'est c'est anecdotite mais c'est je trouve que c'est c'est des points qui sont peuvent être c'est du détail qui est important en fait de de prendre en compte.  
   
 

### 00:46:39 {#00:46:39}

   
**Aida (fr-par-25c):** Donc voilà. Donc donc là c'est vraiment en fait on prend juste le le texte et après en fait on va ça va générer l'ensemble du script donc avec les différents différents speakers. Donc on va pouvoir après générer avec une voie unique. Donc en choisissant le modèle. Donc on a là en fait j'ai trois modèles sur lequel vous pouvez tester. Euh personnellement je recommande la version pro. Euh c'est celui qui aura le plus la voie la plus la plus propre. Euh plus on descend, moins c'est cher et plus ça va vite. Ça enfin voilà. Si si vous voulez en fait mettre des des articles avec en fonction de différents tiers de paiement ou quoi que ce soit, ça peut être une manière aussi de de le faire. Tu as fait un test ou pas là ? On a entendu quelque chose ou encore ?  
   
 

### 00:47:35

   
**Aida (fr-par-25c):** Non, pas encore. Il fait le teasing. Fait le teasing jusqu'au bout. Je fais le teasing jusqu'au bout. Ouais. Et euh et en fait euh euh je vais avoir en fait la possibilité de générer une voix unique, générer une double voie, générer en fait des comparaisons avec du euh du GTTS GTTS version gratuite hein. Euh euh que je crois que c'est ce que vous avez aujourd'hui. Euh c'est du TTS. Oui. Ouais. Voilà. Donc c'est voilà, c'est des choses basiques. Et ici en fait là c'est un benchmark qui va prendre très simplement en fait toutes les voix et qui va exécuter la première phrase pour vous faire entendre en fait ce que ça donne.  
   
 

### 00:48:16

   
**Présentation de Julien Miquel:** L'éditorial de Gaetan de Capel. Stratégie énergétique, il faut sanctuariser le nucléaire. L'éditorial de Gaetan de Capel. Stratégie énergétique, il faut sanctuariser le nucléaire. L'éditorial de Gaetante Capelle, stratégie énergétique, il faut sanctuariser le nucléaire.  
**Aida (fr-par-25c):** Voilà. Donc on en a on en a toute une liste euh qui vont euh qui vont s'exécuter.  
**Présentation de Julien Miquel:** L'éditorial de Gaitan de Capel.  
**Aida (fr-par-25c):** Le pro ça prend  
**Présentation de Julien Miquel:** Stratégie énergétique, il faut sanctuariser le nucléaire.  
**Aida (fr-par-25c):** Voilà. Donc on va pouvoir jouer un petit peu avec toutes toutes ces différentes toutes ces différentes voies et puis en fait on va pouvoir entre guillemets s'amuser à benchmarker en fait les différents résultats. C'est avant tout en fait pour pouvoir sélectionner une voie sur le et pour pouvoir se dire tiens je veux je veux une discussion à une voix de voix,  
**Présentation de Julien Miquel:** L'éditorial  
   
 

### 00:49:09

   
**Aida (fr-par-25c):** je vais utiliser cette voix làà je vais utiliser tel prompt système pour pouvoir lui donner cette intentionnalité là parce que c'est aussi important et donc moi en fait ce que je vais faire c'est vous apporter en fait toute la connaissance et la et la compréhension de comment utiliser la payer pour que en En fait, vous puissiez réaliser ce po  
**Présentation de Julien Miquel:** de Gaetan de Capelle. Stratégie énergétique, il faut sanctuariser le nucléaire. L'éditorial de Gaetan de Capel. Stratégie énergétique. Il faut sanctuariser le nucléaire.  
**Aida (fr-par-25c):** très haut route info ça. Good for news. Mais là, on est donc en fait toutes les sur toutes les voies, on a en fait on a il y a de la documentation. Donc ça explique ça explique les intentions que l'on peut avoir sur les différentes voies mais toutes ces voiesl elles peuvent être modifiables via en fait de l'intention. L'intention là, le prompt que j'ai mis au début, il est pas il est pas anodin en fait.  
   
 

### 00:50:23

   
**Aida (fr-par-25c):** il va avoir une vraie influence. Là, ce que j'ai mis ici, euh c'est vraiment en fait euh ça est vraiment une influence sur la manière dont dont en fait le texte est lu et et en fait c'est ce texte là, on pourrait même en fait le découper par morceau en disant cette partie là, je veux qu'elle soit lue comme ça, celle-là, je veux qu'elle soit lue comme ça. Et voilà, on va avoir ce tout ce découpage là. Donc voilà. Donc là, on a fait un peu l'overview. C'est maintenant à vous de travailler un petit peu. Euh je vais vous proposer d'aller vous connecter en fait sur euh sur la travailler sur le guitar. Bon ouais. Non mais merci beaucoup. C'était super intéressant. Comment vous trouvez les voix comme ça ?  
   
 

### 00:51:19

   
**Aida (fr-par-25c):** À part le fait de dire c'est une voix d'autorité. Non non, c'est bien. On entendu qu'une phrase he mais c'est c'est dommage. Euh ouais déjà ouais. Non, ce qui est intéressant enfin en tout cas pour moi, c'est euh tu vois, j'ai peut-être un peu sous-estimé moi cette partie retravaille du texte, mais probablement pas eux. Cette partie travaille du texte en amont de la génération et je me je me rends compte du coup mieux des capacités qu'on peut développer. Ben en fait, c'est des unte enfin succession de prte. Exactement. En fait, c'est c'est des capacités parce que vous avez des gens en tête, hein. Mais j'avoue que moi j'avais sous-estimé ça. En fait, c'est des c'est des capacités.  
   
 

### 00:51:55

   
**Aida (fr-par-25c):** Après, vous les utilisez ou vous les utilisez pas, vous demandez en fait à un modèle d'intégrer en fait ses ces modifications ou pas, c'est vous qui choisissez. Ouais, c'est vous qui permanent. Voilà. Je pas du tout français. Bon, messieurs, moi aussi je vous abandonne. Merci beaucoup. Merci. Merci à toi. Sortez pas d'ici tant que vous êtes pas en prod, c'est ça ? Vas-y, vas-y. En général, c'est comme ça qu'on fait. Allez, à la prochaine. À la prochaine. Bah oui, à la prochaine. Bonne à toutes.  
   
 

### 00:52:31 {#00:52:31}

   
**Aida (fr-par-25c):** Je vous propose d'aller sur donc mon monitub donc c'est donc Julien Michel Michel tout attaché et donc c'est le repository speech. Vous avez tous un VS code ou quelque chose de ce type là ? Je pense pas. Au pire, on va per de on va se mettre chacun sur un PC. quelque chose pour Oke. Il y a une clé à payer à renseigner. Alors en fait, il y a pas de clé à pay. Il faut juste se loguer enfin que vous ayez un un projet qui soit GCloud login H euh qui soit soit configuré et puis après juste donner le nom du projet que les API soient évidemment bien activés et puis voilà. OK. Donc en fait, on peut le faire comme ça, mais vous pouvez aussi vous connecter directement sur la console la console GCP et euh et que et tester tester en direct, hein.  
   
 

### 00:55:02

   
**Aida (fr-par-25c):** Le script p\*\*\*\*\*, c'est C'est ça. C'est l'interface qu'on peut avoir directement dans la console sur la partie euh vertex studio la partie G média. par nous deux, ils auront pas accès à OK. Tac. Ça c'est le Voilà. Donc ça c'est ça c'est en fait le le la manière de d'aller faire le requêtage. Donc on a soit un custom URL, soit vous choisir n'importe quel OK. Quel chose et là c'est le modèle qu'on choisit. OK. C'est le modèle qu'on choisit pour pouvoir générer faire l'extraction. l'extraction de la donnée en fonction en fait du modèle. Extraction.  
   
 

### 00:56:18

   
**Aida (fr-par-25c):** OK. Voilà. Peuter directement le le contenu. OK. Custom. OK. Alors sur la partie playground tout à gauche, en fait j'ai fait un espèce de petit playground. Ah ok. Euh on peut mettre notre système prompt et dire système prom et voilà. Et on peut mettre en fait les différents textes pour aller OK. pour aller construire ça directement. OK. Donc si par exemple texte ici je pas speaker speakup 2 ça va si on fait les paragraphes d'une manière et les titres d'une autre h explique comme Ah tac sur la sur la partie donc article to speech fallait dans le Ouais, il faut juste mettre le project ID.  
   
 

### 00:57:23

   
**Aida (fr-par-25c):** Donc ça c'est le project du Oui. de votre projet et euh ça c'est pas nécessaire en fait lui il est pas nécessaire en fait il y a deux modes. Il y a deux modes. Il y a un mode local et un mode dans lequel il y a on met les choses les données sur Firebase. OK. Euh ce qui va permettre en fait de se partager de la partie résultat en fait on voit les résultats de tout le monde et donc ça permet de comme il est ici euh dans la partie history bah de voir en fait euh tout ce qui a été généré et donc de pouvoir euh OK euh de pouvoir entre guillemets partager ses résultats. OK. Mais bon, c'est c'est des expérimentations que j'ai pu faire. Voilà, en local, c'est suffisant parce que là, il m'a suit un problème de module. J'avais fait un cristal require XT mais que il manque des trucs ça l'air bon.  
   
 

### 00:58:18

   
**Aida (fr-par-25c):** Et il manque streaml dans le streaml c'est juste à rajouter streaml dans le requirement. Je l'ai oublié. Il y est pas dans Non, il y est dans le je dans le requirement je crois. Ouais, il y est dans le requirement. Faut juste que tu fasses un V1 de Ah ouais, OK. du truc et après tu lances une une console V tu fais streaml Streamlit run article texte speech et après tu mets le app. OK. OK. Paramètres avancé. Mode strict. En fait, il les a mis là. OK. OK. constructeur instruction de style l'éditorial de Gaetan de Capel stratégie énergétique il faut sanctuariser le nucléaire la grande vertu de cette nouvelle programmation puriannuelle de l'énergie est de remplacer ce projet qui prévoyait la disparition de 14 des 57 réacteurs nucléaires existants en offrande à la gauche écologiste.  
   
 

### 00:59:20 {#00:59:20}

   
**Aida (fr-par-25c):** Ce qui devait arriver est arrivé. Le gouvernement a présenté ce lundi de nouveaux chiffrages pour la programmation pluriannuelle de l'énergie PPE. le document stratégique qui fixe les orientations de la politique énergétique de la France. que le V1 je me souviens plus j'avais source en fait de Ah oui c un source en fait de de ton V1 activate et puis voilà mais parce que le mais est-ce que je l'ai pas encore créé là le V ah mais je plus c'est la commande c'était Python 3 V ouais c'est c'est et faut faut être dans le article tout speech ou dans le non la racine en fait tu t'en Ouais et après tu fais source alors j'ai une erreur tu fais source et on va Ah il il l'a pas créé ouais non c'est ça canop je Alors c ti En même temps, je vous fais une démo gravity. Vous l'avez déjà fait le Et sérieusement, vous en pensez quoi ?  
   
 

### 01:01:07 {#01:01:07}

   
**Aida (fr-par-25c):** Euh moi je suis plus après peut-être par habitude mais team cursor. Ouais, j'ai peut-être pas poussé jusqu'au bout l'utilisation de antigravity mais ça m'a pas fait basculer honnêtement. OK, c'était ce que j'ai fait. Je sais pas si vous l'utilisez au quotidien. Tout le temps. Tout le temps. OK. Quoi ? Qu'est-ce que US central ? Ah mon temp, j'ai l'impression. point. Ouais, c'est juste que j'ai pas de le dupliquer. Euh app local, j'ai mis les différents bquet que j'ai. Ouais.  
   
 

### 01:01:58 {#01:01:58}

   
**Aida (fr-par-25c):** Et parle de région, est-ce que vous avez un interdiction sur central 1 ? Ça c'est possible. Euh je regarder le beta project customer demo. Ah customer démo. Il faut que vous mettiez le vôtre. C'est ce que j'ai où il est là ? Ah ok. Ah il est mis en dur. OK. Je Ouais. OK. OK. Qu' s'en fiche de je me rappelle jamais. En fait, c'est dynamique, il faut faire un rerun en fait. On est obligé de faire un rerun à chaque fois. Non, mais sur l'interface interface non, il l'a pas rechargé.  
   
 

### 01:03:21

   
**Aida (fr-par-25c):** Mais non, celui aussi. Check modèle IP. Ouais. Non non, si j'ai pas Non, ça c'est le ça c'est le test ça. Ah ok, j'utilise pas le texte. Non, ça c'est Non, mais ça c'est le notebook. Euh j'ai mis Non, c'est pas le NX pas. Oui, tu peux le changer ça. Non, ça changera rien. C'est c'est pas utilisé cette partie là. C'était un la partie app qui est utilisée. Ouais. B si je où est-ce qu'il est ? Non, mais recharge relance-le. Je l' relancé.  
   
 

### 01:03:59 {#01:03:59}

   
**Aida (fr-par-25c):** C'est relancé. Ouais ouais. Ok. Il est pas mis en dur pour ça. Si non, j'ai fait une recherche sur le projet où il où il prend la région. OK. ure aussi location H si tout je pense. OK. OK, c'est bon. Extraction. J'ai réussi à lancer le collège. Je vais essayer de l'extraction. Ouais, tu dois avoir un problème de de project ID aussi, je pense. OK. Qu'est-ce que j'ai ? Ah c'est mieux.  
   
 

### 01:06:09 {#01:06:09}

   
**Aida (fr-par-25c):** Ouais. Donc dans le fichier, j'ai mini\_UR URL\_ tout\_ audio. Les valeurs elles sont en dures. Faut faire appel au est capable de lire est capable de lire ce genre de chose. Et il faut aussi par la localisation se mettant en Europe Prestin sinon tu auras pas le droit en US central. Et du coup intér de présenter nos capacités de synthèse vocale. OK. question municipale 2020 pas avec la clôture du officielle lundi 2 mars alors dans l'obligation des le socialiste Emmanuel Brigoir obtiendrait 31 % des par la candidat rachid qu'en Ah ça c'est la même chose hein. Mais ouais si nos infographies intégré infographie intégré ou pour la partie sport. Non voà c'est de la politique du coup souvent des des histogrammes et cetera et en fait vous voudrez que qu'on lise l'histogramme ?  
   
 

### 01:07:29 {#01:07:29}

   
**Aida (fr-par-25c):** Je sais pas. C'est possible. Ouais, je pense. Je voudrais pas qu'il en je voudrais d'une être sûr que la façon dont nous l'intègre nous on intègre ça dans la page est consommable et visible et après est-ce que nous on a envie de le rendre lisible et est-ce que ce genre de contenu très visuel sont adaptés à une lecture ? Ça dépend. Tu vois ça ça c'est un truc qu'il faut à mon avis euh Ouais. Là en fait ça dépend mais ça peut en fait ça peut manquer en fait dans la narration. Oui, c'estàd queen fait quand euh on a en fait le déroulé en fait de du texte et que en fait on euh toute l'information est dans le dans le dans l'image, ben en fait euh là on sait pas qui est premier, on sait enfin on n'a pas l'information euh de base.  
   
 

### 01:08:13 {#01:08:13}

   
**Aida (fr-par-25c):** La pratique, on va dire éditoriale, c'est normalement l'infographie quelle qu'elle soit doit être en complément, elle soutient. Oui, d'accord. Voilà. Et là, c'est un très bon exemple que sous les yeux parce qu'en fait ici tu as le résultat des sondages en histogramme et juste audessus tu as le paragraphe qui raconte exactement ce qui m'on. Donc là sur cet exemple là, on on pourrait largement passer ça à la limite ce serait redondant parce que en fait c'est un cas aussi intéressant c'estàd que si c'est pour que l'audio nous lise exactement deux fois la même chose, c'est pas possible. Pas génial. Mais c'est pas 100 % des cas. Il y a probablement plein de cas où l'infographie qu'on va injecter, elle est pas forcément racontée entièrement dans le texte. Ouais.  
   
 

### 01:08:55 {#01:08:55}

   
**Aida (fr-par-25c):** Et et là et et là si nous on la traduit pas en audio, bah du coup il va manquer une information potentiellement essentielle. Donc il je pense qu'il y a pas mal de cas. Donc en fait il y a si je comprends bien en fait il y a ce cas ce cas un peu qui trou dans la raquette de l'infographie n'est pas décrite et et ça fait partie de l'information. Donc il faut détecter ces informations là. Est-ce que en fait l'image et le texte sont redondants ? Ça ça on est capable de ça Géini il vous le fait voilà il vous le fait. Oui, non, c'est c'est très simple. Et oui, c'est inclus donc rien à faire. Non, voici le texte. J'ai pris la décision ou même l'infographie présente des informations euh partiellement exclusives ou parle-moi uniquement de l'information exclusive de l'infographie.  
   
 

### 01:09:46 {#01:09:46}

   
**Aida (fr-par-25c):** Oui, ça il va pouvoir le détecter en disant OK voilà ça manque. Oui. Donc ça je te le raconte. Après, il y a une question aussi je pense dans la façon dont on va voudra le présenter au consommateur, c'est est-ce que par exemple il y a un changement de ton de voie ? parce qu'il y a une introduction. Oui, c'est ça. Euh pour pour différencier comme un encar en fait. Voilà. Sur un encar, j'ai trouvé que c'était intéressant en fait de faire changer de de type de voix. Ouais. Ouais. Euh parce que en fait c'est ça permet de sans avoir besoin de raconter ou de faire d'introduction de montrer en fait euh on me fait un aparté, on explique avant de reprendre.  
   
 

### 01:10:22 {#01:10:22}

   
**Aida (fr-par-25c):** Ouais, bien sûr. C'est important ça. Je pense ça fait partie effectivement de tous les trucs qu'on rajoute, les citations, les encadrés. Exactement. Il y a aussi une question que je viens que je me pose que maintenant, c'est la question des vidéos qui viennent aussi en enrichissement et en soutien d'un texte. Oui. Euh je sais pas aujourd'hui évidemment nous on les exclut complètement notre player mais il y a probablement un sujet là-dessus aussi parce que je dis n'importe quoi. Euh un article sur une image, tu vois et donc vous cliquez enfin grosso modo machin regardez vous allez voir regarder en image. Je dis n'importe quoi la la chute du skier hier à Milan. Donc on va raconter machin et cetera. Et l'intérêt le le celle de l'article c'est l'image.  
   
 

### 01:11:01

   
**Aida (fr-par-25c):** C'est l'image. Ouais. Qu'est-ce que l'audio peut apporter pour compenser le fait que l'image n' pas ? Est-ce qu'il va la décrire ? Est-ce que est-ce que encore une fois la même chose ? Est-ce que l'article suffit dans la description pour qu'on ait pas besoin de rajouter un peu de couleur sur on voit ça à l'image ? Je pense que c'est des questions posées. Ouais. Et pos aussi. Ah c'est ça en fait. Il y a deux il y a plusieurs cas. Il y a le cas où en fait la personne ben en fait elle est complètement aveugle et euh et c'est un sujet c'est un sujet euh je veux pouvoir consommer mais je peux pas boire et je veux pas rater quoi que ce soit.  
   
 

### 01:11:35

   
**Aida (fr-par-25c):** Et rien qu'en fait entre guillemets entendre en fait le commentateur qui vient en fait euh en prenant le bon passage pour pas que ça soit trop trop lourd parce que en fait voir voir la partie dans lequelle bah on entend rien et c'est que visuel, c'est pas pertinent mais waouh à un moment donné où il y a une exaltation et du commentaire en ça peut être pertinent. rajouter en fait sur une partie partie descriptive pour compléter en disant bon ben voilà on voit ça ça peut être assez assez pertinent. Nous ce qui est intéressant je sais pas à quel point vous l'aviez étudié c'est justement tous ces enrichissements euh hors texte qu'on vient mettre dans les articles qui soient super important pour la compréhension parce que c'est le cœur du sujet un peu h et parfois pas du tout. Oui. Parfois pas du tout. Parfois tu lis un quelqu'un quelqu'un a foutu une vidéo pour faire de la vidéo vue le sujet est plus ou moins lié mais si tu es en train de lire ton article et tout d'un coup on te parle d'une vidéo qui raconte un sujet tout à fait annexe bon là on a perdu nos lecteurs.  
   
 

### 01:12:42 {#01:12:42}

   
**Aida (fr-par-25c):** C'est ça. C'est c'est c'est ça c'est je sais pas si c'est le truc que tu Est-ce que l'outil est capable de détecter euh l'importance du média euh que ce soit d'ailleurs une vidéo, un mbet de tweet, enfin je veux dire tout tout ce qu'on peut faire qui peut être plus ou moins lié et est-ce qu'il peut détecter la valeur h et du coup l'intérêt de le traduire ou pas en deux ? Là, j'ai j'ai envie j'ai envie de dire que technologiquement c'est possible mais c'est vous qui avez l'intention, c'est vous qui c'est vous qui décider ce que vous vous souhaitez faire. Ouais. Ouais. Parce que euh il y a tous ces cas un petit peu à la marge qu'il faut en fait bah qu'il faut entre guillemets adapter. Euh mais c'est votre choix en fait.  
   
 

### 01:13:28 {#01:13:28}

   
**Aida (fr-par-25c):** Nous ce qu'on peut faire c'est vous vous aid c'est ça et vous aider dans votre choix. notre choix en c'est ça. Donc soit en fait prendre un bout de la vidéo parce que c'est pertinent dans l'article euh il il a joué et l'intégrer en fait dans le flux audio faire que de la description et en fait convertir du texte ou d'image est peu important là pour le coup ça soit du texte ou une image on de la manière convertir ça dans quelqu'un qui parle de ça qui décrit en fait le média en fait en et on peut lui dire de manière conditionnelle euh ne le fait que si que si en fait le média est pertinent parce que s'il est pas pertinent par rapport au texte que tu viens juste de lire et tu es capable de faire un truc qui reprend exactement l'audio de la vidéo nickel ou avec du coup les vraies voix des vraies personnes. Ben en fait ça c'est on veut pas le faire avec Gémini TTS ou avec Gémini ou quoi que ce soit. C'est juste voilà en fait Gini va vous aider à dire c'est entre là et là qu'il faut on extrait l'audio et puis on on l'assemble et c'est facile c'est vraiment facile.  
   
 

### 01:14:47

   
**Aida (fr-par-25c):** Je euh on peut vous aider mais j'ai l'impression que là techniquement il y a pas de problème votre côté he voilà donc et moi mon but c'est que vous ayez des trouviez bien des solutions à tous vos problèmes euh de voix tout ça macronisme l'audio. Elle est là donc on le reprend hein. Il y a d'autres questions de ressources plus humaines chez nous qui vont clonage de On est d'accord. OK de leur destin. OK. OK. Bon, c'est intéressant. Nous, ça fait partie des quatre tests qu'il va falloir qu'on garde bien en tête. Ouais. Mais ce qui est important là, c'est de vraiment bien définir en fait les quatre tests et qu'on puisse puisse les travailler ensemble et qu'on définisse le bon KPI, le bonne chose. Ouais.  
   
 

### 01:15:36 {#01:15:36}

   
**Aida (fr-par-25c):** En terme de voix, d'audio, aujourd'hui, vous êtes ça vous alors aujourd'hui euh c'est ETX et euh déjà on a pas mal de problèmes techniques he sur les soit des rafraîchissements au milieu de de l'article, soit des coupures, soit non lecture non lecture dès le début. Euh ce il y a des pas mal d'erreurs aussi sur euh sur les longueurs de l'audio. Donc euh ouais, parfois on a des euh on a des des des articles et on a que 30 secondes 40 secondes. Donc du coup ça se voit que à partir d'un moment ça coupe et donc il y a pas mal de de problèmes techniques. Au-delà des problèmes techniques, il y a des tout ce qui est voix et tout donc c'est un petit peu robotique aussi. De l'UDR Antoine Valentin en haut de sa voix contre l'Inion des droites. Analyse dans la trisème circonscription de haute Savoie.  
   
 

### 01:16:32 {#01:16:32}

   
**Aida (fr-par-25c):** Après bon nous nous on coupe la photo, la légende et tout ça. Donc on passe directement au titre chapeau et après articles. On coupe aussi tout ce qui est les blocs de relance des autres articles. Oui ben oui, c'est logique c'est pas euh est-ce qu'il faut aujourd'hui pour aller récupérer uniquement les données textuelles Non. Euh voilà. Donc en gros aujourd'hui c'est c'est ça en fait, c'est cette voix un petit peu robotique vs des problèmes techniques qui OK. et vers le fin. Je vais juste voir là sur la sur la mise sur la mise à disposition là de de l'audio sur présence. Je pense que l'idée c'est c'est de mettre en ligne du MP3 sur un sur un store CS sur un CDN et c'est tout. Voilà, c'est ça. Assez simple.  
   
 

### 01:17:29 {#01:17:29}

   
**Aida (fr-par-25c):** Ouais, manière assez classique. Oui, du blu des lèvres. Abon la fin. C'est le parfum encore trop ce matin il écarte la petite tasse ou baigne un sachet d'herbe dans une occument par pas encore l'heure 8/ 10\. Il avait reculé au premier tour sur sa présence. C'est un peu ça change de voix entre speaker 1 et speaker 1\. Là, c'est c'est généré en tant que des segments autonomes complètement distincts. OK. Distin euh donc ça peut générer en fait ce ce cet cet effet là. D'accord. Mais c'est OK. Donc faut tout si c'est speaker 1, il faut tout que je mette au même endroit. OK. Voilà. C'est ce qui est plus efficace, sachant que il y a quand même une limite en terme de en terme en terme de de taille de d'audio généré.  
   
 

### 01:18:26

   
**Aida (fr-par-25c):** Ouais, ça ça je me rappelle qu'il y avait une limite de X caractère ou je sais plus quoi. même pas la plein caractère et sur nos on je fasse des chunks plusieurs chun de l'art tout le reste et ça parce que en fait c'est un c'est beaucoup à gérer à générer c'est des terministes l'impact c'est en fait c'est des légers changements on décid demain de donc il y a des choses qu'on peut faire en c'est visible alors faut demander un pack intéressant demander fixer en fait la la le side OK de la voix euh Ouais parce qu'en fait à chaque génération c'est un nouveau site non même si on va pouvoir pourir fixer ça player c'est des articles qui ont plus de x % de là dans le code c'est ce qui est fait rapport entre texte ça c'est pas mal parce que C'est ça sert à rien parce que sinon tu vas donner le chapeau et l'intro. Ouais d'histoire. Peut-être que c il autour de cette règle que nous on pourrait on va faire par exemple la température alors en fait si on rentre un peu plus dans le dans le code pour pour mieux comprendre comment ça fonctionne voir beaucoup d'intégration mais je pense que c'est valable aussi pour des vidéos parce que des articlesquel il y a essentiellement les vidéos pas je pense qu'il faudrait peut-être se faire une règle ratio, je sais pas si on est capable de le détecter ratio texte versus audio.  
   
 

### 01:20:13

   
**Aida (fr-par-25c):** Texte brut versus pour les articles on a des exemples mais on a des vidéos du coup ça dans le cor du texte en plus de la principale bah des gens en sport puis qu'ils ont tout le temps les exclure. Donc là ici dans cette configuration là la partie mon texte non c'est surtout regarde dans le foot plutôt va voir un vieux truc de foot combine audio veder mets-toi sur je sais pas actu alors hop champion donc là sur cette partie là on a la possibilité donc là en fait on définit VO la voix, on va avoir en fait toute la configuration, on va définir la modalité donc sortir de l'audio et donc on peut rajouter en fait le le fait de définir de définir en fait un site spécifique, définir la langue, enfin on peut aller rajouter des configurations spécifiques. Donc là dans le prbuild voice config. Ouais. Jusque là, il y a plusieurs générations qui sont fait en parallèle enfin pas en parallèle successivement pardon. Oui. Oui.  
   
 

### 01:21:38

   
**Aida (fr-par-25c):** En fait il y a plein de choses qu'on peut faire, on peut paralléliser, on peut il y a énormément de choses qui qui est possible. J'ai dit c'est un c'est quoi le nombre de caractères maximum par euh euh par des lui c'est un facho rappelle. connu euh juste savoir si c'est les mêmes limites que sur Ch ou il est venu protester pour que il sur Ouais, d'accord. OK. Tapé dessus et lui il s'est fait lâcher quoi. Il y a des vidéos on voit il tabass d'habitement. Il y a des vidéos sur les après il faut qu'on trouve une vidéo pour voir pourrait disparaître à horizon 2025 en France et ce sans qu'aucun act en 2024 R COD prévient sans régulation forte 9 et 23 et la tendance devrait se poursuivre en 2024 régulations fortes et rapide du pouvoir public 34 de mode pourrai disparaître à horizon 2025 ce on vi évidemment ça je pense qu'il faut le virer aussi parce que sinon c'est un podcast en podcast en revanche tu vois il y a il y a une info là il y a une info comme disait Julien ça se  
   
 

### 01:23:11

   
**Aida (fr-par-25c):** trouve si l'info est racontée dans le texte on est pas obligé de la mettre mais c'est vrai que probablement cette info est super intéressante mais qu' faud qu'on soit capable de son constitué de manière en autre truc qui dit tweet de machinette voilà ce que ça dit et il y en a plusieurs comme ça ouais c'est tac tac tac il y a aussi les cas ça ils font ça les revues de presse tu sais gen fait un match il font des revues de press et c'est pareil souvent c'est un peu de texte et puis soit la photo d'un journal soit le tweet et ça c'est pareil restitution sans ces enrichissements Ça il manque quelque chose clairement. Ouais, il manque le cœur du sujet. Et euh Julien, j'ai une question, je pense que c'est dans le système, on peut jeter facilement parce qu'on a le titre et après nous on a euh la signature. C'est écrit par quel journaliste ? Ça c'est on peut l'ajouter pour dire on peut lire le titre.  
   
 

### 01:24:06 {#01:24:06}

   
**Aida (fr-par-25c):** Oui, bien sûr. veut dire écrit par euh Oui, vous pouvez euh vous pouvez le en fait euh soit vous le faites de manière fixe, vous faites rajout euh ajouter en fait lu par euh ça ou vous demandez en fait à Géini d'intégrer ça parce que vous avez tout ça dans les les métadata ou en entrée et vous lui donner un peu un template de d'écriture, ça peut être une manière de faire ce qui en fait vous avez deux avantages en fait vous avez des avantages à faire l'un ou l'autre. Premier avantage, si vous le mettez en dur en disant lu écrit par n na, c'est que en fait ça va être déterminé, ça va toujours être la même manière. Euh et vous pouvez même se dire que vous changez de voix pour pour cette partie-là parce que Ouais. parce que ça permettre de c'est un aparté en fait, c'est pas le texte en tant que tel. Intéressant, je trouve ça intéressant. Donc ça c'est ça peut être pas mal.  
   
 

### 01:25:02 {#01:25:02}

   
**Aida (fr-par-25c):** L'autre possibilité c'est de dire que en fait c'est ça fait partie de l'article complet. et que en fait euh vous faites une lecture à deux voix et en fait tous les apartés vous le faites avec la même voix et c'est un aparté. Ouais. OK. Je Et et en fait il peut il peut vous proposer de l'écrire d'une certaine manière, ce qui peut être pertinent dans un certain cas ou dans d'autres cas. C'est vous qui choisissez si vous voulez du déterministe ou euh on peut concevoir le système que vous souhaitez. D'accord. les intéressant cette idée je trouve de mettre une voix différente pour le titre le chapeau. surtout dans les peut-être moins dans les articles classiques mais par exemple dans les éditoriaux où j'ai pris la décisionale c'est qui va donner son cap Julien c'est vraiment lui qui rapport c'est vrai que du coup tu as l'impression que c'est le journaliste qui te parle et c'est vrai que le décorélé du titre qui dit l'édito de quelqu'un qui appelle pour pas que ça fasse à un de long qui dit son propre c'est pas mal ouais et je pense qu'il faut on peut peut-être réfléchir aussi à cette idée peut-être de changer la voix du titre et du chapeau.  
   
 

### 01:26:09 {#01:26:09}

   
**Aida (fr-par-25c):** et de tout autre écart du texte, on en parlait tout à l'heure, des encadrés, des citations chez ceux qui quittaient l'aveu d'un désirséen pour l'étouffer. Des batailles pour un trône de pierre, Run Rotillo en a connu. La droite en a mené des éclatantes victoires aux espoirs déchus. Cet ancien vigilériste futur à tour témoin, soutien et acteur d'une fabrique politique de au bout d'un cycle. Après la chute de François Fillon en 2017, le traumatisme du score de quand tu changes de voix sur un titre, faudrait avoir un peu plus de télé. Et donc ça je pense qu'en fait c'est une vous avez deux possibilités. Soit vous en fait vous faites la génération à deux voies mais bon il y a une taille de génération maximum soit vous faites partie du principe que chaque voie vous les générez de manière différente et que vous assemblez en fait la totalité et vous c'est vous qui définissez les délais qu'il y a entre les chaque passage.  
   
 

### 01:27:13

   
**Aida (fr-par-25c):** OK ? Ce qui ce qui est en fait euh ce qui est assez pertinent limite de code oui c'est ça faut le faire au niveau code euh par des pauses. Exactement. Je peux vous faire des exemples si vous voulez vous aider à dans la doc c'est c'est que c'est ce qu'il y a de plus opérationnel dans les bench que vous avez tous fait là plus que moi. Est-ce que vous avez vu des gens qui dans le corps du texte quand il y a une citation entre guillemets qui changeait la voix ou le ton de la voix pour signifier que le journaliste donne la parole à quelqu'un ? Vous avez vu ça ou pas ? ou c'est même chose juste malin à déclarer bidul le plus souvent c'est on change les voix lorsqu'on change de on passe d'une paragraphe à une autre c'est généralement ce qu'on a mais on fait pas des identification des citations bien identification dans le cor du texte non bon je suis pas sûr que ça se fass peut-être qu'on pourrait changer le ton un tout petit peu mais après ce que lepo il met en avant c'est les voies i et le rentre comme en fait des personnes qui c'est-à-dire ils vont me dire le titre et  
   
 

### 01:28:27 {#01:28:27}

   
**Aida (fr-par-25c):** euh par exemple euh raconté par la voix de lire et ce qui est son nom c'est David par exemple et à chaque fois tu vas avoir tes différents articles et je pense il y a une dizaine de voix qui et à un moment donné si tu es vraiment tu écoutes souvent tu vas reconnaître la voix de tel tel tel speaker ça ça ça c'est un sujet qui marche très bien et pas que dans le monde du speech, c'est en fait le fait de faire de l'AB testing AB testing sur des sur des voies sur des des clitatures parce que vous allez voir en fait ce qui fonctionne et ce qui fonctionne pas. Et et comme en fait c'est que de la config au final ça peut être pertinent en fait de dire bon ben voilà pour un article je vais je vais le générer en fait pour dans plusieurs versions différentes avec plusieurs promes différents potentiellement et voir ce que ça peut donner les caps quand parce que c'est pas les parce que les clics c'est pas de la pist mais c'est vraiment la durée du le combien la personne elle a resté sur Ouais est-ce que est-ce que la personne à écouter jusqu'au bout jusqu'au bout et euh on fait une moyenne entre A et B sur le temps global de l'épou.  
   
 

### 01:29:42 {#01:29:42}

   
**Aida (fr-par-25c):** Exactement. Donc il y a Est-ce qu'elle a écouté jusqu'au bout ? C'est est-ce que en fait elle a dans la foulée elle a elle a fait un autre une autre lecture derrière ? Ouais ça ça peut être intéressant. Il y a aussi en fait tout ce qui est est-ce que vous voulez créer des radios ? des radios en fait avec les les news du jour et donc en fait on a une radio plus RSS. Euh ça ça marche très bien euh parce que ça permet en fait d'enchaîner les les différentes lectures. La personne en fait elle elle est captée en fait dans ce ces différents articles, elle écoute les choses et comme de toute manière elle est abonnée, enfin elleutilise et donc plus elleutilise et plus elle se connecte tous les jours, plus en fait elle elle trouve ça pertinent. Ça on l'a eu sur pas mal de retours de lecteurs dans entretien.  
   
 

### 01:30:32 {#01:30:32}

   
**Aida (fr-par-25c):** Voudrait avoir un podcast podcastisé de Exactement. C'est comme je sauvegarde un article pour le lire après d'avoir aussi ça plus personnelle où tu ajoutes et après tu lances la lecture et euh et après on peut aller plus loin parce qu'on en fait on a des outils de recommandation. On travaille beaucoup avec Spotify euh notamment sur de la reco euh personnalisée, on va dire bon ben voilà, tu as écouté tel tu as écouté tel article, je te fais tu une une playlist qui qui est euh Ouais. qui est pertinente parce que je te recommande les différents articles. Parfait. Et est-ce que tu aimes plus la voix parce que si peut peut y avoir ça ou est-ce que tu aimes plus le sujet ? Ça peut être ça peut être des points en fait qui sont intéressants à à aller à les capturer comme information. Et ouais, moi j'ai il y a un un produit que j'aime bien, c'est la newsletter de l'IB newsletter list classique avec série d'articles je crois qu' un petit un petit petit bout d'écrit texte et il y a un truc qui s'appelle écouter cette newsletter.  
   
 

### 01:31:37

   
**Aida (fr-par-25c):** Alors euh la techno probablement pas euh optimisée mais il y a un mode où tous les matins en fait tu as ton bulletin d'infos de Dieu. Oui. Puis quand tu vois les habitudes des lecteurs c'est beaucoup dans les transports ou sur matin et cetera, c'est c'est un truc qu'il faudrait que nous on mette tu vois en future app Figaro serait génial tous les matins sois un truc d'écouter ce qu'il faut retenir ce matin. on le fait sous diverses formats, articles, stories, newsletter, tout ça. Effectivement, il y a un truc à aller faire nous inventer un produit audio. Produit audio, c'est c'est enfin je pense que c'est il y a les deux prochains produits d'avenir, c'est l'audio et la vidéo. C'est c'est aussi. Je sais pas si vous avez testé la partie Notebook LM, la partie génération de vidéo. Ah non, j'ai testé que la partie génération audio podcast.  
   
 

### 01:32:30

   
**Aida (fr-par-25c):** La partie génération de vidéos. C'est en fait partie du principe que en fait générer de la vidéo cure euh pour à partir de sources textuelles. En fait, on on génère en fait une voix un un texte qui est illustré par des images et c'est et en fait c'est pas c'est pas en fait des gens virtuels que l'on voit dans la rue, c'est en fait une c'est une visualisation, c'est des slides. Donc en fait c'est un parti prix mais qui permett d'expliquer les choses plus de manière plus dynamique en venant générer ou animer ou contextualiser en fait les différentes images. Donc résultat un autre produit que vous pourriez avoir là si vous avez beaucoup d'infographies c'est en fait de venir ponctuer ces infographies d'une d'une écoute. Et donc en fait, je regarde une vidéo et je regarde je regarde une infographie commentée. H D'accord. Et en fait c'est un produit vidéo et ça vous coûte pas plus cher en fait.  
   
 

### 01:33:39 {#01:33:39}

   
**Aida (fr-par-25c):** Et ça permet en fait d'aller d'aller d'avoir un autre contact avec les personnes qui peuvent être qui veulent qui sont visuels et qui en fait consomment ça sur en mode l'eau et fort sur sur leur téléphone dans les transports en commun. Euh c'est c'est un autre produit. D'ailleurs, est-ce que vous avez réfléchi genre un truc qui dit une recommandation d'autres articles en audio ou playlist audio à la fin de la lecture d'un article ? Non, aujourd'hui on on a rien et et tout le monde s'arrête, tout le marché à la fin de la lecture d'un article s'arrête. Il y a pas des gens qui font comme on fait tous avec les vidéos. Next, next parce qu'il y a plein de trucs qu'on pourrait faire. On pourrait aller chercher les liens d'enrichissement qu'on met en pied d'article, la ré conseil. Bah tu enchaînes avec ça par exemple s'ils sont bien choisis qui tout à l'heure qu' était pas toujours bien choisis mais ils sont bien choisis et euh il y a peut-être pour euh enfin tout bêtement augmenter le nombre de la ration le la bah même sur la recour on peut vous on peut vous aider en fait on a des des outils hein qui sont faits pour ça hein donc euh et qui sont basé et qui sont basés sur les feedback des utilisateurs.  
   
 

### 01:35:02 {#01:35:02}

   
**Aida (fr-par-25c):** C'estd que c'est c'est alimenté par le les comportements des utilisateurs qui font que tu as lu donc tu es intéressé par ça et c'est logique mais c'est renforcé par le feedback d'un utilisateur ou tel autre article et c'est induit que par les utilisateurs. Donc c'est des choses qui sont euh sur lesquelles il faut exploiter en fait les données de type GA4 ou ou piano, ce que vous avez euh pour pouvoir récupérer cette information et de de s contextualisation et et la recommandation. Un sachet d'herbe dans une eau fume. Ce n'est pas encore là. C'est mieux. C'est mieux. J'ai pris la décision d'être candidat à l'élection présidentielle", a confié Brune Rotaillou dans un message écrit à certains de ses proches. Je dis "Son engagement dans la course en vue de 2027 est le fruit d'un nourrissement prudent, une étude minutieuse des circonstances avec lesquelles il s'agissait de composer pas se laisser par les événements ni par les autres dont il a fallu contenir l'impatience bienveillante s'agissant de ceux qui rêvaient à sa place.  
   
 

### 01:36:17

   
**Aida (fr-par-25c):** C'est marrant d'avoir incarné ça parce que c'est vraiment l'idée d'avoir un espèce de présentateur une bataille pour un trône de pierre en avant des alors c'est un personnage tout à fait effectif c'est un avant deutiliser une incarnation virtuelle comme le post journalist remplace par quelque chose parce que j'ai un mélange entre elle a enregistré des voix réelles de Bryan par exemple et du coup c'est avec Bran C'est vraiment la voix, c'est vraiment ta voix la voix mais c'est par rapport les configurations et les paramètres qu'on a mis après. Les déclarations le premier ministre François Bayer était l'invité de la matinale de BFM TV et RMC ce mardi à mo sur la parce que on a pas sur tous les articles il y a que sur les articles pu pas voir le cré Voici ce qu'il peut retenir de son intervention. une dérive inacceptable de l'État concernant les jours que Figaro et madame tout ce que vous avez fait va se retrouver dans la partie historique que bon c'est normal après c'est sur le disque hein OK avec les paramètres avec voilà les différents pompes des choses qui ont été qui ont été passé truc à faire aussi il y a des promes qui sont il y a des parties qui sautent je peux après tu peux mais le problème c'est que du pouvoir depuis bien de 15  
   
 

### 01:37:43

   
**Aida (fr-par-25c):** cesse de se chercher au bout d'un cycle. Résume-oi. Il s'arrête là. Pasour de l'audio un audio adapté au je demandé je même dans le dossier entraîné mes articles qu'est-ce que c'est. Ouais ouais en fait on est à 8000 oct en combiné. du c'est il y a pas cette motion de Non mais de toute façon je pensais pas l'idée de 4000 oct sur le text field oui 4000 pour le le prompt ok c'est Ouais qui va jusqu'au bout c'est ça c'est tout à l'heure c'était le bon exemple et après ce que vous pouvez faire dans les options vocales là en fait on voit ici le extremely fast. Voilà, c'est condition générale de vente. Ça en fait c'est un peu le nouveau format du en fait c'est c'est une manière on va dire contextuelle de de changer en fait l'intentionnalité effectivement.  
   
 

### 01:39:12 {#01:39:12}

   
**Aida (fr-par-25c):** Et on n pas évoqué une partie, c'est peut-être la partie fond sonore. Comment on arrive à mixer un texte avec un fond sonore ? Est-ce que c'est une composition qu'on doit faire nous-même ? Je sais que sur le SSML, il y avait la possibilité de faire ça. Est-ce que on peut le faire aussi avec Géini de enfin de Géini ? Alors en fait ou en fait c'est effectivement une composition qu'on fait qu'il faut faire vous-même. Je vous ai parlé tout à l'heure en fait de LIA. OK. Et sur Iliria en fait, il va vous permettre de réaliser cette génération audio. OK. C'est une API à part encore. C'est une AP à part qui est extrêmement simple. C'est un texte.  
   
 

### 01:40:00

   
**Aida (fr-par-25c):** La version actuelle c'est que en anglais. Il faut que le PR soit en anglais qu'il soit relativement court. Il génère que 30 secondes. OK. Euh donc 30 secondes voilà, il a plein de limitations, il enfin il existe et la prochaine version elle est incroyable mais la prochaine versionage voilà pour pour l'habillage c'est c'est suffisant. Donc là euh si si on a un habillage prédéfini par exemple là là ça va créer un habillage et si demain je dois mettre un habillage que c'est pub ça marche très très bien pour faire ça euh j'ai plein d'exemples si vous voulez euh en gros tu te dis que demain j'ai envie de mettre un fond sonore sur je sais pas moi mon chapeaucord bêtises ou sur telle typologie d'article, j'ai envie de mettre un fond sonore pendant que tu as généré ton texte. Comment tu arrives à composer les deux sur le texte speech que tu as généré et le fond ?  
   
 

### 01:41:03 {#01:41:03}

   
**Aida (fr-par-25c):** J'ai OK. Donc avec Pub OK sur les séries d'articles où tu veux peut-être faire des trucs un peu J'ai plein d'exemples he du de composition d'assemblage quoi que ce soit. La différence par rapport au SSML c'est on doit déf que ce type de contenu qui doit être lu dans versus le STSML je pouvais aller marche bien que tu racontes un phrase précise que les séries d'articles en série de la phrase du moment où tu allais starter une durée et c'est peut-être devrait coller à ce qu'on peut avec 2.5 5\. Du coup, alors c'est pas que c'est pas que c'est plus possible, c'est en fait c'est pas c'est pas prévu. OK. Aujourd'hui, c'est c'est quelque chose qui est pas prévu. Euh par contre euh l' liria, la prochaine version, on pourra lui mettre le prompt, un prompt qui est dérivé du segment audio que vous voulez euh que vous voulez en fait habiller et et on lui fera un prompte spécifique pour aller générer un habillage qui soit pertinent dans ce pour ce pour ce texte là.  
   
 

### 01:42:15

   
**Aida (fr-par-25c):** OK ? Donc là en fait un exemple c'est très musique d'ascenseur, on est d'accord parce que j'ai mis juste background audio for news. Euh donc le même avoir des nuances qui Ouais un petit peu. Ouais donc on peut mettre du négative. Je dis je veux pas de bit je veux c je veux ça je veux en fait j'ai réussi à faire des choses bien avec avec ce modèle fait background je sais pas tragique news ou happy news voir s'il y a des vraies différences des lèvres il goûte le se cherche au bout d'un cycle après la chute de François Fill en 2017 le traumatisme du score presque en 2022 considérablement à pour ce genre de problématique là typiquement François Fillon qui nous dit qui une fois sur deux ou une fois sur X qui va nous dire François Fillon il y a pas moyen de le corriger ? Euh c'est peut-être pas vraiment déterminé, c'est de lu dire bah tiens, c'est ça ton dictionnaire de prononciation.  
   
 

### 01:43:51

   
**Aida (fr-par-25c):** Ouais, je j'ai pas la réponse à tout de suite, faut que je cherche ça par l'épais théorisé par le bacisme faut que je je travaille un peu plus sur le prte. Certains il vont seuls sûr de leur destin ou des lèvres ilent. OK. Certains il vont il faut regarder côté aussi pour les pic comme tu nous disais tout à l'heure la tonalité. Je j'ai le code qui est prêt là, je vais vous le pousser. OK. Il y a des codio. Ça c'est généré avec Lia aussi. Et et c'est euh Il est où la musique ? musique colk mechanical pulse vous avez compris j'ai je j'ai des petits des petits j'ai un générateur de de fiction sonore que je travaille beaucoup sur sur le sujet c'est des projets perset perso.  
   
 

### 01:45:34

   
**Aida (fr-par-25c):** OK. Voilà. Donc euh je fais que de la fiction, pas mélanger les sujets et je vais pousser le changement là sur le side. Elle sert à quoi la librairie synthétise long audio request ? Elle fait la même chose que Alors ça c'est pour c'est pourirp. Ah c'est que pour c'est chip ça. Ah cloud exposit. OK. Ouais, en fait c'est doc de G TTS qui m' Ça c'est G TTS mais en fait c'est la la doc est pas est pas folle et en fait je suis là pour compléter la doc GTS en fait c'est en fait il y a les différents modèles mais en fait ils ont rajouté GTS dans un truc qui était bien structuré qui était bien cohérent mais en fait les voies c'est en fait les voix c'est les mêmes noms que sur cette chirp D'accord. Et donc en fait, on va retrouver un certain nombre de choses.  
   
 

### 01:47:44 {#01:47:44}

   
**Aida (fr-par-25c):** OK. On a bien en fait tous les euh toutes les localisation, les différentes différentes voies pour tester aussi enfin les autres voies qui est les autres modèles là. Le flash et le flash. Alors il est il est moins propre, on est clair. Il est moins cher, il est plus rapide. Le le lit c'est encore moins cher et encore plus rapide mais c'est moins de moins bonne qualité. Donc euh voilà. Donc on a 4 minutes parce que voilà c'est ça. Donc le text field et duration. Voilà 555 secondes. OK. Et ça à nous de faire cette vérification de avant la trancature, j'imagine. Euh doit y avoir un paramètre qui permet de savoir que ça a été tronqué dans les dans les paramètres de retour.  
   
 

### 01:49:08 {#01:49:08}

   
**Aida (fr-par-25c):** que le type de contenu qu'on envoie pas directement le paramètres génér Ce qui va ce qui va ce qui va influencer ça c'est nous en entrée c'est on va les paramètres que nous on va décider d'envoyer à paramètre on envoie un contenu je sais pas politique ou fiction ça va être ça va pas du tout influencer ça va être ton prom ou non c'estàd qu'en fait la voix elle est il y a le prompte il y a le promete chapeau mais en fait il y a les virgules les points euh les enfin les mots qui influencent très légèrement euh quand même enfin les virgues les points complètement des deux trucs mais de manière déterministe. Oui oui oui. Euh partout mais en fait euh il y a de partout il a on peut lui faire on peut lui faire euh être tragique sur du contenu du contenu euh nous de le faire varier de se décembre infé de conten en fait sur la la partie sur la partie génération vous allez vous allez si jamais en fait vous mettez euh Euh un comment s'appelle un section, une température qui est qui est plus importante, vous allez laisser plus de liberté pour euh mieux s'exprimer de manière contextuelle.  
   
 

### 01:50:40 {#01:50:40}

   
**Aida (fr-par-25c):** Plus c'est bar et plus en fait il va être strict sur voilà. Euh cette liberté, il va l'exploiter par uniquement par rapport au paramètres d'entrée, pas par rapport au contenu qui lui a envoyé. Non non, il va non il va utiliser le plus la température est élevée, plus il va utiliser le contenu pour s'adapter en fait au contenu et le lire de manière adéquate par rapport au contenu 2026\. Donc c'est en fait c'est c'est vous qui choisissez en fait le en gros en plus de Ouais. c'est une trè c nation interprétation interprétation du modèle par rapport au c'est ça c'est donc là je mets une température à de qui est maximum on laisse un maximum de liberté euh donc là c'est quoi le texte donc économie industrie automobile complète le podium faire générer un petit benchmark c'est un paramètre que je viens de rajouter à l'instant donc je teste si ça marche en même Su l'industrie automobile française a perdu un tiers de ses effectif entre 2010 et 2023 constate l'INC.  
   
 

### 01:51:57 {#01:51:57}

   
**Aida (fr-par-25c):** L'industrie automobile française a perdu un/ers de ses effectifs entre 2010 et 2023, constate l'INC. Et donc, je vais le faire générer avec une température à zéro. OK. La voix que j'aimais bien c'était l'industrie automobile française a perdu un tiers de ses effectifs entre 2010 et 2023 constate Lincerd personnel de de sélection de voix truc c'est juste ça si pause il essayer mettre longue pause pause là pour l'instant en train de voir si ça peut changer quelque chose ou pas. Je viens pour l'accessibilité du coup lorsqueon est sur une navigation en clavier, est-ce que les lab buzz et tout sont en français par exemple ou c'est vous qui contrôlez la page en fait tout le contenu de ce que tu vas envoyer à ton audio. C'est toi qui va le décider ce que tu vas mettre dedans. Ouais. Le but derrière, c'est vraiment que tu sois autonome sur qu'est-ce que je veux dans mon audio.  
   
 

### 01:53:23 {#01:53:23}

   
**Aida (fr-par-25c):** OK. Si demain tu dis bah je veux interpréter que les chapeaux, enfin j'ai pas envie de mettre le chapeau, je je veux pas interpréter les titres, j'en fais rien. C'est toi qui déterminera ce que tu veux. mis à part les médias ou tu pourras pas enfin je pense pas qu'on pourra interpréter des médias sauf si les médias on peut on peut en fait demander à Géini qui génère qui génère en fait un on va dire un captioning ou enfin une description euh dans le ton que vous voulez mais c'est votre choix c'est par défaut ça ça l' pas oui ça ouais c'est doute même sur un prompting sur les identifier les trucs des des personnalités publiques ou quoi, je pense pas que tu puisses C'est le le faire correctement quoi. Je pense pas que ce soit une h sur les médias, faudra quand même qu'on se penche pour savoir ce qu'on veut faire jusqu'où on veut aller sur l'audioisation du médias. Peut-être dans un temps un, on peut dire bon, on fait comme aujourd'hui à savoir les oubli quoi ni pas des éclatons de victoire aux espoirs déchus.  
   
 

### 01:54:29

   
**Aida (fr-par-25c):** Cet ancien viiriste futur à tour témoin, soutien et acteur d'une famille politique qui privée du pouvoir depuis bientôt 15 ans ne cesse de se chercher. Au bout d'un cycle après la chute de France, pause. Le traumatisme du Tu l'as mis où la médium pause ? juste avant le son son texte là et juste après. Nor c'est 500 mseondes. C'était beau. Essayer de corriger la lecture entre les fragments qui s'enchaînent trop vite. Ouais, je voulais voir si juste juste comme ça. Ouais. Ils ont pris une déc bout d'un cycle après chercher au bout d'un cycle après la vidéo vidé et un texte qui est archi court parce que dans la vidéo mais au milie pense que le contenu milie texte dans la vidéo au milieu non ça va être ça suffit mais qu'est-ce qu'on fait ça en c'est pas très grave C'est c'est comment dire c'estable mais c'est vrai que Ouais comme ça ouais audio qui te dit euh prendre ce je  
   
 

### 01:55:39

   
**Aida (fr-par-25c):** vidéo l'écrivain il est c'est bizarre ça c'est des petits trucs qui vont être compliqués on pourra toujours créer chercher des règles pour les exclure. C'est la voix que tu préfères pour l'instant. Je reviens viennent des Miatrix. J'ai pas tout essé honnêtement. C'est qui me paraît le plus naturel qui vient dans le générateur en fait la partie benchmark qui génère en fait sur le même texte toutes les voies. OK. Et après comme ça ça te permet avec le même promte avec la même chose. Exactement. Je peux avoir un texte ? Oui. Tu mets ton texte et ton texte comme ça. OK. Tu mets euh sur le générateur euh tu avec unurl du contenu un scrapur euh oui c'est vrai.  
   
 

### 01:56:25 {#01:56:25}

   
**Aida (fr-par-25c):** Pas grave. Bon après je peux le rajouter ici hein. Bon je un peu compliqué. Je me rappelle une des raisons pourquoi on avait on avait arrêté d'utiliser antigravity. C'était lent. C'était lent. Ouais, c'est vrai. Oh, on le trouvait hyper lent par rapport à à cure sort. C'est c'est ça dépend. C'était une des remarques qu'on avait fait sur notre sur notre équipe quand on était passé survit, on s'était dit "Ouais, il y a vraiment un gap entre". Ça dépend quel modèle vous mettez derrière. Euh je crois qu'on était sur Claude, on essayé de comparer un modèle égal. Un modèle égal ? Ouais.  
   
 

### 01:57:20 {#01:57:20}

   
**Aida (fr-par-25c):** Ouais. Et que j'ai mis flash ça va extrêmement vite. Ouais. Si on part pour des modèles flash. Ouais. Ouais. Mais le modèle pas de pas et te rappelle Paul on s'était dit ça sur c'est long. Moi je l'ai pas assez assez utilisé parce que j'avais une expert au lancé où il m'avait inventé des hey script et on leur du coup je Ah oui je mais que j'ai pas commencé un un abandon définitif pour que je revienne soit finon en 2017\. J'ai pas j'ai pas eu l'occasion de trop tester ça. Je ce jour-là, je l'avais je l'avaisé, je retourné au terit et la pause, elle marche bien en plein milieu. En fait, ça c'est à partir du moment où tu as un texte et que tu veux mettre une pause dramatique à tel tel moment, ça fonctionne très bien.  
   
 

### 01:58:13 {#01:58:13}

   
**Aida (fr-par-25c):** Ça fonctionne plutôt bien au sein d'un texte pour faire les les différents euh bullet points un peu. Ouais. Voilà. Ça marche pas pourah en début fin euh faut voir je sais plus comment essayer de le placer style avant les guillemets des choses comme ça savoir si s'il l'interprète bien ou pas du tout une question de caractère ou tu me dis je peux trouver des toilettes s'il te bien sûr pour voir où assistant parlementaires. fait là fait. Il m'a j'avais lancé un une génération déjà l'extraction dur un moment la génération un moment et puis là je reviens. Il a il est revenu à l'étape d'extraction. Je sais après c'est du watch. Ouais mais je pas pas modifier pas modifier un truc. Rapeur a été relevé dans les rangs de et sur l'entraînement de voie personnalisée, comment ça marche sur Gini 2.5 Pro ou est-ce que c'est toujours basé sur CH ou euh non, en fait on a on a cette fonctionnalité là qui existe sur Gini TTS. OK, c'est basé sur des euh des frag en fait ça va être 30 secondes d'audio. OK. euh dans lequel en fait on on lit une un texte spécifique et qui va permettre de prendre l'empreinte vocale et enfin toutes les toutes les caractéristiques de de enfin voilà de la voix et puis et puis voilà. OK, c'est que 30 secondes. C'est assez court il me semble dans ça a beaucoup évolué ça du coup depuis depuis 2 ans. Ah oui oui. Après c'est en c'est en aujourd'hui en privé de preview. On sait pas que c'est pour tout le monde. Donc il faut si vous le faut qu'on vous faut que je je monte un caisse parce que on avait fait un point il y a 2 ans je crois avec Solem et je sais plus qui. Sirvio crois.  
   
 

### Transcription terminée après 02:01:24

*Cette transcription modifiable a été générée par ordinateur et peut contenir des erreurs. Les utilisateurs peuvent également modifier le texte après sa création.*