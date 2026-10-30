# ACCURACY AUDIT (example episode; written before any fix was made)
Example audit (from the episode build). Scope: every VO line + its on-screen claim that touches Kestin 2025, Roediger & Karpicke 2006, Malenka & Bear 2004, Contractor & Reyes 2026.

## Sources read this turn (local copies were kept by the build and are not shipped)
| key | source | local copy (not shipped) |
|---|---|---|
| K | Kestin, Miller, Klales, Milbourne & Ponti, "AI tutoring outperforms in-class active learning…", *Sci Rep* 15:17458, published 03 June 2025, doi 10.1038/s41598-025-97652-6 (peer-reviewed) | kestin_nature_20261030T1303Z.html/.txt |
| KS | Kestin 2025 Supplementary Information (prompts, model, group sizes) | kestin_supp_*.docx/.txt |
| R | Roediger & Karpicke 2006, "Test-Enhanced Learning", *Psychol Sci* 17(3):249–255 | roediger_20261030T1304Z.pdf/.txt |
| M | Malenka & Bear 2004, "LTP and LTD: an embarrassment of riches", *Neuron* 44:5–21 | malenka_hu-berlin_*.pdf/.txt |
| C | Contractor & Reyes, "Experimental Evidence on the Learning Impact of Generative AI", arXiv 2607.08849 v2 (4 Oct 2026), econ.GN — **PREPRINT, not peer-reviewed** | contractor_20261030T1303Z.pdf/.txt, contractor_abs_* |
| G | Harvard Gazette, Oct 2025, "What if AI could help students learn…" | gazette_20261030T1309Z.html/.txt |
| E | ETCJ, 2026-10-17, "The Harvard AI tutor study eleven months later" (secondary; context only) | evidence/ |

## Key facts verified (exact quotes)
- Sample: "Of the 233 enrolled students, 194 were eligible…" (K, Methods); course "Harvard's largest physics class (N = 233)". Groups 96 / 98 (KS).
- Design: "followed a crossover design … each experiencing two lessons … in consecutive weeks … group 1 engaged with an AI-supported lesson at home … conditions were reversed" (K, Methods).
- Control: "All in-class lessons employed research-based best practices for in-class active learning" (K); "Active learning pedagogies … have demonstrated significant improvements over passive lectures" (K, Intro).
- Scores: "higher median (M) post-score (M = 4.5, N = 142) compared to those in the in-class active learning group (M = 3.5, N = 174). The median learning gains for students, relative to the pre-test baseline (M = 2.75, N = 316), in the AI-tutored group were over double those for students in the in-class active learning group." (K, Results). So the "2x" is **gains** (1.75 vs 0.75), not scores (4.5 vs 3.5 = 1.29x).
- Time: "we assume 60 minutes spent on learning" (in class); AI median 49 min; ~70% under 60, ~30% over (K, Results).
- Test timing: "Following each lesson, students completed post-tests" / "3) took a post-class quiz as a test of learning" (K, Methods). No delayed test is reported anywhere in K or KS.
- Tutor: GPT-4-0613 (KS). Prompt: "DO NOT give away the full solution…", "Keep responses BRIEF" (KS); "we enriched our prompts with comprehensive, step-by-step answers, guiding the AI tutor to deliver accurate and high-quality explanations" (K); "personalized feedback on demand" (K).
- Authors' limits: "we do not presume that structured AI tutoring will always outperform…"; future work "systematic integration of well-established retention enhancing strategies (e.g., spacing)" (K, Discussion).
- Follow-up: "Kestin added that follow-up research is in progress focused on understanding the long-term impacts of tutor bots, including retention." (G). No results published as of 2026-10-17 (E).
- R: "on the 5-min retention tests, restudying produced better recall than testing (81% vs. 75%)… after 1 week: The tested group recalled 56% of the material, whereas the restudy group recalled only 42%" (R, Exp. 1).
- M: "'early' phase of LTP—that component of LTP lasting 60 or so minutes"; "'late phases' … of LTP require new protein synthesis and gene transcription"; induction "requires synaptic activation of NMDARs during postsynaptic depolarization" (M).
- C (preprint): "complete unaided assessments immediately and one week later. AI access raises test scores, and a smaller gain persists a week later. Gains remain for students who use AI as a tutor ('augmentation') and fade for students who have AI write for them ('automation')." Tool: ChatGPT (GPT-4o), essay task, 211 Middlebury undergrads. Use types are self-chosen and classified from logs: "While descriptive, these results suggest…". Augmentation week-later test diff +0.24 SD (p = 0.095); automation essay advantage falls 1.64 SD, test diff −0.24 SD (p = 0.538).

## Line-by-line verdicts
| line | draft claim | verdict | why (source) | fix |
|---|---|---|---|---|
| C01 | "…against one of its best-taught classes, and the students using it learned more than twice as much. In less time." | **IMPRECISE** | "2x" is median *gains* over pre-test, not learning or scores (K). "best-taught classes" is our gloss; K says active learning with research-based best practices. "less time": median 49 vs an *assumed* 60; ~30% spent longer (K). | "Harvard pitted an AI tutor against a strong active-learning class. On the test, its students gained more than twice as much. In less time." Chip BEST-TAUGHT CLASS → ACTIVE-LEARNING CLASS; kinetic LEARNED→GAINED. |
| C01X | "…at least ten new papers have cited it [past two weeks]" | superseded | Replaced by the (B) citation line with Oct 1–30 data. | see CITATIONS.md |
| C02 | "If that's real, it's huge." | opinion | — | none |
| W00 | Kestin & colleagues, Harvard, Sci Rep, June 2025 | **CORRECT** | "Published: 03 June 2025", Sci Rep 15:17458 (K) | none |
| W01 | faced active learning, "which reliably beats lectures" | **CORRECT** | K Intro + the meta-analysis it cites | none |
| W02 | 194 students, one lesson each way, "so everyone's compared with themselves" | **IMPRECISE** | Crossover is correct (K), but headline medians compare two groups (N = 142 vs 174), not within-student differences; the regression clusters by student. | "…so every student tried both." Card COMPARED WITH THEMSELVES → EVERY STUDENT TRIED BOTH. |
| W04 | typical student 2.75 → class 3.5 → tutor 4.5 | **CORRECT** (medians) | K Results. They are medians of different sets (pre N = 316, post 174/142), so "typical" = median. | none |
| W05 | "More than double the gain, in a median of forty-nine minutes instead of sixty." | **CORRECT** | gains 1.75 vs 0.75; 49 min median vs 60 assumed (K). The "assumed" nuance is not said aloud; it's not wrong as worded. | none |
| W06/T01 | opinion / framing | opinion | — | none |
| T02 | "It's complete bullshit." | **EDITORIAL OVERSTATEMENT (flagged)** | K is peer-reviewed and the immediate result is real; the problem is what it can and can't claim. Kept because the bleep must stay exactly as is. V01 states the fair version on screen and in the VO. | none (flag only) |
| Q01 | "When did they test?" | opinion/question | — | none |
| Q02 | "Right after the lesson. And then they never checked again." | **IMPRECISE** | Post-test right after each lesson is correct (K). "Never checked again" is true *of the paper*, but Harvard says retention follow-up is in progress (G). | "Right after the lesson. And the paper never tests them again." Visual THEN: NEVER AGAIN. stays (it's about the paper). |
| F01 | neurons that fire together strengthen their connection | **CORRECT** (simplified) | LTP needs NMDAR activation during postsynaptic depolarization, i.e. coincident activity (M). | none |
| F02 | first boost fades in ~an hour unless new proteins lock it in | **CORRECT** | early LTP "lasting 60 or so minutes"; late LTP "require[s] new protein synthesis" (M) | none |
| F03 | a test right after catches quick boost + lasting change, can't tell apart | **CORRECT as reasoning** (our inference, not a claim from K) | Grounded in M + R; it's an analogy from synapse to test score. Worded as reasoning, not as a finding. | none |
| F05 | 5 min: rereaders 81 vs testers 75; 1 week: 56 vs 42 for testers | **CORRECT** | R Exp. 1 exact numbers | none |
| F06 | "Test too early, and you can crown the wrong winner." | **CORRECT** (as "can") | R | none |
| F07 | tutor "loaded with step-by-step answers and feedback on demand. Help like that can lift today's score more than it builds what lasts." | **IMPRECISE / misleading** | Step-by-step answers were in the *prompt* as reference, and the tutor was told "DO NOT give away the full solution" (KS). Implies the tutor handed out answers. The 2nd sentence is speculation not tested by K. The on-screen chat showed Step 1-2-3 walkthrough to "solve". | "The tutor itself was well built: told not to hand over full solutions, with feedback on demand. But a same-day score can't show what lasts." Chat → hints + feedback; chart tagged ILLUSTRATION. |
| F09 | preprint "did check a week later, and found that split. Students who used ChatGPT as a tutor stayed ahead. The ones who let it write for them lost their edge." | **IMPRECISE** | Preprint (flagged on card ✓). Use-types self-chosen; authors call it descriptive. Augmentation +0.24 SD p = 0.095; automation test diff imprecise (C). "that split" implied it tested our F07 claim. | "A newer preprint did test a week later, and found a split. Students who chose to use ChatGPT as a tutor stayed ahead. The ones who had it write for them lost their edge." + on-screen SELF-CHOSEN · DESCRIPTIVE tag. |
| V01 | "A well-built AI tutor beat a strong class, on a test right after the lesson." | **CORRECT** | K | none |
| V02 | "…learning is what's still there next week, and nobody looked." | **IMPRECISE** | Harvard says a retention follow-up is in progress (G); nothing published (E). | "…and this study didn't look." Card AND NOBODY LOOKED. → THIS STUDY DIDN'T LOOK. |
| V03 | "Whether it stuck, nobody knows." | **CORRECT (as of 2026-10-30)** | No published retention data for this tutor (K, G, E). Keep. | none |

## Does any WRONG verdict change the argument?
No line is WRONG. The core argument ("an immediate post-test can't separate short-term boost from lasting learning, so the 2x shows same-day performance, not retention") holds on the sources. The fixes make the video fairer to Kestin: it did show a real, large immediate gain against a strong control. **No STOP. Build proceeds.**

