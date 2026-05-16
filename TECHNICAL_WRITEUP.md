# Linguo: Real-Time AI Spanish Tutor

## Overview

Linguo is a voice-first, real-time AI language tutor built using Pipecat and the Gemini Live API. The system simulates a conversational language-learning experience similar to speaking with a human tutor, rather than interacting with a traditional screen-based learning app.

The project focuses on low-latency spoken interaction, interruption handling, conversational roleplay, and adaptive tutoring flows. Learners can practice Spanish entirely through voice using teaching sessions, verbal quizzes, free-form roleplay conversations, and on-the-fly doubt resolution.

The primary goal was building a production-leaning real-time conversational pipeline with strong voice UX and clear separation of concerns, rather than UI polish.

---

## Core Features

### 1. Real-Time Voice Tutoring
Full conversational voice interaction using streaming audio input and output. Users can learn Spanish entirely through speech without relying on typing or screen-heavy interaction.

### 2. Teaching Mode
The tutor introduces vocabulary and phrases in a structured format using explanation, examples, repetition, and comprehension checks.

**Current lesson modules:**
- Greetings
- Numbers
- Ordering Food / Coffee

### 3. Quiz Mode
Verbal quizzes with conversational prompts and corrective feedback. The system accepts semantically close answers and tolerates speech-to-text imperfections during evaluation.

### 4. Conversation Practice / Roleplay
Users can enter roleplay scenarios such as ordering coffee in Spanish. The tutor stays in-character while gently correcting mistakes during the interaction.

### 5. Doubt Resolution
Learners can interrupt the tutor at any point to ask questions about grammar or vocabulary. The tutor answers briefly and resumes the previous conversational context naturally.

### 6. Progress Review
The tutor can summarize previously practiced vocabulary and topics during the session to reinforce learning continuity.

### 7. Persistent Memory
Basic long-term learner memory implemented using JSON persistence. User progress, completed lessons, and vocabulary exposure persist across sessions.

---

## System Architecture

The system follows a modular real-time voice pipeline architecture using Pipecat.

### High-Level Flow

```
User Voice Input
  → Browser UI (WebRTC)
  → Pipecat Real-Time Pipeline
  → Voice Activity Detection (Silero VAD)
  → Gemini Live API
  → Tutor Orchestration Logic
  → Lesson / Quiz Manager
  → Memory Layer (progress.json)
  → Streaming Voice Response Back to User
```

### Architecture Decisions

The project intentionally separates:
- Transport
- Voice pipeline
- Tutoring logic
- Curriculum content
- Memory persistence

This separation made it easier to iterate on tutoring behaviors without modifying lower-level audio infrastructure.

Pipecat was chosen because it provides fine-grained control over the in-process real-time pipeline and interruption handling behavior, which was important for experimentation with conversational tutoring flows.

---

## Technical Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | Pipecat |
| LLM | Gemini Live API |
| Voice Activity Detection | Silero VAD |
| Frontend | HTML / CSS / JavaScript (WebRTC) |
| Backend | Python |
| Persistence | JSON file (`progress.json`) |

---

## Latency & Voice UX

The system was designed around low-latency conversational interaction. Streaming voice input/output and VAD-based turn detection were prioritized early in development because they are critical to making the tutor feel natural.

**Observed latency:** ~1.5s to ~2.5s from end-of-user speech to audible response generation.

Latency varied depending on:
- Network conditions
- Gemini response generation time
- Speech length
- Interruption timing

Pipecat's streaming pipeline architecture helped maintain conversational responsiveness and enabled smoother interruption recovery during live interactions.

---

## Interruption Handling

One of the primary goals was supporting natural spoken interruptions (barge-in).

**The tutor supports:**
- Interrupting active speech
- Asking doubts mid-lesson
- Switching between teaching and roleplay dynamically
- Resuming conversational context after interruptions

Special focus was placed on maintaining conversational continuity instead of restarting lessons after interruptions.

---

## State Management & Tutoring Logic

The tutoring flow is implemented using structured prompting, lightweight lesson state tracking, and modular lesson definitions.

The project intentionally avoided overly complex orchestration frameworks in favor of simpler prompt-driven conversational control because:
- Development time was limited
- Conversational flexibility was more important than rigid deterministic flows
- Gemini performed well with behavioral instruction tuning

Lesson content is currently hardcoded for reliability and predictable tutoring behavior.

---

## Memory Design

The project implements two forms of memory:

### Short-Term Memory
Conversation context is maintained within the active tutoring session using the Pipecat conversation pipeline and Gemini context window.

### Long-Term Memory
Persistent learner information is stored locally in `progress.json`, which tracks:
- Completed lessons
- Exposed vocabulary
- Session progress

The persistence layer was intentionally kept lightweight to prioritize reliability and simplicity within the assignment timeline.

---

## Challenges Faced

### 1. Real-Time Voice Orchestration
The most difficult aspect was maintaining smooth conversational flow while handling real-time interruptions, dynamic lesson switching, and low-latency responses simultaneously. Real-time voice systems are significantly more sensitive to latency and conversational dead-air compared to traditional chat applications.

### 2. Interruption Recovery
Ensuring that the tutor could answer user doubts without completely abandoning the active roleplay or lesson context required careful prompt engineering to encourage the model to:
- Answer briefly
- Maintain conversational immersion
- Naturally resume the previous activity

### 3. Speech Recognition Noise
The system had to handle multilingual and noisy voice input, including:
- Mixed English + Spanish utterances
- Pronunciation mistakes
- Speech restarts and filler words
- Imperfect STT transcriptions

Prompt tuning was used heavily to make the tutor more tolerant of imperfect spoken input.

### 4. Balancing Structure vs Flexibility
A fully deterministic tutoring state machine would provide stronger control but would reduce conversational flexibility. The project intentionally chose a more prompt-driven approach because it produced more natural conversational behavior within the limited assignment timeline.

---

## Trade-Offs & Design Decisions

### Why Pipecat Instead of LiveKit Agents?
Pipecat was selected because it provides direct control over the real-time voice pipeline and makes it easier to experiment with interruption handling and conversational orchestration inside a single Python process.

### Why Prompt-Driven Orchestration?
Instead of building a large deterministic orchestration graph, the project relied heavily on structured prompting and behavioral instructions. This reduced engineering complexity while still allowing teaching flows, roleplay, quizzes, interruption handling, and conversational recovery.

### Why JSON Persistence?
The assignment allowed lightweight persistence mechanisms such as JSON files. Using JSON-based persistence:
- Reduced setup complexity
- Improved local reliability
- Accelerated iteration during rapid prototyping

---

## Known Limitations

- Pronunciation feedback is heuristic rather than phoneme-level
- Memory persistence is lightweight and not user-scaled
- Quiz grading is prompt-driven rather than deeply semantic
- Latency occasionally increases during longer responses
- The frontend UI is intentionally minimal

---

## Future Improvements

Given more development time, the next improvements would include:

- Pronunciation scoring using phoneme-level alignment
- Adaptive curriculum difficulty based on learner performance
- Spaced repetition scheduling for vocabulary review
- Better semantic quiz grading
- More advanced memory and learner analytics
- Multi-language support beyond Spanish
- Enhanced observability dashboards and latency tracing
- More resilient interruption orchestration

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone <your-repository-url>
cd simple-chatbot
uv sync
```

### 2. Set API Key

```bash
export GEMINI_API_KEY=your_key_here
```

### 3. Run Backend

```bash
uv run bot-gemini.py
```

### 4. Open Client

Open the browser client locally and connect to the running Pipecat pipeline.

---

## Evaluation Approach

A lightweight evaluation approach was used during development using scripted conversational testing.

**The following conversational flows were repeatedly tested:**

**Teaching Flow**
- Greetings lesson
- Numbers lesson
- Ordering food lesson

**Quiz Flow**
- Vocabulary recall
- Pronunciation tolerance
- Semantic answer flexibility

**Roleplay Flow**
- Ordering coffee
- Conversational continuity
- Correction during free-form dialogue

**Interruption Handling**
- Asking grammar doubts mid-conversation
- Switching topics dynamically
- Resuming previous conversational context

**Multilingual Input Handling**
- Mixed English + Spanish input
- Noisy speech
- Accented pronunciation
- Code-switching scenarios

---

## AI Assistance Disclosure

## AI Assistance Disclosure

AI assistants such as ChatGPT and Claude were used selectively during development for debugging support, prompt iteration, documentation refinement, and architectural brainstorming.

All core implementation decisions, orchestration design, integration, testing, behavioral tuning, and final system validation were manually reviewed, iterated upon, and validated during development.

---

## Conclusion

Linguo demonstrates a production-leaning prototype for a real-time conversational language tutor focused on voice-first interaction.

**The project prioritizes:**
- Low-latency conversational UX
- Interruption handling
- Tutoring structure
- Conversational immersion
- Practical engineering trade-offs

Rather than optimizing for UI polish, the implementation focused on building a reliable conversational tutoring pipeline capable of supporting natural spoken learning interactions.
