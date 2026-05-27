# Conference Poster Generation Prompt

> **How to use this file**  
> Copy the prompt block below in full and paste it into your preferred AI image generator
> (e.g., Adobe Firefly, Midjourney, DALL-E 3, Canva AI, or an AI design assistant like Gamma or Tome).  
> For best results, also provide this file as a reference document so the tool can read the exact data.

---

## ✦ FULL POSTER PROMPT

---
```
Design a professional, visually stunning academic conference poster (A0 portrait format,

841mm × 1189mm, 300 DPI) for a computer science / AI research paper.



═══════════════════════════════════════════

PAPER TITLE & AUTHORS

═══════════════════════════════════════════



Title:

  "Modular LLM Scorer: A Reproducible, Statistically Rigorous Benchmark

   Framework for Large Language Model Evaluation"



Authors:

  [Ratnajeet Patil] · [Pune,India]





═══════════════════════════════════════════

VISUAL DESIGN REQUIREMENTS

═══════════════════════════════════════════



COLOR PALETTE (use exactly):

  • Primary background:   #0D1117  (near-black, deep charcoal)

  • Section backgrounds:  #161B22  (dark card panels)

  • Accent 1 – Electric blue:   #58A6FF  (headings, borders, highlights)

  • Accent 2 – Emerald green:   #3FB950  (correct / success indicators)

  • Accent 3 – Amber orange:    #F0883E  (warnings, emphasis)

  • Accent 4 – Purple glow:     #BC8CFF  (statistical labels)

  • Body text:            #E6EDF3  (light, high contrast on dark)

  • Muted text:           #8B949E  (captions, labels)

  • Dividers:             #30363D



TYPOGRAPHY:

  • Title font:     "Inter" Extra-Bold, 72–80pt, white

  • Section heads:  "Inter" Semi-Bold, 36pt, Electric Blue (#58A6FF)

  • Body text:      "Inter" Regular, 22–24pt, #E6EDF3

  • Code / labels:  "JetBrains Mono" Regular, 18–20pt, Amber (#F0883E)

  • All caps small: for table column headers and domain labels



STYLE:

  • Dark-mode glassmorphism aesthetic

  • Rounded rectangle panels (border-radius ~12px) with subtle inner glow

  • 1px Electric Blue (#58A6FF) border on each panel

  • Subtle gradient overlay on header: left #58A6FF → right #BC8CFF at 15% opacity

  • Pipeline arrows rendered as clean rounded-corner SVG-style connectors

  • Icons: minimal, outline-style (Feather Icons or Material Symbols)

  • No clipart; no stock photos; data-driven visual elements only



═══════════════════════════════════════════

POSTER LAYOUT  (7 rows, left-to-right flow)

═══════════════════════════════════════════



┌─────────────────────────────────────────────────────────────────┐

│  ROW 1 — HEADER BANNER  (full width, 10% height)                │

│  • Logo/icon left: abstract neural network node cluster         │

│  • Title centered (2 lines)                                     │

│  • Author / institution / conference right                      │

│  • Gradient accent bar (blue→purple) along very bottom edge     │

└─────────────────────────────────────────────────────────────────┘

┌───────────────────────┬─────────────────────────────────────────┐

│  ROW 2 LEFT           │  ROW 2 RIGHT                            │

│  ABSTRACT / MOTIVATION│  KEY CONTRIBUTIONS                      │

│  (40% width, 12%)     │  (60% width, 12%)                       │

└───────────────────────┴─────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐

│  ROW 3 — SYSTEM PIPELINE  (full width, 18%)                     │

│  Horizontal flowchart with 8 labeled boxes + arrows             │

└─────────────────────────────────────────────────────────────────┘

┌───────────────────────┬─────────────────────────────────────────┐

│  ROW 4 LEFT           │  ROW 4 RIGHT                            │

│  DOMAINS & DATASETS   │  SCORING & STATISTICAL METHODS          │

│  (45% width, 14%)     │  (55% width, 14%)                       │

└───────────────────────┴─────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐

│  ROW 5 — EXPERIMENTAL RESULTS TABLE + BAR CHART (full width,18%)│

└─────────────────────────────────────────────────────────────────┘

┌───────────────────────┬─────────────────────────────────────────┐

│  ROW 6 LEFT           │  ROW 6 RIGHT                            │

│  CODE SANDBOX DIAGRAM │  REPRODUCIBILITY FEATURES               │

│  (45% width, 14%)     │  (55% width, 14%)                       │

└───────────────────────┴─────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐

│  ROW 7 — FOOTER: Conclusion · GitHub QR · References · Contact  │

│  (full width, 8%)                                               │

└─────────────────────────────────────────────────────────────────┘



═══════════════════════════════════════════

SECTION CONTENT  (render exactly as below)

═══════════════════════════════════════════



──────────────────────────────────────────

ROW 1 · HEADER

──────────────────────────────────────────

TITLE (line 1): Modular LLM Scorer

TITLE (line 2): A Reproducible, Statistically Rigorous Benchmark Framework

                for Large Language Model Evaluation



SUBTITLE TAG (small pill badge, Electric Blue border):

  ✦ NLP · Benchmarking · Statistical Evaluation · Open Source



──────────────────────────────────────────

ROW 2 LEFT · ABSTRACT / MOTIVATION

──────────────────────────────────────────

Section icon: 🔬 (outline style)

Section heading: "Motivation"



Body text (render verbatim, 3 short paragraphs):



  Existing LLM benchmarks lack statistical rigor, suffer from

  non-reproducible sampling, and use opaque LLM-as-judge grading —

  making fair cross-model comparison impossible.



  We present Modular LLM Scorer: a modular, deterministic benchmarking

  pipeline that evaluates LLMs across four cognitive domains using

  rule-based graders, 95% confidence intervals, and sandboxed code

  execution — with full prompt and token logging for reproducibility.



  All evaluation is deterministic. No LLM judge is used.



──────────────────────────────────────────

ROW 2 RIGHT · KEY CONTRIBUTIONS

──────────────────────────────────────────

Section icon: ⭐ (outline style)

Section heading: "Key Contributions"



Render as 4 numbered highlight cards (rounded, Electric Blue left border):



  1  Statistical Rigor

     95% Wilson Score Confidence Intervals per domain, difficulty

     tier, and dataset · McNemar's test for model comparison



  2  Full Reproducibility

     Git commit hash tracking · exact prompt logging · per-sample

     input/output token counts · deterministic seeded sampling



  3  Multi-Layer Code Safety

     Pattern validation → subprocess isolation → 10 s timeout

     Sandboxed execution enabled by default



  4  Multi-Provider Framework

     8 model providers: OpenAI · Gemini · Groq · Together ·

     OpenRouter · Hugging Face · Ollama · Echo



──────────────────────────────────────────

ROW 3 · SYSTEM PIPELINE  (horizontal flowchart)

──────────────────────────────────────────

Section heading: "System Architecture"



Draw 8 rounded rectangle boxes connected left-to-right with arrows.

Use alternating accent colors for box borders.

Label each box with its name LARGE and a small subtitle below.



Box 1  (Blue border)

  Name:     Dataset Root

  Subtitle: data/raw_datasets

  Icon:     🗄



Box 2  (Blue border)

  Name:     Validator + Normalizer

  Subtitle: HF · JSON · CSV · JSONL · SQuAD

  Icon:     ✔



Box 3  (Green border)

  Name:     Stratified Sampler

  Subtitle: Top-2 datasets/domain · seeded

  Icon:     ⚖



Box 4  (Green border)

  Name:     Prompt Builder

  Subtitle: Domain-specific + refusal block

  Icon:     📝



Box 5  (Amber border)

  Name:     Model Adapter

  Subtitle: 8 providers · cache · retry

  Icon:     🤖



Box 6  (Amber border)

  Name:     Rule Evaluator

  Subtitle: Math · Logic · Knowledge · Code

  Icon:     📏



Box 6b (Purple border, branching DOWN from box 6, labeled "Code domain")

  Name:     Code Sandbox

  Subtitle: Pattern → Subprocess → Timeout

  Icon:     🔒



Box 7  (Purple border)

  Name:     Scorer

  Subtitle: Accuracy · CIs · Error breakdown

  Icon:     📊



Box 8  (Blue border)

  Name:     Report Generator

  Subtitle: JSON · JSONL · Markdown

  Icon:     📄



Arrows between boxes: Electric Blue (#58A6FF), rounded, with small

arrowheads. The code sandbox box branches down from Evaluator with a

dashed Purple arrow labeled "Code".



──────────────────────────────────────────

ROW 4 LEFT · DOMAINS & DATASETS

──────────────────────────────────────────

Section heading: "Benchmark Domains"



Render as a 2-column table inside a dark card:



Domain     | Weight | Datasets

───────────┼────────┼────────────────────────────────────────

Math       | 25 %   | GSM8K (main + socratic), SVAMP,

           |        | Hendrycks MATH (8 variants)

Logic      | 25 %   | ProofWriter, ReClor

Knowledge  | 35 %   | SQuAD, Natural Questions, TriviaQA

Code       | 15 %   | HumanEval, MBPP (full + sanitized)



Below the table, render 4 colored pill badges (one per domain):

  [MATH 25%]  in Electric Blue

  [LOGIC 25%] in Purple

  [KNOWLEDGE 35%] in Emerald

  [CODE 15%]  in Amber



Then add the sampling strategy in small text:

  "Mode sizes: quick = 500 · half = 1 500 · full = 6 000 samples

   Difficulty split: 30% easy · 50% medium · 20% hard

   Selection: top-2 datasets per domain by sample count"



──────────────────────────────────────────

ROW 4 RIGHT · SCORING & STATISTICAL METHODS

──────────────────────────────────────────

Section heading: "Statistical Methods"



Sub-section 1 — Wilson Score CI (render the formula in a dark box):



  Formula display (centered, large):

  CI₉₅ = ( p̂ + z²/2n ± z√(p̂(1−p̂)/n + z²/4n²) ) / (1 + z²/n)



  Where:  p̂ = accuracy  ·  n = sample count  ·  z = 1.96



  Caption: "Applied per domain, difficulty tier, and dataset.

            Handles 0 % and 100 % accuracy correctly."



Sub-section 2 — McNemar's Test:



  Formula display:

  χ² = (|b − c| − 1)² / (b + c)



  Where:  b = M1 correct, M2 wrong  ·  c = M2 correct, M1 wrong

          α = 0.05



  Caption: "Requires ≥ 25 disagreements. Paired-sample test

            for statistically significant model comparison."



Sub-section 3 — Final Score Formula:



  score = Σ  domain_accuracy[d] × domain_weight[d]

             d ∈ {math, logic, knowledge, code}



──────────────────────────────────────────

ROW 5 · EXPERIMENTAL RESULTS

──────────────────────────────────────────

Section heading: "Example Results: 4-Model Comparison (mode = half, seed = 42)"



LEFT HALF — Results Table (dark card, rounded, striped rows):



Model                | Overall  | Math   | Logic  | Knowledge | Code   | CI 95%

─────────────────────┼──────────┼────────┼────────┼───────────┼────────┼──────────────

llama3.1:8b          | 0.423    | 0.381  | 0.510  | 0.442     | 0.271  | [0.39–0.45]

mistral:7b-instruct  | 0.448    | 0.412  | 0.547  | 0.461     | 0.263  | [0.42–0.48]

qwen2:7b-instruct    | 0.456    | 0.374  | 0.501  | 0.512     | 0.258  | [0.43–0.48]

deepseek-coder:6.7b  | 0.371    | 0.294  | 0.418  | 0.327     | 0.489  | [0.34–0.40]



Table style: header row in Electric Blue; alternating row colors

#161B22 / #1C2128; best value per column highlighted in Emerald Green.



RIGHT HALF — Grouped Horizontal Bar Chart:



Title: "Per-Domain Accuracy by Model"

4 groups (one per domain), 4 bars per group.

X-axis: 0.0 → 0.6 accuracy

Color per model (consistent legend):

  llama3.1:8b         → Electric Blue  #58A6FF

  mistral:7b-instruct → Emerald Green  #3FB950

  qwen2:7b-instruct   → Purple         #BC8CFF

  deepseek-coder:6.7b → Amber Orange   #F0883E



Add small error bars representing the 95% CI width.

Add thin vertical dashed reference line at x = 0.50 labeled "50%".

Legend in bottom-right corner of chart panel.



Below chart, add a note box (Amber left-border):

  ★ McNemar's test: mistral vs llama — χ² = 3.56, p = 0.059 (not significant)

  ★ qwen2 leads knowledge domain by +7.0 pp over llama baseline

  ★ deepseek-coder leads code domain by +21.8 pp over closest generalist



──────────────────────────────────────────

ROW 6 LEFT · CODE SANDBOX DIAGRAM

──────────────────────────────────────────

Section heading: "Multi-Layer Code Safety"



Render as a vertical 3-layer diagram (stacked dark cards with arrows):



┌─────────────────────────────────────┐

│  LAYER 1 — Pattern Validation       │  ← Purple card

│  Blocks: exec · eval · open() ·     │

│  os.system · subprocess import ·    │

│  shell commands                     │

└───────────────────┬─────────────────┘

                    ▼  (passes)

┌─────────────────────────────────────┐

│  LAYER 2 — Subprocess Isolation     │  ← Amber card

│  Candidate code runs in a separate  │

│  Python subprocess — cannot touch   │

│  parent process memory              │

└───────────────────┬─────────────────┘

                    ▼  (passes)

┌─────────────────────────────────────┐

│  LAYER 3 — Timeout Guard            │  ← Green card

│  5-second limit per test run        │

│  → returns "code-timeout" on breach │

└─────────────────────────────────────┘



Below diagram, add 2-column error type list (small):

  empty-code        syntax-error

  test-failed       code-timeout

  output-mismatch   execution-error

  format-error      other



──────────────────────────────────────────

ROW 6 RIGHT · REPRODUCIBILITY FEATURES

──────────────────────────────────────────

Section heading: "Reproducibility Checklist"



Render as a checklist (large checkmarks in Emerald, dark card):



  ✅  Git commit hash stored in every result JSON

      (appends * if working tree is dirty)



  ✅  Full prompt text logged per sample (JSONL)

      → enables exact re-evaluation at any future date



  ✅  Per-sample token tracking

      input_tokens · output_tokens · total by domain



  ✅  Deterministic seeded sampling

      --seed 42  or  --seeds 42,43,44 for multi-run averaging



  ✅  Locked requirements.txt

      Pinned dependency versions for environment reproducibility



  ✅  43 / 43 evaluator validation tests passing (100 %)

      python validate_pipeline.py



  ✅  --dry-run flag

      Preview exact sample counts without API calls



──────────────────────────────────────────

ROW 7 · FOOTER

──────────────────────────────────────────

LEFT (30%) — Conclusion box (Emerald left border):

  "Modular LLM Scorer provides the statistical

   infrastructure needed for credible, reproducible

   LLM evaluation: Wilson score CIs, McNemar's tests,

   sandboxed execution, and full audit trails —

   in a single pip-installable framework."



CENTER (40%) — Key statistics strip (4 large number cards):



  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐

  │    4     │  │    8     │  │   43/43  │  │   95%    │

  │ Domains  │  │ Provider │  │  Tests   │  │   CIs    │

  │  Math    │  │ Adapters │  │ Passing  │  │  Wilson  │

  │ Logic    │  │          │  │          │  │  Score   │

  │ Know.    │  │          │  │          │  │          │

  │ Code     │  │          │  │          │  │          │

  └──────────┘  └──────────┘  └──────────┘  └──────────┘



  Each number in Electric Blue 80pt bold; label beneath in muted text.



RIGHT (30%) — GitHub + References:



  [QR CODE placeholder — square, Electric Blue on dark]

  Caption: "github.com/ratnajeet00/Modular-LLM-Scorer"



  References (tiny, 16pt):

  [1] Cobbe et al. 2021 — GSM8K

  [2] Chen et al. 2021 — HumanEval

  [3] Austin et al. 2021 — MBPP

  [4] Rajpurkar et al. 2016 — SQuAD

  [5] Hendrycks et al. 2020 — MATH

  [6] Liang et al. 2022 — HELM



  Contact: [your.email@institution.edu]



═══════════════════════════════════════════

GLOBAL VISUAL POLISH INSTRUCTIONS

═══════════════════════════════════════════



1. SPACING: 24px inner padding inside each panel; 16px gap between panels.



2. GLOW EFFECTS:

   • Section headings cast a faint Electric Blue text-shadow (blur 8px).

   • Key metric numbers (43/43, 95%, 8) cast a faint colored glow.

   • Pipeline box borders have a very subtle outer glow (4px blur, 20% opacity).



3. BACKGROUND TEXTURE:

   • Very faint dot-grid pattern (#30363D dots, 5% opacity) on the main background

     to add depth without distracting from content.



4. ARROWS IN PIPELINE:

   • 2px stroke, Electric Blue, rounded line-caps.

   • Arrowhead filled Electric Blue.

   • Label "Code" on the dashed branch to sandbox box.



5. TABLES:

   • Header row background: Electric Blue at 20% opacity.

   • Alternating rows: #161B22 and #1C2128.

   • Best value per column: Emerald text + faint Emerald left border on that cell.

   • No outer table border — panels provide containment.



6. BAR CHART:

   • Bars are rounded at right end (border-radius on right caps).

   • Error bars: thin 1px lines, same color as bar, with small horizontal serifs.

   • Grid lines: muted (#30363D), very thin, every 0.1 interval.



7. CHECKLIST:

   • ✅ emoji rendered large (26pt); aligned with body text start.

   • Sub-text in muted color (#8B949E), 2pt smaller than body.



8. CONSISTENCY:

   • Every section panel uses the SAME dark card style (#161B22 bg, #58A6FF border).

   • All icons are the SAME outline weight.

   • Only Electric Blue, Emerald, Amber, and Purple used for data — never mixed randomly.

   • Domain color coding is consistent across table, chart, and badges:

       Math      → Electric Blue

       Logic     → Purple

       Knowledge → Emerald

       Code      → Amber



9. FOOTER STAT CARDS:

   • Each stat card is a rounded rectangle (#1C2128 bg) with a top accent bar

     in the corresponding accent color.

   • Large number centered, label below in muted text.



10. PRINT SAFETY:

    • Minimum 12mm clear margin on all edges (for A0 printing bleed).

    • All text minimum 18pt for legibility at arm's length.

    • No pure white (#FFFFFF) text — use #E6EDF3 to avoid blowout on print.



═══════════════════════════════════════════

OUTPUT SPECIFICATION

═══════════════════════════════════════════



Format:   A0 Portrait  (841 × 1189 mm)

DPI:      300

Color:    CMYK-safe (use the hex values above; avoid neon RGB-only values)

Export:   PDF (vector) + PNG fallback at 150 DPI for digital display

Fonts:    Embed Inter + JetBrains Mono



If generating in Canva / Figma / PowerPoint:

  • Use "Custom size": 33.11 in × 46.81 in

  • Or at 150 DPI: 4967 × 7016 px canvas



═══════════════════════════════════════════

NEGATIVE SPACE GUIDELINES

═══════════════════════════════════════════



DO NOT:

  ✗ Add decorative images, stock photos, or irrelevant icons

  ✗ Use gradients behind body text (only in header banner)

  ✗ Use more than 5 font sizes

  ✗ Use colors not listed in the palette for data elements

  ✗ Compress or omit any data from the results table

  ✗ Use serif fonts anywhere on the poster

  ✗ Place text closer than 8px to a panel border



DO:

  ✓ Let the dark background breathe — don't overfill panels

  ✓ Use whitespace deliberately between each row

  ✓ Make the pipeline (Row 3) the visual centerpiece of the poster

  ✓ Ensure the results table is readable from 1.5 metres away

  ✓ Keep the footer compact — 8% of total height maximum
```
---

## Notes for the Designer

| Item | Value |
|---|---|
| Paper | Modular LLM Scorer |
| Authors | [Fill in before printing] |
| Conference | [Fill in before printing] |
| GitHub | github.com/ratnajeet00/Modular-LLM-Scorer |
| Python version | 3.10+ |
| Key dependency | scipy >= 1.8.0 |
| Validation | 43/43 evaluator tests passing |
| Providers | OpenAI, Gemini, Groq, Together, OpenRouter, HuggingFace, Ollama, Echo |
| Domains | Math (25%), Logic (25%), Knowledge (35%), Code (15%) |
| Modes | quick=500, half=1500, full=6000 samples |

### Real Data to Use in Results Table

The result values in Row 5 are **illustrative placeholders**.  
Replace them with actual benchmark run values from:

```
bech mark/{model}_{timestamp}.json  →  fields: accuracy, per_domain, confidence_intervals_95
```

Run all four models with the same seed to get comparable numbers:

```powershell
python run_benchmark.py --model local --model-name llama3.1:8b         --mode half --seed 42
python run_benchmark.py --model local --model-name mistral:7b-instruct  --mode half --seed 42
python run_benchmark.py --model local --model-name qwen2:7b-instruct    --mode half --seed 42
python run_benchmark.py --model local --model-name deepseek-coder:6.7b  --mode half --seed 42
```

Then generate the McNemar's comparison:

```powershell
python run_benchmark.py --compare "bech mark\llama3.1_result.json" "bech mark\mistral_result.json"
```

---

*Last updated: May 2026 · Modular LLM Scorer v1.0*
