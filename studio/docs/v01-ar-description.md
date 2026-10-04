# Description YouTube — V01 AR

**Provisoire.** La voix arabe n'existe pas encore : les chapitres sont calculés sur l'alignement estimé
(`src/data/v01_ar.vo.json`, `estimated: true`), avec `LEAD + début du groupe p…`, arrondis à la seconde inférieure.
Durée provisoire de `V01-AR` : **12:31** (22 542 images). À recalculer sur le Mac après le vrai alignement
(voir `v01-ar-etat.md`). Les points à trancher sont dans `v01-ar-questions.md`.

Titre proposé : **لماذا لم تعد تستطيع البقاء وحدك مع نفسك؟**
(c'est aussi le titre de l'écran de fin des Shorts ; sans point d'interrogation à l'écran, avec dans le titre YouTube).
Variante plus courte : **خمس عشرة دقيقة وحدك… أم صعقة كهربائية؟**

Textes de miniature (sur le modèle « YOU WOULD HAVE PRESSED IT. », « 15 MIN. ALONE. », « RATHER THE SHOCK? ») :

1. **كنتَ ستضغط عليه.**
2. **15 دقيقة. وحدك.**
3. **أم الصعقة؟**

---

خمس عشرة دقيقة وحدك في غرفة فارغة. لا هاتف، ولا شيء تقرؤه. أنت وأفكارك فقط، وزرٌّ يصعقك بشحنة كهربائية. ضغط عليه رجلان من كل ثلاثة.

ماذا حدث فعلًا في تجربة 2014؟ نتحدث عن شرود الذهن، وعن ردّ فعلنا الأول: أن نمدّ يدنا إلى الشاشة، وعن سؤال أقدم بكثير: كيف نتعلّم أن نبقى وحدنا مع أنفسنا؟

من مختبر علم النفس إلى باسكال، ومن عزلة الغزالي إلى الخلوة والذكر في الطريق الصوفي الذي أسلكه، الطريقة الكركرية. وفي النهاية تمرين بسيط من دقيقتين تجرّبه الليلة.

00:00 خمس عشرة دقيقة وحدك، وزرّ
00:56 التجربة
03:06 الأغرب في الأمر
05:09 باسكال رأى ذلك قبلنا
05:56 الغرفة الفارغة
07:03 الخلوة، وقصة الغزالي
08:46 الذكر
09:53 تمرين الدقيقتين لهذه الليلة
11:30 عودة إلى الزر

المصادر

تجربة الزر
Wilson, T. D., et al. (2014). “Just think: The challenges of the disengaged mind.” Science, 345(6192), 75–77. DOI: https://doi.org/10.1126/science.1250830
النص الكامل: https://pmc.ncbi.nlm.nih.gov/articles/PMC4330241/

شرود الذهن
Killingsworth, M. A., & Gilbert, D. T. (2010). “A Wandering Mind Is an Unhappy Mind.” Science, 330(6006), 932. DOI: https://doi.org/10.1126/science.1192439
المقال: https://www.imm.uzh.ch/news/schatzkammer/Science_2010.330.932.pdf

الإنترنت والشاشات في فرنسا
Médiamétrie, L'Année Internet 2025 (بالفرنسية): https://www.mediametrie.fr/fr/lannee-internet-2025
The Media Leader، نقلًا عن Médiamétrie: نحو 20 جلسة إنترنت يوميًا (بالفرنسية): https://fr.themedialeader.com/?p=102193
Arcep, Arcom, CGE, ANCT / CREDOC, Baromètre du numérique, édition 2025 (بالفرنسية): https://www.arcep.fr/cartes-et-donnees/nos-publications-chiffrees/barometre-du-numerique/le-barometre-du-numerique-edition-2025.html
هذه الأرقام تخصّ فرنسا، وليست تقديرات عالمية.

بليز باسكال
Blaise Pascal, Pensées (الخواطر)، باب « Divertissement » (التسلية)، الشذرة 4 (Lafuma 136؛ Sellier 168). المخطوط الأصلي بخط باسكال: Recueil original، الصفحتان 139 و210 (BnF, fr. 9202): https://www.penseesdepascal.fr/Divertissement/Divertissement4-moderne.php
الاقتباسان في الفيديو ترجمة عربية عن الأصل الفرنسي.

أبو حامد الغزالي
الغزالي، المنقذ من الضلال. ترجمة إنجليزية: W. Montgomery Watt, The Faith and Practice of al-Ghazali (1953): https://www.ghazali.org/works/watt3.htm
الغزالي، إحياء علوم الدين، الكتاب السادس عشر: كتاب آداب العزلة.

القرآن الكريم، سورة الرعد، الآية 28: https://quran.com/13/28

الطريقة الكركرية
Mohamed Faouzi al-Karkari (محمد فوزي الكركري), The Foundations of the Karkariya Order، ترجمة Yousef Casewit وKhalid Williams: https://wardahbooks.com/products/the-foundations-of-the-karkariya-order

الصور
دمشق، مئذنة العروس في الجامع الأموي، 1914. المصوّر مجهول؛ من كتاب Syria, the Land of Lebanon (1914). ملكية عامة، ويكيميديا كومنز: https://commons.wikimedia.org/wiki/File:SL_1914_D160_the_bride_minaret_of_the_umayyad_mosque.jpg
بيانات الخريطة: Natural Earth، ملكية عامة: https://www.naturalearthdata.com/about/terms-of-use/

---

## Notes de préparation (hors description à publier)

- Chapitres : p7, p18, p28, p34, p41, p50, p54, p62, comme la version anglaise. Valeurs **estimées** (vitesse de parole
  supposée) : elles bougeront de plusieurs secondes avec la vraie voix. Recalcul : début du premier segment du groupe
  dans `src/data/v01_ar.vo.json` + 0,8 s, arrondi à la seconde inférieure.
- Titres d'œuvres dans leur langue d'origine : المنقذ من الضلال (al-Munqidh min al-ḍalāl), إحياء علوم الدين
  (Iḥyāʾ ʿulūm al-dīn), كتاب آداب العزلة ; Pensées en français ; les articles scientifiques en anglais.
- Mêmes sources et mêmes liens que `v01-en-description.md`, sans revérification en ligne dans cette session
  (aucun appel réseau). Le DOI et le lien PMC de Wilson, les liens Médiamétrie, The Media Leader et Commons restent
  à recontrôler avant publication, comme pour l'anglais.
- Pas de traduction du verset dans la description : en arabe, la voix récite le verset lui-même.
- La voix cite le Munqidh directement en arabe (« فكان لساني لا ينطق بكلمة واحدة ») : l'édition arabe à citer, et
  l'ordre des mots, sont dans `v01-ar-questions.md`. Idem pour la traduction arabe de Pascal et le titre arabe
  éventuel du livre de la Karkariya (je ne l'invente pas).
- Sous-titres : `python3 tools/srt.py src/data/v01_ar.vo.json out/package_ar/v01.ar.srt` après le vrai alignement
  (267 entrées sur l'alignement estimé).
