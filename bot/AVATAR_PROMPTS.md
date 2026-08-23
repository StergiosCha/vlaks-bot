# ΒΛΑΞ — avatar prompts (Kouts · Θέμης · Μπάλκαν Φούιτ)

Τρεις ξεναγοί, ένα στυλ. Ο επισκέπτης διαλέγει έναν· πρέπει να μοιάζουν με **σετ**:
ίδιο render, ίδιο κάδρο, ίδιο φόντο, ίδιος φωτισμός. Αλλάζει μόνο ο άνθρωπος.

Και οι τρεις είναι υπαρκτά πρόσωπα του αρχείου (George Koutsotolis, Themis Tziros,
Γιάννης «Μπάλκαν Φούιτ» Ευαγγελόπουλος). Τα prompts φτιάχνουν **στιλιζαρισμένους
χαρακτήρες κινουμένων σχεδίων**, όχι φωτορεαλιστική ομοιότητα — και καλό είναι να το
δουν οι ίδιοι πριν ανέβουν.

---

## 0. Το συμβόλαιο του στυλ (μένει ίδιο και στα τρία)

> 3D stylised character portrait, Pixar/DreamWorks style, semi-realistic. […ο χαρακτήρας…]
> Head-and-shoulders, looking straight at camera, centred, plenty of headroom.
> Solid warm off-white background, soft studio lighting, subsurface scattering skin,
> subtle pores and hair strands, clean readable silhouette. Octane render, 4k, square 1:1.

Κανόνες που κρατούν το σετ ενιαίο:
- **Ίδιο κάδρο**: head-and-shoulders, το κεφάλι ~70% του πλάτους, κενό από πάνω.
- **Ίδιο φόντο**: solid warm off-white (`#efe6d6`-ish). Το widget το κόβει σε κύκλο πάνω σε μαύρο.
- **Καμία στολή-καρναβάλι**: ένα μόνο αντικείμενο-σήμα ανά χαρακτήρα (μπαρ / στηθοσκόπιο / τρομπόνι).
- **Χωρίς κείμενο** μέσα στην εικόνα (τα μοντέλα γράφουν λάθος ελληνικά).

---

## 1. ΚΟΥΤΣ — ο γίγαντας *(το έχουμε ήδη)*

```
3D stylised character portrait, Pixar/DreamWorks style, semi-realistic. Giorgos, Greek man late 30s:
enormous, heavyset gentle giant — very broad shoulders and thick neck filling the frame, round belly
hinted below, big soft face. Completely bald shiny head, full thick dark beard neatly trimmed, thick
eyebrows, warm kind eyes, friendly grin. Black t-shirt with a small hand-block-printed pattern on the
chest. Head-and-shoulders, looking straight at camera, centred, plenty of headroom. Solid warm
off-white background, soft studio lighting, subsurface scattering skin, subtle pores and hair strands,
clean readable silhouette. Octane render, 4k, square 1:1.
```

**Παραλλαγή για το ΒΛΑΞ** (αν θέλεις να μη φοράει το t-shirt του καταστήματος):
αντικατάστησε τη φράση του t-shirt με:
`plain black t-shirt, a faded gold "ΞΙ"-like geometric mark barely visible on the chest`.

---

## 2. ΘΕΜΗΣ — ο γιατρός («θα τον αναγνωρίσετε επειδή θα τον δείτε να δαγκώνει το μπαρ»)

```
3D stylised character portrait, Pixar/DreamWorks style, semi-realistic. Themis, Greek man in his early
40s: lean and wiry, narrow shoulders, alert upright posture — the exact physical opposite of a heavyset
man. Short dark hair pushed back, three-day stubble, sharp cheekbones, thick dark eyebrows raised in
permanent mild diagnosis. Bright, intense, slightly manic but kind eyes behind clear round wire glasses;
a wide confident grin showing conspicuously perfect white teeth. Wearing a rumpled white doctor's coat
thrown over a black party shirt with the collar open, a stethoscope hanging casually around his neck
like a scarf. Head-and-shoulders, looking straight at camera, centred, plenty of headroom. Solid warm
off-white background, soft studio lighting, subsurface scattering skin, subtle pores and hair strands,
clean readable silhouette. Octane render, 4k, square 1:1.
```

Μικρές στροφές του χαρακτήρα, αν δεν σου βγει με την πρώτη:
- πιο τρελογιατρός: `one eyebrow higher than the other, hair slightly disheveled as if he has been awake since yesterday`
- πιο σοβαρός: `calm clinical expression, faint amused smile instead of a grin`
- το σήμα του: `holding up a tiny shot glass at chest height like a specimen he is about to prescribe`
  *(μόνο για μία από τις παραλλαγές — όχι στο βασικό idle)*

---

## 3. ΜΠΑΛΚΑΝ ΦΟΥΙΤ — ο οικοδεσπότης («ποιητής της Δ. Μακεδονίας», τρομπόνι)

```
3D stylised character portrait, Pixar/DreamWorks style, semi-realistic. Giannis, Greek man in his late
40s: medium build, slightly stooped from years behind a bar, broad friendly face weathered by mountain
winters. Long dark wavy hair falling past his shoulders, streaked with grey, tucked behind one ear; a
full untrimmed salt-and-pepper beard. Deep laugh lines, heavy-lidded warm brown eyes with an amused,
half-complaining expression, one eyebrow slightly raised. Wearing a worn dark denim shirt with sleeves
rolled up over a faded band t-shirt, a bartender's apron strap visible on one shoulder, a small
old-school tattoo on the forearm. The brass bell of a trombone catches the light at the bottom edge of
the frame, just below his shoulder. Head-and-shoulders, looking straight at camera, centred, plenty of
headroom. Solid warm off-white background, soft studio lighting, subsurface scattering skin, subtle
pores and hair strands, clean readable silhouette. Octane render, 4k, square 1:1.
```

Μικρές στροφές:
- πιο γκρινιάρης-με-αγάπη: `mouth slightly open mid-sentence, as if he has just said "μην καν'ς έτσ' τώρα"`
- πιο ποιητής: `softer gaze, chin slightly lifted, hand not visible`
- πιο μάγαζας: `a coffee-stained white towel over the shoulder instead of the apron strap`

---

## 4. Οι εκφράσεις (5 ανά χαρακτήρα — τις παίζει το widget)

Πάρε το εγκεκριμένο **master** του κάθε χαρακτήρα και ζήτα τις υπόλοιπες **με reference
image** (Gemini/nano-banana: ανέβασε την εικόνα και γράψε «same character, same framing,
same background, same lighting· άλλαξε μόνο …»). Ποτέ ξανά από το μηδέν — αλλιώς αλλάζει
πρόσωπο.

| state | τι ζητάς | πότε παίζει |
|---|---|---|
| `idle` | το master, ουδέτερο φιλικό βλέμμα | ηρεμία |
| `wave` | `raising one open hand in a small greeting beside the face, warmer smile` | άνοιγμα του chat |
| `thinking` | `eyes glancing up and to the side, one hand at the chin/beard, mouth closed, slight frown of concentration` | όσο τρέχει η απάντηση |
| `talking` | `mouth open mid-word, eyebrows lifted, animated and engaged` | όσο γράφει την απάντηση |
| `sorry` | `apologetic expression, slight shrug, both palms turned up at chest height` | «δεν το έχουμε» / handoff |

Χαρακτηριστικά ανά χαρακτήρα για το `thinking` (κρατούν το αστείο ζωντανό):
- Κουτς: `hand on the back of his bald head`
- Θέμης: `pressing two fingers to the side of his own neck as if taking his pulse`
- Φούιτ: `pinching the bridge of his nose, eyes shut, mid-sigh`

---

## 5. Πώς τα φτιάχνεις με Gemini

Στο Google AI Studio (ή με το `google-genai` SDK) με μοντέλο εικόνας
(`gemini-3-pro-image-preview`, `gemini-2.5-flash-image`, ή Imagen):

```bash
cd ~/Dropbox/vlax-archive
venv/bin/python bot/make_avatar.py --generate kouts themis fuit     # φτιάχνει masters
venv/bin/python bot/make_avatar.py                                   # κόβει τα κυκλικά
```

Χειροκίνητα: γέννα 6–8 εκδοχές, διάλεξε **μία** ανά χαρακτήρα, σώσε την ως
`bot/assets/<id>_master.png` (`kouts` / `themis` / `fuit`), και μετά τρέξε τις εκφράσεις
με reference image, σώζοντας ως `bot/assets/<id>_<state>.png`.

Τεστ μικρού μεγέθους πριν κλειδώσεις: δες το στα 48px. Αν δεν ξεχωρίζει ποιος είναι
ποιος — φαλακρός/γυαλιά/μαλλιά — άλλαξε το σιλουέτα-σήμα, όχι το χρώμα.
