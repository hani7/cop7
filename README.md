# Copetrolite

Première version d’une application de gestion des interventions industrielles : backend Django REST, base MySQL et frontend React/Vite en français.

## Ce qui est disponible

- Connexion par session, protection CSRF, mots de passe hachés et limitation des tentatives de connexion.
- Gestion des clients et comptes utilisateurs, désactivation plutôt que suppression de l’historique.
- Menu **Techniciens** : fiches avec spécialité, coordonnées, statut et projets affectés ; recherche et filtre actifs/désactivés. L’administrateur peut ajouter et modifier les fiches, le chef de projet client consulte uniquement les techniciens de son périmètre. Le matricule et le coût horaire ne sont plus affichés dans les formulaires ni dans la liste ; les anciennes valeurs sont conservées en base.
- Fiches techniciens complétées : nom, prénom, date de naissance, adresse, téléphone, email, poste/spécialité, expérience professionnelle et certificats/habilitations. Import d’un CV PDF, JPG ou PNG et extraction locale de l’expérience, à vérifier avant utilisation.
- Projets avec client, site, chef de projet client, techniciens affectés, tarif horaire et budget.
- Pointage manuel avec dates/heures, pauses, description et calcul des heures nettes.
- Soumission, validation ou refus motivé, correction et nouvelle soumission.
- Historique daté des transitions, avec l’identité de l’utilisateur.
- Factures à partir des pointages validés, tarifs et coordonnées client figés à l’émission.
- Paiements partiels ou complets, contrôle du solde, consultation et impression de la facture depuis le navigateur.
- Tableau de bord, recherche, filtres et interface adaptée aux téléphones.

## Les rôles

| Rôle | Accès |
| --- | --- |
| Administrateur | Comptes, clients, projets, suivi des pointages, factures et paiements |
| Superviseur interne | Clients, projets, affectations et consultation des pointages |
| Technicien | Ses projets, saisie/correction de ses propres pointages et soumission |
| Chef de projet client | Ses seuls projets, consultation des pointages soumis et validation/refus |

Il n’existe pas de rôle comptable. La validation appartient au chef de projet client affecté au projet, y compris lorsqu’un autre chef de projet travaille pour le même client. Les techniciens et chefs de projet clients n’accèdent pas aux coûts internes, aux tarifs ni aux endpoints financiers.

Circuit : **brouillon → soumis → validé → facturé**. Un refus retourne le pointage au technicien. Les pointages soumis, validés ou facturés ne sont pas modifiables. Les heures ne peuvent pas se chevaucher, même entre deux projets.

## Démarrage local

Le projet utilise **MySQL Community Server 8.4.11 sur `127.0.0.1:3308`**, installé dans `.runtime/`. La base `copet` et les tables Django sont créées ; toutes les migrations ont été appliquées. `.env` contient un compte `copet_app` limité à cette base et son mot de passe généré localement.

L’application utilise bien MySQL, conformément au choix du projet. XAMPP et son ancien serveur sur 3306 sont conservés. Le serveur MariaDB portable préparé précédemment sur 3307 est arrêté ; ses fichiers sont conservés dans `.runtime/mariadb-data/`. Ces anciennes bases ne contenaient aucune donnée applicative. La base active de l’application se trouve sur MySQL, port 3308.

Dans PowerShell, à la racine du projet :

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-db.ps1
.\env\Scripts\python.exe manage.py createsuperuser
.\env\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

`createsuperuser` est nécessaire seulement pour créer votre premier administrateur : choisissez son identifiant et son mot de passe dans le terminal. Aucun compte applicatif n’a été créé automatiquement.

Dans un deuxième terminal :

```powershell
cd frontend
npm.cmd run dev
```

Ouvrir **http://127.0.0.1:5173**. Vite transmet `/api/` au backend local. Utiliser `npm.cmd` évite la restriction PowerShell sur `npm.ps1`.

### Accès client par projet

Dans **Projets → Accès client**, l’administrateur crée un identifiant et un mot de passe propres au projet. Le formulaire permet aussi de générer un mot de passe, de le remplacer et de désactiver l’accès. Notez le mot de passe avant de fermer le formulaire : il est stocké haché et ne peut pas être relu.

Le client ouvre **http://127.0.0.1:5173/project/login** (ou `/project/login` sur l’adresse réseau de l’application), puis utilise les identifiants transmis par l’administrateur. Il arrive sur les pointages à valider et peut les valider ou les refuser avec un motif. Ce compte accède uniquement à son projet, même si l’entreprise cliente possède plusieurs projets. Les comptes chefs de projet existants conservent leur accès habituel.

Après mise à jour d’une autre installation, appliquer la migration `0013_project_access_user` avec `python manage.py migrate` avant de démarrer le serveur.

### Accès technicien Android sur le réseau local

L’APK de développement ouvre **http://192.168.1.64:5173/tech/login**. Il fonctionne seulement lorsque le PC et le téléphone sont sur le même réseau Wi-Fi et que les serveurs locaux sont démarrés. Cette adresse utilise HTTP : ne l’utilisez que sur un réseau de confiance; les identifiants ne sont pas chiffrés sur le réseau.

Arrêtez avec `Ctrl+C` les serveurs Django/Vite déjà lancés. Dans le terminal backend, autoriser l’origine mobile pour cette session PowerShell, puis démarrer Django :

```powershell
$env:DJANGO_CSRF_TRUSTED_ORIGINS = 'http://localhost:5173,http://127.0.0.1:5173,http://192.168.1.64:5173'
.\env\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Dans un autre terminal :

```powershell
cd frontend
npm.cmd run dev:lan
```

Autoriser le port 5173 dans le pare-feu Windows si le téléphone ne peut pas ouvrir la page. Pour reconstruire l’APK (Java et Android SDK requis), à la racine du projet :

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\android\build-local.ps1
```

L’APK de test est créé dans `android/app/build/outputs/apk/debug/copetrolite-technician-debug.apk`. Il inclut une icône Copetrolite, un écran de lancement natif, une page de reconnexion si le serveur local est indisponible et une connexion WebView limitée à l’hôte local configuré. Ce paquet de développement utilise une signature de test et cette adresse IP locale; il faudra le reconstruire si l’adresse IP du PC change. Avant de le distribuer, configurez un domaine HTTPS accessible depuis le téléphone et une clé de signature de production.

Le serveur MySQL portable est un processus local, pas un service Windows automatique. Après redémarrage de Windows, relancer `start-db.ps1`. Ce script reconnaît le serveur déjà lancé et ne démarre pas un deuxième exemplaire. Pour arrêter proprement ce serveur :

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\stop-db.ps1
```

Les données persistantes se trouvent dans `.runtime/mysql-data/`. Ce dossier et ses identifiants sont ignorés par Git ; le conserver et le sauvegarder avec la base. Ne pas le supprimer pour « nettoyer » le projet.

## Accès avec phpMyAdmin

Le serveur **Copet - MySQL 8.4 (3308)** est configuré dans `C:/xampp/phpMyAdmin/config.inc.php`, en conservant le serveur XAMPP initial. La configuration précédente est sauvegardée dans `.runtime/phpmyadmin-config.before-mysql.php`.

1. Démarrer Apache dans XAMPP et le serveur local avec `start-db.ps1`.
2. Ouvrir **http://localhost/phpmyadmin/** et sélectionner **Copet - MySQL 8.4 (3308)** dans la liste des serveurs.
3. Se connecter avec `MYSQL_USER` et `MYSQL_PASSWORD` du fichier `.env`.
4. Ouvrir `copet` : les tables `eliteapp_*`, `django_*` et `auth_*` sont présentes.

Le compte de base `copet_app` et le compte administrateur de l’application Django sont deux comptes différents. L’administration Django est accessible à **http://127.0.0.1:8000/admin/** pour les superutilisateurs ; elle est en consultation afin de préserver les validations et l’historique. Les modifications métier se font dans React.

## Configuration et réinstallation

Le projet conserve **Django 6.1.2** et **Python 3.14** avec le backend `django.db.backends.mysql`. Cette installation utilise **MySQL 8.4 LTS** ; garder le port 3308 dans `.env` pour joindre le bon serveur.

Le fichier `.env` est déjà configuré : ne pas l’écraser. La configuration avant le passage à MySQL est sauvegardée dans `.runtime/env.before-mysql`. Les identifiants du serveur portable sont stockés localement dans `.runtime/mysql-admin.cnf` et `.runtime/mysql-app-password.txt` ; aucun secret ne figure dans les scripts suivis par Git.

Sur une nouvelle installation uniquement, depuis la racine du projet :

```powershell
Copy-Item .env.example .env
.\env\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Reporter la clé générée dans `DJANGO_SECRET_KEY`. La devise du projet est le **dinar algérien (`APP_CURRENCY=DZD`)**, affiché avec le code **DZD** dans les montants et les formulaires. Après modification de `.env`, redémarrer Django puis actualiser le navigateur. `APP_TIME_ZONE` définit le fuseau métier ; les heures saisies sont envoyées en UTC et affichées dans le fuseau du navigateur.

`.env` est ignoré par Git. Le fichier exemple ne contient aucun véritable secret. Sans `.env`, le secret de développement change à chaque redémarrage : renseigner une clé stable pour conserver les sessions.

Pour réinstaller le serveur portable dans un nouveau dossier de projet :

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\download-db.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\init-db.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-db.ps1
.\env\Scripts\python.exe scripts\provision-db.py
.\env\Scripts\python.exe manage.py migrate
```

Le téléchargement utilise l’archive officielle via HTTPS et compare son empreinte MD5 à celle publiée par MySQL avant extraction. `init-db.ps1` refuse d’écraser un dossier de données existant. `provision-db.py` configure les comptes et `.env` ; il refuse de remplacer une connexion à une ancienne base contenant des données applicatives sans migration de ces données. Exécuter le provisionnement immédiatement après le premier démarrage pour définir les mots de passe locaux. Le serveur écoute uniquement sur l’adresse locale `127.0.0.1`.

Références : [MySQL Community Server 8.4](https://dev.mysql.com/downloads/mysql/8.4.html) et [initialisation officielle de MySQL](https://dev.mysql.com/doc/refman/8.4/en/data-directory-initialization.html).

## Premier parcours

### CV et expérience des techniciens

Dans **Techniciens → Ajouter un technicien** (ou modifier une fiche), sélectionnez le CV puis cliquez sur **Extraire l’expérience du CV**. Si le champ Expérience est vide, la rubrique reconnue le remplit directement : vérifiez et corrigez ce texte, puis cliquez sur **Enregistrer**. Si une expérience existe déjà ou si la rubrique n’est pas reconnue, vérifiez l’aperçu puis cliquez sur **Utiliser cette expérience** (ou **Remplacer l’expérience par ce texte**) avant d’enregistrer. **Enregistrer** sauvegarde la fiche et le document ; l’extraction seule n’enregistre rien. Les certificats/habilitations sont saisis en texte avec leur organisme et leur validité éventuelle.

Le champ **Expérience professionnelle** dispose d’un éditeur avec gras, italique, soulignement, listes à puces ou numérotées, nouvelles lignes, séparateurs et annuler/rétablir. La mise en forme est conservée dans le profil après enregistrement. Les anciens textes restent lisibles et le collage insère du texte simple. La limite de 20 000 caractères inclut la mise en forme enregistrée.

Les CV sont limités à **10 Mo et 10 pages**, aux formats **PDF, JPG et PNG**. Un PDF protégé par mot de passe doit être déverrouillé avant import. Le CV reste joignable même si l’extraction échoue ; l’expérience peut toujours être saisie manuellement. Si aucune rubrique Expérience n’est reconnue, le texte lu est proposé pour sélectionner les passages utiles.

Le texte des PDF est lu avec [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/page.html). Pour les images et les PDF scannés, le projet utilise le [moteur OCR local de Windows](https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr.ocrengine.trycreatefromuserprofilelanguages), en français si disponible, sinon dans une langue installée du profil Windows. Aucun CV n’est envoyé à un service externe. L’OCR demande Windows et un pack de langue OCR installé ; les PDF avec texte et la saisie manuelle restent utilisables sur les autres systèmes.

Les documents sont conservés dans `.runtime/uploads/technician-cvs/` : sauvegarder ce dossier avec la base MySQL. Ils se téléchargent via l’API authentifiée, uniquement pour les administrateurs et superviseurs internes. Les chefs de projet clients et techniciens ne reçoivent pas les données personnelles ajoutées ni les liens de CV.

Après récupération de cette version sur une autre installation :

```powershell
.\env\Scripts\python.exe -m pip install -r requirements.txt
.\env\Scripts\python.exe manage.py migrate
```

Redémarrer Django après installation des dépendances et migration.

### Circuit des interventions

1. Administrateur : créer une entreprise dans **Clients**.
2. Administrateur : dans **Équipe**, créer un compte « Chef de projet client » et le rattacher à cette entreprise.
3. Administrateur : dans **Techniciens**, ajouter les comptes techniciens ; créer éventuellement un superviseur interne dans **Équipe**.
4. Administrateur ou superviseur : créer un projet, sélectionner le client, son chef de projet et les techniciens ; renseigner le tarif horaire.
5. Technicien : se connecter, saisir un pointage passé, puis cliquer sur **Soumettre**.
6. Chef de projet client : se connecter, vérifier le pointage et cliquer sur **Valider**, ou le refuser en indiquant un motif.
7. Administrateur : créer une facture, sélectionner le projet et les pointages validés, vérifier l’échéance et la taxe, puis émettre.
8. Administrateur : enregistrer le paiement et vérifier le solde.

La taxe est saisie explicitement ; aucune règle fiscale locale n’est présumée. Le document imprimable de cette première version sert au suivi interne : les coordonnées et identifiants de l’entreprise émettrice restent à ajouter avant utilisation comme document commercial définitif.

## Vérification

Les tests rapides utilisent une base SQLite **en mémoire**, créée puis détruite par Django. Ils ne se connectent pas à XAMPP.

```powershell
.\env\Scripts\python.exe manage.py check --settings=coproject.test_settings
.\env\Scripts\python.exe manage.py test eliteapp --settings=coproject.test_settings
.\env\Scripts\python.exe manage.py makemigrations --check --dry-run --settings=coproject.test_settings
cd frontend
npm.cmd test
npm.cmd run build
```

Avec Vite démarré, ouvrir `http://127.0.0.1:5173/tests/experience-editor.html` pour les tests navigateur de l’éditeur d’expérience. Le résultat est affiché dans l’élément `#result` ; les appels API sont simulés et aucune fiche réelle n’est modifiée.

Les 18 tests backend ont également été exécutés avec succès sur MySQL Community Server 8.4.11. Pour les relancer sur ce serveur :

```powershell
.\env\Scripts\python.exe scripts\test-mysql.py
```

Ce script crée une base de test avec un nom aléatoire puis la détruit. Il n’écrit pas dans `copet`. Les tests couvrent le parcours complet, l’isolation entre clients et projets, la protection des coûts internes, la CSRF, les chevauchements, les refus et corrections, le verrouillage des heures, la double facturation, les tarifs figés et les dépassements de paiement. Les courses entre transactions simultanées ne sont pas encore couvertes par cette suite.

## API principale

Toutes les URL se terminent par `/`. L’API utilise des sessions Django, pas des jetons dans le stockage du navigateur. Les réponses de listes sont paginées (`count`, `next`, `previous`, `results`).

| Endpoint | Usage |
| --- | --- |
| `GET /api/auth/session/` | Session courante et jeton CSRF |
| `POST /api/auth/login/` | Connexion avec `username`, `password` et en-tête `X-CSRFToken` |
| `POST /api/auth/logout/` | Déconnexion |
| `/api/users/`, `/api/clients/`, `/api/projects/` | Liste, création, détail et modification par PATCH selon le rôle |
| `/api/time-entries/` | Pointages accessibles à l’utilisateur |
| `POST /api/time-entries/{id}/submit/` | Soumission par le technicien |
| `POST /api/time-entries/{id}/approve/` | Validation par le chef de projet client |
| `POST /api/time-entries/{id}/reject/` | Refus avec `reason` |
| `POST /api/invoices/` | `project`, `entry_ids`, `due_date`, `tax_percent` |
| `POST /api/payments/` | `invoice`, `amount`, `date`, `method`, `reference` |
| `GET /api/dashboard/` | Indicateurs limités au périmètre de l’utilisateur |

## Structure

```text
coproject/             Configuration Django et MySQL
eliteapp/models.py    Données et contraintes
eliteapp/access.py    Périmètres d’accès par rôle
eliteapp/serializers.py Validation des entrées API
eliteapp/services.py Validation des pointages, factures, paiements
eliteapp/views.py     Endpoints et sessions
eliteapp/tests.py     Tests du parcours et des permissions
frontend/src/        Interface React, formulaires, styles et appels API
.env.example         Paramètres locaux à compléter
```

Cette première version est destinée à un seul prestataire avec plusieurs entreprises clientes. Le pointage hors ligne, le chronomètre, la gestion des heures supplémentaires, les frais, les certifications, les avoirs et l’intégration paie ne sont pas encore implémentés. `npm run build` prépare les fichiers React ; le déploiement public et leur hébergement avec Django restent à configurer séparément.

Références techniques : [construction d’une application React](https://react.dev/learn/build-a-react-app-from-scratch), [guide Vite](https://vite.dev/guide/), [backend MySQL de Django](https://github.com/django/django/blob/main/docs/ref/databases.txt).
#   c o p 7  
 