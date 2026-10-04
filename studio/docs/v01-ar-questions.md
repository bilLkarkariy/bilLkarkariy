# V01 AR — questions pour Billel

4 octobre 2026. Le texte de la voix (`script/v01_texte_playground_balises_ar.txt`) n'a pas été touché. Tout ce qui
suit concerne l'écran, la description et deux points du texte figé que je signale sans les corriger. Pour chaque
question : ce que j'ai fait par défaut, et ma recommandation. Rien de religieux n'a été tranché par moi.

## 1. Questions religieuses (à trancher par toi)

1. **Le verset récité par la voix clonée.** En arabe, la voix dit le verset elle-même (s63 : « والقرآن يقولها في جملة
   واحدة: «أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ» »). Une voix de synthèse qui récite du Coran peut gêner une
   partie du public, et sa prononciation (harakat, tajwîd) n'est pas garantie.
   - a. garder la voix clonée, et vérifier à l'écoute chaque harakat ;
   - b. enregistrer toi-même cette seule phrase (le verset) et l'insérer à la place ;
   - c. la voix dit « والقرآن يقولها في جملة واحدة: » puis silence, le verset seulement affiché.
   Je recommande **b** : ta voix pour le verset, le reste en clone. (Le texte figé ne change pas dans a et b.)
2. **Écran pendant le verset.** Fait comme demandé : texte uthmani exact, Amiri Quran, fondu seul, **rien dessous** (ni
   référence, ni traduction), musique et bruitages à zéro, ni grain ni lumière de fenêtre. La ligne de référence
   « سورة الرعد · الآية 28 » n'est pas affichée (les sources restent dans la description). Tu confirmes ?
3. **Comparaison avec les mantras** (s62, « تقاليد أخرى تسمّيه «مانترا» », héritée du français) et la métaphore du
   meuble dans la pièce vide : à garder telles quelles en arabe ? (Même question que pour l'anglais.)
4. **Mots sur les fiches.** Khalwa : le mot « خلوة » en grand, avec en dessous « الاعتكاف الروحي », repris mot pour mot de
   la voix (« هذه الكلمة هي الخلوة. الاعتكاف الروحي. »). En arabe, « اعتكاف » désigne d'abord la retraite à la mosquée :
   veux-tu garder ce mot à l'écran, ou « العزلة الروحية » ? Dhikr : « ذكر » avec « التذكّر » (comme la voix, s62).
   Fondements : « الخلوة » et « الاسم المفرد ». Astaghfirullāh : « أستغفر الله » en or, avec « أطلب المغفرة من الله »
   dessous (la voix le dit aussi).
5. **Translittérations retirées.** En arabe, les lignes latines KHALWA, DHIKR, AL-KHALWA, AL-ISM AL-MUFRAD,
   ASTAGHFIRULLĀH sont vides (le mot arabe est déjà là). D'accord ?

## 2. Le texte figé de la voix : deux remarques (rien n'a été changé)

1. **Citation d'al-Ghazali (s58).** La voix dit « «فكان لساني لا ينطق بكلمة واحدة» ». Dans les éditions du *Munqidh*
   que je connais, l'ordre est « فكان لا ينطق لساني بكلمة واحدة ». Entre guillemets, c'est une citation : soit on garde
   la voix telle quelle (c'est le sens exact), soit tu réenregistres avec l'ordre de l'édition. Quelle édition veux-tu
   citer dans la description ?
2. **Citations à l'écran.** Pour « Dieu dessécha ma langue » et « je montais au minaret… », je n'ai **pas** mis de
   citation arabe originale (je ne peux pas vérifier le mot à mot d'une édition ici) : l'écran porte une phrase
   simple, sans guillemets (« جفّ لسانه، فلم يعد يقدر على التدريس », « كان يصعد منارة المسجد طوال النهار، ويغلق بابها على
   نفسه »). Si tu veux le texte du *Munqidh* mot pour mot, donne-moi l'édition et je le pose (`src/i18n/ar.ts`).

## 3. Chiffres et dates

1. **Chiffres.** Par défaut, chiffres occidentaux partout (0123…), à l'écran et dans les sous-titres, comme dans une
   grande partie du Maghreb et sur YouTube. Alternative : chiffres arabes orientaux (٠١٢٣…), courants au Machrek et
   dans le Golfe. Je recommande **les chiffres occidentaux** : c'est ton public marocain, et la vidéo montre des
   documents en chiffres occidentaux.
2. **Décimales.** « 57.5% », « 46.9% » avec un point. Alternative : virgule arabe (٫). Le point va avec les
   chiffres occidentaux.
3. **Pourcentages.** « 51% », « 89% » sans espace (règle arabe). D'accord ?
4. **Mois.** « 4 يوليو 2014 » (Égypte, Golfe, presse internationale). Alternatives : « تموز » (Levant, Irak),
   « يوليوز » (Maroc). Je recommande **يوليو**, le plus compris partout ; « يوليوز » si tu vises d'abord le Maroc.
5. **Dates hégiriennes.** Al-Ghazali : « 1058-1111 » et « بغداد · 1095 », en grégorien seulement. Ajouter l'hégire
   (450-505 هـ, 488 هـ) ? Je recommande de ne rien ajouter à l'écran (il est déjà chargé) ; on peut l'écrire dans la
   description.
6. **Heures.** La réglette de la journée affiche « 0:00 6:00 12:00 18:00 24:00 » (au lieu de « 0 H »). D'accord ?

## 4. Choix de traduction à l'écran

1. **Le Golfe.** La carte dit simplement « الخليج » (sans « العربي » ni « الفارسي », pour rester neutre). D'accord ?
   Les autres noms : « البحر المتوسط », « دجلة », « الفرات », « بادية الشام », « بغداد », « دمشق ».
2. **Documents en français.** Médiamétrie et Arcep : les captures françaises restent à l'écran, avec des fiches en
   arabe par-dessus, comme les articles en anglais (Science, PMC) restent avec leurs fiches arabes. L'anglais avait
   remplacé ces trois captures par des fiches seules. Garder les captures, ou faire comme l'anglais (une ligne à changer
   dans `src/components/Citation.tsx`) ? Je recommande de **les garder** : ce sont des preuves, comme les articles.
3. **Pascal.** Le manuscrit autographe reste à gauche ; la transcription française imprimée est remplacée par une
   feuille blanche où la phrase est composée en arabe (texte de la voix), surlignée en or au même moment. Pas de faux
   fac-similé. D'où vient la traduction arabe de Pascal dans la voix ? Si c'est une traduction publiée, je la cite dans
   la description ; sinon la description dit « ترجمة عربية عن الأصل الفرنسي ».
4. **Mots latins qui restent.** « Science » (nom de la revue, sur la fiche de la date) et « «OTHER TECHNIQUES» »
   (le mot surligné dans l'article anglais). D'accord ?
5. **Guillemets.** « » partout, comme dans le texte de la voix.
6. **Livre de la Karkariya.** La description cite le titre anglais (*The Foundations of the Karkariya Order*). Existe-t-il
   un titre arabe original à citer ? Je ne l'ai pas inventé.

## 5. Police et mise en page

1. **Amiri partout.** Tout l'arabe s'écrit en Amiri, y compris les petites étiquettes qui sont en Plex Mono en
   français. Agrandi de 10 % (texte) et de 30 % (étiquettes) pour compenser. Alternative pour les étiquettes : une
   police arabe sans empattement (par exemple IBM Plex Sans Arabic, cousine de Plex Mono), à poser dans
   `public/fonts/` sur le Mac. Je recommande d'abord de **regarder les PNG** (`v01-ar-images-fixes.md`) : si les
   étiquettes se lisent mal, Plex Sans Arabic.
2. **Colonne des étapes de l'exercice.** Le numéro et les lignes s'alignent sur le bord droit de leur colonne, contre
   le dessin (la colonne ne change pas de côté). D'accord, ou préfères-tu tout le cadre en miroir (texte à droite,
   dessin à gauche) ?

## 6. Titre et miniatures

- Titre proposé : **لماذا لم تعد تستطيع البقاء وحدك مع نفسك؟** (variante : **خمس عشرة دقيقة وحدك… أم صعقة كهربائية؟**).
- Miniatures : **كنتَ ستضغط عليه.** / **15 دقيقة. وحدك.** / **أم الصعقة؟**
- Lequel préfères-tu ? Je recommande le premier titre (il reprend la phrase de l'écran de fin) et la miniature 1.

## 7. Voix

- `tts.voice_id` est vide dans `script/v01_ar.json` : c'est toi qui choisis la voix arabe de ton clone (jamais
  « Sidi Mounir »). Les balises ([slowly], [pause], [matter-of-fact]…) sont celles du texte figé.
