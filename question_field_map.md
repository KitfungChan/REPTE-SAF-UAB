# L2Q3 Mappament nº de pregunta ↔ camp ID ↔ escala/direcció ↔ denominador ↔ taula d'estadístiques

> Cobre totes les 16 preguntes de l'enquesta (inclús la nova pregunta d'accesibilidad/equitat C6 i els camps desmullats d'E1/E2), per un total de **18 categories de pregunta** (25 files de camp).
> Ús: qualsevol script d'anàlisi pot alinear segons «una pregunta, un camp»; l'ordre de columnes és:
> **nº de pregunta / camp ID / escala(escalar) / direcció(sentit) / denominador(denominators) / taula d'estadístiques corresponent / col de 2026 / nota**

## Explicació

- **escala escalar**: `categorical`(categoría/nominal)·`binary`(0-1)·`ordinal`(ordinal)·`interval`(interval)·`ratio`(ratio).
- **direcció sentit**: `positive`(més gran millor)/`negative`(més gran pitjor); binary/categorical = `-`.
- **preguntada_a**: `well_defined`(tothom)/`well_defined_n_excluded`(sols un subgrups, excloent la resta).
- **track_pairing**: `true` sols per a `canvi_benestar`(ancora longitudinal).
- **denominador**: `all_valid`(tothom and valid)·`movers_n`(practicans A3∈{1,2})·`abonat_sisi`(membres Sí)·`nonmovers_n`(no-practicans A3=3, target ≥150).
- **ull de n**: n_min_conclusion=30; n_min_privacy=30 és una recomanació d'ull de privacitat, no és una garantia; subgrups n<30 no es mostren.

## Taulella de mappament

| nº de pregunta | camp ID | escala(escalar) | direcció(sentit) | denominador(denominators) | taula d'estadístiques | col de 2026 | nota |
|---|---|---|---|---|---|---|---|
| A1 gène | generes | categorical | - | all_valid | pertinencia_generes | col2 | home/donna/no binari/sense opinió; per a creure de gène × pertinença |
| A3 situació | situacio | categorical | - | all_valid | situacio_grups | col4 | **clau de grup**: {1,2}→practicans movers_n; {3}→no-practicans nonmovers_n; preguntada_a=well_defined_n_excluded |
| A4 ¿membre? | abonat | binary | - | abonat_sisi | abonat_grups | col5 | Sí/No; denominador = nombre de membres |
| B1 freqüència | frecuencia | ordinal | positive | movers_n | freq_esport | col16(falten 106) | 1=1 setmanal…4>5 setmanals; llim de 4 dies; sols practicans |
| B3 ¿assolit? | habit_estar | ordinal | positive | movers_n | habit_arrel | — | 1=no assolit,2=gairbé assolit,3=assolit; sols practicans |
| C1 salud física | salut_fisica | interval | positive | all_valid | salut_fisica | col11-15 | int 1-5; tothom positiu |
| C2 ànim | stat_emocional | interval | positive | all_valid | stat_emocional | col16-19 | int 1-5; tothom positiu |
| C3 hores de son | son_hores | ordinal | - | all_valid | son_hores | col20-23 | ordered int interval 0-1…>9; no monòton, sentit=- |
| C3 qualitat de son | son_qualitat | interval | positive | all_valid | son_qualitat | col24-27 | int 1-5; tothom positiu (desmultiat de les hores) |
| C4 estrès | estres | ordinal | negative | all_valid | estres_freq | col28-31 | de freqüència Mai…Molt sovint; puntuació inversa |
| C5 beneficis | beneficis | interval | positive | movers_n | benefici_movers | col32-36 | int 1-5; sols practicans |
| D1 vincle/pertinença | pertinenca | interval | positive | all_valid | pertinencia | col37-40 | int 1-5; tothom positiu |
| C6 accesibilidad/equitat | accesibilidad | ordinal | positive | all_valid | accesibilidad_grups | novell | percepció d'accesibilitat del SAF per a tu (1=molt difícil…5=molt accessible); tothom positiu; mesura directa d'equitat |
| E1 obacle(1) | obstacle_1 | binary | - | nonmovers_n | obstacles_noesport | novell | no hi ha temps / s'educa molt; 0/1 |
| E1 obacle(2) | obstacle_2 | binary | - | nonmovers_n | obstacles_noesport | novell | lluny / no hi ha transport; 0/1 |
| E1 obacle(3) | obstacle_3 | binary | - | nonmovers_n | obstacles_noesport | novell | car / no hi te descompte de membre; 0/1 |
| E1 obacle(4) | obstacle_4 | binary | - | nonmovers_n | obstacles_noesport | novell | no m'interessa / no hi te preferència; 0/1 |
| E1 obacle(5) | obstacle_5 | binary | - | nonmovers_n | obstacles_noesport | novell | raons físiques / lesions; 0/1 |
| E1 obacle(6) | obstacle_6 | binary | - | nonmovers_n | obstacles_noesport | novell | falta companyia / ningú; 0/1 |
| E1 obacle(7) | obstacle_7 | binary | - | nonmovers_n | obstacles_noesport | novell | falta vestidor / instal·lacions; 0/1 |
| E2intenació(preci) | intencio_1 | interval | positive | nonmovers_n | intencio_noesport | novell | 4 tipus d'incentius en camps; int 1-5 |
| E2intenació(flexibilitat de temps) | intencio_2 | interval | positive | nonmovers_n | intencio_noesport | novell | temps / flexibilitat de classe; int 1-5 |
| E2intenació(community social) | intencio_3 | interval | positive | nonmovers_n | intencio_noesport | novell | social / companyia / comunitat; int 1-5 |
| E2intenació(orientació de salut) | intencio_4 | interval | positive | nonmovers_n | intencio_noesport | novell | beneficis de salut / orientació; int 1-5 |
| E3 ancora longitudinal | canvi_benestar | ordinal | positive | all_valid | canvi_benestar_panel | novell·longitudinal | comparació fa un any, negatiu→positiu; track_pairing=true |

## Diccionari de denominadors(denominators)

| name | criteri | n_min_conclusion | n_min_privacy | target_n | ús |
|---|---|---|---|---|---|
| all_valid | tothom recollit and de valid | 30 | 30 | — | A1/A3/A4/C1/C2/C3/C4/C6/D1/E3 |
| movers_n | practicans A3∈{1,2} | 30 | 30 | — | B1/B3/C5 (falten 106) |
| abonat_sisi | membres A4=Sí | 30 | 30 | — | % de membres de A4 |
| nonmovers_n | no-practicans A3=3 | 30 | 30 | ≥150 | obacles E1 /intenació E2 |

> Nota: `n_min_privacy=30` sols és una recomanació d'ull de privacitat, no és una garantia; les dades reals del SAF no hi entren al repositori, subgrups n<30 no es mostren.

## Vista general de les taules d'estadístiques(metrics)

| metric | by(camp) | denominador | taula | direcció |
|---|---|---|---|---|
| situacio_grups | situacio | all_valid | situacio_grups | — |
| abonat_grups | abonat | abonat_sisi | abonat_grups | — |
| freq_esport | frecuencia | movers_n | freq_esport | + |
| habit_arrel | habit_estar | movers_n | habit_arrel | + |
| salut_fisica | salut_fisica | all_valid | salut_fisica | + |
| stat_emocional | stat_emocional | all_valid | stat_emocional | + |
| son_hores | son_hores | all_valid | son_hores | - |
| son_qualitat | son_qualitat | all_valid | son_qualitat | + |
| estres_freq | estres | all_valid | estres_freq | - |
| benefici_movers | beneficis | movers_n | benefici_movers | + |
| pertinencia_generes | pertinenca × generes | all_valid | pertinencia_generes | + |
| pertinencia | pertinenca | all_valid | pertinencia | + |
| accesibilidad_grups | accesibilidad | all_valid | accesibilidad_grups | + (accesibilidad/equitat) |
| obstacles_noesport | obstacle_1..7 | nonmovers_n | obstacles_noesport | — |
| intencio_noesport | intencio_1..4 | nonmovers_n | intencio_noesport | + |
| canvi_benestar_panel | canvi_benestar | all_valid | canvi_benestar_panel | + (parellament longitudinal) |
