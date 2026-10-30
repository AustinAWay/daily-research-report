# CITATIONS (example episode) of Kestin et al. 2025 (Sci Rep, doi 10.1038/s41598-025-97652-6)
Pulled Fri 2026-10-30 ~08:11 CT (13:11 UTC). Window: **publication date 2026-10-01 .. 2026-10-30**.

## Counts (cross-checked)
| source | query | result |
|---|---|---|
| OpenAlex | works?filter=cites:W4411505840,from_publication_date:2026-10-01,to_publication_date:2026-10-30 | **23** |
| Semantic Scholar | /paper/DOI:.../citations, publicationDate in window (2 S2 records dated 2026-12 excluded) | **27** |
| overlap (same DOI) | | 14 |
| **unique union** | OpenAlex ∪ S2 | **36** |
| all-time total | OpenAlex cited_by_count (updated 2026-10-29T09:56:32.521200) | **211** |
| all-time total | S2 citationCount (influential 10) | **219** |
(OpenAlex `from_created_date` is paywalled ("Plan upgrade required"), so the window is by publication date only. No API key requested.)

## How they cite it (classification from S2 citation contexts + 2 open full texts; S2 returned no intents for any of these)
- NO READABLE CONTEXT: **20**
- SUPPORTING, no caveat: **9**
- NEUTRAL / passing: **2**
- CRITICAL / LIMITS: **1**
- SUPPORTING, notes immediate: **1**
- SUPPORTING, notes post-test: **1**
- SUPPORTING, notes short-term: **1**
- UNCLEAR: **1**

Readable contexts: **16 of 36**. Of those 16: **9** cite it as plain evidence that AI tutoring works / students learned more (no timing caveat); **3** describe the gains accurately as immediate / short-term / post-test but don't treat that as a limit; **1** calls out the timing as a limit (Augmentation or Erosion?, Educ Psychol Rev: "on post-lesson tests rather than at a delay"); 2 neutral; 1 unclear.

## Honest "frustrating" angle (supported)
Of the October citing papers whose citing sentence can be read, most (9/16) repeat the headline as "it works", and only 1 flags that the test was the same day. Not claimed: anything about the 20 papers without readable context.
**VO line (C01X):** see PROGRESS.md / final take. Card shows 36 (count-up), with OPENALEX 23 · S2 27 · and 16 READ → 9 "IT WORKS" → 1 FLAGS SAME-DAY TEST.

## Table
| date | title | id | in | class | quote (citing sentence) |
|---|---|---|---|---|---|
| 2026-10-01 | Augmentation or Erosion? Regulating Cognitive Offloading in Generative AI-Supported STEM L | 10.1007/s10648-026-10224-6 | S2+OA | **CRITICAL / LIMITS** | The tutor of Kestin et al. ( 2025 ) did produce gains, though on post-lesson tests rather than at a delay; that both conditions held there, with constitutive processing preserved and freed capacity reallocated to it, is the framework’s interpretation of the result, not a mechanism the study tested. / …randomized trial in undergraduate physics, an AI tutor deliberately engineered around the same pedagogical principles (flags post-lesson (not delayed) tests) |
| 2026-10-01 | The institutional stack: Realigning U.S. AI governance | 10.1016/j.telpol.2026.103294 | S2 | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-01 | AI feedback effects on argumentative writing: The role of secondary students’ feedback rec | 10.1016/j.lindif.2026.102979 | S2 | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-01 | Knowledge, attitudes, perceptions, and utilization of artificial intelligence in higher ed | 10.1007/s44217-026-02213-2 | S2+OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-01 | On-Premises Multi-Course RAG Tutoring for Business Education: Hardware-Software Trade-offs | 7a06680c2a9e4e9f4714fd3d2dd4668b486c03fc | S2 | **SUPPORTING, notes immediate** | Kestin et al. report a complementary result from a randomized crossover study in undergraduate physics: a deliberately designed AI tutor produced higher immediate learning gains than the comparison active-learning class sessions [7]. ("higher immediate learning gains") |
| 2026-10-01 | Designing and Evaluating a Socratic-Scaffolded Conversational AI Assistant for Educational | 10.1080/10447318.2026.2717500 | S2+OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-01 | A Tutor(bot) for Every Student: Tutorial on Building and Deploying Customized Large Langua | 10.2196/preprints.113470 | OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-07 | Prompt-as-Lesson: Authoring AI-Delivered Lessons for Fidelity and Observability | 10.34190/ecel.25.1.5451 | S2 | **SUPPORTING, no caveat** | Prompts embedded in custom agents have been shown to be valuable in the field of physics education (Kestin et al., 2025).  |
| 2026-10-07 | From Cognitive Overload to Individualized Learning: AI Tutoring in Electrical Engineering | 10.34190/ecel.25.1.5273 | S2 | **SUPPORTING, no caveat** | Their implementation has shown potential for performance improvements, particularly within STEM disciplines (Kestin et al. , 2025) and they are most effective when used to supplement human teachers rather than replace them outright (Batsaikhan and Correia, 2024).  |
| 2026-10-07 | Who Am I in the Age of AI? Exploring the Epistemic and Ethical Implications of Automation  | 10.1093/9780198945215.003.0243 | OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-08 | Socioeconomic status and rural–urban inequalities in AI access and academic performance fo | 10.1177/17577438261496828 | S2+OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-08 | AI Tutors and Human Tutors in Online Universities: A Critical Narrative Review of Replacem | 10.5539/ijbm.v21n6p31 | S2 | **SUPPORTING, notes post-test** | In a carefully designed undergraduate physics trial, Kestin et al. (2025) reported substantial post-test advantages for a custom AI tutor relative to an active-learning condition. ("post-test advantages") |
| 2026-10-08 | Evaluating Retrieval-Augmented LLM Tutoring with Synthetic Learners: A Factorial Simulatio | 10.3390/app16199938 | S2+OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-08 | Envidia: imitar, suplantar y aparentar | 10.62486/978-9915-9928-6-0.ch04 | OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-08 | Pereza: delegar aquello que deberíamos aprender, pensar o decidir | 10.62486/978-9915-9928-6-0.ch07 | OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-08 | Lujuria: la fascinación desbordada por lo artificial | 10.62486/978-9915-9928-6-0.ch03 | OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-08 | Como pode um chatbot de IA otimizar a aprendizagem e estimular o pensamento crítico na int | 10.21814/diacritica.6752 | OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-13 | Supplemental generative AI tutoring improves financial modeling scores in a two class quas | 10.1007/s10791-026-10706-9 | S2+OA | **SUPPORTING, no caveat** | Existing studies have shown that generative AI tutors have the characteristics of personalization, interactivity, and real-time feedback [6, 7], which can effectively make up for the lack of personalized guidance in traditional teaching [8, 9] and improve students’ learning outcomes [10, 11]. / The present study differs from prior RCTs such as [11] in its quasi-experimental design and lack of time-matched control, wh (background evidence + design contrast) |
| 2026-10-13 | From a Student's Question to the Half-Derivative: A Constructivist Teaching Model - Part I | 626a64db0a9da0b3b6c4e6853042faf90f043416 | S2 | **SUPPORTING, no caveat** | In the randomized crossover experiment of Kestin and co-authors [21] (an introductory physics course at Harvard University, autumn 2023, 194 students), students learned more in a lesson taught by an AI tutor with a research-based design than in active in-class instruction. ("students learned more") |
| 2026-10-14 | Autentisk ledelse utvikles mellom mennesker: Sosiokulturell læring og GenKI som supplerend | 10.23865/magma.v29.1605 | S2 | **NEUTRAL / passing** | Som kul tu relt red skap kan GenKI støt te be greps for stå el se, syn lig gjø re al ter na ti ve per spek ti ver og sti mu le re til re flek sjon over egne for tolk nin ger og me nings­ dan nel ser (Cong­Lem & Daneshfar, 2024; Hyde et al., 2024; Kestin et al., 2025; Yin et al., 2025). (list citation) |
| 2026-10-15 | Calidad Pedagógica de Materiales Educativos Generados por Inteligencia Artificial en Educa | 10.61384/r.c.a..v6i4.2133 | S2+OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-16 | Designing an AI Agent That Does Not Tutor: Design Rules for Socratic Probing in Introducto | 20255980faaf11ee618148144d84175a5d4bb934 | S2 | **SUPPORTING, no caveat** | The obvious response is to put an AI tutor in front of students, and most current work does so [11–14]. / The best of them work: a randomized trial found an LLM tutor built on research-based pedagogy outperforming in-class active learning [11], and a Socratic chatbot has been deployed in a large introductory mechanics course [12]. ("The best of them work") |
| 2026-10-19 | Exploring Visual Access and Proactive AI Tutoring for Handwritten Mathematics | 41b7c5df1696ce531e8d0da56cd2864be0402164 | S2 | **SUPPORTING, no caveat** | AI tutoring outperformed in-class active learning in a physics course [43]. ("AI tutoring outperformed") |
| 2026-10-19 | Generative AI in University Mathematics Education Using the ‎Theory–Context–Methodology Fr | 10.62159/isej.v7i3.2140 | S2 | **SUPPORTING, notes short-term** | Chan and Hu (2023) documented generally positive university-student perceptions, whereas Kestin et al. (2025) measured greater short-term learning gains with a deliberately structured AI tutor than with an active-learning condition in undergraduate physics. ("greater short-term learning gains") |
| 2026-10-19 | Human Factors in AI-Assisted Interpreter Training: A Design Science Approach to Human-Cent | 10.3390/computers15100732 | OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-19 | The Access Fallacy: Why Naive Comparisons Overstate the Value of Course Chatbots | 10.1007/978-981-92-6910-5_35 | OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-20 | Generative Artificial Intelligence and Distributive Epistemic Justice | 10.1007/s13347-026-01225-y | S2+OA | **SUPPORTING, no caveat** | Well-designed AI tutoring can also match or exceed in-person active learning (Kestin et al., 2025 ; see also Ma et al., 2014 ). / Schools already short of qualified teachers may also lean on lower-tier AI as a cheap replacement for staffing, which inverts the conditions under which AI tutoring has been shown to produce learning gains (Kestin et al., 2025; Létourneau et al., 2025 ). ("can match or exceed") |
| 2026-10-21 | A diagnostic human agency framework for AI driven education from a PRISMA guided systemati | 10.1007/s44217-026-02173-7 | S2 | **UNCLEAR** | Recent empirical studies show that overreliance on generative AI can induce “metacognitive laziness,” where students bypass the deep cognitive work required for genuine skill acquisition [17, 26, 27]. (context is a multi-ref sentence on "metacognitive laziness"; cannot tell which ref is Kestin) |
| 2026-10-21 | Moving Minds, Moving Bodies: Rethinking AI Literacy and Health Literacy Through Embodied E | 10.1111/ejed.70904 | S2+OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-21 | AI-supported virtual laboratory for flipped physics learning: effects on middle school stu | 10.3389/fpsyg.2026.1939220 | S2+OA | **SUPPORTING, no caveat** | They found that students using the AI tutor achieved higher learning gains in less time and reported higher engagement and motivation than students in the active learning condition. (context from Frontiers full text) |
| 2026-10-22 | Impacts of generative AI skill development on academic adaptation and learning outcomes am | 33823a3fc5746c8ea5234229a8e5844d327d5d6d | S2 | **SUPPORTING, no caveat** | Kestin et al. found substantial learning benefits from a purpose-built GenAI tutor in undergraduate physics (Kestin et al., 2025). / Intervention studies similarly suggest that outcomes depend on how GenAI support is designed and used (Bastani et al., 2025; Kestin et al., 2025). ("substantial learning benefits") |
| 2026-10-23 | Adaptive Generative Tutoring in Resource-Limited Secondary Education: Effects on Participa | 10.3390/educsci16111780 | S2+OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-25 | Responsible GenAI Augmentation and Cognitive Agency in Higher Education | 10.3390/su182110831 | S2+OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-26 | Rethinking Formative Feedback in HyFlex and Applied Contexts: A Distributed, Time-Decouple | 10.57186/jalhe_2026_v12a12 | S2+OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |
| 2026-10-26 | Generative AI and AI literacy in Elementary Education: A Systematic Review of Research pub | 10.12973/eu-jer.16.1.91 | S2+OA | **NEUTRAL / passing** | Research on the use of Generative AI in education has shown mixed but cautiously positive results, while calling for further research directed towards elementary education ( Deng et al., 2025; Dimeli & Kostas, 2025; Kestin et al., 2025). (context from full text) |
| 2026-10-26 | The Credential Mirage in AI-Era Higher Education: A Counterfactual Competence Audit for Tr | 10.68050/jams.2026.869 | OA | **NO READABLE CONTEXT** | — (abstract does not mention Kestin; full text not accessible here) |

## Raw files (sha256)
- oa_oct_created_20261030T1311Z.json `e034c72badc923d7d0c57a9db887c8d01e2dec99bb2e5efb3fe734e291195c64`
- oa_oct_pub_20261030T1311Z.json `0d1404b6f8571f88cef4768f988f28fb51b901fc91f2fa344aebd151eb99f465`
- oa_work_20261030T1311Z.json `b6cafd38277a1aa9ade4fae43d96e9bbe291b14670d639c3c53b3e84dac9e7e1`
- s2_cites_20261030T1311Z.json `e6baa374d1b72632e7e15a1f51fdb90603053fc5d4baec9753164565737e8d6d`
- s2_paper_20261030T1311Z.json `b05e48e413effd9ae1b31c7a30ce48dada1f2ae07a1ee4f7878c1d1017f4d661`
- merged_oct.json, dump_oct.txt, fulltext/ (fetch attempts; MDPI/Springer pages blocked, 228–1378 B)

## Update after the citation re-check (09:00 CT)
Final VO line C01X (take C01Xg): "At least thirty-six papers cited it this month. Of the sixteen I could read, nine just say it works. Only one questions the same-day test."
Final card: AT LEAST 36 (OA 23 · S2 27, published Oct 1–30) → OF THE 16 I COULD READ: 9 JUST SAY "IT WORKS" · 3 NOTE THE TIMING, BUT NOT AS A LIMIT · 1 QUESTIONS THE SAME-DAY TEST · +3 OTHER (2 passing, 1 unclear) · other 20 of 36 not classified. (Supersedes the "Card shows … 1 FLAGS SAME-DAY TEST" note above.)
"At least": 36 is the union of two indexes, which lag new publications, so it is a floor.
