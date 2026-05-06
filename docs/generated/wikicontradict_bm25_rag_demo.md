# WikiContradict Retrieval-Backed RAG Demo

This is a small retrieval-backed demo over naturally occurring Wikipedia contradiction passages from WikiContradict. It is not a full Wikipedia dump experiment, but it does replace fixed hand-assigned passages with an actual BM25-style retrieval step.

## Headline

- Top-1 aligned retrieval rate: `0.616601`
- Top-1 conflict retrieval rate: `0.300395`
- Top-5 contains both aligned and conflicting passages: `0.719368`

## Example Retrievals

### 1

- Question: Which of the following are present in Nymphaea nouchali var. caerulea: apomorphine, aporphine, or neither?
- Gold answers: `['Apomorphine', 'Aporphine']`
- Conflict answers: `['Aporphine']`
- `aligned` score `47.812438`: The underwater rhizomes of nymphaea nouchali var. caerulea are edible. Like other species in the genus, nymphaea nouchali var. caerulea contains the psychoactive alkaloid aporph...
- `conflict` score `40.742639`: Apomorphine is said to be main psychoactive compound present in nymphaea nouchali var. caerulea. Other compounds include nuciferine.
- `conflict` score `40.640995`: Like other species in the genus, Nymphaea nouchali var. caerulea contains the psychoactive alkaloid aporphine (not to be confused with apomorphine, a metabolic product of aporph...
- `aligned` score `14.73376`: Apomorphine is said to be main psychoactive compound present.
- `aligned` score `12.31311`: Other methods of bleeding control in surgery include the use of blood substitutes, which at present do not carry oxygen but expand the volume of the blood to prevent shock. Bloo...

### 2

- Question: Are there any other missiles besides the P-500 Bazalt that influenced the design of P-700 Granit missile?
- Gold answers: `['No.', 'Yes.']`
- Conflict answers: `['Yes.']`
- `aligned` score `49.732795`: The P-700 was derived from the P-500 Bazalt missile with a turbojet.
- `conflict` score `39.990148`: The missile was partially derived from the P-500 Bazalt.
- `conflict` score `10.539327`: Alonso del Castillo Maldonado (died after 1547) was an early Spanish explorer in the Americas. He was one of the last four survivors of the Pánfilo de Narváez expedition, along ...
- `aligned` score `10.372646`: In the spring of 1528, during the Pánfilo de Narváez's 1527 expedition, thirteen of the fifteen survivors decided to leave the Galveston island, abandoning Cabeza de Vaca (becau...
- `aligned` score `9.58606`: Eastern Orthodox Church reject as incompatible with the Orthodox faith any such use of the "two lungs" expression to imply that the Eastern Orthodox and Roman Catholic churches ...

### 3

- Question: Did the formation of the grooves on Phobos occur as a single event?
- Gold answers: `['No.', 'Yes.']`
- Conflict answers: `['Yes.']`
- `conflict` score `15.83311`: In November 2018, following further computational probability analysis, astronomers concluded that the many grooves on Phobos were caused by boulders, ejected from the asteroid ...
- `aligned` score `10.353819`: The model designed in 2015 supported the discovery that some of the grooves are younger than others, implying that the process that produces the grooves is ongoing.
- `conflict` score `8.032582`: Amanieu d'Albret was one of the six cardinals who did not participate in the 1513 papal conclave.
- `conflict` score `8.032582`: Amanieu d'Albret was one of the six cardinals who did not participate in the 1513 papal conclave.
- `aligned` score `7.570973`: Bombus polaris is part of the subgenus Alpinobombus along with Bombus alpinus, Bombus balteatus, Bombus hyperboreus, and Bombus neoboreus. Alpinobombus bees occur in arctic and ...

### 4

- Question: Did Bishop Heber meet D’Oyly in the 1840s in Patna ?
- Gold answers: `['Yes', 'No']`
- Conflict answers: `['No']`
- `aligned` score `41.740413`: Bishop Heber, who visited Patna in the 1840s, described Charles D'Oyly as the “best gentleman artist I ever met”.
- `conflict` score `11.600597`: Amanieu d'Albret was one of the six cardinals who did not participate in the 1513 papal conclave.
- `conflict` score `11.600597`: Amanieu d'Albret was one of the six cardinals who did not participate in the 1513 papal conclave.
- `conflict` score `10.279184`: After working for the Company for forty years, Charles D'Oyly's failing health compelled him to retire and leave India in 1838
- `aligned` score `10.013759`: Charles D'Oyly sketched incessantly and took an active interest in the arts generally, finding these leisure pursuits to be an agreeable way to relieve the boredom associated wi...

### 5

- Question: What year did President Oler take the stand in court?
- Gold answers: `['President Oler took the stand in 1911', 'President Oler appeard in court in the 1890s']`
- Conflict answers: `['President Oler appeard in court in the 1890s']`
- `aligned` score `18.92788`: President Wesley M. Oler took the stand for the company in 1911 when detectives traveled to Rockland Lake to find the icehouses packed with ice but no workers to load the produc...
- `conflict` score `18.92788`: President Wesley M. Oler took the stand for the company in 1911 when detectives traveled to Rockland Lake to find the icehouses packed with ice but no workers to load the produc...
- `conflict` score `7.601481`: Amanieu d'Albret was one of the six cardinals who did not participate in the 1513 papal conclave.
- `conflict` score `7.601481`: Amanieu d'Albret was one of the six cardinals who did not participate in the 1513 papal conclave.
- `aligned` score `7.493734`: In 1969, Valgard Murray worked with Else Christensen to found the Odinist Fellowship, and served as vice president.

## Read

- This is best used as a deployment-style discussion figure, not as a replacement for the main benchmark matrix.
- The useful point is that once retrieval is made explicit, the system often surfaces both supportive and stale passages, which is exactly the setting where the arbitration rule matters.
