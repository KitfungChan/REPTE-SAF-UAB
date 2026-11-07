# REPTE SAF UAB 2026 — repositori del projecte del repte

Aquest repositori és el **repositori complet** del projecte del repte **REPTE SAF UAB 2026** (40è aniversari del SAF, 11/7–8).
Hi entra l'entregable i els materials del repte d'aquesta edició; les diferents parts (resultats de la tria de cada equip) es concentren en un mateix directori.

> ⚠️ Les dades reals del SAF **no hi pot entrar al repositori** (regla del repte). `.gitignore` ja exclou `DADES/` i les taules/PDF originals.

## Tria: L2Q3 «Què hauríem de mesurar l'any vinent?»

Es dissenya la segona enquesta / segon sistema de mesura, perquè el SAF pot parlar del «retorn de veritat»:
el retorn queda limitat al benestar / hàbit / pertinença autoinformats de l'estudiant (benestar, hàbit, pertinença), no a diners ni a notes.

## Entregables (L2Q3)

| Fitxer | Explicació |
|---|---|
| `2026-11-07-L2Q3-问卷原文.docx` | Text original de l'enquesta (replicable) |
| `2026-11-07-L2Q3-测量体系攻坚方案.docx` | Tria i pla d'atac del sistema de mesura |
| `SAF_L2Q3_presentacio.pptx` | Presentació de 3 minuts |
| `2026-11-07-L2Q3-数据模型模板.xlsx` | Plantilla del modelo de dades |
| `saf_enquesta_analisi.ipynb` | Notebook d'anàlisi de l'enquesta |

### Modelo de dades (schema + diagrama ER + validador executable)

L'entregable tènic del modelo de dades, coherent amb els documents d'aquesta taula. **`schema.yaml` és l'única font autoritativa llegible per màquina del modelo de dades** (preguntes / escales / direcció / Qualificació per salt / denominadors / onades); la resta de fitxers s'orguen al voltant seu, sense redefinir cada cop el mateix modelo:

| Fitxer | Explicació | Relació amb `schema.yaml` |
|---|---|---|
| `schema.yaml` | Metadades de les preguntes + definició de denominadors + nº d'invitats per onada | **única font llegible per màquina** |
| `question_field_map.md` | Mappament pregunta ↔ camp ↔ escala/direcció ↔ denominador ↔ taula d'estadístiques | Índex llegible per a humans exportat des de `schema.yaml` |
| `validate.py` | Corre amb dades simulades integrades: construeix la tabla larga, calcula Denominator/Metric, corre les comprovacions d'afirmacions | Consumidor executable de `schema.yaml` |
| `saf_model_er.html` | Vista prèvia estàtica del diagrama ER (s'obre directament al navegador) | Producte de vista prèvia de `entitats.svg` |
| `saf_model.py` | Prototype de modelo relacional executable (layers Storage/Dimension/Presentation, codi pur en python) | **referència / mirror històric**, no font autoritativa; no el modifiquis com a segona definició del modelo |

Nota: el diagrama d'entitats (`entitats.svg`) el gestiona un altre membre de l'equip.

Ideia central del modelo de dades: **es substiteix la wide table de 33 cols originals per una tabla larga, on cada percentual porta el seu denominador n**, convertint els buits de l'enquesta 2026 (denominador impossible de reconstruir, criteris de pregunta salt desuniforms) en un punt a favor. Més detalls a `schema.yaml`.

## Restriccions dures (cada número ha de dir d'on surt)

- **font, denominador n, contra quin grup es compara, moment únic**
- Les dades reals sols serveixen per aquest repte; no es publiquen ni s'exporten fora de l'equip, no s'identifica ningú (subgrups n<30 no es mostren)

## Normativa de l'entrega

- Les dades reals del SAF no hi paten al repositori (veure `.gitignore`)
- Els missatges de commit són curtet, en castellà/anglès, i descriuen el canvi

## Referències

Harvey S B, Øverland S, Hatch S L, et al. Exercise and the prevention of depression: results of the HUNT cohort study[J]. American journal of psychiatry, 2018, 175(1): 28-36.

Cornelissen V A, Smart N A. Exercise training for blood pressure: a systematic review and meta‐analysis[J]. Journal of the American heart association, 2013, 2(1): e004473.

Rhodes R E, Smith N E I. Personality correlates of physical activity: a review and meta-analysis[J]. British journal of sports medicine, 2006, 40(12): 958-965.

Sutin A R, Stephan Y, Luchetti M, et al. The five-factor model of personality and physical inactivity: A meta-analysis of 16 samples[J]. Journal of research in personality, 2016, 63: 22-28.

Caille P, Stephan Y, Sutin A R, et al. Personality and change in physical activity across 3–10 years[J]. Psychology & health, 2024, 39(5): 670-690.
