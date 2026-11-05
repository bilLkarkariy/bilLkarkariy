# Grille d'audit « état des lieux » — Red Team IA

> Version 1.0 du 2026-11-05 · 86 points de contrôle · 20 questions Flash. Fichier généré par `tools/build_grille.py` depuis `data/grille.yaml` : modifier le YAML, pas ce fichier.

Version de travail : **[03-grille-audit-etat-des-lieux.xlsx](03-grille-audit-etat-des-lieux.xlsx)**, avec saisie guidée, scores calculés, synthèse, graphique et plan d'action. Cette page sert à la lecture, à la revue et au diff.

## Mode d'emploi

1. **Diagnostic Flash** (avant-vente, environ 45 min) : 20 questions posées à un décideur, réponses Oui / Partiel / Non / Ne sait pas.
2. **Audit** : pour chaque point de contrôle, collecter les preuves attendues puis noter la maturité de 0 à 4 (ou N/A).
3. **Score d'un domaine** = somme (maturité × criticité) ÷ somme (4 × criticité), sur les contrôles évalués.

| Maturité | Libellé | Définition |
|---|---|---|
| 0 | Inexistant | Aucune pratique, ou pratique inconnue des interlocuteurs. |
| 1 | Initial | Pratique ponctuelle, dépendante de personnes, non documentée. |
| 2 | Défini | Pratique documentée, mais appliquée partiellement ou sans preuve. |
| 3 | Maîtrisé | Pratique appliquée sur tout le périmètre, preuves disponibles. |
| 4 | Optimisé | Pratique mesurée, testée (exercice, red team) et améliorée en continu. |

| Criticité | Libellé | Définition |
|---|---|---|
| 3 | Critique | Défaillance exploitable directement ou à impact majeur ; vecteur observé lors de Black October. |
| 2 | Important | Défaillance qui aggrave fortement un incident ou en retarde la détection. |
| 1 | Utile | Bonne pratique de maturité ; impact indirect. |

Niveaux : **Critique** < 25 % · **Fragile** < 50 % · **Intermédiaire** < 75 % · **Robuste** ≥ 75 %.

## Diagnostic Flash

| N° | Surface | Question | Contrôle |
|---|---|---|---|
| 1 | A | Avez-vous un inventaire à jour (moins d'un mois) de tout ce que vous exposez sur Internet, filiales et prestataires compris ? | [A1.1](#a11) |
| 2 | A | Le jour où une faille critique comme PHP2Shell est publiée, savez-vous en moins de 4 heures quels serveurs sont concernés ? | [A1.2](#a12) |
| 3 | A | Mesurez-vous le délai réel entre la publication d'une faille critique et son correctif en production ? Est-il inférieur à 72 heures ? | [A2.1](#a21) |
| 4 | A | Avez-vous une procédure, déjà exercée, pour décider en quelques heures de couper ou protéger un service exposé à une faille critique ? | [A2.2](#a22) |
| 5 | A | Pouvez-vous lister en une heure toutes les applications qui utilisent une bibliothèque donnée (par exemple LiteLLM), versions comprises ? | [A3.1](#a31) |
| 6 | A | Une nouvelle version piégée d'une bibliothèque publiée ce matin sur PyPI ou npm pourrait-elle arriver automatiquement dans vos builds ? | [A3.2](#a32) |
| 7 | A | Vos administrateurs et accès distants utilisent-ils tous une MFA résistante au phishing, protocoles hérités désactivés ? | [A4.1](#a41) |
| 8 | A | Une alerte critique déclenchée un samedi à 3 h du matin est-elle prise en charge en moins d'une heure ? | [A6.1](#a61) |
| 9 | A | Existe-t-il un seul compte, humain ou agent, capable de supprimer à la fois une base de production et ses sauvegardes ? | [A7.1](#a71) |
| 10 | A | Votre direction suit-elle un indicateur du délai entre la découverte d'une faille et son correctif en production ? | [A8.3](#a83) |
| 11 | B | Pouvez-vous lister tous les agents d'IA qui agissent dans votre SI aujourd'hui, avec leurs droits et leur propriétaire ? | [B1.1](#b11) |
| 12 | B | Un nouvel agent d'IA peut-il être branché sur vos outils sans validation formelle de la sécurité ? | [B1.2](#b12) |
| 13 | B | Vos agents d'IA ont-ils chacun leur propre identité, ou utilisent-ils les comptes et jetons de vos collaborateurs ? | [B2.1](#b21) |
| 14 | B | Un agent de développement pourrait-il, avec son jeton actuel, supprimer une base de production ? | [B2.2](#b22) |
| 15 | B | Vos agents peuvent-ils supprimer, payer, envoyer à l'extérieur ou modifier des droits sans validation humaine ? | [B3.1](#b31) |
| 16 | B | Si un agent se met à agir hors de ses instructions, pouvez-vous le couper en moins de 5 minutes ? L'avez-vous déjà testé ? | [B3.2](#b32) |
| 17 | B | Un de vos agents lit-il des contenus externes (courriels, web) tout en ayant accès à des données sensibles et la possibilité d'envoyer des informations à l'extérieur ? | [B4.2](#b42) |
| 18 | B | Savez-vous quels serveurs MCP et connecteurs vos agents utilisent, et qui peut les modifier ? | [B5.1](#b51) |
| 19 | B | Pouvez-vous prouver, pour une action donnée d'un agent, qui l'a demandée, quelles données il a lues et ce qu'il a modifié ? | [B8.1](#b81) |
| 20 | B | Savez-vous aujourd'hui quelle part du trafic de vos espaces clients ou de votre site provient d'agents d'IA ? | [B10.1](#b101) |

## Surface A — Failles accélérées par l'IA

La surface classique (applications, équipements, dépendances, identités), désormais découverte et exploitée à vitesse machine.

### A1 · Inventaire et surface d'exposition

*Savoir ce qui est exposé avant qu'un agent de reconnaissance autonome ne le découvre.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="a11"></a>**A1.1** ★ | L'inventaire des actifs exposés sur Internet (domaines, sous-domaines, adresses IP, applications web, API, interfaces d'administration) est exhaustif, couvre filiales et prestataires, et est mis à jour au moins mensuellement. | Export daté de l'inventaire ou de l'outil de gestion de surface d'attaque ; écart mesuré entre l'inventaire et la découverte externe réalisée par l'auditeur.<br>*Revue documentaire ; test technique (découverte passive puis active dans le périmètre autorisé)* | 3 | CSF : ID.AM-01, ID.AM-02<br>ATLAS : AML.T0116, AML.T0006 | Campagne Cairn contre 1 200 sites marchands (19 oct.), Cadre multi-agents contre Taïwan (juil. 2026) |
| <a id="a12"></a>**A1.2** ★ | Pour chaque application exposée, la pile technique et ses versions (langage et environnement d'exécution comme PHP, framework, CMS, serveur web) sont connues, ce qui permet de répondre en moins de 4 heures à la question « sommes-nous exposés à cette CVE ? ». | Inventaire logiciel (SBOM ou CMDB) ; exercice chronométré sur une CVE récente, par exemple CVE-2026-109618 / CVE-2026-109619.<br>*Exercice chronométré ; revue documentaire* | 3 | CSF : ID.AM-02, ID.RA-01<br>ATLAS : AML.T0049 | PHP2Shell (21 oct. 2026) |
| <a id="a13"></a>**A1.3** | Les équipements de bordure et embarqués (pare-feu, VPN, routeurs, NAS, caméras, objets connectés, appliances) sont inventoriés avec leur firmware et leurs composants logiciels, et leurs interfaces d'administration ne sont pas exposées sur Internet. | Inventaire des équipements avec versions de firmware ; résultat du scan des interfaces d'administration exposées.<br>*Revue documentaire ; test technique* | 3 | CSF : ID.AM-01, PR.PS-03, PR.IR-01<br>ATLAS : AML.T0049, AML.T0122 | ANSSI : le risque PHP gagne les équipements (28 oct.) |
| <a id="a14"></a>**A1.4** | Les services d'IA exposés (points d'accès de modèles, passerelles LLM, notebooks, serveurs MCP, consoles d'agents) figurent dans l'inventaire et aucun n'est accessible publiquement sans authentification. | Liste des services d'IA exposés ; tests d'accès anonymes réalisés par l'auditeur.<br>*Test technique ; revue documentaire* | 2 | CSF : ID.AM-02, PR.AA-03<br>ATLAS : AML.T0132, AML.T0006.002 | — |
| <a id="a15"></a>**A1.5** | Une surveillance continue de la surface externe alerte sur toute nouvelle exposition (sous-domaine, port, certificat, service) en moins de 24 heures. | Configuration de l'outil de surveillance ; exemples d'alertes récentes et délais de traitement.<br>*Revue documentaire ; échantillonnage* | 2 | CSF : DE.CM-01, ID.AM-01<br>ATLAS : AML.T0116 | Campagne Cairn contre 1 200 sites marchands (19 oct.) |

### A2 · Vulnérabilités et vélocité de correctif

*Tenir la cadence quand le volume de failles critiques explose : l'asymétrie entre découverte par la machine et correction par l'humain.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="a21"></a>**A2.1** ★ | Des délais maximaux de correction sont définis par criticité et par exposition (par exemple 24 à 48 heures pour une faille critique exploitée ou exposée sur Internet) ; le délai réel est mesuré et respecté. | Politique de gestion des vulnérabilités ; délais réels de correction sur les 6 derniers mois ; taux de respect.<br>*Revue documentaire ; échantillonnage* | 3 | CSF : ID.RA-01, PR.PS-02 | PHP2Shell (21 oct. 2026), Krebs : 3 % des failles critiques en un mois (23 oct.) |
| <a id="a22"></a>**A2.2** ★ | Une procédure de crise pour les correctifs existe : veille CERT-FR et éditeurs, décision de mise hors ligne préventive, mesures compensatoires (filtrage applicatif, désactivation de fonctionnalité), communication. Elle a été exercée dans les 12 derniers mois. | Procédure ; compte rendu d'exercice ou retour d'expérience sur PHP2Shell.<br>*Revue documentaire ; entretien* | 3 | CSF : ID.RA-02, RS.MA-01, ID.IM-04 | PHP2Shell (21 oct. 2026) |
| <a id="a23"></a>**A2.3** | La priorisation s'appuie sur l'exploitabilité réelle (catalogue KEV de la CISA, score EPSS, avis CERT-FR, exposition Internet) et pas uniquement sur le score CVSS. | Règles de priorisation ; exemples de tickets montrant l'usage de ces critères.<br>*Revue documentaire ; échantillonnage* | 2 | CSF : ID.RA-05, ID.RA-02 | — |
| <a id="a24"></a>**A2.4** | La capacité de correction est dimensionnée pour absorber un pic (trois à dix fois plus de vulnérabilités critiques en un mois) : astreinte, automatisation du déploiement, renfort externe contractualisé à l'avance. | Plan de capacité ; chiffres et délais du dernier pic ; contrats de renfort.<br>*Entretien ; revue documentaire* | 2 | CSF : ID.RA-05, PR.PS-02, GV.RR-02 | Krebs : 3 % des failles critiques en un mois (23 oct.), Anthropic : 29 000 candidates, 6 000 triées (8 oct.) |
| <a id="a25"></a>**A2.5** | Un processus de réception des signalements de vulnérabilités existe (fichier security.txt, politique de divulgation coordonnée) et peut absorber des signalements produits en masse par des outils d'IA. | security.txt publié ; politique de divulgation ; volumétrie et délais de traitement des signalements.<br>*Test technique ; revue documentaire* | 1 | CSF : ID.RA-08, RS.MA-02 | Anthropic : 29 000 candidates, 6 000 triées (8 oct.) |

### A3 · Chaîne d'approvisionnement logicielle (dont bibliothèques d'IA)

*Empêcher qu'une dépendance compromise (paquet, action CI, outil de prestataire) n'ouvre la porte aux secrets et aux clés d'API.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="a31"></a>**A3.1** ★ | Les dépendances de chaque application en production sont inventoriées (SBOM), y compris les bibliothèques d'IA : SDK de modèles, passerelles LLM de type LiteLLM, frameworks d'agents. | SBOM par application ; liste des bibliothèques d'IA en production.<br>*Revue documentaire ; test technique (analyse de composition)* | 3 | CSF : ID.AM-02, GV.SC-07<br>OWASP : LLM03:2025<br>ATLAS : AML.T0010.001, AML.M0023 | LiteLLM 1.107.0 piégée (21 oct.) |
| <a id="a32"></a>**A3.2** ★ | Les dépendances sont épinglées avec vérification d'intégrité (fichiers de verrouillage, empreintes), installées depuis un miroir interne avec quarantaine des nouvelles versions et détection des paquets malveillants. | Fichiers de verrouillage ; configuration du miroir ou du proxy de paquets ; règles de quarantaine.<br>*Revue documentaire ; test technique* | 3 | CSF : ID.RA-09, PR.PS-01<br>OWASP : LLM03:2025<br>ATLAS : AML.T0011.001, AML.T0010.001 | LiteLLM 1.107.0 piégée (21 oct.) |
| <a id="a33"></a>**A3.3** | Les chaînes CI/CD sont durcies : actions et outils tiers épinglés par empreinte de commit, secrets à portée minimale et éphémères (fédération OIDC), séparation build et publication, artefacts signés avec provenance. | Définitions des pipelines ; inventaire des secrets CI ; politique de signature.<br>*Revue de configuration* | 3 | CSF : PR.PS-06, PR.AA-05<br>ATLAS : AML.T0010.001 | LiteLLM 1.107.0 piégée (21 oct.) |
| <a id="a34"></a>**A3.4** | Les noms de paquets internes sont protégés contre la confusion de dépendances (noms réservés sur les registres publics, registres privés prioritaires). | Liste des paquets internes ; vérification de leur réservation sur les registres publics.<br>*Test technique* | 2 | CSF : ID.RA-09<br>ATLAS : AML.T0010.001, AML.T0011.001 | Agents Claude hors périmètre en évaluation (janv.-juil. 2026) |
| <a id="a35"></a>**A3.5** | Les outils d'administration à distance et les prestataires infogérés (RMM, MSP, éditeurs SaaS) sont évalués ; leurs accès sont nominatifs, limités et surveillés ; un plan existe en cas de compromission du fournisseur. | Registre des prestataires à accès privilégié ; clauses contractuelles ; journaux d'accès des prestataires.<br>*Revue documentaire ; échantillonnage* | 2 | CSF : GV.SC-07, GV.SC-08, DE.CM-06 | Storm-0940 et ARTEX via ConnectWise (21 oct.) |
| <a id="a36"></a>**A3.6** | Les dépendances proposées par des assistants d'IA sont vérifiées avant installation (existence, ancienneté, réputation, mainteneur) pour éviter les paquets « hallucinés » que des attaquants enregistrent à l'avance. | Règle de développement ; contrôle automatique des nouvelles dépendances en CI.<br>*Revue documentaire ; test technique* | 2 | CSF : ID.RA-09<br>OWASP : LLM09:2025, LLM03:2025<br>ATLAS : AML.T0060, AML.T0062 | — |

### A4 · Identités humaines et accès

*Résister aux attaques d'identifiants menées à un débit que seuls des agents automatisés atteignent.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="a41"></a>**A4.1** ★ | Une authentification multifacteur résistante au phishing (FIDO2, clés d'accès, carte à puce) est imposée aux administrateurs et aux accès distants ; les protocoles d'authentification hérités sont désactivés. | Politiques d'accès conditionnel ; rapport de couverture MFA ; état des protocoles hérités.<br>*Revue de configuration* | 3 | CSF : PR.AA-03<br>ATLAS : AML.T0012 | Storm-0940 et ARTEX via ConnectWise (21 oct.) |
| <a id="a42"></a>**A4.2** | Les attaques par pulvérisation de mots de passe et par bourrage d'identifiants à haut débit sont détectées et freinées (limitation de débit, verrouillage intelligent, alertes sur volumes anormaux par locataire). | Règles de détection ; alertes des 3 derniers mois ; seuils configurés.<br>*Revue de configuration ; test technique (contrôlé)* | 3 | CSF : DE.CM-01, DE.CM-03<br>ATLAS : AML.T0012 | Storm-0940 et ARTEX via ConnectWise (21 oct.) |
| <a id="a43"></a>**A4.3** | Les comptes à privilèges sont cloisonnés (modèle en tiers, comptes d'administration dédiés, accès juste-à-temps) et les chemins d'attaque vers l'administration du domaine et du cloud sont cartographiés puis réduits. | Cartographie des chemins d'attaque (type graphe AD/Entra) ; nombre de comptes à privilèges ; politique d'accès juste-à-temps.<br>*Test technique (collecte en lecture seule) ; revue documentaire* | 3 | CSF : PR.AA-05<br>ATLAS : AML.T0090, AML.T0091 | VAPOR PANDA (29 oct.) et CyberStrikeAI (2 nov.) |
| <a id="a44"></a>**A4.4** | Les droits sont revus au moins tous les six mois et les comptes inactifs ou orphelins sont désactivés. | Comptes rendus de revue des droits ; statistiques des comptes inactifs.<br>*Échantillonnage* | 1 | CSF : PR.AA-01, PR.AA-05 | — |

### A5 · Cryptographie et PKI : les fondamentaux

*Rappel de Black October : une partie des failles du mois venaient d'erreurs humaines élémentaires, pas de l'IA.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="a51"></a>**A5.1** | Les certificats et clés (TLS, signature de code, PKI interne) sont inventoriés avec propriétaire, algorithme, taille de clé et date d'expiration. | Inventaire des certificats ; rapport d'outil de découverte.<br>*Revue documentaire ; test technique* | 2 | CSF : ID.AM-08, PR.DS-01 | eMudhra : clés d'AC triviales (17-20 oct.) |
| <a id="a52"></a>**A5.2** | Les clés sont générées avec des générateurs d'aléa conformes, protégées (HSM ou coffre-fort de secrets) et leur qualité est contrôlée (clés faibles, réutilisées ou trop courtes). | Procédure de génération ; résultats de contrôle de qualité des clés.<br>*Revue documentaire ; test technique* | 2 | CSF : PR.DS-01 | eMudhra : clés d'AC triviales (17-20 oct.) |
| <a id="a53"></a>**A5.3** | La dépendance aux autorités de certification tierces est maîtrisée : renouvellement automatisé (ACME) et plan de remplacement si une autorité est révoquée ou n'est plus reconnue. | Liste des AC utilisées ; plan de bascule ; taux d'automatisation.<br>*Entretien ; revue documentaire* | 1 | CSF : GV.SC-07, ID.AM-08 | eMudhra : clés d'AC triviales (17-20 oct.) |

### A6 · Détection et réponse à vitesse machine

*Détecter et contenir avant qu'un agent attaquant passe de l'accès initial à l'administration du domaine.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="a61"></a>**A6.1** ★ | La détection et la réponse couvrent 24 h/24 et 7 j/7 les actifs exposés et les identités (SOC interne ou service managé), avec une prise en charge des alertes critiques en moins d'une heure. | Contrat ou organisation SOC ; délais de prise en charge mesurés ; périmètre couvert.<br>*Revue documentaire ; échantillonnage* | 3 | CSF : DE.CM-01, DE.CM-09, RS.MA-01 | Campagne Cairn contre 1 200 sites marchands (19 oct.), VAPOR PANDA (29 oct.) et CyberStrikeAI (2 nov.) |
| <a id="a62"></a>**A6.2** | Les journaux (web, identité, EDR, cloud, DNS) sont centralisés, horodatés de façon cohérente et conservés assez longtemps pour une investigation a posteriori (12 mois recommandés). | Architecture de journalisation ; durées de conservation par source.<br>*Revue de configuration* | 2 | CSF : PR.PS-04, DE.AE-03 | — |
| <a id="a63"></a>**A6.3** | Des scénarios de détection visent les attaques automatisées : rafales d'exploitation multi-cibles, enchaînement rapide reconnaissance → exploitation, trafic de serveurs vers des API de modèles d'IA, outillage d'agents (MCP, frameworks) sur des hôtes non autorisés. | Règles de détection correspondantes ; résultats de tests de détection.<br>*Revue de configuration ; test technique (émulation)* | 2 | CSF : DE.AE-02, DE.CM-09<br>ATLAS : AML.T0124, AML.T0103, AML.T0096 | VAPOR PANDA (29 oct.) et CyberStrikeAI (2 nov.), Cadre multi-agents contre Taïwan (juil. 2026), Agent Hermes et DeepSeek (Unit 42, mai 2026) |
| <a id="a64"></a>**A6.4** | Le plan de réponse à incident est testé chaque année par un exercice de crise incluant un scénario d'attaque automatisée massive, la décision d'isolement et les notifications réglementaires (RGPD, NIS2, DORA selon le cas). | Plan de réponse ; compte rendu du dernier exercice et actions correctives.<br>*Revue documentaire ; entretien* | 2 | CSF : RS.MA-01, ID.IM-02, RS.CO-02 | — |

### A7 · Sauvegardes et résilience

*Garantir qu'aucune identité, humaine ou agent, ne peut détruire à la fois la production et ses sauvegardes.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="a71"></a>**A7.1** ★ | Les sauvegardes critiques sont immuables ou hors ligne, hors de portée des comptes d'administration courants, des comptes de service et des agents d'IA ; leur restauration est testée au moins tous les six mois. | Architecture de sauvegarde ; matrice des identités ayant un droit de suppression ; procès-verbaux de tests de restauration.<br>*Revue de configuration ; exercice* | 3 | CSF : PR.DS-11, RC.RP-03<br>ATLAS : AML.T0101 | PocketOS (avr. 2026) |
| <a id="a72"></a>**A7.2** | Des objectifs de reprise (RTO/RPO) sont définis pour les services critiques et un mode dégradé permet de mettre un service hors ligne sans arrêter l'activité. | Analyse d'impact ; procédures de mode dégradé ; résultats de tests.<br>*Revue documentaire ; entretien* | 2 | CSF : RC.RP-01, PR.IR-03 | PHP2Shell (21 oct. 2026) |

### A8 · Usage défensif de l'IA et boucle de remédiation

*Raccourcir la boucle découverte → correctif, là où se joue l'avantage du défenseur.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="a81"></a>**A8.1** | Des outils d'IA sont utilisés pour rechercher des vulnérabilités (revue de code, analyse de configuration, fuzzing assisté) sur les applications critiques, dans un cadre validé (données, fournisseurs, périmètre). | Liste des outils et du périmètre ; validation sécurité et juridique ; résultats obtenus.<br>*Entretien ; revue documentaire* | 2 | AI RMF : GOVERN 6.1<br>CSF : ID.RA-01, ID.IM-02 | PHP2Shell (21 oct. 2026), Anthropic : 29 000 candidates, 6 000 triées (8 oct.) |
| <a id="a82"></a>**A8.2** | Les découvertes issues d'outils d'IA passent par un circuit de tri, de déduplication et de validation humaine avant d'entrer dans le backlog de correction ; la capacité de validation est suivie. | Processus de tri ; indicateurs de volume, de faux positifs et de délais de validation.<br>*Revue documentaire ; échantillonnage* | 2 | CSF : RS.MA-02, ID.RA-01 | Anthropic : 29 000 candidates, 6 000 triées (8 oct.) |
| <a id="a83"></a>**A8.3** ★ | Le délai découverte → correctif déployé est mesuré de bout en bout, fait l'objet d'un objectif et est suivi par la direction. | Tableau de bord ; comptes rendus de comité.<br>*Revue documentaire* | 2 | CSF : GV.OV-01, ID.IM-01 | Anthropic : 29 000 candidates, 6 000 triées (8 oct.) |

## Surface B — Risques agentiques

Les agents d'IA de l'organisation (et ceux de tiers) : ce qu'ils peuvent lire, faire, et ce qu'on peut prouver de leurs actions.

### B1 · Gouvernance et inventaire des systèmes d'IA

*On ne protège pas un agent dont on ignore l'existence (shadow AI).*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="b11"></a>**B1.1** ★ | Un registre des systèmes d'IA et des agents existe : agents internes, SaaS, copilotes, agents de code, agents de navigateur, automatisations sans code. Pour chacun : propriétaire, fournisseur, modèle, données accessibles, outils, niveau d'autonomie. | Registre ; comparaison avec les flux réseau vers les fournisseurs d'IA et les applications SaaS détectées.<br>*Revue documentaire ; test technique (découverte)* | 3 | AI RMF : GOVERN 1.6, MAP 4.1<br>ATLAS : AML.M0023 | SailPoint : 92 %, 44 %, 52 % (mai 2025) |
| <a id="b12"></a>**B1.2** ★ | Une politique d'usage de l'IA et des agents est adoptée par la direction : usages autorisés et interdits, données autorisées, processus d'approbation d'un nouvel agent, responsabilités. | Politique signée ; processus d'approbation ; exemples de dossiers approuvés ou refusés.<br>*Revue documentaire ; entretien* | 3 | AI RMF : GOVERN 1.4, GOVERN 2.3 | SailPoint : 92 %, 44 %, 52 % (mai 2025) |
| <a id="b13"></a>**B1.3** | L'usage d'IA non déclarée est détecté : flux vers des API de modèles, extensions de navigateur, comptes personnels, agents installés sur les postes. | Règles de détection (proxy, CASB, EDR) ; volumétrie des usages non déclarés détectés.<br>*Test technique ; revue de configuration* | 2 | AI RMF : GOVERN 1.6<br>CSF : DE.CM-03<br>ATLAS : AML.T0112.000 | — |
| <a id="b14"></a>**B1.4** | Chaque agent est classé par niveau de risque (données, actions, autonomie, exposition) et les obligations réglementaires associées sont identifiées (AI Act, notamment le rôle de déployeur ; RGPD ; NIS2 ou DORA selon le secteur). | Grille de classification ; analyse réglementaire par agent.<br>*Revue documentaire* | 2 | AI RMF : GOVERN 1.1, MAP 1.5 | — |
| <a id="b15"></a>**B1.5** | Les rôles sont définis pour chaque agent : propriétaire, responsable de la supervision humaine, contact en cas d'incident ; la direction arbitre les risques résiduels. | Matrice RACI ; fiches agents ; décisions d'acceptation de risque.<br>*Revue documentaire ; entretien* | 2 | AI RMF : GOVERN 2.1, GOVERN 3.2 | — |

### B2 · Identités non humaines et privilèges des agents

*Un agent ne doit jamais détenir plus de droits que la tâche n'en exige.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="b21"></a>**B2.1** ★ | Chaque agent dispose de sa propre identité (compte de service ou identité de charge de travail dédiée), distincte des comptes humains ; aucun agent n'opère avec les identifiants personnels d'un employé. | Liste des identités d'agents ; contrôle par échantillonnage des identifiants utilisés par les agents.<br>*Revue de configuration ; échantillonnage* | 3 | CSF : PR.AA-01<br>OWASP : LLM06:2025, ASI03<br>ATLAS : AML.M0026 | PocketOS (avr. 2026), Agents tiers dans les comptes bancaires (22 oct.) (sources partielles) |
| <a id="b22"></a>**B2.2** ★ | Les jetons et clés des agents sont à portée minimale (ressources, actions, environnements) et de courte durée de vie ; aucun n'autorise d'action destructive hors du périmètre de la tâche (pas de jeton d'administration de production pour un agent de développement). | Inventaire des jetons d'agents avec portée et durée ; revue des droits effectifs.<br>*Revue de configuration ; test technique* | 3 | CSF : PR.AA-05<br>OWASP : LLM06:2025, ASI03<br>ATLAS : AML.T0091.000, AML.M0028 | PocketOS (avr. 2026) |
| <a id="b23"></a>**B2.3** | Aucun secret n'est stocké dans les prompts, fichiers de configuration d'agents, mémoires ou dépôts ; les secrets sont délivrés par un coffre-fort avec rotation et journalisation. | Résultats d'analyse de secrets sur les dépôts et configurations d'agents ; configuration du coffre-fort.<br>*Test technique (analyse de secrets)* | 3 | OWASP : LLM02:2025, ASI03<br>ATLAS : AML.T0083, AML.T0055, AML.T0098 | LiteLLM 1.107.0 piégée (21 oct.), Agents d'évaluation de l'AISI (juil. 2026) |
| <a id="b24"></a>**B2.4** | Les clés d'API des fournisseurs d'IA sont inventoriées, plafonnées (budgets, quotas), surveillées et révocables en quelques minutes. | Inventaire des clés ; quotas configurés ; procédure de révocation testée.<br>*Revue de configuration ; exercice* | 2 | OWASP : LLM10:2025<br>ATLAS : AML.T0034, AML.T0012 | LiteLLM 1.107.0 piégée (21 oct.) |
| <a id="b25"></a>**B2.5** | La délégation d'autorité est explicite et vérifiable : un agent agissant pour un utilisateur ne dépasse jamais les droits de cet utilisateur et n'hérite pas des privilèges d'un autre agent. | Architecture de délégation (OAuth, jetons d'échange) ; tests d'escalade de privilèges.<br>*Test technique* | 2 | OWASP : ASI03<br>ATLAS : AML.M0027, AML.M0037 | — |

### B3 · Autonomie et garde-fous d'action

*Borner ce qu'un agent peut faire seul, et pouvoir l'arrêter immédiatement.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="b31"></a>**B3.1** ★ | Les actions de chaque agent sont classées par impact (lecture, écriture réversible, irréversible, externe). Les actions irréversibles ou à fort impact (suppression, paiement, envoi externe, changement de droits, mise en production) exigent une validation humaine portant sur l'action exacte. | Matrice des actions par agent ; configuration des validations ; journaux de validations.<br>*Revue de configuration ; test technique* | 3 | AI RMF : MAP 3.5, GOVERN 3.2<br>OWASP : LLM06:2025, ASI02<br>ATLAS : AML.M0029 | PocketOS (avr. 2026) |
| <a id="b32"></a>**B3.2** ★ | Un arrêt d'urgence permet de suspendre un agent, ou l'ensemble des agents, en moins de 5 minutes (révocation des jetons, coupure des outils), et il a été testé. | Procédure d'arrêt ; compte rendu de test avec durée mesurée.<br>*Exercice* | 3 | AI RMF : MANAGE 2.4<br>OWASP : ASI10 | Agents d'évaluation de l'AISI (juil. 2026), Agents OpenAI et Hugging Face (juil. 2026) |
| <a id="b33"></a>**B3.3** | Le périmètre d'action est imposé techniquement (filtrage réseau sortant par liste blanche, bac à sable, quotas) et non par les seules instructions données au modèle. | Règles de filtrage sortant des environnements d'agents ; architecture de bac à sable.<br>*Revue de configuration ; test technique* | 3 | AI RMF : MEASURE 2.7<br>OWASP : LLM06:2025, ASI10<br>ATLAS : AML.M0032, AML.T0105, AML.T0097 | Agents Claude hors périmètre en évaluation (janv.-juil. 2026), Agents d'évaluation de l'AISI (juil. 2026), Agents OpenAI et Hugging Face (juil. 2026) |
| <a id="b34"></a>**B3.4** | Des limites de débit, de budget et de nombre d'actions par tâche bornent le rayon d'impact d'un agent défaillant ou détourné (disjoncteurs). | Configuration des limites ; alertes de dépassement.<br>*Revue de configuration* | 2 | OWASP : LLM10:2025, ASI08<br>ATLAS : AML.M0036, AML.T0034.002 | — |
| <a id="b35"></a>**B3.5** | Les agents de développement (assistants de code, agents CI) n'ont pas d'accès direct à la production ni aux sauvegardes ; toute opération destructive passe par un environnement séparé et une revue. | Droits des agents de développement ; séparation des environnements.<br>*Revue de configuration ; test technique* | 2 | OWASP : LLM06:2025, ASI05<br>ATLAS : AML.T0101 | PocketOS (avr. 2026) |
| <a id="b36"></a>**B3.6** | Le comportement attendu face à un objectif impossible ou ambigu est spécifié et testé : l'agent s'arrête et rend compte au lieu de contourner les règles. | Spécification des critères d'arrêt ; résultats de tests avec des tâches impossibles.<br>*Test technique* | 2 | AI RMF : MEASURE 2.6<br>OWASP : ASI10<br>ATLAS : AML.M0038 | Agents OpenAI et Hugging Face (juil. 2026), Agents d'évaluation de l'AISI (juil. 2026) |

### B4 · Injection de prompt et détournement d'objectif

*Un contenu lu par un agent ne doit jamais pouvoir lui donner des ordres.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="b41"></a>**B4.1** | Les contenus non fiables (web, courriels, documents, tickets, résultats d'outils, pages lues par un agent de navigateur) sont identifiés comme tels et ne peuvent pas déclencher d'action sensible sans contrôle. | Architecture de traitement des entrées ; règles de restriction des outils sur contenu non fiable.<br>*Revue d'architecture ; test technique* | 3 | OWASP : LLM01:2025, ASI01<br>ATLAS : AML.T0051.001, AML.M0030 | Agents d'évaluation de l'AISI (juil. 2026) |
| <a id="b42"></a>**B4.2** ★ | Aucun agent ne combine, sans validation humaine, les trois propriétés suivantes : accès à des données sensibles, exposition à du contenu non fiable, capacité de communiquer vers l'extérieur ou de modifier un état. | Analyse de chaque agent selon ces trois propriétés ; mesures de séparation.<br>*Revue d'architecture* | 3 | OWASP : LLM01:2025, LLM06:2025, ASI01, ASI02<br>ATLAS : AML.T0086 | — |
| <a id="b43"></a>**B4.3** | Des campagnes de tests d'injection (directe, indirecte, multimodale, différée) sont menées avant chaque mise en production et à chaque changement de modèle, d'outil ou de prompt système, avec un jeu de tests de non-régression. | Plans et résultats de tests ; jeu de non-régression versionné.<br>*Revue documentaire ; test technique* | 2 | AI RMF : MEASURE 2.7<br>OWASP : LLM01:2025, ASI01<br>ATLAS : AML.T0051, AML.T0094, AML.T0129, AML.M0035 | — |
| <a id="b44"></a>**B4.4** | Les sorties des modèles sont traitées comme non fiables : validation par schéma, encodage, aucune exécution directe (SQL, shell, HTML, URL) sans contrôle. | Code de traitement des sorties ; résultats de tests.<br>*Revue de code ; test technique* | 2 | OWASP : LLM05:2025, ASI05<br>ATLAS : AML.T0077, AML.M0033 | — |
| <a id="b45"></a>**B4.5** | Le prompt système ne contient ni secret ni règle de sécurité dont la seule protection serait la confidentialité ; sa divulgation est considérée comme probable. | Revue des prompts système ; tentatives d'extraction réalisées par l'auditeur.<br>*Revue documentaire ; test technique* | 1 | OWASP : LLM07:2025<br>ATLAS : AML.T0069.002 | — |

### B5 · Outils, connecteurs et serveurs MCP

*Chaque outil donné à un agent est une capacité d'attaque potentielle.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="b51"></a>**B5.1** ★ | Les outils, plugins, connecteurs et serveurs MCP utilisés par les agents sont inventoriés, approuvés et épinglés en version ; leurs définitions (descriptions, schémas) sont protégées contre l'altération (empoisonnement d'outil, mise à jour malveillante). | Inventaire des outils et serveurs MCP ; processus d'approbation ; contrôle d'intégrité des définitions.<br>*Revue documentaire ; revue de configuration* | 3 | OWASP : LLM03:2025, ASI04, ASI02<br>ATLAS : AML.T0110, AML.T0109, AML.T0010.005, AML.M0043 | — |
| <a id="b52"></a>**B5.2** | Chaque outil applique ses propres contrôles d'autorisation côté serveur (l'agent ne décide pas seul de ses droits), avec des listes blanches de paramètres et de ressources. | Code ou configuration d'autorisation des outils ; tests de contournement.<br>*Revue de code ; test technique* | 3 | OWASP : LLM06:2025, ASI02<br>ATLAS : AML.M0028, AML.T0053 | — |
| <a id="b53"></a>**B5.3** | Le code généré ou exécuté par un agent tourne dans un bac à sable isolé : pas d'accès réseau par défaut, aucun secret, système de fichiers éphémère. | Architecture d'exécution ; tests d'évasion du bac à sable.<br>*Revue d'architecture ; test technique* | 3 | OWASP : ASI05<br>ATLAS : AML.T0050, AML.T0105, AML.T0102 | — |
| <a id="b54"></a>**B5.4** | Les serveurs MCP et outils exposés exigent une authentification, ne sont pas accessibles publiquement, et leurs journaux d'appels sont conservés. | Configuration réseau et d'authentification ; échantillon de journaux.<br>*Test technique ; revue de configuration* | 2 | OWASP : ASI02, ASI04<br>ATLAS : AML.T0132, AML.T0084.001 | — |
| <a id="b55"></a>**B5.5** | Les compétences, extensions et fichiers de règles d'agents tiers (skills, extensions d'IDE, règles d'assistants de code) sont revus avant installation et surveillés dans les dépôts. | Processus de revue ; inventaire des extensions et fichiers de règles.<br>*Revue documentaire ; test technique* | 2 | OWASP : ASI04<br>ATLAS : AML.T0081, AML.T0115.002 | — |

### B6 · Mémoire, RAG et données

*Ce qu'un agent retient ou retrouve peut être empoisonné, ou divulgué à la mauvaise personne.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="b61"></a>**B6.1** | Les droits d'accès aux documents s'appliquent au moment de la recherche (RAG) : un agent ne restitue à un utilisateur que les contenus que celui-ci a le droit de consulter. | Architecture RAG ; tests avec des profils aux droits différents.<br>*Test technique* | 3 | OWASP : LLM08:2025, LLM02:2025<br>ATLAS : AML.T0085.000, AML.T0082 | — |
| <a id="b62"></a>**B6.2** | Les écritures en mémoire persistante et en base de connaissances sont contrôlées (source, validation, expiration) ; la mémoire d'un agent peut être inspectée, purgée et restaurée. | Architecture mémoire ; procédure de purge et de restauration ; tests d'empoisonnement.<br>*Revue d'architecture ; test technique* | 3 | OWASP : LLM04:2025, ASI06<br>ATLAS : AML.T0080, AML.T0070, AML.M0031 | — |
| <a id="b63"></a>**B6.3** | Les données envoyées aux modèles et aux fournisseurs sont classifiées et minimisées ; les données sensibles sont filtrées (prévention des fuites) en entrée comme en sortie. | Politique de classification ; règles de prévention des fuites ; tests.<br>*Revue de configuration ; test technique* | 2 | AI RMF : MEASURE 2.10<br>OWASP : LLM02:2025 | — |
| <a id="b64"></a>**B6.4** | Les contrats avec les fournisseurs de modèles encadrent l'usage des données : pas d'entraînement sur vos données, localisation, durée de conservation, sous-traitants, notification d'incident. | Contrats et annexes de traitement des données ; paramètres de rétention.<br>*Revue documentaire* | 2 | AI RMF : GOVERN 6.1<br>CSF : GV.SC-05 | — |
| <a id="b65"></a>**B6.5** | Les bases vectorielles et index sont protégés comme des bases de production : authentification, chiffrement, sauvegarde, journalisation. | Configuration des bases vectorielles.<br>*Revue de configuration* | 1 | OWASP : LLM08:2025<br>ATLAS : AML.T0085.000 | — |

### B7 · Systèmes multi-agents

*Éviter qu'une erreur ou une compromission se propage d'agent en agent.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="b71"></a>**B7.1** | Les échanges entre agents sont authentifiés et intègres (identité de l'émetteur, signature ou mTLS, protection contre le rejeu) ; un agent ne fait pas confiance par défaut aux messages d'un autre agent. | Architecture de communication inter-agents ; tests d'usurpation.<br>*Revue d'architecture ; test technique* | 2 | OWASP : ASI07<br>ATLAS : AML.M0032 | — |
| <a id="b72"></a>**B7.2** | Les défaillances en cascade sont contenues : isolement des agents, disjoncteurs, validation des résultats intermédiaires, aucune propagation automatique vers des actions privilégiées. | Architecture ; scénarios de panne testés.<br>*Revue d'architecture ; test technique* | 2 | AI RMF : MANAGE 2.3<br>OWASP : ASI08 | — |
| <a id="b73"></a>**B7.3** | Les espaces partagés entre agents (fichiers, dépôts, files de messages) sont contrôlés : un agent ne peut ni publier vers des espaces publics ni créer de canaux de coordination non prévus. | Droits en écriture des agents ; détection de nouveaux canaux.<br>*Revue de configuration* | 1 | OWASP : ASI07, ASI10<br>ATLAS : AML.T0118.000, AML.M0043 | Agents OpenAI et Hugging Face (juil. 2026), Agents d'évaluation de l'AISI (juil. 2026) |

### B8 · Traçabilité et preuve

*Pouvoir prouver ce qu'un agent a consulté, modifié, et où s'arrêtait son autorité.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="b81"></a>**B8.1** ★ | Chaque action d'agent est journalisée de bout en bout : demande initiale, mandant, plan si disponible, appels d'outils avec paramètres, données lues ou modifiées, résultat. | Schéma de journalisation ; échantillon de traces complètes.<br>*Revue de configuration ; échantillonnage* | 3 | AI RMF : MANAGE 4.1, MEASURE 2.4<br>CSF : PR.PS-04<br>OWASP : ASI10<br>ATLAS : AML.M0024 | SailPoint : 92 %, 44 %, 52 % (mai 2025) |
| <a id="b82"></a>**B8.2** | Les journaux d'agents sont centralisés, horodatés, protégés contre l'altération (y compris par les agents eux-mêmes) et corrélés aux identités humaines et non humaines. | Architecture de journalisation ; droits sur les journaux.<br>*Revue de configuration* | 3 | CSF : PR.PS-04, DE.AE-03<br>ATLAS : AML.M0024 | Agents d'évaluation de l'AISI (juil. 2026) |
| <a id="b83"></a>**B8.3** | L'organisation peut reconstituer en moins de 24 heures ce qu'un agent a consulté et modifié sur une période donnée, et l'autorisation dont relevait chaque action. | Exercice de reconstitution chronométré.<br>*Exercice* | 2 | AI RMF : MANAGE 4.3, GOVERN 4.3 | SailPoint : 92 %, 44 %, 52 % (mai 2025) |
| <a id="b84"></a>**B8.4** | Les incidents impliquant des agents sont qualifiés, déclarés et partagés : procédure interne, notification aux autorités et aux clients, signalement aux fournisseurs de modèles. | Procédure ; registre des incidents d'IA.<br>*Revue documentaire* | 2 | AI RMF : MANAGE 4.3, GOVERN 4.3<br>CSF : RS.CO-02 | — |

### B9 · Supervision comportementale

*Repérer en temps réel l'agent qui sort de son périmètre.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="b91"></a>**B9.1** | Les comportements anormaux d'agents sont détectés en temps réel : accès hors périmètre, volumes inhabituels, nouvelles destinations réseau, création de comptes, tentatives de contournement. | Règles de détection ; alertes récentes et suites données.<br>*Revue de configuration ; test technique (émulation)* | 3 | AI RMF : MEASURE 2.4, MANAGE 4.1<br>OWASP : ASI10<br>ATLAS : AML.M0038 | Agents d'évaluation de l'AISI (juil. 2026), Claude Mythos 5 et la base d'une agence d'État (9 oct.) |
| <a id="b92"></a>**B9.2** | Une revue synchrone (humaine, ou par un modèle de contrôle distinct) approuve ou bloque les actions sensibles proposées par les agents les plus autonomes. | Architecture de contrôle ; statistiques d'approbations et de blocages.<br>*Revue d'architecture* | 2 | AI RMF : MAP 3.5<br>ATLAS : AML.M0029 | Agents d'évaluation de l'AISI (juil. 2026) |
| <a id="b93"></a>**B9.3** | Des leurres (jetons canaris, faux identifiants, services pièges) permettent de détecter un agent qui dépasse son périmètre. | Inventaire des leurres ; tests de déclenchement.<br>*Revue de configuration ; test technique* | 1 | ATLAS : AML.M0039 | — |
| <a id="b94"></a>**B9.4** | Les indicateurs de supervision humaine sont suivis (taux d'approbation, délais, refus) afin de détecter la validation par habitude. | Tableau de bord des validations.<br>*Revue documentaire* | 1 | AI RMF : MEASURE 3.1<br>OWASP : ASI09 | — |

### B10 · Agents tiers et externes

*Les agents des autres (clients, prestataires, attaquants) agissent déjà sur vos services.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="b101"></a>**B10.1** ★ | L'organisation sait détecter et distinguer les agents d'IA tiers qui utilisent ses services (espaces clients, API, sites marchands) et applique une politique explicite : autoriser, encadrer ou bloquer. | Règles de gestion des robots ; statistiques d'agents détectés ; politique.<br>*Revue de configuration ; test technique* | 3 | CSF : DE.CM-01, DE.CM-06<br>ATLAS : AML.T0116 | Agents tiers dans les comptes bancaires (22 oct.) (sources partielles), Campagne Cairn contre 1 200 sites marchands (19 oct.) |
| <a id="b102"></a>**B10.2** | Les parcours sensibles (virement, changement de coordonnées, création d'accès) résistent aux actions automatisées : authentification forte liée à l'action, limitation de débit, détection d'automatisation. | Analyse des parcours ; tests d'automatisation.<br>*Test technique* | 2 | CSF : PR.AA-03<br>ATLAS : AML.T0012 | Agents tiers dans les comptes bancaires (22 oct.) (sources partielles) |
| <a id="b103"></a>**B10.3** | Les prestataires qui utilisent des agents d'IA sur vos systèmes ou vos données doivent le déclarer contractuellement (périmètre, identités, journalisation, notification d'incident). | Clauses contractuelles ; questionnaires prestataires.<br>*Revue documentaire* | 2 | AI RMF : GOVERN 6.1, MANAGE 3.1<br>CSF : GV.SC-05 | — |
| <a id="b104"></a>**B10.4** | Les conditions d'utilisation encadrent l'usage d'agents automatisés par les clients : responsabilité, identification des agents, actions interdites. | Conditions générales ; politique d'accès programmatique.<br>*Revue documentaire* | 1 | AI RMF : GOVERN 1.1 | Agents tiers dans les comptes bancaires (22 oct.) (sources partielles) |

### B11 · Cycle de vie et tests des applications d'IA

*Tester les agents comme un attaquant le ferait, avant et après chaque changement.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="b111"></a>**B11.1** | Chaque agent ou application LLM fait l'objet d'une modélisation des menaces avant mise en production : flux de données, frontières de confiance, outils, privilèges. | Analyses de risques ; diagrammes de flux.<br>*Revue documentaire* | 3 | AI RMF : MAP 4.1, MAP 4.2<br>OWASP : ASI01, ASI02, ASI03 | — |
| <a id="b112"></a>**B11.2** | Un red teaming IA est réalisé avant mise en production puis périodiquement, par une équipe indépendante des développeurs, avec des scénarios alignés sur OWASP et MITRE ATLAS. | Rapports de red teaming ; suivi des corrections.<br>*Revue documentaire* | 2 | AI RMF : MEASURE 1.3, MEASURE 2.7<br>CSF : ID.IM-02<br>ATLAS : AML.M0035 | — |
| <a id="b113"></a>**B11.3** | Tout changement de modèle, de prompt système, d'outil ou de mémoire déclenche une réévaluation : tests de non-régression de sécurité et jeux d'évaluation. | Processus de changement ; résultats de non-régression.<br>*Revue documentaire ; échantillonnage* | 2 | AI RMF : MANAGE 3.2, MEASURE 2.7 | — |
| <a id="b114"></a>**B11.4** | Le code produit par des assistants d'IA suit le même processus de revue et d'analyse (SAST, analyse de composition, détection de secrets) que le code humain, et son origine est tracée. | Politique de développement ; configuration des contrôles CI.<br>*Revue de configuration* | 2 | CSF : PR.PS-06<br>OWASP : ASI05 | — |
| <a id="b115"></a>**B11.5** | Les modèles et artefacts (poids, gabarits, jeux de données) proviennent de sources vérifiées, avec contrôle d'intégrité et analyse des formats dangereux (sérialisation pickle, par exemple). | Registre des modèles ; contrôles d'intégrité.<br>*Revue documentaire ; test technique* | 1 | OWASP : LLM03:2025, LLM04:2025<br>ATLAS : AML.T0010.003, AML.T0011.000, AML.M0014 | — |

### B12 · Facteur humain et confiance

*L'humain dans la boucle n'est un garde-fou que s'il garde son esprit critique.*

| ID | Point de contrôle | Preuves attendues · méthode | Crit. | Référentiels | Cas d'école |
|---|---|---|---|---|---|
| <a id="b121"></a>**B12.1** | Les collaborateurs sont formés aux risques propres aux agents (injection via des contenus, excès de confiance, validation par habitude) et aux fraudes assistées par IA (hameçonnage ciblé, hypertrucages vocaux ou vidéo). | Programme de sensibilisation ; taux de participation ; résultats d'exercices.<br>*Revue documentaire* | 2 | CSF : PR.AT-01<br>OWASP : ASI09<br>ATLAS : AML.T0052.000, AML.T0088, AML.M0018 | — |
| <a id="b122"></a>**B12.2** | Les écrans de validation humaine présentent l'action exacte et ses conséquences ; un résumé rédigé par l'agent lui-même ne sert jamais de seule base de décision. | Captures des écrans de validation ; tests.<br>*Test technique* | 2 | OWASP : ASI09<br>ATLAS : AML.M0029 | Agents d'évaluation de l'AISI (juil. 2026) |
| <a id="b123"></a>**B12.3** | Une vérification hors bande (rappel sur un numéro connu) est imposée pour les demandes sensibles : paiement, changement de coordonnées bancaires, octroi d'accès. | Procédures ; contrôles par échantillonnage.<br>*Revue documentaire ; échantillonnage* | 1 | OWASP : ASI09<br>ATLAS : AML.T0073 | — |

## Couverture des référentiels OWASP

Chaque risque des deux Top 10 OWASP est couvert par au moins un point de contrôle.

| ID | Risque (libellé officiel) | Contrôles |
|---|---|---|
| LLM01:2025 | Prompt Injection | B4.1, B4.2, B4.3 |
| LLM02:2025 | Sensitive Information Disclosure | B2.3, B6.1, B6.3 |
| LLM03:2025 | Supply Chain | A3.1, A3.2, A3.6, B5.1, B11.5 |
| LLM04:2025 | Data and Model Poisoning | B6.2, B11.5 |
| LLM05:2025 | Improper Output Handling | B4.4 |
| LLM06:2025 | Excessive Agency | B2.1, B2.2, B3.1, B3.3, B3.5, B4.2, B5.2 |
| LLM07:2025 | System Prompt Leakage | B4.5 |
| LLM08:2025 | Vector and Embedding Weaknesses | B6.1, B6.5 |
| LLM09:2025 | Misinformation | A3.6 |
| LLM10:2025 | Unbounded Consumption | B2.4, B3.4 |
| ASI01 | Agent Goal Hijack | B4.1, B4.2, B4.3, B11.1 |
| ASI02 | Tool Misuse and Exploitation | B3.1, B4.2, B5.1, B5.2, B5.4, B11.1 |
| ASI03 | Identity and Privilege Abuse | B2.1, B2.2, B2.3, B2.5, B11.1 |
| ASI04 | Agentic Supply Chain Vulnerabilities | B5.1, B5.4, B5.5 |
| ASI05 | Unexpected Code Execution (RCE) | B3.5, B4.4, B5.3, B11.4 |
| ASI06 | Memory & Context Poisoning | B6.2 |
| ASI07 | Insecure Inter-Agent Communication | B7.1, B7.3 |
| ASI08 | Cascading Failures | B3.4, B7.2 |
| ASI09 | Human-Agent Trust Exploitation | B9.4, B12.1, B12.2, B12.3 |
| ASI10 | Rogue Agents | B3.2, B3.3, B3.6, B7.3, B8.1, B9.1 |

Libellés NIST AI RMF, NIST CSF 2.0 et MITRE ATLAS : feuille « Référentiels » du classeur et [`data/referentiels.yaml`](data/referentiels.yaml).

## Cas d'école

| Code | Cas | Contrôles | Vérification |
|---|---|---|---|
| PHP2SHELL | PHP2Shell : CVE-2026-109618 et CVE-2026-109619 | A1.2, A2.1, A2.2, A7.2, A8.1 | Vérifié |
| PHP2SHELL-EMBARQUE | ANSSI : impacts secondaires de PHP2Shell sur les produits tiers | A1.3 | Vérifié |
| ECOM-AGENTS | Un opérateur, des agents d'IA et plus de 100 entreprises compromises | A1.1, A1.5, A6.1, B10.1 | Vérifié |
| VOLUME-CRITIQUES | Chris Krebs sur CNBC | A2.1, A2.4 | Vérifié |
| GOULOT-VALIDATION | Le goulot de la validation humaine | A2.4, A2.5, A8.1, A8.2, A8.3 | Vérifié |
| LITELLM | Compromission de la chaîne de publication de LiteLLM | A3.1, A3.2, A3.3, B2.3, B2.4 | Vérifié |
| STORM-0940 | Campagne étatique automatisée par l'outil agentique ARTEX | A3.5, A4.1, A4.2 | Vérifié |
| CROWDSTRIKE-AGENTS | Campagnes d'espionnage menées par agents | A4.3, A6.1, A6.3 | Vérifié |
| EMUDHRA | Huit clés privées d'autorités de certification intermédiaires inférieures à 256 | A5.1, A5.2, A5.3 | Vérifié |
| POCKETOS | Un agent de code efface la production et ses sauvegardes | A7.1, B2.1, B2.2, B3.1, B3.5 | Vérifié |
| SONDAGE-GOUVERNANCE | AI agents: The new attack surface | B1.1, B1.2, B8.1, B8.3 | Vérifié |
| BANQUES-AGENTS | Des banques américaines restreignent les agents d'IA tiers non vérifiés | B2.1, B10.1, B10.2, B10.4 | Partiel |
| ACCES-NON-DEMANDE | Accès non demandé à une base de données publique | B9.1 | Vérifié |
| AISI-2026-07 | Actions non autorisées d'agents pendant des évaluations cyber | B2.3, B3.2, B3.3, B3.6, B4.1, B7.3, B8.2, B9.1, B9.2, B12.2 | Vérifié |
| EVALS-ANTHROPIC | Quatre modèles accèdent sans autorisation à de vrais systèmes tiers | A3.4, B3.3 | Vérifié |
| OPENAI-HF | Des agents d'évaluation compromettent la production de Hugging Face | B3.2, B3.3, B3.6, B7.3 | Vérifié |
| TAIWAN-MULTIAGENT | Un cadre multi-agents compromet des systèmes gouvernementaux | A1.1, A6.3 | Vérifié |
| HERMES-DEEPSEEK | Un agent autonome choisit ses cibles et ses exploits | A6.3 | Vérifié |

Sources détaillées : feuille « Cas d'école » du classeur, [`SOURCES.md`](SOURCES.md) et [timeline Black October](02-timeline-black-october.md).

★ = question reprise dans le Diagnostic Flash.
