# Copetrolite — Guide de présentation

Support en français : 33 diapositives au format 16:9, avec logo du projet.
Durée suggérée : 25 à 35 minutes ; démonstration facultative de 8 à 10 minutes.

Le PowerPoint est modifiable. Les notes ci-dessous figurent aussi dans ses notes de présentation.

## 01. COPETROLITE

Présenter Copetrolite comme une application de gestion des interventions industrielles. Elle relie les entreprises clientes, les équipes internes et les techniciens dans un circuit commun. Cette présentation décrit le code présent dans le projet au 18 octobre 2026 ; elle ne constitue pas une preuve de déploiement en production.

Sources : Synthèse du projet

## 02. Un suivi continu de chaque intervention

Les bénéfices présentés sont les objectifs du fonctionnement de l’application. Aucun gain de productivité chiffré n’a été mesuré. Le socle existant couvre le suivi opérationnel, documentaire et financier.

Sources : Modèles, services métier et interface

## 03. Le parcours métier de bout en bout

Le pointage est d’abord un brouillon. Sa soumission déclenche le travail de validation client. Seul un pointage validé et encore non facturé peut entrer dans une facture. Le paiement constitue une étape distincte de la facturation.

Sources : eliteapp/access.py · services.py · serializers.py

## 04. Les modules disponibles

Pour l’administrateur, Équipe et Calendrier se trouvent dans Paramètres. Les autres menus principaux sont Vue d’ensemble, Projets, Pointages, Techniciens, Clients, Facturation et Paiements. Le contenu de Paiements diffère entre administrateur et technicien.

Sources : frontend/src/App.jsx · forms.jsx

## 05. Quatre rôles, des responsabilités distinctes

Le code définit exactement quatre rôles. Il n’existe pas de rôle comptable séparé. Un compte d’accès client par projet utilise le rôle de chef de projet client avec un périmètre plus restreint.

Sources : eliteapp/models.py · access.py · views.py

## 06. Matrice des droits

Le client peut consulter des informations limitées sur les personnes de son périmètre, sans documents privés. Le superviseur consulte les comptes mais ne les crée ni ne les modifie. Le technicien retrouve ses gains dans un endpoint distinct, sans accès aux factures ou paiements clients. Les coûts de projet sont consultables en interne.

Sources : Contrôles serveur : access.py · views.py · serializers.py

## 07. Le tableau de bord administrateur

Le tableau de bord actuel présente quatre indicateurs principaux. Pour les profils non administrateurs, les heures validées remplacent le reste à encaisser. L’indicateur heures validées exclut les pointages déjà passés à l’état facturé ; il ne doit donc pas être présenté comme un cumul historique de toute l’activité approuvée.

Sources : DashboardView · frontend/src/App.jsx

## 08. Clients : un référentiel structuré

La fiche client regroupe les coordonnées nécessaires au suivi. Le formulaire actuel rend plusieurs champs administratifs obligatoires. Une facture conserve un instantané de certaines informations client à son émission.

Sources : ClientViewSet · ClientSerializer · forms.jsx

## 09. Équipe : créer et maîtriser les comptes

Le mot de passe est enregistré sous forme hachée. Les écrans ne permettent pas de relire le mot de passe stocké. Les restrictions de modification empêchent notamment certaines incohérences de rattachement lorsqu’un historique existe.

Sources : UserViewSet · UserSerializer · forms.jsx

## 10. Le dossier complet du technicien

Le matricule est généré selon un compteur annuel au format CP-année-numéro. La photo, l’adresse, le CV et les autres informations privées ne sont pas exposés aux clients ou aux techniciens par la réponse utilisateur limitée. Une suppression de technicien avec projets ou pointages est bloquée.

Sources : UserSerializer · UserViewSet · TechnicianPhoto.jsx · CertificateUploads.jsx

## 11. Détecter l’expérience depuis un CV

L’extraction repose sur PyMuPDF et des règles de repérage des rubriques, avec OCR Windows si nécessaire. Les titres reconnus comprennent expérience professionnelle, parcours professionnel et work experience. Il ne s’agit pas d’une analyse universelle de toutes les mises en page. Le résultat retourné est limité à 20 000 caractères.

Sources : eliteapp/cv.py · CVImport.jsx

## 12. De l’import à une expérience exploitable

La distinction entre extraction et sauvegarde est essentielle lors de la démonstration. Le bouton d’extraction ne suffit pas pour joindre le CV. L’éditeur propose gras, italique, soulignement, listes et annuler/rétablir. En cas d’absence de rubrique détectée, le texte proposé peut être corrigé puis adopté.

Sources : CVImport.jsx · ExperienceEditor.jsx · UserSerializer

## 13. Extraire la photo du CV

Le code sélectionne une image candidate ; il ne réalise pas de reconnaissance faciale et ne garantit pas un recadrage du visage sur un CV scanné. Lors de la sauvegarde d’une fiche sans photo, une image peut aussi être extraite automatiquement du CV. Une photo déjà présente est conservée ; une photo explicitement importée est prioritaire.

Sources : extract_cv_photo · save_photo_from_cv · CVImport.jsx · TechnicianPhoto.jsx

## 14. CV : qualité, confidentialité et contrôle

Le README mentionne encore une ancienne limite de dix pages ; le code et le formulaire actuels n’imposent plus cette limite. Les PDF protégés doivent être déverrouillés. L’OCR dispose d’un budget de traitement d’environ 60 secondes. Les tests OCR utilisent une simulation, ils ne prouvent pas la disponibilité du moteur Windows de ce poste.

Sources : cv.py · CVImport.jsx · test_cv.py

## 15. Préparer les projets et les affectations

Le formulaire actuel utilise un nom libre pour le chef de projet client. Il faut donc distinguer cette information descriptive d’un véritable compte de connexion. Le backend prend également en charge les comptes chefs de projet historiques rattachés au projet. Les champs financiers sont masqués dans les réponses projet des techniciens et clients.

Sources : ProjectSerializer · ProjectViewSet · forms.jsx · ProjectAccess.jsx

## 16. L’espace du superviseur interne

Il peut voir les tarifs et les coûts calculés des projets. Il ne doit pas être présenté comme un simple lecteur de projets : le backend lui permet de créer et modifier les clients et projets. En revanche, il ne saisit pas les heures à la place du technicien.

Sources : views.py · access.py · App.jsx

## 17. Un accès centré sur le terrain

Le formulaire actuel simplifie la saisie à une date et une durée. Il ne demande pas directement une heure de début, une heure de fin et une pause, même si ces informations existent dans le modèle serveur. Le technicien ne gère pas les comptes ni les documents privés des autres personnes.

Sources : App.jsx · forms.jsx · entries_for · projects_for

## 18. Le cycle d’un pointage

Les chevauchements sont recherchés sur tous les projets du technicien. Un refus crée un état distinct, modifiable par son auteur. Le client ne voit pas les brouillons. Les transitions et corrections sont historisées avec l’identité de l’acteur.

Sources : TimeEntrySerializer · transition_entry · TimeEntryEvent

## 19. Les gains du technicien

Les gains utilisent les tarifs et le calendrier actuels. Ils peuvent donc changer si ces paramètres sont modifiés. Ce module ne constitue pas un système de paie, un bulletin de salaire ou une preuve de virement. Les données de gains sont accessibles en lecture seule au technicien.

Sources : ProjectViewSet.earnings · ProjectSerializer.get_technician_labor_cost

## 20. Deux modes d’accès au périmètre client

Les restrictions reposent sur le projet attribué et le client actif. L’appartenance à la même entreprise ne suffit pas pour valider les pointages d’un autre projet. Le compte dédié est redirigé vers les pointages à valider.

Sources : projects_for · entries_for · LoginView · App.jsx

## 21. Valider ou refuser les heures

L’auteur de la décision, sa date et le motif éventuel sont enregistrés. Un administrateur ne dispose pas d’une action de validation de substitution dans le circuit actuel. La validation est une action métier tracée, pas une signature électronique certifiée.

Sources : transition_entry · entry-detail dans App.jsx

## 22. Configurer un accès client par projet

Le formulaire permet de générer un mot de passe. L’envoi d’un email ou d’une invitation automatique n’est pas implémenté dans ce parcours. Un client désactivé ne peut plus utiliser cet accès projet.

Sources : ProjectAccess.jsx · ProjectViewSet.client_access · LoginView

## 23. Facturer les interventions validées

Le serveur bloque les pointages non validés, les doublons et le mélange de projets. La facture conserve notamment les noms client et projet, l’adresse, le bon de commande et les montants. Le document imprimable actuel est décrit comme un outil de suivi interne ; les informations de l’entreprise émettrice restent à compléter avant usage commercial définitif.

Sources : create_invoice · InvoiceCreateSerializer · InvoiceDetail · README

## 24. Suivre les règlements clients

Ces enregistrements concernent les paiements reçus des clients. Aucun raccordement bancaire automatique n’est présent dans le périmètre examiné. Les modifications et suppressions de paiements ne sont pas exposées par l’API actuelle.

Sources : record_payment · PaymentSerializer · Invoice.balance

## 25. Tarifs et jours fériés

Le calcul du forfait client regroupe les pointages sélectionnés dans une seule émission de facture. Il ne faut pas promettre une déduplication du forfait entre plusieurs factures séparées portant sur la même date et le même technicien. Les dates fériées sont saisies par l’administrateur, sans présumer d’un calendrier légal automatique.

Sources : create_invoice · get_technician_labor_cost · PublicHolidayViewSet

## 26. Séparer les données et conserver les traces

La désactivation permet de conserver les liens historiques. Les contrôles du backend complètent l’affichage conditionnel des menus. Cette présentation ne remplace pas un audit de sécurité ou une recette complète d’exploitation.

Sources : access.py · views.py · services.py · serializers.py

## 27. Un usage web et un accès Android

Le README décrit un APK de développement lié à une adresse réseau locale. Une distribution plus large nécessite notamment une adresse accessible en HTTPS et une signature de production. Ces travaux ne sont pas réalisés dans le cadre de cette présentation.

Sources : README · frontend/src/App.jsx · styles.css

## 28. Une architecture organisée par responsabilité

Les consignes générales mentionnent PostgreSQL, mais coproject/settings.py configure actuellement django.db.backends.mysql et le README documente MySQL. La présentation reflète cette configuration observée, sans la modifier. La base de données et les documents locaux doivent être sauvegardés ensemble.

Sources : coproject/settings.py · test_settings.py · cv.py · README

## 29. Un exemple simple, de l’heure au solde

Exemple purement pédagogique : huit heures sont déclarées puis validées. Avec un tarif client de 2 500 DZD par heure, la facture hors taxe atteint 20 000 DZD. Avec un tarif technicien de 1 000 DZD, ses gains calculés sont de 8 000 DZD. Après un règlement client de 12 000 DZD, le solde restant est de 8 000 DZD. Aucune donnée réelle du projet n’est utilisée.

Sources : Formules : services.py · ProjectSerializer

## 30. Le scénario à présenter en direct

Changer explicitement de session entre les rôles pour montrer les différences de menus et de données. Ne pas manipuler de véritables données personnelles dans une démonstration publique. Préparer un CV lisible avec un portrait intégré pour rendre le résultat de l’extraction observable.

Sources : Parcours issus des écrans et règles métier existants

## 31. Périmètre livré et vérifications

Tests lancés séparément : eliteapp.tests puis eliteapp.test_cv avec coproject.test_settings. Total : 61 tests, 58 réussis, 2 échecs d’assertion et 1 erreur. Les écarts CV/profils sont préexistants : attente de casse de l’adresse, validation du téléphone lors de la mise à jour photo, absence de certificate_documents dans une réponse de mise à jour. Le moteur OCR est simulé dans ses tests. Aucun code applicatif n’a été modifié pour cette livraison documentaire.

Sources : Exécution locale : manage.py test · 18/10/2026

## 32. Une chaîne de travail partagée

Conclure sur la complémentarité des rôles. L’extraction de l’expérience et de la photo facilite la constitution des dossiers techniciens ; le circuit de pointage structure ensuite le suivi du travail. Ouvrir les échanges sur les besoins de déploiement et les priorités d’évolution.

Sources : Synthèse du projet

## 33. Sources et limites de cette présentation

Écarts documentaires identifiés : ancienne limite de dix pages du CV, anciennes informations sur le matricule, et ancienne description de la saisie horaire. Les fonctionnalités sont présentées selon les fichiers actuels. L’environnement utilise MySQL malgré la mention générique de PostgreSQL dans les consignes. Les fichiers de configuration sensibles et les données applicatives n’ont pas été lus pour produire ce document.

Sources : Sources locales uniquement

## Vérifications exécutées

- `env/Scripts/python.exe manage.py test eliteapp.tests --settings=coproject.test_settings --verbosity 1` : 35 tests réussis.
- `env/Scripts/python.exe manage.py test eliteapp.test_cv --settings=coproject.test_settings --verbosity 1` : 26 tests, 23 réussis, 2 échecs et 1 erreur.
- Écarts préexistants : attente de casse de l’adresse ; téléphone non conforme lors du scénario de photo ; réponse sans certificate_documents lors du scénario de mise à jour des certificats.
- Le moteur OCR est simulé dans les tests ; aucune recette OCR réelle ou de production n’est revendiquée.
- Aucune modification du code applicatif, de la configuration ou de la base métier.

## Régénération

Exécuter `python presentation/generate_presentation.py` depuis la racine. Le générateur utilise ReportLab disponible sur le poste et python-pptx installé séparément dans `.runtime/presentation-tools`. Ces outils ne sont pas ajoutés aux dépendances de l’application.
