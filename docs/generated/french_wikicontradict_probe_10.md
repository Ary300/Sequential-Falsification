# French WikiContradict Transfer Probe

This is a small multilingual transfer probe: English WikiContradict questions and answers are translated to French, then searched against French Wikipedia.

## Headline

- Completed examples: `10` / `10`
- Failed examples: `0`
- Top-1 gold-answer hit rate: `0.0`
- Top-1 conflict-answer hit rate: `0.0`
- Top-3 gold-answer hit rate: `0.0`
- Top-3 conflict-answer hit rate: `0.0`
- Top-3 both-hit rate: `0.0`

### 1

- English question: Which of the following are present in Nymphaea nouchali var. caerulea: apomorphine, aporphine, or neither?
- Translated question: Lesquels des éléments suivants sont présents dans Nymphaea nouchali var. caerulea : apomorphine, aporphine ou aucun des deux ?
- Translated gold answers: `['Apomorphine', 'Aporphine']`
- Translated conflict answers: `['Aporphine']`

### 2

- English question: Are there any other missiles besides the P-500 Bazalt that influenced the design of P-700 Granit missile?
- Translated question: Existe-t-il d'autres missiles que le P-500 Bazalt qui ont influencé la conception du missile P-700 Granit ?
- Translated gold answers: `['No.', 'Oui.']`
- Translated conflict answers: `['Oui.']`

### 3

- English question: Did the formation of the grooves on Phobos occur as a single event?
- Translated question: La formation des rainures sur Phobos s'est-elle produite en un seul événement ?
- Translated gold answers: `['No.', 'Oui.']`
- Translated conflict answers: `['Oui.']`

### 4

- English question: Did Bishop Heber meet D’Oyly in the 1840s in Patna ?
- Translated question: L'évêque Heber a-t-il rencontré D’Oyly dans les années 1840 à Patna ?
- Translated gold answers: `['Oui', 'Non']`
- Translated conflict answers: `['Non']`

### 5

- English question: What year did President Oler take the stand in court?
- Translated question: En quelle année le président Oler a-t-il pris la parole devant le tribunal ?
- Translated gold answers: `['Le président Oler a pris la parole en 1911', 'Le président Oler fait appel devant les tribunaux dans les années 1890']`
- Translated conflict answers: `['Le président Oler fait appel devant les tribunaux dans les années 1890']`
- `Robert Brasillach` gold=`False` conflict=`False`: Robert Brasillach ([ʁɔbɛʁ bʁazijak] ), né le 31 mars 1909 à Perpignan et mort fusillé le 6 février 1945 au fort de Montrouge, à Arcueil, est un homme de lett...
- `Auschwitz` gold=`False` conflict=`False`: Auschwitz (en allemand : Konzentrationslager Auschwitz , « camp de concentration d'Auschwitz ») est le plus grand complexe concentrationnaire du Troisième Re...
- `Camp de concentration de Natzweiler-Struthof` gold=`False` conflict=`False`: Le Konzentrationslager (KL) Natzweiler, plus connu en France sous le nom de camp du Struthof ou camp de concentration de Natzweiler-Struthof, est un camp de ...

This is a transfer spot-check, not a multilingual theorem-3 replacement.
