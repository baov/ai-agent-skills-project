---
name: clarify-with-choices
description: >
  Doctrine for validating with multiple-choice questions — how a skill questions the user
  before writing anything, and how it degrades when the host agent offers no multiple-choice
  mechanism. Loaded by the skills that validate structuring decisions (codebase-cartographer,
  codebase-harness, ddd-advisor), rarely invoked directly. Use it too when writing or revising
  a skill that has to ask the user for a decision, or when wondering how many questions to ask,
  in what shape, or what to do when the user answers "your call". Not to be confused with
  code-assimilation-quiz, whose multiple-choice questions quiz the developer so that they
  learn, not to settle a decision.
---

# Validating with multiple-choice questions

The multiple-choice question is the point of contact between a skill and the person using it. It is where the rule shared by every skill in this repository plays out: **nothing structuring gets written without explicit validation**.

It is also the only place where agents genuinely differ. The rest — reading files, running scripts, writing markdown — behaves the same everywhere. Asking a multiple-choice question does not.

## The mechanism, depending on the host

Before the first question, work out what the agent has to work with:

| Situation | What to do |
|---|---|
| The host exposes a multiple-choice question tool | Use it. Clickable interface, no blind typing, unambiguous answers. |
| The host exposes none | **Degraded mode**: present the question as text, numbered options, then stop and wait for the answer. |

Never hardcode a tool name in a skill. Names vary from one agent to the next and change from version to version; a skill that names its tool is a skill that breaks elsewhere.

**Degraded mode is no excuse for skipping the question.** A numbered list in a message counts as validation. What is forbidden is writing without having asked — not asking in plain text.

**Ask in the user's own language.** The questions are addressed to a person: write them in the language that person works in — the language of the project being worked on — never in English by default. This repository is in English; what a skill says out loud is not.

```
Three things to settle before I write the glossary:

1. Do "Order" and "Purchase" mean the same thing here?
   a) Yes, one term to keep — I go with "Order"
   b) No, they are two distinct concepts
   c) Other / let me explain

2. …

Answer with something like "1a 2c" and I will carry on.
```

## The shape of a round

In this order, always:

1. **What I understood** — a short bulleted summary of what the agent inferred from the code. That is what makes the question answerable: without it, the user arbitrates blind.
2. **What I am unsure about** — 1 to 3 questions.

Then we write. Once written, briefly announce what was produced and move on, **without asking for confirmation again**: the user already validated through the multiple-choice question.

## Writing the questions

| Rule | Reason |
|---|---|
| 3 questions maximum per round | Beyond that, the user skims and validates without reading. |
| 2 to 4 options, mutually exclusive | Overlapping options produce an answer nobody knows how to read. |
| Short options — 2 to 6 words | They are read on a narrow screen, sometimes on a phone. |
| An "other / let me explain" option where it helps | An escape hatch avoids forcing a wrong choice. |
| Short, direct wording | The question is about the project, not about the method. |

Ask the question **only the user** can answer. What can be read in the code is read in the code: asking about what is already visible spends attention that belongs to the real uncertainties.

## Special cases

**No uncertainty at all** (rare). Offer a simple validation anyway: "Here is what I am about to write in X — shall I go ahead?"

**"Your call" / "you decide".** Make a reasonable default choice, **state it explicitly**, and move on. Do not ask again: the user has just delegated, handing the decision back is an answer beside the point.

**Multi-select.** When the options are not exclusive (enabling several blocks, keeping several invariants), say so in the prompt and provide "all" and "none". "None" is a legitimate answer: it ends the skill cleanly, with no negotiation.

**An answer outside the options.** A user who answers beside the question is still answering: take their answer literally, not the closest option.

## Forbidden

- **Writing a structuring file without asking first.** Even when the answer looks obvious.
- **Hardcoding a tool name.** See above.
- **Chaining rounds without producing anything.** A question exists to unblock a piece of writing; three rounds in a row with nothing written mean the skill is questioning instead of moving forward.
- **Rephrasing a question already settled.** A validated decision holds for the lifetime of the skill.
