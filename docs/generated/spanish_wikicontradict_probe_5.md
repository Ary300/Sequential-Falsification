# Spanish WikiContradict Transfer Probe

This is a small multilingual transfer probe: English WikiContradict questions and answers are translated to Spanish, then searched against Spanish Wikipedia.

## Headline

- Top-1 gold-answer hit rate: `0.4`
- Top-1 conflict-answer hit rate: `0.2`
- Top-3 gold-answer hit rate: `0.4`
- Top-3 conflict-answer hit rate: `0.4`
- Top-3 both-hit rate: `0.4`

### 1

- English question: Which of the following are present in Nymphaea nouchali var. caerulea: apomorphine, aporphine, or neither?
- Spanish question: ¿Cuáles de los siguientes están presentes en Nymphaea nouchali var. caerulea: apomorfina, aporfina o ninguno?
- Spanish gold answers: `['Apomorfina', 'Aporfinas']`
- Spanish conflict answers: `['Aporfinas']`

### 2

- English question: Are there any other missiles besides the P-500 Bazalt that influenced the design of P-700 Granit missile?
- Spanish question: ¿Hay algún otro misil además del P-500 Bazalt que haya influido en el diseño del misil P-700 Granit?
- Spanish gold answers: `['No.', 'Sí.']`
- Spanish conflict answers: `['Sí.']`

### 3

- English question: Did the formation of the grooves on Phobos occur as a single event?
- Spanish question: ¿La formación de los surcos en Fobos ocurrió como un solo evento?
- Spanish gold answers: `['No.', 'Sí.']`
- Spanish conflict answers: `['Sí.']`
- `Fobos (satélite)` gold=`True` conflict=`False`: Fobos (del griego Φóβoς, "miedo") es el más grande de los dos satélites de Marte y el más cercano al planeta, siendo Deimos el otro satélite. Ambos fueron de...
- `Heracles` gold=`True` conflict=`True`: Heracles o Héracles​ (en griego antiguo: Ἡρακλῆς),​ llamado Hércules por los romanos, es el héroe​ más célebre de la mitología griega.​ Es especialmente cono...

### 4

- English question: Did Bishop Heber meet D’Oyly in the 1840s in Patna ?
- Spanish question: ¿El obispo Heber conoció a D’Oyly en la década de 1840 en Patna ?
- Spanish gold answers: `['Sí', 'No']`
- Spanish conflict answers: `['No']`
- `Historia de Daca` gold=`True` conflict=`True`: La historia de Daca, una de las megaciudades habitadas más antiguas del mundo, comienza con la existencia de los primeros asentamientos urbanizados en el áre...

### 5

- English question: What year did President Oler take the stand in court?
- Spanish question: ¿En qué año el presidente Oler subió al estrado en el tribunal?
- Spanish gold answers: `['El presidente Oler subió al estrado en 1911', 'El presidente Oler apeló ante el tribunal en la década de 1890']`
- Spanish conflict answers: `['El presidente Oler apeló ante el tribunal en la década de 1890']`

This is a transfer spot-check, not a multilingual theorem-3 replacement.
