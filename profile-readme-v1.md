<div align="center">

# 👋 Nik Abdul Aqmal Bin Zunaidi

### Final-year Computer Science @ UPNM · Applied NLP & ML · Backend engineering

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1200&color=2E86C1&center=true&vCenter=true&width=520&lines=Building+Sentiri+%E2%80%94+NLP+for+autism+therapy+centres;Fine-tuning+transformers+for+Malay+%2B+code-switched+text;Django+%2B+PyTorch+%2B+RAG+%2B+Swift;Measure+it%2C+or+it+didn%27t+happen" alt="Typing SVG" />

<sub>📍 Malaysia · 🎓 CGPA 3.79, First Class · ✉️ nikabdulaqmal@gmail.com</sub>

<a href="mailto:nikabdulaqmal@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white" /></a>
<a href="https://github.com/nickaqmal02"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" /></a>
<!-- Add your LinkedIn URL here and uncomment:
<a href="https://linkedin.com/in/YOUR-HANDLE"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white" /></a>
-->

</div>

---

## 🚧 What I'm building right now

| Project | What it is | Where it stands |
|---|---|---|
| **Sentiri** | Clinical + NLP platform for autism therapy centres — WhatsApp chat analysis, sentiment, topic modelling, and a grounded RAG assistant | Final-year project, working end-to-end on 266 real therapy messages |
| **ApexAgent** | A macOS-native voice agent in Swift — local LLM fallback, on-device speech, Accessibility API tool use | Working demo, built in one week with `vim` + `swift build` |
| **Evaluation work** | A reproducible XLM-R / mBERT / IndoBERT / DistilBERT comparison plus topic-model and RAG evaluation harnesses | Published as an executable Quarto notebook (HTML + PDF) |

The through-line: I don't trust a model until I've tried to break it. Every project below has numbers behind it, including the numbers that went against me.

---

## 📌 Featured work

### 🧠 Sentiri — Autism Therapy Chat Analyzer
**Python · Django 6 · PyTorch · PostgreSQL · ChromaDB · LangChain · Celery**

A therapy centre runs on WhatsApp: parents describe sleep, meltdowns, school, feeding. Sentiri turns those exports into structured, private, clinically useful signal.

- **Role-based platform** — separate dashboards for admin, therapist, doctor, and client; DSM-5 specifier workflow where a therapist proposes a diagnosis and a doctor approves it.
- **Sentiment analysis** — XLM-RoBERTa fine-tuned on 2,000 self-labelled Malay / code-switched messages (128 positive · 92 neutral · 46 negative) across a 432-message held-out split.
- **Topic modelling** — BERTopic (UMAP → HDBSCAN → c-TF-IDF) with Sastrawi stemming, resolving to **5 supervisor-confirmed themes**: *Progress & Sessions* (105 msgs), *Speech & Emotional Feedback* (109), *Behaviour & Transitions* (80), *Sleep & Routine* (68), *School & Play Interaction* (38).
- **Grounded RAG assistant** — multilingual MiniLM embeddings → ChromaDB → cross-encoder rerank (retrieve 20, answer from top 5), so answers about clinic policies cite the actual document chunk.
- **Reservation agent** — LangChain + GLM-5.3 with Redis-backed per-client memory; the LLM proposes a booking, Python verifies availability and office hours, and only then is it confirmed.
- **Notifications** — Celery Beat fires 08:00 reminders for the day's sessions plus instant alerts on new bookings.
- **Privacy by design** — a PII wall strips 54 client/therapist name tokens before any text reaches a model, and cleaning is dual-purpose: light for sentiment (emotion words survive), aggressive for topics (stopwords, slang, emoji normalisation, stemming).

<p>
<a href="https://github.com/nickaqmal02/finalyearenginefulleffort"><img src="https://img.shields.io/badge/View_repository-181717?style=flat-square&logo=github&logoColor=white" /></a>
</p>

---

### 📊 Do I keep XLM-R? A model evaluation I was willing to lose
**Python · PyTorch · Quarto · Jupyter**

My project shipped XLM-R because it "handles Malay natively." That's a hypothesis, not a result — so I tested it against three baselines on the same 432-message split.

| Model | Accuracy | Macro-F1 | Negative recall | Params |
|---|---|---|---|---|
| **mBERT** | **0.882** | **0.881** | 0.919 | 178M |
| **XLM-R** | 0.863 | 0.862 | **0.933** | 278M |
| IndoBERT | 0.509 | 0.046 | 0.899 | 124M |
| DistilBERT | 0.345 | 0.171 | 1.000 | 135M |

- **The hypothesis lost.** I expected XLM-R to win on rojak (mixed Malay-English). mBERT won both slices: **0.951 vs 0.926** on rojak, **0.923 vs 0.863** on pure Malay.
- **The decision held anyway.** In a therapy context the expensive error is missing a distressed message. XLM-R's negative recall (0.933) and hardest-case accuracy (0.950) won that requirement, so I kept it and documented the trade-off instead of hiding the loss.
- **Two baselines collapsed** (minority-class collapse, 0.509 / 0.345). They're in the notebook, reported as-is, not quietly deleted.
- **Topic modelling can't be measured with accuracy** — no labels exist. So I defended it architecturally: a 42% multi-topic rate proving keyword rules are insufficient, and NPMI-based c_v coherence (−0.753) interpreted honestly for a corpus averaging 3 tokens per document rather than dressed up as a win.

That last project taught me the thing I now optimise for: *an evaluation that can embarrass you is the only kind worth running.*

<p>
<a href="https://github.com/nickaqmal02/MatrixEvaluationModel"><img src="https://img.shields.io/badge/View_repository-181717?style=flat-square&logo=github&logoColor=white" /></a>
</p>

---

### 🎙 ApexAgent — a macOS voice agent in pure Swift
**Swift · Ollama · Deepgram · Accessibility API**

Jarvis, but local. Voice in → intent → tool execution → voice out, with an online *and* an offline path for every stage:

- **Speech → text:** Deepgram Flux (streaming WebSocket) online, Apple Speech on-device offline.
- **Intent → action:** GLM API online, Ollama + Qwen3 8B locally; tools are shell processes and Accessibility API clicks on real UI elements.
- **Text → speech:** Deepgram Aura-2, or `AVSpeechSynthesizer` with no network at all.

No Xcode project, no storyboards — Swift Package Manager from the terminal. The interesting constraint wasn't the AI, it was building a native app without the tooling everyone says you need.

<p>
<a href="https://github.com/nickaqmal02/ApexAgent"><img src="https://img.shields.io/badge/View_repository-181717?style=flat-square&logo=github&logoColor=white" /></a>
<a href="https://github.com/nickaqmal02/ApexAgent/blob/main/media/simpledemo.mp4"><img src="https://img.shields.io/badge/Watch_demo-EA4335?style=flat-square&logo=googleplay&logoColor=white" /></a>
</p>

---

### 🔎 PersonalRAG — a second brain in the terminal
**Python · Textual · Groq · vector search**

A personal retrieval-augmented agent with a real TUI: ingest PDFs, semantic search, cited answers with source tracking, persistent local embeddings. This is where I learned that retrieval quality — not prompt wording — decides whether a RAG system is useful.

<p>
<a href="https://github.com/nickaqmal02/PersonalRAG"><img src="https://img.shields.io/badge/View_repository-181717?style=flat-square&logo=github&logoColor=white" /></a>
</p>

<details>
<summary><b>🧰 More things I've built</b></summary>

- **ShopeHunt** — mobile store locator (Ionic + Firebase + Google Maps API) with live stock and GPS navigation.
- **Django × Stripe e-commerce** — payments, cart, order state machine.
- **Diet optimiser** — Laravel + PHP, constraint-based meal planning.
- **Fuzzy logic visualisation** — group coursework on fuzzy inference, built as an interactive explainer.
- **CLI notes app**, **React flip game**, **image filtering in Python** — learning projects kept public on purpose.

</details>

---

## 🛠 Tech I actually ship with

**Languages**
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Swift](https://img.shields.io/badge/Swift-F05138?style=for-the-badge&logo=swift&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![PHP](https://img.shields.io/badge/PHP-777BB4?style=for-the-badge&logo=php&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=postgresql&logoColor=white)

**Web & backend**
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Laravel](https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

**ML & NLP**
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging_Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![BERTopic](https://img.shields.io/badge/BERTopic-8A2BE2?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F00?style=for-the-badge&logo=databricks&logoColor=white)

**Data & tooling**
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Neovim](https://img.shields.io/badge/Neovim_(LazyVim)-57A143?style=for-the-badge&logo=neovim&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)

---

## 📊 GitHub

<div align="center">
  <img height="160" src="https://github-readme-stats.vercel.app/api?username=nickaqmal02&show_icons=true&theme=tokyonight&hide_title=true" alt="GitHub stats" />
  <img height="160" src="https://github-readme-stats.vercel.app/api/top-langs/?username=nickaqmal02&layout=compact&theme=tokyonight&hide_title=true" alt="Top languages" />
</div>

---

## 🎓 Education & awards

| | |
|---|---|
| **B.Sc. Computer Science (Honours)** | National Defence University of Malaysia (UPNM) · CGPA **3.79** |
| **STPM** | Science stream · 3.92 |
| **Awards** | Dean's List · First Class Award, UPNM |
| **Certifications** | MATLAB Fundamentals & Machine Learning · Django & REST APIs · Full-stack (Tailwind, JS, PostgreSQL) |
| **Also learning** | FastAPI + Poetry, vector databases, and a RAG bootcamp — currently rebuilding retrieval pipelines from scratch to understand them |

---

## 💬 How I work

> I'd rather understand a pipeline than copy one. My notes for this project live in a [1,400-line engineering journal](https://github.com/nickaqmal02/finalyearenginefulleffort/blob/main/progress.md) — every bug, every wrong hypothesis, and the reasoning that fixed it.

I'm aiming at **AI engineering**: models in production, evaluated honestly, wrapped in backends that real people can use.

---

<div align="center">

**Open to conversations about NLP, applied ML, and backend engineering.**

<a href="mailto:nikabdulaqmal@gmail.com"><img src="https://img.shields.io/badge/Say_hello-D14836?style=for-the-badge&logo=gmail&logoColor=white" /></a>

<sub><img src="https://komarev.com/ghpvc/?username=nickaqmal02&label=profile+views&color=2E86C1&style=flat-square" alt="Profile views" /></sub>

</div>
