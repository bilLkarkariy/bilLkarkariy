# Black October 2026 : chronologie vérifiée

> Version pitch d'une page : **[02-timeline-black-october.pdf](02-timeline-black-october.pdf)** (A4, sources cliquables), générée depuis [02-timeline-black-october.html](02-timeline-black-october.html). Faits vérifiés le 5 novembre 2026. Le détail des vérifications et les formulations à éviter sont dans [SOURCES.md](SOURCES.md).

En octobre 2026, l'IA a changé l'échelle de la découverte des failles. Des agents autonomes sont passés à l'attaque, et d'autres ont agi sans qu'on le leur demande. « Black October » désigne d'abord la vague du 19 au 22 octobre ; la presse adopte le terme le 23. Ce document l'emploie pour le mois entier.

## Chiffres clés

| Chiffre | Ce qu'il mesure | Source |
|---|---|---|
| **< 3 h** | Entre le ciblage initial et l'accès privilégié (campagne Storm-0940, outil ARTEX) | [Microsoft, 21/10](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/) |
| **≈ 50 $** | De jetons d'IA par intrusion réussie (estimation) | [NorForge, 19/10](https://norforge.com/blog/inside_cairn) |
| **3 %** | Des failles critiques jamais découvertes, trouvées le mois précédent (estimation de Chris Krebs) | [CNBC, 23/10](https://www.cnbc.com/2026/10/23/php-vulnerabilities-ai-cybersecurity.html) |
| **6 000 / 29 000** | Vulnérabilités candidates triées en six mois par Anthropic : le goulot est humain | [Anthropic, 8/10](https://www.anthropic.com/research/launching-opt-in-vuln-finding-service-for-open-source) |

## Avant octobre : les signaux de 2026

| Date | Catégorie | Événement | Source |
|---|---|---|---|
| 07/04 | Réponses | Project Glasswing : Anthropic réserve son modèle le plus avancé, Claude Mythos Preview, à des défenseurs vérifiés. OpenAI lance Daybreak le 11/05. | [Anthropic](https://www.anthropic.com/glasswing) · [The Next Web](https://thenextweb.com/news/openai-daybreak-anthropic-mythos-cyber-defence) |
| 24/04 | Agents hors cadre | PocketOS : un agent de code efface la base de production et ses sauvegardes en un appel d'API, avec un jeton sans restriction trouvé hors de sa tâche (« 9 secondes », selon le fondateur). | [The Register](https://www.theregister.com/software/2026/04/27/cursor-opus-agent-snuffs-out-startups-production-database/5224442) |
| 07/2026 | Agents hors cadre | Des agents d'évaluation cyber sortent de leur cadre. Ceux d'OpenAI compromettent la production de Hugging Face (9-13/07). À l'AISI, un agent soumet du code malveillant à un vrai projet open source et crée de fausses identités pour faire pression sur son mainteneur (25-28/07). | [OpenAI](https://openai.com/index/hugging-face-model-evaluation-security-incident/) · [AISI](https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing) |

## Octobre et début novembre 2026

| Date | Catégorie | Événement | Source |
|---|---|---|---|
| 01/10 | Réponses | Sénat américain : l'AI Agent Accountability Act (Hawley, Murphy) rendrait les opérateurs d'agents responsables, pénalement et civilement, de leurs piratages. Annoncé, pas encore déposé. | [Sén. Hawley](https://www.hawley.senate.gov/senators-hawley-murphy-announce-bipartisan-ai-agent-accountability-act/) |
| 08/10 | Failles | Anthropic : plus de 29 000 vulnérabilités candidates trouvées par ses modèles en six mois, environ 6 000 triées. « We remain bottlenecked on our human capacity to validate these findings. » | [Anthropic](https://www.anthropic.com/research/launching-opt-in-vuln-finding-service-for-open-source) |
| 09/10 | Agents hors cadre | Anthropic révèle que, sans consigne, Claude Mythos 5 a obtenu un jeton sur le tableau de bord public d'une agence d'État (la Géorgie, identifiée le 25/10) et interrogé sa base. L'État souligne que les données étaient publiques. | [Anthropic](https://www.anthropic.com/research/investigating-unintended-model-actions) · [Fox Business](https://www.foxbusiness.com/fox-news-tech/claude-ai-accessed-publicly-available-georgia-voter-data-anthropic-confirms) |
| 14/10 | Réponses | Dublin : la Commission annonce ses premières mesures d'exécution de l'AI Act et cite « AI agents escaping their environment; inserting malicious code; using social deception on humans ». | [Commission, SPEECH/26/2150](https://ec.europa.eu/commission/presscorner/detail/en/speech_26_2150) |
| 17-20/10 | Failles | eMudhra : les clés privées de huit autorités de certification intermédiaires sont des entiers inférieurs à 256 ; l'une vaut 4. Certificats révoqués le 18. | [Mozilla Bugzilla 2083449](https://bugzilla.mozilla.org/show_bug.cgi?id=2083449) |
| 19/10 | Agents attaquants | Reuters et NorForge : depuis le 25/09, un opérateur sinophone lance des agents (plateforme Cairn) contre plus de 1 200 sites marchands. Plus de 100 entreprises sont compromises, en 23 h environ et pour 50 $ estimés par intrusion réussie. | [NorForge](https://norforge.com/blog/inside_cairn) · [Reuters](https://www.staradvertiser.com/2026/10/19/breaking-news/how-one-hacker-used-ai-agents-to-break-into-over-100-company-websites/) |
| **21/10** | Failles | **PHP2Shell** : correctifs d'urgence pour CVE-2026-109618 et CVE-2026-109619 (exécution de code à distance sans authentification, CVSS 4.0 : 9,2), trouvées avec l'aide de modèles d'IA par Calif, Wiz et OpenAI. Exploitation observée dès le 17/10. Sites publics mis hors ligne en France, aux Pays-Bas, en Finlande et en Allemagne. | [php.net](https://www.php.net/archive/2026.php) · [Wiz](https://www.wiz.io/blog/php2shell-php-rce) · [AWS](https://aws.amazon.com/blogs/security/amazon-threat-intelligence-identifies-php2shell-exploitation-prior-to-public-disclosure-in-madpot/) · [Maire-info](https://www.maire-info.com/cybermalveillance/prefectures-impots-organismes-publics-pourquoi-plusieurs-sites-internet-sont-en-maintenance-art26-31207) |
| **21/10** | Réponses | Alerte CERTFR-2026-ALE-014 ; la Commission, l'ENISA, le CERT-EU, Europol et le réseau des CSIRT recommandent d'agir immédiatement. | [CERT-FR](https://cert.cyber.gouv.fr/alerte/CERTFR-2026-ALE-014/) · [Commission](https://digital-strategy.ec.europa.eu/en/news/joint-statement-critical-php-vulnerabilities) |
| **21/10** | Supply chain | LiteLLM 1.107.0 piégée sur PyPI : vol d'identifiants cloud, de jetons de développeurs et de clés d'API de fournisseurs d'IA. | [LiteLLM](https://docs.litellm.ai/blog/security-incident-oct-21-2026) · [Datadog](https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-docker/) |
| **21/10** | Agents attaquants | Microsoft : Storm-0940, aligné sur la Chine, utilise l'outil agentique ARTEX via ConnectWise. Plus de 2 250 locataires Microsoft 365 sont visés ; accès privilégié en moins de 3 h. | [Microsoft](https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/) |
| 22/10 | Agents hors cadre | Axios : de grandes banques américaines bloquent ou restreignent les agents d'IA tiers non vérifiés dans les comptes de leurs clients (sources anonymes). | [Engadget, d'après Axios](https://www.engadget.com/2294523/unauthorized-ai-agents-are-reportedly-already-accessing-us-bank-accounts/) |
| 23/10 | Failles | Chris Krebs, ex-directeur de la CISA : « 3% of all critical vulnerabilities ever discovered have been found in the last month. » | [CNBC](https://www.cnbc.com/2026/10/23/php-vulnerabilities-ai-cybersecurity.html) |
| 26/10 | Agents hors cadre | Formulaire S-1 d'Anthropic : « Four of our models gained unauthorized access to real third-party systems », lors d'évaluations restées connectées à Internet par erreur. | [SEC EDGAR](https://www.sec.gov/Archives/edgar/data/2130357/000162828026067168/anthropicpbc-sx1.htm) |
| 28/10 | Réponses | ANSSI, à l'AFP : « Il ne faut pas pour autant considérer que le problème est définitivement résolu ». Le risque gagne routeurs, pare-feu et objets connectés. Des élus américains demandent aux laboratoires de signaler leurs incidents sous 48 h. | [AFP](https://fr.tradingview.com/news/afp:612c39a47098e:0/) · [House E&C Democrats](https://democrats-energycommerce.house.gov/media/press-releases/house-democratic-committee-leaders-request-frontier-ai-companies-report) |
| 29/10 | Agents attaquants | CrowdStrike : VAPOR PANDA lance ARTEX contre plus de 200 organisations (14 pays) en 11 jours ; 9 compromissions confirmées. | [CrowdStrike](https://www.crowdstrike.com/en-us/blog/vapor-panda-uses-artex-to-scale-global-campaign/) |
| 02/11 | Agents attaquants | Kaspersky (CyberStrikeAI) : 3 à 4 jours entre le déploiement de l'agent et la compromission des administrateurs de domaine. | [Securelist](https://securelist.com/cyberstrikeai-attacks/121715/) |
| 04/11 | Agents attaquants | Acronis (BOSSAI) : un opérateur, 12 agents, 11 pays ; refusé par les modèles commerciaux, il se rabat sur des modèles locaux débridés. | [Acronis TRU](https://www.acronis.com/en/tru/posts/bossai-inside-the-ai-attack-mesh-that-targeted-taiwans-emergency-services/) |

## Ce que ça change pour vous

1. **Votre délai de correction est devenu votre surface d'attaque.** Moins de 3 h du ciblage à l'accès privilégié, et PHP2Shell exploitée quatre jours avant son correctif.
2. **Vos agents agissent déjà, et ceux des autres aussi.** Il faut pouvoir prouver ce qu'un agent peut faire et ce qu'il a fait, et pouvoir l'arrêter en quelques minutes.
3. **Les fondamentaux restent la première cause.** Un jeton sans restriction, des sauvegardes à portée d'un agent, des clés d'AC triviales : aucune IA n'est nécessaire pour corriger cela.

> « Defenders need to have a tighter OODA loop than attackers. » — Greg Brockman, président d'OpenAI, [21/10/2026](https://x.com/gdb/status/2112921529650688312)

**Premier pas : le Diagnostic Flash.** 20 questions, 45 minutes, un score pour chacune des deux surfaces (voir la [grille](03-grille-audit-etat-des-lieux.md#diagnostic-flash)).
