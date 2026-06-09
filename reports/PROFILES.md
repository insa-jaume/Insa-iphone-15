# People Dataset — Sourcing & Methodology Appendix

This file backs the **216 "core"** people in `data/all_people.csv` — the deeply-profiled top
leadership/board and marquee figures. It records (a) how the data was gathered, (b) how the
character indices were derived, and (c) the public sources used per company.

> **Note on the 572 "extended" people.** `data/all_people.csv` also contains 572 additional
> real, verifiable people (VPs, distinguished engineers, fellows, and named researchers such
> as paper authors), marked `data_tier = extended`. Their factual fields (title, education,
> prior company, notable work, origin where public) are in **`data/people_raw/<NN>_<slug>.csv`**,
> gathered from the same kinds of public sources listed below — official leadership/research
> pages, theorg.com, **arXiv paper bylines**, university/conference bios, and reputable press.
> Their character indices are assigned by the role rubric (not per-biography), and their
> compensation is blank (not public).

## How the data was gathered
For each company, public sources were searched and read: **SEC proxy statements (DEF 14A)**
for executive identities and compensation, **official company leadership pages**, **Wikipedia**,
and reputable press. Only verifiable facts were recorded; unknown fields were left blank rather
than guessed, and weakly-sourced fields were flagged. Compensation was recorded **only** for
disclosed *named executive officers* (NEOs) — for private companies (OpenAI, SpaceX) and
non-US-style disclosers (Saudi Aramco; TSMC discloses only the CEO) most pay is not public and
is left blank.

## How the 3 character indices were derived (interpretive)
The character indices are **not measurements**. They are consistent, transparent assessments of
**public figures** from their **documented public biographies**:

- **adversity_origin_score (0–100):** refugee / fled persecution / working-class / teen-single-
  mother / housing-project origins → 80–95; immigrant or first-generation / rural working-class →
  60–80; ordinary professional family, none documented → 40–55; privileged/dynastic → 20–35.
- **mental_strength (0–100):** documented resilience — survived near-death company crisis /
  public ousting-and-comeback / combat veteran / extreme documented adversity → 85–95; long
  high-pressure founder/CEO tenure → 78–90; senior exec → 62–78.
- **potential_index (0–100):** iconic founder-CEO or Nobel/Turing-level figure → 90–100; division
  CEO / co-founder / top researcher → 78–90; C-suite → 68–84; established director → 58–80.

The `documented_adversity` column in the CSV cites the specific public fact behind a high
adversity/mental score (e.g. "Son of Polish-Jewish Holocaust survivors").

## Notable documented origin stories (a sample, all sourced below)
- **Jensen Huang** (NVIDIA, CEO) — sent from Taiwan to the US as a child; cleaned bathrooms at a
  Kentucky boarding school.
- **Michael Kagan** (NVIDIA, CTO) — reportedly rejected by a Russian university over his Jewish
  name; funded his studies working as a cleaner.
- **Tim Cook** (Apple, CEO) — working-class Alabama; shipyard-worker father.
- **Johny Srouji** (Apple) — Arab-Christian minority in Israel; carpenter father.
- **Sergey Brin** (Alphabet, co-founder) — refugee; family fled Soviet antisemitism in 1979.
- **Ruth Porat** (Alphabet, President) — two-time breast-cancer survivor; father fled Vienna on
  Kristallnacht.
- **Satya Nadella** (Microsoft, CEO) — immigrant; raised a son with cerebral palsy.
- **Mustafa Suleyman** (Microsoft AI) — son of a Syrian immigrant taxi driver; Oxford dropout.
- **Jeff Bezos** (Amazon) — born to a 17-year-old single mother; adopted by a Cuban immigrant
  stepfather. **Indra Nooyi** (board) — immigrant who worked as a receptionist while at Yale.
- **Morris Chang** (TSMC, founder) — wartime displacement across China and Hong Kong; failed his
  MIT doctoral qualifier twice. **Ursula Burns** (board) — raised in a Manhattan housing project.
  **Rafael Reif** (board) — son of Eastern-European Jewish refugees who fled to Venezuela.
- **Hock Tan** (Broadcom, CEO) — immigrant from Penang on scholarship; two children with autism.
  **Henry Samueli** (chair) — son of Polish-Jewish Holocaust survivors.
- **Elon Musk** (Tesla/SpaceX) — immigrant via Canada. **Vaibhav Taneja** (Tesla CFO) — humble
  Delhi origins; rose from PwC trainee.
- **Susan Li** (Meta CFO) — immigrant from China; entered college at 15. **Tony Xu** (board) —
  immigrant; credits early work as a dishwasher.
- **Sarah Friar** (OpenAI CFO) — grew up amid The Troubles in Northern Ireland. **Mira Murati**
  (ex-CTO) — emigrated from Albania on a scholarship. **Fidji Simo** — first in her family to
  finish high school.
- **Tom Mueller** (SpaceX) — logger's son; worked as a logger to fund his education.

---

## Sources by company
Primary compensation figures come from each company's most recent DEF 14A proxy statement (or, for
TSMC, its annual report). SEC EDGAR HTML sometimes blocks automated fetching, in which case figures
were corroborated through reputable reporting of the same filing.

### NVIDIA
Comp (FY2025 NEOs): Huang $49,866,251; Kress $21,362,532; Puri $21,590,897; Shoquist $19,217,903;
Teter $19,201,821.
- nvidianews.nvidia.com/bios · en.wikipedia.org/wiki/Jensen_Huang · en.wikipedia.org/wiki/Chris_Malachowsky
- en.wikipedia.org/wiki/Curtis_Priem · spectrum.ieee.org/nvidia-cto-michael-kagan-profile · en.wikipedia.org/wiki/Bill_Dally
- en.wikipedia.org/wiki/John_Dabiri · research.nvidia.com/person/william-dally · DEF 14A FY2025 (SEC EDGAR CIK 0001045810)

### Apple
Comp (FY2024 NEOs): Cook $74.6M; Maestri/Adams/O'Brien/Williams ≈ $27.1–27.2M.
- apple.com/leadership · apple.com/newsroom/2026/04 (Cook→Exec Chair, Ternus→CEO) · macrumors.com/2025/01/10/tim-cook-2024-salary
- law360 (Adams ≈ $27.2M) · en.wikipedia.org/wiki/Tim_Cook · ynetnews.com (Johny Srouji) · Apple DEF 14A FY2025

### Alphabet (Google)
Comp (FY2024 NEOs): Pichai $10,725,043; Ashkenazi $49,978,135; Porat $30,166,427; Raghavan $46,992,166;
Schindler $47,024,009; Walker $30,162,760.
- Alphabet 2025 DEF 14A (SEC EDGAR CIK 0001652044) · en.wikipedia.org/wiki/Sundar_Pichai · en.wikipedia.org/wiki/Sergey_Brin
- en.wikipedia.org/wiki/Ruth_Porat · en.wikipedia.org/wiki/Demis_Hassabis · en.wikipedia.org/wiki/Jeff_Dean · blog.google (Porat)

### Microsoft
Comp (FY2025 NEOs): Nadella $96.5M; Hood $29.5M; Althoff $28.2M; Smith ≈ $28.3M; Numoto $11.87M.
- news.microsoft.com/source/leadership · Microsoft FY2025 DEF 14A (SEC EDGAR CIK 0000789019)
- cnbc.com/2025/10/21 (Nadella $96.5M) · theregister.com/2025/10/22 · en.wikipedia.org/wiki/Satya_Nadella · en.wikipedia.org/wiki/Mustafa_Suleyman

### Amazon
Comp (FY2024 NEOs): Bezos $1,681,840; Jassy $1,596,889; Olsavsky $25,717,606; Garman $33,180,619;
Herrington $34,193,958; Zapolsky $25,717,606; Selipsky $34,284,148.
- Amazon 2025 DEF 14A (SEC EDGAR CIK 0001018724) · aboutamazon.com/news/workplace/amazon-s-team-members
- en.wikipedia.org/wiki/Jeff_Bezos · en.wikipedia.org/wiki/Indra_Nooyi · en.wikipedia.org/wiki/Werner_Vogels · cnbc.com (Bezos teen-mother)

### TSMC
Comp: only C.C. Wei is public — FY2024 ≈ NT$2.42B (~US$74M, approximate conversion).
- tsmc.com/english/aboutTSMC/executives · investor.tsmc.com (board) · en.wikipedia.org/wiki/Morris_Chang
- en.wikipedia.org/wiki/C._C._Wei_(business_executive) · en.wikipedia.org/wiki/L._Rafael_Reif · en.wikipedia.org/wiki/Ursula_Burns
- TSMC 2024 Annual Report (governance/compensation chapter)

### Broadcom
Comp (FY2025 NEOs): Tan $205,278,006; Spears $28,164,046; Brazeal $28,619,011; Kawwas $2,115,626
(Tan FY2024 was only $2.6M cash due to front-loaded equity).
- Broadcom FY2025 DEF 14A (SEC EDGAR CIK 0001730168) · broadcom.com/company/about-us/executives · en.wikipedia.org/wiki/Hock_Tan
- en.wikipedia.org/wiki/Henry_Samueli · en.wikipedia.org/wiki/Henry_Nicholas · theregister.com/2024/02/28 (pay structure)

### Saudi Aramco
Comp: not individually disclosed (executive directors receive no board pay; non-exec remuneration not
itemized). All comp blank.
- aramco.com/en/about-us/our-leadership/board-of-directors · en.wikipedia.org/wiki/Amin_H._Nasser
- en.wikipedia.org/wiki/Yasir_Al-Rumayyan · en.wikipedia.org/wiki/Andrew_Liveris · en.wikipedia.org/wiki/Bob_Dudley · en.wikipedia.org/wiki/Stuart_Gulliver

### Tesla
Comp (FY2024 NEOs): Musk $0; Taneja $139,500,000; Zhu $376,000 (Zhu figure flagged unverified).
- Tesla 2025 DEF 14A (SEC EDGAR CIK 0001318605) · entrepreneur.com (Taneja $139.5M; Musk $0) · businesstoday.in (Taneja "Delhi boy")
- en.wikipedia.org/wiki/Elon_Musk · en.wikipedia.org/wiki/Vaibhav_Taneja · en.wikipedia.org/wiki/Robyn_Denholm · ir.tesla.com/corporate

### Meta Platforms
Comp (FY2024 NEOs): Zuckerberg $27,219,874; Olivan ≈ $25.5M; Li $23,620,488; Cox ≈ $23.6M;
Bosworth $23,594,826 (Zuckerberg salary $1; bulk is security/aircraft).
- meta.com/media-gallery/executives · Meta FY2024 DEF 14A (SEC EDGAR CIK 0001326801) · en.wikipedia.org/wiki/Susan_Li_(business_executive)
- en.wikipedia.org/wiki/Javier_Olivan · en.wikipedia.org/wiki/Tony_Xu · en.wikipedia.org/wiki/Patrick_Collison · en.wikipedia.org/wiki/Alexandr_Wang

### OpenAI (private — no comp disclosure)
- openai.com (leadership/board pages) · en.wikipedia.org/wiki/Sam_Altman · en.wikipedia.org/wiki/Ilya_Sutskever
- en.wikipedia.org/wiki/Mira_Murati · en.wikipedia.org/wiki/Sarah_Friar · en.wikipedia.org/wiki/Fidji_Simo · en.wikipedia.org/wiki/Adebayo_Ogunlesi

### SpaceX (private — no comp disclosure)
- en.wikipedia.org/wiki/Elon_Musk · en.wikipedia.org/wiki/Gwynne_Shotwell · en.wikipedia.org/wiki/Tom_Mueller
- en.wikipedia.org/wiki/Hans_Koenigsmann · aero.engin.umich.edu/people/dontchev-kiko · en.wikipedia.org/wiki/Garrett_Reisman · theorg.com/org/spacex

---

*Note on uncertainty:* a number of birth years, exact join dates, and a few origins were not
publicly confirmable and are left blank in the dataset rather than asserted. Where a single secondary
source was the only basis, the underlying research flagged it "(unverified)". Compensation figures for
NEOs trace to the cited proxy filings; where SEC EDGAR blocked automated retrieval, figures were
corroborated through multiple reputable reports of the same filing.
