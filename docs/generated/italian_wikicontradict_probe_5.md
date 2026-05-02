# Italian WikiContradict Transfer Probe

This is a small multilingual transfer probe: English WikiContradict questions and answers are translated to Italian, then searched against Italian Wikipedia.

## Headline

- Completed examples: `5` / `5`
- Failed examples: `0`
- Top-1 gold-answer hit rate: `0.2`
- Top-1 conflict-answer hit rate: `0.2`
- Top-3 gold-answer hit rate: `0.2`
- Top-3 conflict-answer hit rate: `0.2`
- Top-3 both-hit rate: `0.2`

### 1

- English question: Which of the following are present in Nymphaea nouchali var. caerulea: apomorphine, aporphine, or neither?
- Translated question: Quali dei seguenti sono presenti in Nymphaea nouchali var. caerulea: apomorfina, aporfina o nessuna delle due?
- Translated gold answers: `['Apomorfina', 'Aporfina']`
- Translated conflict answers: `['Aporfina']`

### 2

- English question: Are there any other missiles besides the P-500 Bazalt that influenced the design of P-700 Granit missile?
- Translated question: Ci sono altri missili oltre al P-500 Bazalt che hanno influenzato il design del missile P-700 Granit?
- Translated gold answers: `['N&#176;', 'Sì, sì.']`
- Translated conflict answers: `['Sì, sì.']`

### 3

- English question: Did the formation of the grooves on Phobos occur as a single event?
- Translated question: La formazione dei solchi su Phobos si è verificata come un singolo evento?
- Translated gold answers: `['N&#176;', 'Sì, sì.']`
- Translated conflict answers: `['Sì, sì.']`
- `Marte (astronomia)` gold=`True` conflict=`True`: Marte è il quarto pianeta del sistema solare in ordine di distanza dal Sole; è visibile a occhio nudo ed è uno dei pianeti di tipo terrestre (roccioso) come ...
- `Clima di Marte` gold=`True` conflict=`True`: Il clima di Marte è da secoli oggetto di curiosità scientifica sia perché è l'unico pianeta terrestre la cui superficie può essere facilmente osservata diret...

### 4

- English question: Did Bishop Heber meet D’Oyly in the 1840s in Patna ?
- Translated question: Il vescovo Heber incontrò D’Oyly nel 1840 a Patna ?
- Translated gold answers: `['Si', 'No']`
- Translated conflict answers: `['No']`

### 5

- English question: What year did President Oler take the stand in court?
- Translated question: In che anno il presidente Oler ha preso la parola in tribunale?
- Translated gold answers: `['Il presidente Oler prese posizione nel 1911', "Il presidente Oler ricorre in tribunale negli anni '90 dell'Ottocento"]`
- Translated conflict answers: `["Il presidente Oler ricorre in tribunale negli anni '90 dell'Ottocento"]`

This is a transfer spot-check, not a multilingual theorem-3 replacement.
