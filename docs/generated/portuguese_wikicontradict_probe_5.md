# Portuguese WikiContradict Transfer Probe

This is a small multilingual transfer probe: English WikiContradict questions and answers are translated to Portuguese, then searched against Portuguese Wikipedia.

## Headline

- Completed examples: `5` / `5`
- Failed examples: `0`
- Top-1 gold-answer hit rate: `0.0`
- Top-1 conflict-answer hit rate: `0.0`
- Top-3 gold-answer hit rate: `0.0`
- Top-3 conflict-answer hit rate: `0.0`
- Top-3 both-hit rate: `0.0`

### 1

- English question: Which of the following are present in Nymphaea nouchali var. caerulea: apomorphine, aporphine, or neither?
- Translated question: Quais das seguintes opções estão presentes em Nymphaea nouchali var. caerulea: apomorfina, aporfina ou nenhuma das duas?
- Translated gold answers: `['Apomorfina', 'Aporfinas']`
- Translated conflict answers: `['Aporfinas']`

### 2

- English question: Are there any other missiles besides the P-500 Bazalt that influenced the design of P-700 Granit missile?
- Translated question: Existem outros mísseis além do P-500 Bazalt que influenciaram o projeto do míssil P-700 Granit?
- Translated gold answers: `['Nº.', 'Sim.']`
- Translated conflict answers: `['Sim.']`

### 3

- English question: Did the formation of the grooves on Phobos occur as a single event?
- Translated question: A formação das ranhuras em Fobos ocorreu como um único evento?
- Translated gold answers: `['Nº.', 'Sim.']`
- Translated conflict answers: `['Sim.']`

### 4

- English question: Did Bishop Heber meet D’Oyly in the 1840s in Patna ?
- Translated question: O bispo Heber conheceu D’Oyly na década de 1840 em Patna ?
- Translated gold answers: `['Sim', 'Não']`
- Translated conflict answers: `['Não']`

### 5

- English question: What year did President Oler take the stand in court?
- Translated question: Em que ano o presidente Oler testemunhou no tribunal?
- Translated gold answers: `['Presidente Oler testemunhou em 1911', 'O presidente Oler apelou no tribunal na década de 1890']`
- Translated conflict answers: `['O presidente Oler apelou no tribunal na década de 1890']`

This is a transfer spot-check, not a multilingual theorem-3 replacement.
