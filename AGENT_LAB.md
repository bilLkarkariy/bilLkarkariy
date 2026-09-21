# Billel — Agent Lab

Portfolio interactif de `bilLkarkariy/bilLkarkariy` : quatre mini-jeux pédagogiques autour de Doksima, AgentFlow, EchoTrust et PixelLight. Les données, pannes, avis et crédits du jeu sont fictifs. Aucun appel à un modèle, aucune publication réelle, aucune clé API.

## Structure

- `src/template.html`, `src/style.css`, `src/app.js` : sources du jeu préparé et validé dans la conversation.
- `docs/index.html` : site autonome généré, ouvrable directement dans un navigateur.
- `assets/agent-lab-preview.webp` et `.png` : aperçus capturés depuis l'application.
- `profile-block.md` : bloc inséré dans le README sans remplacer le contenu existant.
- `tools/` et `tests/` : construction, aperçu, intégration du README et tests Chromium.

## Publication

Le workflow **Agent Lab — build, test and preview** construit le site, exécute les tests, génère les aperçus puis committe ces fichiers et le bloc README sur `main`. Il ne force jamais un push. Il est lancé pour les modifications des sources et peut être relancé manuellement depuis l'onglet Actions.

Pour la première activation du jeu, choisir dans **Settings → Pages → Deploy from a branch → main → /docs → Save**. Le workflow ne modifie pas les réglages administrateur de GitHub Pages. Une fois Pages activé, il demande une reconstruction après chaque mise à jour du jeu.

Adresse prévue : https://billkarkariy.github.io/bilLkarkariy/

Le profil affiche un aperçu cliquable ; le JavaScript du jeu s'exécute sur Pages, pas à l'intérieur du README.

## Développement local

```bash
python3 tools/build.py
python3 -m http.server 8080 --directory docs
```

Pour les tests et l'aperçu :

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium
python3 tests/test_lab.py
python3 tools/render_preview.py
python3 tools/update_readme.py
```

Les flèches, ZQSD ou WASD déplacent le personnage lorsque le plateau a le focus ; E ouvre la station proche. Les stations sont également cliquables. Des commandes tactiles sont proposées sur mobile. Pause arrête les animations ambiantes ; Rejouer efface uniquement la progression du mini-jeu dans ce navigateur.

## Vérification et limites

Les tests couvrent les quatre stations, les garde-fous, les reprises, le changement de station pendant un traitement, les erreurs de stockage, le clavier et les largeurs de 320 à 1440 pixels. Le rapport est généré dans `tests/last-report.json`. Les tests utilisent `set_content` et une doublure de stockage explicite ; ils ne remplacent pas une vérification du déploiement réel, de la persistance native intersessions, de Safari/Firefox ou un audit complet d'accessibilité.

Ne pas publier le PDF du CV, des documents clients ou des secrets dans ce dépôt public.
