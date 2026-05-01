# Open-Wikipedia Retrieval Probe

This probe replaces the benchmark-contained retrieval corpus with live Wikipedia search and page extracts.
It is still a lightweight open-web probe rather than a full production RAG service, but it is materially closer to deployment than the bounded in-benchmark BM25 demo.

## Headline

- Top-1 gold-answer hit rate: `0.3`
- Top-1 conflict-answer hit rate: `0.0`
- Top-5 gold-answer hit rate: `0.3`
- Top-5 conflict-answer hit rate: `0.1`
- Top-5 both-hit rate: `0.1`
- Top-5 neither-hit rate: `0.7`

## Example Retrievals

### 1

- Question: Which of the following are present in Nymphaea nouchali var. caerulea: apomorphine, aporphine, or neither?
- Gold answers: `['Apomorphine', 'Aporphine', 'Apomorphine']`
- Conflict answers: `['Aporphine']`

### 2

- Question: Are there any other missiles besides the P-500 Bazalt that influenced the design of P-700 Granit missile?
- Gold answers: `['No.', 'Yes.', 'No.']`
- Conflict answers: `['Yes.']`

### 3

- Question: Did the formation of the grooves on Phobos occur as a single event?
- Gold answers: `['No.', 'Yes.', 'No.']`
- Conflict answers: `['Yes.']`
- `Water on Mars` gold=`True` conflict=`False`: Although very small amounts of liquid water may occur transiently on the surface of Mars, limited to traces of dissolved moisture from the atmosphere and thin films, large quant...
- `Solar System` gold=`True` conflict=`False`: The Solar System is the gravitationally bound system of the Sun and the masses that orbit it, most prominently its eight planets, of which Earth is one. The system formed about ...
- `Enceladus` gold=`True` conflict=`False`: Enceladus is the sixth-largest moon of Saturn and the 18th largest in the Solar System. It is about 500 kilometres (310 miles) in diameter, about a tenth of that of Saturn's lar...
- `Climate of Mars` gold=`True` conflict=`False`: The climate of Mars has been a topic of scientific curiosity for centuries, in part because it is the only terrestrial planet whose surface can be easily directly observed in de...
- `Ariel (moon)` gold=`True` conflict=`False`: Ariel is the fourth-largest moon of Uranus. Ariel orbits and rotates in Uranus's equatorial plane, which is almost perpendicular to the planet's orbit, giving the moon an extrem...

### 4

- Question: Did Bishop Heber meet D’Oyly in the 1840s in Patna ?
- Gold answers: `['Yes', 'No', 'Yes']`
- Conflict answers: `['No']`

### 5

- Question: What year did President Oler take the stand in court?
- Gold answers: `['President Oler took the stand in 1911', 'President Oler appeard in court in the 1890s', 'President Oler took the stand in 1911']`
- Conflict answers: `['President Oler appeard in court in the 1890s']`
- `James Baldwin` gold=`False` conflict=`False`: James Arthur Baldwin (né Jones; August 2, 1924 – December 1, 1987) was an American writer and civil rights activist who garnered acclaim for his essays, novels, plays, and poems...
- `Timeline of the Joe Biden presidency (2021 Q3)` gold=`False` conflict=`False`: The following is a timeline of the presidency of Joe Biden during the third quarter of 2021, from July 1 to September 30, 2021. For a complete itinerary of his travels, see List...

## Read

- The useful signal is whether open retrieval surfaces the gold answer, the stale/conflicting answer, or both.
- A high both-hit rate is the deployment regime where arbitration matters most, because retrieval is surfacing genuine conflict rather than a single clean source.
