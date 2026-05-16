# Evaluation Harness

This project uses lightweight scripted conversational evaluation to validate key tutoring behaviors and reduce regressions during development.

---

## Evaluation Goals

The evaluation process focuses on verifying:

- **Conversational continuity** – smooth transitions between teaching modes
- **Interruption handling** – graceful responses to learner questions mid-flow
- **Tutoring consistency** – stable educational behavior across sessions
- **Multilingual/code-switching robustness** – handling mixed-language input
- **Quiz behavior** – appropriate questioning and feedback patterns
- **Roleplay recovery** – maintaining immersion and context
- **Memory recall** – referencing previous lesson content

---

## Scripted Test Scenarios

### 1. Teaching Flow

**Input**
```text
Teach me greetings in Spanish
```

**Expected Behavior**
- Tutor starts structured greetings lesson
- Introduces vocabulary gradually
- Encourages learner participation

---

### 2. Quiz Mode

**Input**
```text
Quiz me on greetings
```

**Expected Behavior**
- Tutor asks verbal quiz questions
- Provides corrective feedback
- Accepts semantically close answers

---

### 3. Roleplay Conversation

**Input**
```text
Let's roleplay ordering coffee
```

**Expected Behavior**
- Tutor enters conversational roleplay mode
- Maintains conversational immersion
- Corrects learner gently

---

### 4. Interruption Handling

**Input**
```text
Why do we say quiero?
```
*(during active roleplay)*

**Expected Behavior**
- Tutor answers briefly
- Maintains conversational context
- Resumes roleplay naturally

---

### 5. Code-Switching Robustness

**Input**
```text
Hola, can you explain this in English?
```

**Expected Behavior**
- Tutor handles multilingual input
- Explains concept clearly
- Continues lesson smoothly

---

### 6. Progress Review

**Input**
```text
What did I learn today?
```

**Expected Behavior**
- Tutor summarizes completed topics
- References previously practiced vocabulary

---

## Manual Regression Testing

During development, these scripted conversations were repeatedly replayed after orchestration and prompt changes to verify that:

- Conversational flow remained stable
- Interruption handling did not regress
- Tutoring behaviors stayed consistent
- Lesson transitions continued functioning correctly

---

## Current Limitations

The current evaluation approach is lightweight and primarily conversational/manual rather than fully automated.

Future improvements could include:

- Automated transcript evaluation
- Semantic grading benchmarks
- Latency instrumentation
- Conversation replay testing
- Structured behavioral scoring
