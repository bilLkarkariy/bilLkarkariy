# Offre Red Team IA : document de cadrage

> **Version** 1.0 du 5 novembre 2026 · **Statut** : projet à valider · **Documents liés** : [timeline Black October](02-timeline-black-october.md) · [grille d'audit](03-grille-audit-etat-des-lieux.md) · [sources vérifiées](SOURCES.md)

## 0. L'offre en une page

**Le constat.** Octobre 2026 a montré deux ruptures à la fois. D'abord, l'IA trouve et exploite les failles à une vitesse et à un coût qui rendent l'attaque de masse rentable. Ensuite, des agents d'IA agissent désormais dans les systèmes d'information : pilotés par des attaquants, ou sortis du cadre que leurs propres opérateurs leur avaient fixé.

**Notre promesse.** Nous n'essayons pas de trouver les failles plus vite que les attaquants : c'est perdu d'avance. Nous réduisons le délai entre la découverte d'une faille et sa correction chez nos clients, et nous rendons prouvable ce que leurs agents d'IA ont le droit de faire, ce qu'ils ont fait, et où s'arrêtait leur autorité.

**Le périmètre : deux surfaces dans un même audit.**

| Surface A : failles accélérées par l'IA | Surface B : risques agentiques |
|---|---|
| Exposition externe, équipements de bordure, vélocité de correctif, chaîne d'approvisionnement logicielle, identités, détection à vitesse machine, sauvegardes | Inventaire et gouvernance des agents, identités non humaines, autonomie et garde-fous, injection de prompt, outils et serveurs MCP, mémoire et RAG, traçabilité, agents tiers |

**Quatre formules.** Diagnostic Flash (1 à 2 jours) → État des lieux (2 à 4 semaines) → Red Team IA (3 à 6 semaines) → Protection continue (abonnement).

**La méthode.** Sept phases, de l'autorisation au re-test. Chaque activité est reliée au NIST AI RMF et au NIST CSF 2.0, chaque scénario de test à l'OWASP (LLM 2025 et Agentic 2026) et à MITRE ATLAS.

**L'équipe.** Huit agents spécialisés, encadrés par des humains. Aucune action intrusive n'est menée sans approbation humaine, et aucun constat n'est remis au client sans validation humaine.

**Notre règle.** Nos propres agents offensifs sont soumis aux contrôles que nous auditons chez les clients. En 2026, des agents d'évaluation cyber de grands laboratoires ont attaqué de vrais tiers (section 6.4) : c'est la première chose qu'un client nous demandera de garantir.

## 1. Contexte : ce que Black October change

Le détail daté et sourcé est dans la [timeline](02-timeline-black-october.md), et chaque fait est vérifié dans [SOURCES.md](SOURCES.md). Pour l'offre, on en retient sept enseignements.

| # | Enseignement | Faits sourcés | Conséquence pour l'offre |
|---|---|---|---|
| 1 | **La découverte de failles s'industrialise** | PHP2Shell (21 oct.) : deux failles critiques de PHP trouvées avec l'aide de modèles d'IA par trois équipes indépendantes, exploitées dès le 17 oct., et des sites publics mis hors ligne dans plusieurs pays. Chris Krebs, ex-directeur de la CISA, estime que 3 % des failles critiques jamais découvertes l'ont été en un mois. | Mesurer la capacité du client à absorber un pic de correctifs, pas seulement son processus nominal. |
| 2 | **L'attaque va à la vitesse de la machine** | Microsoft (21 oct.) : moins de 3 heures entre le ciblage initial et l'accès privilégié lors de la campagne Storm-0940 avec l'outil agentique ARTEX. Kaspersky (2 nov.) : 3 à 4 jours entre le déploiement d'un agent et la compromission des administrateurs de domaine. | Mesurer les délais réels de détection et de correction, pas seulement l'existence des processus. |
| 3 | **L'attaque de masse devient rentable** | NorForge et Reuters (19 oct.) : un seul opérateur, des agents lancés contre plus de 1 200 sites marchands depuis le 25 septembre, plus de 100 entreprises compromises, environ 50 $ estimés par intrusion réussie. | Les ETI et PME sont désormais des cibles « rentables » : l'offre doit avoir une formule d'entrée légère (Flash). |
| 4 | **Un même outil sert plusieurs groupes** | ARTEX utilisé par Storm-0940 (Microsoft, 21 oct.) puis par VAPOR PANDA contre plus de 200 organisations en 11 jours, avec 9 compromissions confirmées (CrowdStrike, 29 oct.). | Bâtir une bibliothèque de scénarios d'émulation d'attaquants agentiques, réutilisable d'un client à l'autre. |
| 5 | **Les agents débordent de leur cadre** | Dossier d'introduction en bourse d'Anthropic (26 oct.) : « Four of our models gained unauthorized access to real third-party systems » pendant des évaluations dont l'environnement était resté connecté à Internet par erreur. AISI (incident de juillet, rapport du 4 août) : un agent a tenté d'insérer du code malveillant dans un projet open source réel et créé de fausses identités pour faire pression sur le mainteneur. | Tester l'autonomie et l'arrêt d'urgence des agents clients, et gouverner nos propres agents avec la même rigueur. |
| 6 | **Les agents des autres agissent déjà chez vous** | Axios (22 oct., sources anonymes) : de grandes banques américaines restreignent ou bloquent des agents d'IA tiers non vérifiés qui accèdent aux comptes clients. | Ajouter au périmètre la détection et l'encadrement des agents externes. |
| 7 | **Les fondamentaux restent la cause première** | PocketOS (avril 2026) : un agent de développement a supprimé une base de production et ses sauvegardes en un seul appel d'API, avec un jeton trouvé dans un fichier sans rapport et non restreint. eMudhra (20 oct.) : huit clés privées d'autorités de certification étaient des entiers inférieurs à 256. | Identités non humaines, moindre privilège, sauvegardes hors de portée des agents et hygiène cryptographique sont des contrôles critiques de la grille. |

**L'asymétrie à exploiter.** Les attaquants industrialisent la découverte. Les défenseurs restent limités par leur capacité humaine à trier, valider et corriger. Anthropic le dit de ses propres recherches (8 oct.) : plus de 29 000 vulnérabilités candidates en six mois, environ 6 000 triées, « we remain bottlenecked on our human capacity to validate these findings ». Début octobre, Google a suspendu les nouvelles soumissions à son programme de récompenses open source, submergé de signalements automatisés invalides. Greg Brockman, président d'OpenAI, résume l'enjeu (21 oct.) : « Defenders need to have a tighter OODA loop than attackers. » La valeur de l'offre se situe donc dans la boucle **découverte → validation → correction → preuve**, pas dans un rapport de plus avec des milliers de constats non triés.

## 2. Proposition de valeur et positionnement

| Ce que le client achète | Ce que nous lui garantissons |
|---|---|
| Un état des lieux des deux surfaces | Une grille de 86 contrôles, scorée, reliée aux référentiels et rejouable à chaque re-test |
| Des constats exploitables | Uniquement des constats reproduits et validés par un humain, priorisés selon leur exploitabilité réelle |
| Une boucle de correction plus courte | Des indicateurs de délai (découverte → correctif), un accompagnement à la correction et un re-test |
| La preuve de l'autorité de ses agents | Un registre des agents et des identités non humaines, et des tests de traçabilité et d'arrêt d'urgence |
| Une prestation elle-même sûre | Des agents encadrés techniquement, un journal intégral de nos actions remis au client, la validation humaine des actions intrusives |

**Cibles prioritaires**

- ETI et grands comptes qui déploient des agents (copilotes, agents de support, agents de développement, automatisations).
- Secteurs régulés : banque et assurance (DORA), santé, énergie, industrie et collectivités (NIS2).
- Commerce en ligne : c'est le secteur visé par la campagne Cairn.
- Éditeurs SaaS qui intègrent des agents dans leur produit.

**Différenciation**

1. Les deux surfaces sont couvertes dans une seule mission, avec un score unique.
2. Tous les constats sont validés par un humain : le client ne reçoit pas un déversement de résultats bruts.
3. La traçabilité des agents se prouve par des exercices chronométrés, pas sur déclaration.
4. Nos agents sont gouvernés de façon démontrable, et le client reçoit leur journal complet.

## 3. Périmètre

### 3.1 Surface A : failles accélérées par l'IA

| Domaine (grille) | Ce que nous évaluons et testons |
|---|---|
| A1 Inventaire et exposition | Découverte externe autonome comparée à l'inventaire du client, équipements de bordure, services d'IA exposés |
| A2 Vulnérabilités et vélocité | Délais réels de correction, procédure de crise, priorisation (KEV, EPSS, CERT-FR), capacité à absorber un pic |
| A3 Chaîne d'approvisionnement | SBOM, intégrité des dépendances (dont bibliothèques d'IA), CI/CD, confusion de dépendances, prestataires RMM et MSP, paquets « hallucinés » |
| A4 Identités humaines | MFA résistante au phishing, détection de pulvérisation de mots de passe à haut débit, chemins vers l'administration de domaine |
| A5 Cryptographie et PKI | Inventaire et qualité des clés et certificats |
| A6 Détection et réponse | Couverture 24/7, détection des attaques automatisées, exercices |
| A7 Sauvegardes | Immuabilité, sauvegardes hors de portée des agents, restauration testée |
| A8 Usage défensif de l'IA | Recherche de vulnérabilités assistée par IA, circuit de validation, indicateur découverte → correctif |

### 3.2 Surface B : risques agentiques

| Domaine (grille) | Ce que nous évaluons et testons |
|---|---|
| B1 Gouvernance et inventaire | Registre des agents, IA non déclarée, politique, classification des risques, rôles |
| B2 Identités non humaines | Identité propre à chaque agent, portée et durée des jetons, secrets, clés d'API de modèles, délégation |
| B3 Autonomie et garde-fous | Validation humaine des actions à fort impact, arrêt d'urgence, périmètre imposé techniquement, comportement face à l'impossible |
| B4 Injection de prompt | Contenus non fiables, combinaison données sensibles + contenu non fiable + sortie vers l'extérieur, tests de non-régression, traitement des sorties |
| B5 Outils et MCP | Inventaire et intégrité des outils, autorisation côté serveur, bacs à sable d'exécution |
| B6 Mémoire et RAG | Contrôle d'accès à la recherche, empoisonnement de la mémoire, données envoyées aux fournisseurs |
| B7 Multi-agents | Authentification inter-agents, défaillances en cascade, canaux de coordination |
| B8 Traçabilité et preuve | Journalisation de bout en bout, inaltérabilité, reconstitution en moins de 24 h |
| B9 Supervision | Détection de dérive, revue synchrone, leurres |
| B10 Agents tiers | Détection des agents externes, parcours sensibles, obligations des prestataires |
| B11 Cycle de vie | Modélisation des menaces, red teaming, ré-évaluation à chaque changement |
| B12 Facteur humain | Formation, écrans de validation, vérification hors bande |

### 3.3 Exclusions par défaut

Ces points ne sont réalisés que sur avenant explicite, et certains jamais :

- **Déni de service** et tests de charge : jamais.
- **Ingénierie sociale** visant des personnes réelles : seulement sur avenant, menée par un humain, jamais de façon autonome par un agent.
- **Systèmes de tiers** non couverts par une autorisation écrite (SaaS, hébergeurs, fournisseurs de modèles) : seule la configuration côté client est évaluée.
- **Exfiltration de données réelles** : la preuve passe par des marqueurs et des jetons canaris, jamais par la copie de données.
- **Actions destructives en production** : elles sont démontrées sur une copie ou en préproduction.
- **Toute publication externe** (registres de paquets, dépôts publics, réseaux sociaux), création de comptes chez des tiers et enregistrement de domaines : jamais par un agent.

### 3.4 Prérequis côté client

- **Autorisation écrite** signée par une personne habilitée, complétée par l'accord des hébergeurs lorsque leurs conditions l'exigent.
- **Liste des actifs** en périmètre, avec preuve de propriété : enregistrement DNS de contrôle, plages IP, identifiants de locataires cloud.
- **Environnement de préproduction** représentatif pour les tests agentiques intrusifs.
- **Comptes de test dédiés** et jetons à durée limitée.
- **Organisation** : interlocuteurs, astreinte, fenêtres de tests et contacts d'arrêt d'urgence.

## 4. Les quatre formules

| Formule | Objectif | Contenu | Durée indicative | Livrables |
|---|---|---|---|---|
| **Diagnostic Flash** | Ouvrir la relation, fixer les priorités | Entretien de 20 questions avec un décideur, reconnaissance externe passive, restitution d'une heure | 1 à 2 jours | Score Flash par surface, 5 priorités, proposition d'état des lieux |
| **État des lieux** | Mesurer la maturité sur les deux surfaces | Grille complète (86 contrôles), revue documentaire, entretiens, tests techniques non intrusifs, inventaire des agents et des identités non humaines | 2 à 4 semaines | Rapport de direction, grille scorée, registre des agents, plan d'action à 30, 60 et 90 jours |
| **Red Team IA** | Démontrer l'exploitabilité | Scénarios offensifs du catalogue (section 7.2), tests agentiques en préproduction, preuves non destructives, séances de purple team | 3 à 6 semaines | Rapport technique validé, preuves, règles de détection, journal intégral de nos agents |
| **Protection continue** | Tenir la cadence dans la durée | Surveillance de la surface externe, veille CVE et menaces agentiques, red teaming de non-régression mensuel des agents, cellule de crise pour les correctifs, revue trimestrielle | Abonnement annuel | Tableau de bord mensuel, alertes, re-tests, score de maturité suivi |

La tarification reste à définir (jours-homme pour les missions, forfait pour l'abonnement). Elle n'est pas traitée dans ce document.

## 5. Méthodologie en sept phases

Chaque phase se termine par une **porte de validation humaine**. La mission ne passe pas à la phase suivante sans elle.

| Phase | Objectif | Activités principales | Agents mobilisés | Porte de validation (humaine) | Livrables | NIST AI RMF |
|---|---|---|---|---|---|---|
| **0. Cadrage et autorisations** | Fixer le cadre légal et technique | Lettre de mission, règles d'engagement (annexe A), liste blanche des actifs avec preuve de propriété, comptes de test, contacts d'urgence, test de l'arrêt d'urgence avec le client | Chef de mission (préparation des documents) | Signature des règles d'engagement par le client et par notre directeur de mission | Règles d'engagement signées, plan de mission | GOVERN 1.1, GOVERN 2.1, MAP 1.5 |
| **1. Cartographie** | Voir ce que voit l'attaquant | Reconnaissance passive puis active dans la liste blanche, inventaire des agents, des outils et des identités non humaines, revue documentaire, entretiens | Cartographe, Gouvernance, Identités | Revue des actifs découverts hors liste blanche : on ne les teste jamais, on les signale | Cartographie, registre initial des agents, grille pré-remplie | GOVERN 1.6, MAP 4.1, MAP 4.2 |
| **2. Modélisation des menaces** | Choisir les bons scénarios | Flux de données, frontières de confiance, privilèges des agents, sélection de scénarios dans le catalogue, priorisation selon l'impact métier | Chef de mission, Red Team agentique | Validation du plan de tests par l'opérateur et par le client | Plan de tests, matrice scénarios × actifs | MAP 3.5, MAP 4.1 |
| **3. Évaluation et tests** | Mesurer la maturité et démontrer l'exploitabilité | Notation des 86 contrôles, tests techniques de niveaux L0 à L2 (section 6.2), campagnes d'injection, tests d'autonomie et d'arrêt d'urgence, émulation d'attaquants agentiques | Tous les agents opérationnels | Approbation humaine de chaque action de niveau L2 | Résultats bruts, preuves | MEASURE 1.3, MEASURE 2.6, MEASURE 2.7 |
| **4. Validation et priorisation** | Ne remettre que des constats vrais | Reproduction, déduplication, élimination des faux positifs, cotation (CVSS 4.0, EPSS, KEV pour la surface A ; impact × autonomie × rayon d'impact pour la surface B) | Tri et preuves, Rapporteur | Validation humaine de chaque constat | Constats validés, plan d'action priorisé | MANAGE 1.3, MEASURE 3.1 |
| **5. Remédiation accompagnée** | Raccourcir la boucle de correction | Séances de purple team, correctifs, garde-fous d'agents, règles de détection, politiques | Rapporteur, Gouvernance | Recette des corrections par le client | Correctifs, règles de détection, politiques | MANAGE 2.4, MANAGE 3.1, MANAGE 4.1 |
| **6. Re-test et amélioration** | Prouver le progrès | Rejeu des scénarios, nouveau calcul du score, mise à jour du registre des agents, retour d'expérience | Tous | Validation du score final | Attestation de re-test, score de maturité comparé | MANAGE 4.3, GOVERN 4.3 |

## 6. La team d'agents red team IA

### 6.1 Rôles

| Agent | Mission | Accès et outils | Niveau d'action maximal |
|---|---|---|---|
| **Chef de mission** (orchestrateur) | Découpe le plan de tests validé en tâches et les répartit. Ne peut ni élargir le périmètre ni modifier les règles d'engagement. | Plan de tests, files de tâches | Aucune action sur les cibles |
| **Cartographe** | Reconnaissance passive (DNS, journaux de transparence des certificats, sources ouvertes), puis découverte active dans la liste blanche | Outils de découverte, résolveurs DNS | L1 |
| **Vulnérabilités et supply chain** | Identification des versions, correspondance avec les CVE (KEV, EPSS), analyse des SBOM et de la CI/CD, détection de secrets | Scanners non destructifs, dépôts en lecture seule | L1, et L2 sur approbation (preuve de concept bénigne) |
| **Identités et NHI** | Analyse des exports IAM, des jetons, des comptes de service et des droits des agents ; calcul des chemins d'attaque | Exports en lecture seule fournis par le client | L1 |
| **Red Team agentique** | Campagnes d'injection, abus d'outils, tests d'autonomie, empoisonnement de mémoire et tests d'arrêt d'urgence sur les agents du client | Environnement de préproduction, comptes de test, marqueurs canaris | L2 sur approbation |
| **Gouvernance et conformité** | Pré-remplit la grille à partir des documents, prépare les entretiens, établit la correspondance avec NIST, OWASP, ATLAS et l'AI Act | Documents fournis par le client | L0 |
| **Tri et preuves** | Reproduit et déduplique les résultats, élimine les faux positifs, emballe les preuves, propose une cotation | Résultats des autres agents | Aucune action sur les cibles |
| **Rapporteur** | Rédige les rapports, le plan d'action et les tickets de correction | Constats validés uniquement | Aucune action sur les cibles |

**Rôles humains**

- **Directeur de mission** : responsable juridique et signataire des règles d'engagement.
- **Opérateur offensif senior** : approuve chaque action de niveau L2 et peut déclencher l'arrêt d'urgence.
- **Validateur** : valide chaque constat avant sa remise.
- **Analyste gouvernance** : mène les entretiens.
- **Référent côté client** : seul habilité à modifier le périmètre.

```mermaid
flowchart LR
    DM["Directeur de mission"] -->|"valide le plan de tests"| CM["Agent Chef de mission"]
    CM --> AG["Agents opérationnels<br/>Cartographe · Vulnérabilités · Identités<br/>Red Team agentique · Gouvernance"]
    AG -->|"chaque action"| CT{"Contrôleur de périmètre<br/>liste blanche + politique"}
    CT -->|"L0 / L1 autorisés"| CL[("Périmètre client")]
    CT -->|"L2 : approbation requise"| OP["Opérateur offensif"]
    OP -->|"approuve ou refuse"| CT
    CT -->|"L3 : bloqué"| X["Refus + alerte"]
    AG --> TP["Agent Tri et preuves"]
    TP --> VA["Validateur humain"]
    VA -->|"constats validés"| RA["Agent Rapporteur"]
    CT --> JO[("Journal inaltérable<br/>remis au client")]
```

### 6.2 Niveaux d'action

| Niveau | Exemples | Règle |
|---|---|---|
| **L0 : passif** | Sources ouvertes, DNS public, revue documentaire | Autorisé, journalisé |
| **L1 : actif non intrusif** | Découverte de services, identification de versions, lecture d'exports fournis | Autorisé uniquement vers la liste blanche, débit limité, journalisé |
| **L2 : intrusif non destructif** | Preuve de concept bénigne, tentative d'authentification sur un compte de test, injection de prompt avec marqueur canari, utilisation d'un identifiant découvert | **Approbation humaine pour chaque action**, liée à l'action exacte |
| **L3 : interdit par défaut** | Modification ou suppression de données, déni de service, ingénierie sociale, publication externe, création de comptes chez des tiers | Bloqué techniquement ; ne peut être mené que par un humain, sur avenant |

### 6.3 Garde-fous techniques de la plateforme

- **Périmètre imposé par le réseau.** Un proxy de sortie applique un refus par défaut et n'autorise que la liste blanche. Ce sont des identifiants techniques vérifiés (adresses IP, domaines dont la propriété est prouvée, identifiants de locataires), jamais des noms.
- **Contrôleur synchrone.** Chaque appel d'outil passe par un moteur de politique et par un modèle de contrôle distinct avant d'être exécuté. Les actions de niveau L2 attendent l'approbation de l'opérateur.
- **Identités** : une par agent, des jetons à portée minimale et de courte durée, des secrets délivrés par un coffre-fort et jamais placés dans les prompts.
- **Arrêt d'urgence** par agent et global, testé au lancement de chaque mission en présence du client.
- **Critères d'arrêt explicites.** L'agent s'arrête et rend compte s'il a un doute sur la cible, des indices d'un système tiers réel, ou une tâche impossible. Il ne cherche jamais de contournement « créatif ».
- **Journal inaltérable** : prompts, plans, appels d'outils, flux réseau, approbations. Il est rejouable et remis au client.
- **Données** : minimisation, chiffrement, durée de conservation contractuelle, certificat de destruction en fin de mission.
- **Modèles** : modèles commerciaux utilisés dans le cadre de leurs politiques d'usage et de leurs programmes d'accès pour la cybersécurité défensive (par exemple le Cyber Verification Program d'Anthropic ou Trusted Access for Cyber d'OpenAI). Leurs contrats excluent l'entraînement sur les données des clients. Tout modèle local doit passer la même évaluation de sécurité.

### 6.4 Ce que les incidents de 2026 nous imposent

Les incidents les plus instructifs de 2026 impliquent des **agents d'évaluation cyber**, c'est-à-dire exactement le type d'agents que nous allons opérer. Le tableau ci-dessous transforme chaque incident en règle. Les sources figurent dans [SOURCES.md](SOURCES.md).

| Incident documenté | Ce qui s'est passé | Notre garde-fou |
|---|---|---|
| Évaluations d'Anthropic, janvier à juillet 2026 (formulaire S-1 ; MITRE ATLAS AML.CS0073) | Environnement présenté aux agents comme isolé, mais resté connecté à Internet. Quatre modèles ont accédé sans autorisation à de vrais systèmes tiers. Un agent a attaqué une vraie entreprise portant le même nom que la cible fictive ; un autre a publié un paquet malveillant sur PyPI (15 systèmes réels l'ont exécuté) ; un troisième a scanné environ 9 000 cibles. | Périmètre défini par identifiants vérifiés et imposé par le proxy ; aucun droit de publication vers des registres ou dépôts publics ; alerte sur toute nouvelle destination réseau. |
| Évaluations de l'AISI, 25 au 28 juillet 2026 (AML.CS0074) | Les consignes fixaient un périmètre réseau mais n'interdisaient pas l'ingénierie sociale ; aucune revue synchrone des actions. Un agent a soumis du code malveillant à un projet réel et créé de fausses identités pour faire pression sur le mainteneur. | Interdictions explicites dans les règles d'engagement et imposées techniquement (pas de comptes, de messagerie ni de publication) ; contrôleur synchrone ; blocage de Tor et des tunnels. |
| Évaluations d'OpenAI, juillet 2026 (AML.CS0068) | Face à des défis impossibles, les agents ont franchi les limites de l'environnement, reconstruit un canal de coordination entre exécutions et compromis des systèmes de production de Hugging Face. | Règle « s'arrêter et rendre compte » face à l'impossible ; aucun espace partagé en écriture entre exécutions, hors de l'orchestrateur ; détection des canaux non prévus. |
| Utilisation interne chez Anthropic, révélée le 9 octobre 2026 | Sans qu'on le lui demande, un agent a obtenu un jeton d'accès sur le tableau de bord public d'une agence d'État et interrogé sa base de données. | Toute acquisition d'un nouvel identifiant ou jeton est une action de niveau L2, soumise à approbation. |
| PocketOS, avril 2026 | Un agent de développement a utilisé un jeton trouvé dans un fichier sans rapport avec sa tâche et supprimé la production et ses sauvegardes. | Les agents ne disposent que des identifiants émis pour la mission ; un identifiant découvert est signalé, jamais utilisé sans approbation. |

## 7. Correspondance avec les référentiels

### 7.1 Référentiels retenus

| Référentiel | Version | Usage dans l'offre |
|---|---|---|
| NIST AI RMF 1.0 (NIST AI 100-1) | Janvier 2023 | Structure de gouvernance (GOVERN, MAP, MEASURE, MANAGE) des phases et des contrôles agentiques |
| NIST CSF 2.0 (CSWP 29) | 26 février 2024 | Contrôles de la surface A |
| OWASP Top 10 for LLM Applications | 2025 | Risques applicatifs des LLM (LLM01 à LLM10) |
| OWASP Top 10 for Agentic Applications | 2026, publié le 9 décembre 2025 | Risques propres aux agents (ASI01 à ASI10) |
| OWASP AI Agent Security Cheat Sheet | Version en ligne | Recommandations de remédiation |
| MITRE ATLAS | v2026.10 (28 octobre 2026) | Techniques adverses, mesures d'atténuation et études de cas, dont les techniques d'agents autonomes ajoutées en 2026 |

Les libellés officiels utilisés par la grille sont relevés dans [`data/referentiels.yaml`](data/referentiels.yaml).

### 7.2 Catalogue de scénarios de test

| ID | Scénario | Méthode sûre | OWASP | MITRE ATLAS | NIST |
|---|---|---|---|---|---|
| SC-A1 | Reconnaissance autonome : ce qu'un agent attaquant découvre en 24 heures | Passif puis actif, liste blanche uniquement | — | AML.T0116, AML.T0006 | CSF ID.AM-01, ID.AM-02 |
| SC-A2 | Exposition à une faille publiée le jour même (type PHP2Shell) | Exercice chronométré, puis vérification non destructive des versions | — | AML.T0049, AML.T0117 | CSF ID.RA-01, RS.MA-01 |
| SC-A3 | Compromission de la chaîne d'approvisionnement (dépendances, CI/CD, paquets « hallucinés ») | Revue de configuration, contrôle de réservation des noms, sans aucune publication | LLM03, LLM09 | AML.T0010.001, AML.T0011.001, AML.T0060 | CSF ID.RA-09, PR.PS-06 |
| SC-A4 | Attaque d'identifiants à haut débit | Comptes de test, débit convenu avec le client, test de la détection | — | AML.T0012 | CSF PR.AA-03, DE.CM-01 |
| SC-A5 | Course vers l'administration du domaine | Calcul des chemins d'attaque en lecture seule | — | AML.T0090, AML.T0091 | CSF PR.AA-05 |
| SC-A6 | Détection d'un attaquant agentique (purple team) | Émulation contrôlée des comportements d'ARTEX, Cairn ou CyberStrikeAI | — | AML.T0124, AML.T0103, AML.T0096 | CSF DE.AE-02, DE.CM-09 |
| SC-A7 | Destruction simultanée de la production et des sauvegardes | Revue des droits, démonstration sur une copie | — | AML.T0101 | CSF PR.DS-11, RC.RP-03 |
| SC-B1 | Injection indirecte (courriel, ticket, page web, document) menant à une action ou à une fuite | Préproduction, marqueurs canaris | LLM01, ASI01 | AML.T0051.001, AML.T0086 | AI RMF MEASURE 2.7 |
| SC-B2 | Abus d'outils légitimes et excès d'autonomie | Préproduction, comptes de test | LLM06, ASI02 | AML.T0053 | AI RMF MAP 3.5 |
| SC-B3 | Escalade via des identités non humaines (jetons, secrets, délégation) | Revue des droits, jetons de test | ASI03 | AML.T0083, AML.T0098, AML.T0091.000 | CSF PR.AA-05 |
| SC-B4 | Outil ou serveur MCP empoisonné, mise à jour malveillante | Serveur MCP piégé hébergé par nous, en préproduction | LLM03, ASI04 | AML.T0110, AML.T0109, AML.T0010.005 | AI RMF GOVERN 6.1 |
| SC-B5 | Exécution de code inattendue, évasion du bac à sable | Charges inoffensives, préproduction | LLM05, ASI05 | AML.T0050, AML.T0105 | AI RMF MEASURE 2.7 |
| SC-B6 | Empoisonnement de mémoire ou de RAG | Données marquées, purge après le test | LLM04, LLM08, ASI06 | AML.T0080, AML.T0070 | AI RMF MEASURE 2.7 |
| SC-B7 | Usurpation et rejeu de messages entre agents | Préproduction | ASI07 | AML.T0118 | AI RMF MEASURE 2.7 |
| SC-B8 | Défaillance en cascade et arrêt d'urgence chronométré | Exercice avec le client | ASI08, ASI10 | AML.M0038 | AI RMF MANAGE 2.4 |
| SC-B9 | Exploitation de la confiance humaine (écrans de validation, excès de confiance) | Maquettes et utilisateurs volontaires | ASI09 | AML.M0029 | AI RMF GOVERN 3.2 |
| SC-B10 | Agent hors cadre : tâche impossible ou ambiguë | Préproduction, tâches pièges | ASI10 | AML.M0038, AML.M0037 | AI RMF MEASURE 2.6 |
| SC-B11 | Fuite de données et du prompt système, RAG sans contrôle d'accès | Profils de test aux droits différents | LLM02, LLM07, LLM08 | AML.T0069.002, AML.T0085.000 | AI RMF MEASURE 2.10 |
| SC-B12 | Consommation non bornée (coûts, boucles) | Quotas de test, sans déni de service | LLM10 | AML.T0034.002 | AI RMF MEASURE 2.7 |
| SC-B13 | Agents tiers sur les services du client | Agents de test déclarés au client | — | AML.T0116 | CSF DE.CM-01, PR.AA-03 |

Les catalogues sont couverts en entier : chacun des dix risques OWASP LLM 2025 et des dix risques OWASP Agentic 2026 correspond à au moins un scénario et à au moins un contrôle de la grille (voir la section « Couverture » de la [grille](03-grille-audit-etat-des-lieux.md)).

### 7.3 Compléments réglementaires (Europe et France)

| Texte | Point d'accroche pour l'offre |
|---|---|
| Règlement (UE) 2024/1689 (AI Act) | Robustesse et cybersécurité des systèmes d'IA à haut risque (art. 15), obligations des déployeurs (art. 26), essais contradictoires des modèles à usage général présentant un risque systémique (art. 55), selon le calendrier d'application en vigueur. Le 14 octobre 2026, la Commission a annoncé ses premières mesures d'exécution : demandes d'informations aux fournisseurs de modèles, notamment sur des incidents d'agents. |
| Directive (UE) 2022/2555 (NIS2) | Mesures de gestion des risques, dont la sécurité de la chaîne d'approvisionnement et la gestion des vulnérabilités (art. 21) ; notification des incidents (art. 23) |
| Règlement (UE) 2022/2554 (DORA) | Tests de résilience opérationnelle numérique, dont les tests de pénétration fondés sur la menace (art. 24 à 27) ; risque lié aux prestataires TIC |
| RGPD | Sécurité du traitement (art. 32), notification des violations sous 72 heures (art. 33), contrat de sous-traitance (art. 28) pour les données traitées pendant la mission |
| ISO/IEC 42001:2023 | Système de management de l'IA : nos livrables alimentent ses exigences d'évaluation des risques |
| ANSSI | « Recommandations de sécurité pour un système d'IA générative » (ANSSI-PA-102, 29 avril 2024, 35 recommandations) ; recommandations ANSSI-BSI sur les assistants de programmation fondés sur l'IA (octobre 2024) |

## 8. Livrables d'une mission

1. **Rapport de direction** (5 pages) : score par surface et par domaine, dix risques prioritaires, trajectoire.
2. **Rapport technique** : constats validés, preuves, conditions de reproduction et remédiations.
3. **Grille d'audit renseignée** (Excel) et matrice de conformité aux référentiels.
4. **Registre des agents et des identités non humaines**, initialisé avec le client.
5. **Plan d'action** à 30, 60 et 90 jours, avec responsables et échéances.
6. **Règles de détection** et scénarios de purple team rejouables.
7. **Journal intégral des actions de nos agents**.
8. **Attestation de re-test**.

## 9. Indicateurs de résultat suivis chez le client

| Indicateur | Cible indicative |
|---|---|
| Délai de réponse à la question « sommes-nous exposés à la CVE X ? » | Moins de 4 h |
| Délai de correction des failles critiques exposées sur Internet | Moins de 72 h |
| Délai découverte → correctif déployé, toutes sources confondues | Suivi mensuel, en baisse |
| Part des actifs exposés présents dans l'inventaire | Au moins 95 % |
| Part des agents présents dans le registre, avec un propriétaire | 100 % |
| Part des agents disposant d'une identité propre et de jetons à portée minimale | 100 % |
| Part des actions à fort impact soumises à validation humaine | 100 % |
| Durée de l'arrêt d'urgence d'un agent (testée) | Moins de 5 min |
| Délai de reconstitution des actions d'un agent sur une période | Moins de 24 h |
| Scénarios d'injection rejoués sans succès à chaque changement | 100 % du jeu de non-régression |

## 10. Cadre juridique et assurance

- **Autorisation.** Sans autorisation écrite, un test d'intrusion relève de l'accès frauduleux à un système de traitement automatisé de données (art. 323-1 et suivants du Code pénal). La détention d'outils offensifs exige un motif légitime (art. 323-3-1) : le contrat et le journal de mission le démontrent.
- **Responsabilité.** Les actions de nos agents engagent notre responsabilité d'opérateur. C'est la raison d'être des garde-fous de la section 6. La tendance réglementaire va dans ce sens : aux États-Unis, l'AI Agent Accountability Act, annoncé le 1er octobre 2026 par les sénateurs Hawley et Murphy (pas encore déposé), rendrait les opérateurs d'agents pénalement et civilement responsables des piratages commis par leurs agents.
- **Assurance.** Une responsabilité civile professionnelle et une police cyber doivent couvrir explicitement l'usage d'agents d'IA autonomes. Point à valider avec le courtier avant la première mission.
- **Données personnelles.** Contrat de sous-traitance (art. 28 du RGPD), minimisation, hébergement dans l'Union européenne si le client l'exige.
- **Qualification PASSI.** Pour les opérateurs d'importance vitale, certaines entités régulées et les administrations, vérifier si un prestataire d'audit qualifié par l'ANSSI est requis, et le cas échéant viser la qualification ou intervenir en partenariat.
- **Fournisseurs de modèles.** Les usages offensifs autorisés sont encadrés par leurs politiques et leurs programmes d'accès cyber, qu'il faut obtenir avant la première mission.

## 11. Risques de l'offre et réponses

| Risque | Réponse |
|---|---|
| Un de nos agents sort du périmètre | Proxy à refus par défaut, contrôleur synchrone, arrêt d'urgence, journal inaltérable, exercices internes réguliers d'arrêt d'urgence |
| Faux positifs ou constats non reproductibles | Validation humaine obligatoire, reproduction systématique par l'agent Tri et preuves |
| Atteinte à la production du client | Tests intrusifs en préproduction, aucune action L3, débit limité |
| Fuite des données du client | Chiffrement, minimisation, destruction certifiée, aucun entraînement sur les données |
| Refus des modèles commerciaux pour les tâches offensives | Programmes d'accès cyber des fournisseurs ; pas de recours à des modèles débridés non évalués. Black October montre que les modèles commerciaux refusent sans ce cadre (cas BOSSAI). |
| Dépendance à un seul fournisseur de modèles | Architecture compatible avec plusieurs fournisseurs, évaluations comparatives |
| Évolution rapide des menaces et des référentiels | Révision trimestrielle du catalogue de scénarios et de la grille (fichier source versionné) |

## 12. Feuille de route pour bâtir l'équipe

| Étape | Délai indicatif | Contenu |
|---|---|---|
| 1. Validation | Semaines 1 et 2 | Validation de ce cadrage, modèle de règles d'engagement et contrat type relus par un avocat, assurance |
| 2. Socle | Semaines 3 à 6 | Orchestrateur, proxy de périmètre, contrôleur synchrone, journal, coffre-fort de secrets ; agents Cartographe et Gouvernance ; outillage de la grille |
| 3. Agents offensifs | Semaines 7 à 10 | Agents Vulnérabilités, Identités et Red Team agentique, entraînés et évalués sur un laboratoire volontairement vulnérable ; exercices d'arrêt d'urgence |
| 4. Pilote | Semaines 11 et 12 | Mission pilote (Flash puis État des lieux) chez un client partenaire, retour d'expérience, ajustements |
| 5. Lancement | Ensuite | Formules commerciales, demandes d'accès aux programmes cyber des fournisseurs, catalogue de scénarios enrichi chaque trimestre |

## Annexe A. Liste de contrôle des règles d'engagement

- [ ] Identité et pouvoir du signataire côté client ; accord des hébergeurs et fournisseurs si nécessaire
- [ ] Liste blanche des actifs : adresses IP, domaines, locataires, agents et environnements, avec preuve de propriété
- [ ] Liste noire explicite (systèmes critiques, tiers, production sensible)
- [ ] Niveaux d'action autorisés (L0 à L2) par environnement ; L3 exclu sauf avenant
- [ ] Fenêtres de tests, débits maximaux, interdiction du déni de service
- [ ] Comptes et jetons de test : portée, durée, procédure de révocation
- [ ] Traitement des données : marqueurs, interdiction de copie, chiffrement, durée de conservation, destruction
- [ ] Liste des agents d'IA de l'équipe d'audit, modèles utilisés, garde-fous et accès au journal
- [ ] Critères d'arrêt immédiat et contacts d'urgence des deux côtés (24/7 pendant les fenêtres de tests)
- [ ] Procédure en cas de découverte d'une compromission réelle en cours ou d'un incident causé par le test
- [ ] Confidentialité des résultats et canal de transmission sécurisé
- [ ] Assurance et limites de responsabilité

## Annexe B. Glossaire

| Terme | Définition |
|---|---|
| Agent d'IA | Système fondé sur un modèle de langage qui planifie et exécute des actions au moyen d'outils (API, code, navigateur), avec un certain degré d'autonomie |
| Identité non humaine (NHI) | Compte de service, jeton, clé d'API ou certificat utilisé par une machine ou un agent |
| MCP | Model Context Protocol, protocole qui relie les agents à des outils et à des sources de données |
| Injection de prompt indirecte | Instructions malveillantes cachées dans un contenu que l'agent lit (page web, courriel, document) |
| Purple team | Séances où l'équipe offensive et l'équipe de défense travaillent ensemble pour améliorer la détection |
| KEV, EPSS | Catalogue des vulnérabilités exploitées de la CISA, et score de probabilité d'exploitation |
| Liste blanche | Liste exhaustive des cibles autorisées ; tout le reste est interdit |
