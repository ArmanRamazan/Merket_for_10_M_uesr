# EduPlatform: Learning Velocity Engine

> From "watch videos" to "learn faster" — AI-powered platform that optimizes
> learning speed through adaptive paths, spaced repetition, Socratic tutoring,
> and knowledge graphs.

## 1. Core Problem

**87.4% of online courses are never completed.**

Current platforms deliver content linearly. They don't adapt to the student,
don't optimize retention, and don't teach HOW to learn. The market is full of
"video hosting + progress bar" solutions disguised as education.

## 2. Product Vision

Not another LMS. A **Learning Intelligence Layer** on top of video content:

```
┌─────────────────────────────────────────────────────────────┐
│  LEARNING VELOCITY ENGINE (the brain)                        │
│  Knowledge graph · Adaptive path · Spaced repetition         │
│  Metacognition dashboard · Learning speed metrics            │
├─────────────────────────────────────────────────────────────┤
│  AI AGENTS (the teachers)                                    │
│  Socratic Tutor · Quiz Generator · Summary Builder           │
│  Knowledge Organizer · Context Mentor                        │
├─────────────────────────────────────────────────────────────┤
│  ACTIVE LEARNING (the practice)                              │
│  Quizzes · Flashcards · Code challenges · Discussions        │
│  Gamification (XP, streaks, badges)                          │
├─────────────────────────────────────────────────────────────┤
│  CONTENT DELIVERY (the foundation)                           │
│  Video courses · Modules · Lessons · Reviews · Enrollment    │
│  CDN · Transcripts · Semantic chapters                       │
└─────────────────────────────────────────────────────────────┘
```

## 3. Core Learning Loop

The product implements a 4-step evidence-based learning cycle:

```
  ┌──────────────┐     ┌──────────────┐
  │  1. CONSUME   │────▶│  2. PRACTICE  │
  │  Video/Text   │     │  Quiz/Code    │
  │  AI Summary   │     │  Active Recall│
  └──────────────┘     └──────┬───────┘
         ▲                     │
         │                     ▼
  ┌──────┴───────┐     ┌──────────────┐
  │  4. CONNECT   │◀────│  3. REFLECT   │
  │  Knowledge    │     │  AI Tutor     │
  │  Graph/Canvas │     │  Socratic Q   │
  └──────────────┘     └──────────────┘

  Spaced Repetition schedules revisits across all 4 steps
```

**Evidence base:**
- Spaced repetition → +60% long-term retention vs massed study
- Active recall (quizzes) → +25% retention vs passive review
- Socratic questioning → deeper conceptual understanding
- Knowledge graphs → visible learning gaps, metacognition
- Gamification + community → up to 96% completion rate

## 4. What We Keep vs Rewrite vs Add

### KEEP (working foundation — Level 0)
- Identity service (auth, roles, email verification)
- Course service (CRUD, categories, modules, lessons, reviews)
- Enrollment service (enrollment, progress tracking)
- Notification service (base notifications)
- Payment service (will enhance, not rewrite)
- Buyer frontend (pages, routing, TanStack Query)
- Infrastructure (Docker, Prometheus, Grafana, Redis)
- Shared library (security, errors, database, health, rate limiting)
- Total: 157 tests — all stay

### ENHANCE (extend existing services)
- Course service: add quiz model, AI-generated summaries, lesson transcripts
- Enrollment service: integrate spaced repetition scheduler (FSRS)
- Notification service: smart reminders based on FSRS schedule
- Frontend: quiz UI, flashcards, knowledge graph visualization

### ADD (new services)
- **AI Service** (Python) — LLM orchestration, model routing, prompt management
- **Learning Engine** (Python) — FSRS scheduler, knowledge graph, adaptive paths
- **xAPI/LRS** — learning event store for analytics and AI training data

## 5. Architecture: Two Contours

Separation of "content delivery" and "learning brain" as independent scaling units:

```
                    ┌──────────────┐
                    │   Frontend    │
                    │  (Next.js)   │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
   ┌─────────────────┐      ┌─────────────────┐
   │ CONTENT CONTOUR  │      │ LEARNING CONTOUR │
   │                  │      │                  │
   │ Course Service   │      │ AI Service       │
   │ Video CDN        │      │ Learning Engine  │
   │ Enrollment       │      │ xAPI/LRS Store   │
   │ Payment          │      │                  │
   │ Identity         │      │ FSRS Scheduler   │
   │ Notification     │      │ Knowledge Graph  │
   │                  │      │ Quiz Bank        │
   │ PostgreSQL       │      │ Vector DB (pgvec)│
   │ Redis            │      │ Redis            │
   └─────────────────┘      └─────────────────┘
```

Content contour scales by users/videos.
Learning contour scales by AI interactions/knowledge points.

## 6. New Services — Detailed Design

### 6.1 AI Service (`services/py/ai/`)

Centralized LLM orchestration with model routing.

```
services/py/ai/
├── app/
│   ├── routes/
│   │   ├── completion.py    — generate quiz, summary, tutor response
│   │   └── health.py
│   ├── services/
│   │   ├── router.py        — model routing: cheap → mid → expensive
│   │   ├── tutor.py         — Socratic tutor logic
│   │   ├── quiz_gen.py      — quiz generation from lesson content
│   │   └── summary.py       — lesson/module summarization
│   ├── domain/
│   │   ├── prompt.py        — prompt templates (versioned)
│   │   └── models.py        — LLMRequest, LLMResponse, ModelTier
│   └── repositories/
│       ├── cache.py         — Redis cache for repeated queries
│       └── llm_client.py    — unified client (Gemini/Claude/OpenAI)
├── tests/
└── migrations/
```

**Model Routing Strategy:**
```
┌─────────────────────┬──────────────────┬───────────────────┐
│ Task                │ Model Tier       │ Cost/1M tokens    │
├─────────────────────┼──────────────────┼───────────────────┤
│ Quiz generation     │ CHEAP            │ $0.08-0.30        │
│ (Gemini Flash Lite) │ (batch, async)   │                   │
├─────────────────────┼──────────────────┼───────────────────┤
│ Lesson summary      │ CHEAP            │ $0.08-0.30        │
│ (Gemini Flash)      │ (cacheable)      │                   │
├─────────────────────┼──────────────────┼───────────────────┤
│ Socratic tutor      │ MID              │ $1.00-3.00        │
│ (Claude Haiku /     │ (interactive)    │                   │
│  GPT-4o Mini)       │                  │                   │
├─────────────────────┼──────────────────┼───────────────────┤
│ Deep explanation /   │ EXPENSIVE        │ $3.00-15.00       │
│ code review         │ (on-demand)      │                   │
│ (Claude Sonnet)     │                  │                   │
└─────────────────────┴──────────────────┴───────────────────┘
```

### 6.2 Learning Engine (`services/py/learning/`)

The "brain" — adaptive paths, spaced repetition, knowledge graph.

```
services/py/learning/
├── app/
│   ├── routes/
│   │   ├── quiz.py          — take quiz, submit answers, get feedback
│   │   ├── flashcards.py    — FSRS-scheduled flashcard deck
│   │   ├── knowledge.py     — knowledge graph CRUD + visualization
│   │   └── dashboard.py     — learning velocity metrics
│   ├── services/
│   │   ├── fsrs.py          — FSRS algorithm (py-fsrs library)
│   │   ├── knowledge_graph.py — concept nodes, edges, mastery levels
│   │   ├── adaptive_path.py — skip known → focus on gaps
│   │   └── velocity.py      — learning speed calculation
│   ├── domain/
│   │   ├── concept.py       — Concept, ConceptEdge, MasteryLevel
│   │   ├── quiz.py          — Quiz, Question, Answer, Attempt
│   │   ├── flashcard.py     — Card, ReviewLog, FSRSParams
│   │   └── metrics.py       — LearningVelocity, RetentionRate
│   └── repositories/
│       ├── quiz_repo.py
│       ├── card_repo.py
│       └── concept_repo.py
├── tests/
└── migrations/
```

**Knowledge Graph Model:**
```sql
-- Concepts (knowledge points per course)
CREATE TABLE concepts (
    id UUID PRIMARY KEY,
    course_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    lesson_id UUID,              -- linked lesson (optional)
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Concept relationships
CREATE TABLE concept_edges (
    id UUID PRIMARY KEY,
    source_id UUID REFERENCES concepts(id),
    target_id UUID REFERENCES concepts(id),
    relation VARCHAR(50),        -- prerequisite, related, extends
    weight FLOAT DEFAULT 1.0
);

-- Per-student mastery of each concept
CREATE TABLE concept_mastery (
    id UUID PRIMARY KEY,
    student_id UUID NOT NULL,
    concept_id UUID REFERENCES concepts(id),
    mastery_level FLOAT DEFAULT 0.0,  -- 0.0 to 1.0
    last_reviewed_at TIMESTAMPTZ,
    next_review_at TIMESTAMPTZ,       -- FSRS scheduled
    review_count INT DEFAULT 0,
    UNIQUE(student_id, concept_id)
);
```

**FSRS Integration:**
```python
# Using py-fsrs (open source, free)
# https://github.com/open-spaced-repetition/py-fsrs
from fsrs import FSRS, Card, Rating

scheduler = FSRS()

# After student answers a quiz question:
card = get_or_create_card(student_id, concept_id)
scheduling = scheduler.review(card, rating=Rating.Good)
# scheduling.card.due → next review datetime
# Save to concept_mastery.next_review_at
```

### 6.3 xAPI Event Store

Lightweight LRS for learning analytics (not a separate service — table in Learning Engine DB).

```sql
CREATE TABLE learning_events (
    id UUID PRIMARY KEY,
    student_id UUID NOT NULL,
    verb VARCHAR(50) NOT NULL,       -- watched, answered, completed, reviewed
    object_type VARCHAR(50) NOT NULL, -- lesson, quiz, flashcard, concept
    object_id UUID NOT NULL,
    result JSONB,                    -- score, duration, success
    context JSONB,                   -- course_id, module_id, device
    timestamp TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_events_student ON learning_events(student_id, timestamp DESC);
CREATE INDEX idx_events_verb ON learning_events(verb, timestamp DESC);
```

## 7. Cost Model: LLM API at Scale

### Per-User AI Consumption Estimate

Average active student per month:
```
Activity                     Tokens (in+out)    Calls/month
─────────────────────────────────────────────────────────────
Quiz generation (per lesson)  2K in + 1K out     ×20 lessons = 60K
Lesson summaries              3K in + 500 out    ×20 lessons = 70K
Socratic tutor interactions   1K in + 500 out    ×30 chats   = 45K
Flashcard hints               500 in + 200 out   ×50 reviews = 35K
─────────────────────────────────────────────────────────────
Total per active user/month:                     ~210K tokens
```

### Cost Per Active User Per Month

```
Scale       Model Mix                           Cost/user/mo
──────────────────────────────────────────────────────────────
10K MAU     80% Gemini Flash ($0.15/M avg)      $0.03
            20% Claude Haiku ($3/M avg)

100K MAU    85% Gemini Flash Lite ($0.08/M)     $0.02
            10% Gemini Flash ($0.15/M)
            5% Claude Sonnet ($9/M)

1M MAU      70% Self-hosted SLM ($0.01/M)       $0.008
            25% Gemini Flash ($0.15/M)
            5% Claude Haiku ($3/M)

10M MAU     80% Self-hosted SLM ($0.005/M)      $0.004
            15% Gemini Flash ($0.08/M)
            5% Claude Haiku ($3/M)
──────────────────────────────────────────────────────────────
```

### Total AI Infrastructure Cost

```
Scale        Active Users    AI Cost/mo    AI Cost/year
───────────────────────────────────────────────────────
10K MAU      3K active       $90           $1,080
100K MAU     30K active      $600          $7,200
1M MAU       300K active     $2,400        $28,800
10M MAU      3M active       $12,000       $144,000
───────────────────────────────────────────────────────
```

**Key insight:** AI costs are manageable because:
1. 80-90% of tasks route to cheapest models (Gemini Flash Lite: $0.08/M)
2. Summaries and quizzes are cached (same lesson → same output for all students)
3. FSRS algorithm runs locally (zero API cost)
4. Knowledge graph operations are pure database (zero API cost)
5. [LLM costs drop ~10x per year](https://www.bvp.com/atlas/the-ai-pricing-and-monetization-playbook)

### Other Infrastructure Costs

```
Component              10K MAU     100K MAU    1M MAU
────────────────────────────────────────────────────────
5× PostgreSQL          $0 (dev)    $200/mo     $800/mo
Redis                  $0 (dev)    $50/mo      $200/mo
Servers (5 services)   $0 (dev)    $300/mo     $1,500/mo
CDN (video)            $50/mo      $500/mo     $3,000/mo
Vector DB (pgvector)   $0 (incl)   $0 (incl)   $100/mo
Monitoring             $0 (self)   $50/mo      $200/mo
────────────────────────────────────────────────────────
Total infra            $50/mo      $1,100/mo   $5,800/mo
Total + AI             $140/mo     $1,700/mo   $8,200/mo
```

## 8. Financial Model

### Pricing Tiers (Hybrid: subscription + AI credits)

```
Tier         Price/mo    Included                      AI Credits
─────────────────────────────────────────────────────────────────
Free         $0          5 courses, basic progress,     10 tutor chats
                         quizzes (cached)               5 summaries

Student      $9.99       Unlimited courses,             100 tutor chats
                         spaced repetition,             unlimited summaries
                         knowledge graph,               50 quiz generations
                         basic analytics

Pro          $19.99      Everything in Student +        unlimited tutor
                         AI Socratic tutor,             unlimited quizzes
                         learning velocity dashboard,   code review
                         export to Obsidian,
                         priority support

Team/B2B     $14.99/     Everything in Pro +            unlimited
             seat        admin dashboard,
                         team analytics,
                         custom content
```

### Unit Economics

```
                    Free    Student   Pro       Team
─────────────────────────────────────────────────────
Revenue/user/mo     $0      $9.99     $19.99    $14.99
AI cost/user/mo     $0.01   $0.03     $0.08     $0.06
Infra cost/user/mo  $0.01   $0.02     $0.02     $0.02
─────────────────────────────────────────────────────
Gross margin        N/A     99.5%     99.5%     99.5%
─────────────────────────────────────────────────────
```

At current API prices, AI cost per user is **negligible** ($0.03–$0.08/mo).
Even at 10M users, total AI spend is ~$144K/year — tiny vs potential revenue.

### Revenue Projections

```
Phase          Users    Paid %   ARPU     MRR          ARR
──────────────────────────────────────────────────────────────
10K MAU        10K      5%       $12      $6,000       $72K
100K MAU       100K     8%       $13      $104,000     $1.25M
1M MAU         1M       10%     $14      $1,400,000   $16.8M
10M MAU        10M      12%     $15      $18,000,000  $216M
──────────────────────────────────────────────────────────────
```

## 9. Implementation Phases

### Phase A: Quiz + AI Foundation (4-6 weeks)
**Goal:** Transform passive video → active learning

New:
- [ ] AI Service — model routing, Gemini Flash integration
- [ ] Quiz model in Learning Engine (questions, answers, attempts)
- [ ] AI Quiz Generator (auto-generate from lesson content)
- [ ] AI Lesson Summary (auto-generate, cache per lesson)
- [ ] Quiz UI in buyer frontend (after-lesson quiz flow)
- [ ] Summary UI (collapsible summary above each lesson)

Enhance:
- [ ] Course service — store lesson transcripts/content for AI processing
- [ ] Enrollment service — link quiz attempts to progress

Metrics: quiz completion rate, time-on-quiz, accuracy

### Phase B: Spaced Repetition + Flashcards (3-4 weeks)
**Goal:** Long-term retention via evidence-based scheduling

New:
- [ ] FSRS integration in Learning Engine (py-fsrs)
- [ ] Flashcard model (cards generated from quiz mistakes + key concepts)
- [ ] Smart notification triggers (FSRS-scheduled review reminders)
- [ ] Flashcard UI (swipe cards, rate difficulty)
- [ ] "Review due" badge in header/dashboard

Enhance:
- [ ] Notification service — FSRS-triggered reminders
- [ ] Enrollment — track review sessions as progress

Metrics: retention rate (7d, 30d), review streak length

### Phase C: Knowledge Graph + Adaptive Path (4-6 weeks)
**Goal:** Personalized learning — skip known, focus on gaps

New:
- [ ] Concept model (knowledge points per course, teacher-defined)
- [ ] Concept mastery tracking (per-student)
- [ ] Adaptive pre-test (diagnose level → skip known material)
- [ ] Knowledge graph visualization (frontend, force-directed graph)
- [ ] Learning velocity dashboard (concepts/hour, trend, comparisons)

Enhance:
- [ ] Course creation — teachers tag concepts per lesson
- [ ] Course curriculum — show mastery overlay

Metrics: time-to-competency, concepts mastered/week

### Phase D: Socratic AI Tutor (3-4 weeks)
**Goal:** Deep understanding through dialogue, not answers

New:
- [ ] Chat interface per lesson (ask questions about content)
- [ ] Socratic prompt pipeline (never give answer directly)
- [ ] Tutor uses lesson content as context (RAG-lite via lesson text)
- [ ] Rate tutor response (thumbs up/down → improve prompts)

Enhance:
- [ ] AI Service — conversation memory (short-term, per session)
- [ ] xAPI events — log tutor interactions for analytics

Metrics: questions asked/lesson, understanding score, NPS

### Phase E: Gamification + Community (3-4 weeks)
**Goal:** Motivation and accountability

New:
- [ ] XP system (earn XP: complete lesson, pass quiz, review flashcard)
- [ ] Streaks (daily learning streak like Duolingo)
- [ ] Badges/achievements (first course, 7-day streak, 100% mastery)
- [ ] Leaderboard (per course, opt-in)
- [ ] Course discussion (comments per lesson, upvotes)

Enhance:
- [ ] Frontend header — XP counter, streak flame
- [ ] Notification — streak at risk reminders

Metrics: DAU/MAU ratio, streak length distribution, completion rate delta

### Phase F: Payments + Seller Dashboard (3-4 weeks)
**Goal:** Monetization and teacher tools

New:
- [ ] Real payment integration (Stripe)
- [ ] Subscription management (free/student/pro tiers)
- [ ] Seller app — basic dashboard (my courses, enrollment stats, revenue)
- [ ] Teacher analytics (completion rate, avg rating, revenue per course)

Enhance:
- [ ] Payment service — Stripe webhook, subscription lifecycle
- [ ] Course service — pricing tiers, free trial logic

Metrics: conversion rate, MRR, churn

## 10. Tech Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| LLM primary | Gemini Flash Lite / Flash | Cheapest ($0.08-0.30/M), fast, good quality |
| LLM tutor | Claude Haiku 4.5 | Best instruction-following for Socratic dialogue |
| Spaced repetition | FSRS (py-fsrs) | Open source, academically validated, free |
| Vector DB | pgvector (PostgreSQL ext) | No new infra, good enough for lesson-level RAG |
| Knowledge graph | PostgreSQL (concepts + edges) | Simple, queryable, no graph DB overhead |
| Quiz storage | PostgreSQL (in learning-db) | Consistent with existing architecture |
| Frontend graph viz | react-force-graph or d3 | Lightweight, no heavy dependencies |
| xAPI events | PostgreSQL table (not full LRS) | YAGNI — full LRS is overkill at this stage |
| Model routing | Custom Python (AI service) | Simple if/else by task type, evolve later |
| Caching | Redis (existing) | Cache AI responses per lesson (same for all students) |

## 11. What NOT to Build (YAGNI)

- No separate vector database (pgvector in PostgreSQL is enough)
- No full xAPI/LRS server (simple events table)
- No MCP server (design APIs to be MCP-wrappable later)
- No self-hosted LLM until 1M+ MAU (API is cheaper at small scale)
- No real-time collaborative canvas (too complex, low ROI now)
- No Rust services until we hit performance limits
- No mobile app (responsive web first)
- No multi-language AI until regional expansion
- No Cloudflare Durable Objects (Docker + Redis handles our scale)

## 12. Success Criteria

```
Metric                  Baseline (now)  Target (Phase E)
─────────────────────────────────────────────────────────
Course completion rate  ~13%            40%+
7-day retention         unknown         60%+
DAU/MAU ratio           unknown         25%+
Time-to-competency      unknown         -30% vs control
Avg quiz score          N/A             70%+
Streak > 7 days         N/A             30% of active
NPS                     unknown         50+
─────────────────────────────────────────────────────────
```

## References

- [FSRS Algorithm](https://github.com/open-spaced-repetition/py-fsrs) — open source spaced repetition
- [Squirrel AI Knowledge Graph](https://squirrelai.com/) — TIME Best Invention 2025
- [Spaced Repetition Evidence](https://pmc.ncbi.nlm.nih.gov/articles/PMC8759977/)
- [LLM Pricing Trends](https://www.bvp.com/atlas/the-ai-pricing-and-monetization-playbook) — 10x cost drop/year
- [AI SaaS Economics](https://www.getmonetizely.com/blogs/the-economics-of-ai-first-b2b-saas-in-2026)
- [Model Routing Strategy](https://ai.koombea.com/blog/llm-cost-optimization)
- [xAPI Standard](https://github.com/adlnet/ADL_LRS) — open source LRS
- [Course Completion Problem](https://dev.to/valynx_saas/874-of-online-courses-never-get-finished-heres-why-and-what-i-built-to-fix-it-48e9)
