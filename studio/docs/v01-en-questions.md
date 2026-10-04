# V01 EN — questions pour Billel

Mis à jour le 4 octobre 2026. La voix et la traduction du verset sont désormais choisies.

## Voix anglaise : décision prise

Billel a fourni une prise complète de son clone anglais, `public/vo/v01_en_brut.wav` (48 kHz, mono, PCM 24 bits). Aucun appel ElevenLabs ni aucune régénération n’est autorisé. Le champ `tts.voice_id` reste vide pour empêcher une génération accidentelle. Les rushes face caméra restent à fournir.

## Coran 13:28 : question tranchée

Billel a choisi Marmaduke Pickthall, *The Meaning of the Glorious Koran* (1930) : “Verily in the remembrance of Allah do hearts find rest!” La dernière proposition est conservée, comme dans le récit FR. `s63` est complet et `_pending` supprimé. La traduction figure sous l’arabe, dans le même composant et le même style que le FR ; son crédit reste dans la description. L’arabe uthmani et Amiri Quran restent inchangés, avec fondu seul et silence total pendant leur affichage.

## Formulations religieuses à valider

Ces formulations reprennent le récit français ; elles ne constituent pas une nouvelle interprétation de ma part.

- **s53–s55 :** « spiritual retreat », « the inward tradition of Islam », « under a master's guidance ». Valides-tu ces termes pour présenter la khalwa et le soufisme à ce public ? La mention générale des quarante jours est conservée : souhaites-tu la nuancer en anglais ?
- **s62 :** la comparaison avec les mantras est héritée du FR (« Other traditions speak of mantras »), ainsi que la métaphore du meuble et du point fixe. Valides-tu ce rapprochement, ou veux-tu éviter toute impression d'équivalence entre pratiques ? « Remembrance » et « the Name » conviennent-ils pour dhikr et le Nom ?
- **s64 :** la voie Karkariya, la date de fondation, le cheikh, la muraqqa'a et les deux retraites de trois puis quarante jours viennent du script FR actuel. La voix FR alignée ne contient pas encore toute la phrase sur ces deux retraites : la version EN suit bien **le script**, sans ajouter de témoignage. Valides-tu l'ensemble en anglais, notamment « This patched cloak is its garment » ?
- **s69 :** « Astaghfirullah » est conservé dans les trois occurrences, avec « I ask God's forgiveness ». Valides-tu le cadre de cette invitation à un public sceptique et la prononciation à enregistrer ?
- **Témoignage :** la pause de 2,5 secondes après `s64` reste celle du script. Aucun témoignage ni récit personnel supplémentaire n'a été écrit. Un ajout futur modifiera les durées.

## Fiches et captures : décisions de montage prises

Toutes les variantes FR restent identiques. En EN, les captures anglophones sont conservées à leur échelle, avec les surlignages existants ; les fiches deviennent des résumés courts. Les étiquettes bibliographiques superposées sont masquées en EN : les crédits sont dans la description.

| Passage / capture | Décision EN |
|---|---|
| `pmc_titre`, `pmc_revue`, titre de `kg_page` | Supprimer le sous-titre de traduction et la fiche répétant le nom de la revue. Le document suffit. |
| `pmc_fin` dans le hook | Conserver la promesse éditoriale, sans dévoiler la phrase. Flou et caviardage restent présents. |
| `pmc_methode` | Résumer la sélection des participants : ils connaissaient déjà le choc et auraient payé pour l'éviter. |
| `pmc_resultats` | Conserver les chiffres 190 et 42 et la petite taille de l'échantillon ; raccourcir le rappel du consentement à payer. |
| `pmc_vagabondage`, `pmc_domicile` | Conserver les proportions comme repères visuels, avec une phrase courte, sans répéter le paragraphe anglais. |
| `pmc_etude9` | Garder l'âge 18–77 et les trois conclusions courtes (résultat, âge, smartphone). |
| `pmc_preparation` | Reformuler : avoir un plan n'a pas rendu ce moment plus agréable. Garder voyage, souvenir, projet. |
| `pmc_scenariste` | Résumer les deux tâches : créer l'histoire et la regarder ; étiquettes WRITER / AUDIENCE. |
| `kg_page`, `kg_methode`, `kg_resultats` | Garder le contexte de l'échantillonnage aléatoire, les trois questions et les chiffres 2,250 / 46.9%. Fiches de synthèse plutôt que traduction littérale. |
| `pmc_techniques` | Résumer l'opposition faire/penser et souligner OTHER TECHNIQUES. La dernière phrase reste caviardée. |
| `ghazali_baghdad`, `ghazali_langue`, `ghazali_coeur`, `ghazali_minaret` | Fiches courtes sur la carrière, la perte de parole et la retraite. Les citations prononcées suivent Watt ; le document anglais porte le détail. |
| `karkariya_fondements` | Garder The retreat / The Name comme repères de vocabulaire, sans ajout doctrinal. |
| `pmc_fin` à la fin | Révéler la phrase anglaise dans le document ; la fiche ne garde que Untutored. L'arrachage reste synchronisé avec le début de la citation. |

**Exception au constat du brief :** Médiamétrie, Arcep et les transcriptions de Pascal sont en français dans les assets existants. En EN, les trois captures statistiques sont remplacées par des fiches anglaises avec les mêmes chiffres. Les transcriptions et les deux manuscrits de Pascal sont remplacés à l'écran par ses citations anglaises publiées, composées comme du texte, sans faux document. Le texte suit W. F. Trotter, fragment 139, reproduit dans l'[édition Gutenberg](https://www.gutenberg.org/files/18269/18269-h/18269-h.htm). Ces choix évitent du français résiduel et préservent tous les assets FR ; les références originales restent dans la description. Souhaites-tu conserver ce traitement de Pascal pour l'EN ?

## Dernier point éditorial

Le chiffre des vingt sessions est formulé « internet sessions » en `s38`, comme dans la source citée par la description FR. En `s74`, le récit FR assimile ces sessions aux ouvertures du téléphone. Souhaites-tu garder cette image ou remplacer cette phrase par une formulation qui n'attribue pas ce chiffre aux déverrouillages ? Ce n'est pas une mesure vérifiée des ouvertures du téléphone.
