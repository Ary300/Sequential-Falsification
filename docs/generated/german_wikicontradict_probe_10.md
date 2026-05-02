# German WikiContradict Transfer Probe

This is a small multilingual transfer probe: English WikiContradict questions and answers are translated to German, then searched against German Wikipedia.

## Headline

- Completed examples: `10` / `10`
- Failed examples: `0`
- Top-1 gold-answer hit rate: `0.1`
- Top-1 conflict-answer hit rate: `0.1`
- Top-3 gold-answer hit rate: `0.1`
- Top-3 conflict-answer hit rate: `0.1`
- Top-3 both-hit rate: `0.1`

### 1

- English question: Which of the following are present in Nymphaea nouchali var. caerulea: apomorphine, aporphine, or neither?
- Translated question: Welche der folgenden sind in Nymphaea nouchali var. caerulea vorhanden: Apomorphin, Aporphin oder keines von beiden?
- Translated gold answers: `['Apomorphin', 'Aporphin']`
- Translated conflict answers: `['Aporphin']`

### 2

- English question: Are there any other missiles besides the P-500 Bazalt that influenced the design of P-700 Granit missile?
- Translated question: Gibt es neben der P-500 Bazalt noch andere Raketen, die das Design der P-700 Granit-Rakete beeinflusst haben?
- Translated gold answers: `['Nr.', 'Ja.']`
- Translated conflict answers: `['Ja.']`

### 3

- English question: Did the formation of the grooves on Phobos occur as a single event?
- Translated question: Ist die Bildung der Rillen auf Phobos als ein einziges Ereignis aufgetreten?
- Translated gold answers: `['Nr.', 'Ja.']`
- Translated conflict answers: `['Ja.']`
- `Opportunity` gold=`True` conflict=`True`: Opportunity (englisch für Chance/Gelegenheit) war ein US-amerikanischer Erkundungsroboter zur geologischen Erforschung des Mars, der von 2004 bis 2018 aktiv ...

### 4

- English question: Did Bishop Heber meet D’Oyly in the 1840s in Patna ?
- Translated question: Hat Bischof Heber D’Oyly in den 1840er Jahren in Patna getroffen?
- Translated gold answers: `['Ja', 'nein']`
- Translated conflict answers: `['nein']`

### 5

- English question: What year did President Oler take the stand in court?
- Translated question: In welchem Jahr trat Präsident Oler vor Gericht?
- Translated gold answers: `['Präsident Oler trat 1911 in den Zeugenstand', 'Präsident Oler legte in den 1890er Jahren vor Gericht Berufung ein']`
- Translated conflict answers: `['Präsident Oler legte in den 1890er Jahren vor Gericht Berufung ein']`

This is a transfer spot-check, not a multilingual theorem-3 replacement.
