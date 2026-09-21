---
name: code-assimilation-quiz
description: Post-implementation assimilation quiz — a teaching code review run as multiple-choice questions, one at a time, so the developer takes ownership of the code the AI wrote. Use ONLY when the user explicitly asks for it, never automatically. Typical triggers — "run the live code review", "quiz me on what was implemented", "check that I understood the code", "multiple-choice questions on the diff", "help me assimilate what you coded", "teaching code review". Do not confuse with a standard code review (hunting for defects) — the goal here is the developer's learning, not criticism of the code.
---

# Live Code Review — Assimilation quiz

## Why this skill exists

When an AI implements code, the developer risks becoming a passive rubber
stamp: the code works, they merge it, but they could neither maintain it nor
defend it in review. This skill flips the dynamic: after an implementation,
the developer takes a multiple-choice quiz built on the real diff. The point
is not to trap them or to grade them, but to turn passive reading into active
recall — the most effective way to remember something and to spot your own
fuzzy areas.

Keep that goal in mind at every step: anything that humiliates, traps or
drowns the developer is counterproductive. Anything that makes them ask
themselves a real question about the code is productive.

## Why this skill matters more as agents write more

One objection comes up naturally: if the trend is to delegate implementation
to agents and read less and less code, what good is a quiz on code nobody
will read? The opposite is true, and it is worth knowing why.

Delegating without reading only works if mechanical constraints hem the agent
in: architecture invariants, shape thresholds, acceptance tests, mutation
testing. But **calibrating those constraints takes judgment that is only
acquired by having read a lot of code**. Knowing that a function is too big,
that a coupling will cost you later, that an edge case is missing — none of
that is learned from reading thresholds, it is learned from having seen the
damage.

Adopting "I don't read the code anymore" as a shortcut, without having built
that judgment first, is a very different bet, and a far riskier one, than the
same sentence coming from an experienced developer. The wording is the same;
what it covers is not.

This skill is one of the places where that judgment is forged. It is not
there to check the code — `premerge-review` handles that — but to make sure
the developer who will be steering agents tomorrow knows what they are
steering. That is also why it stays useful when everything is green: a diff
without a single defect is excellent learning material.

Practical consequence: when the developer says they already know the area
well, take them at their word and shorten the quiz. When they are discovering
a technique, a pattern or a part of the codebase, that is when the quiz pays
off most.

## Step 1 — Define the scope

The quiz is based on the **git diff**, not on your memory of the conversation
(which can diverge from what is actually on disk).

1. Look at uncommitted changes first: `git status`, then `git diff` and
   `git diff --staged`.
2. If nothing is uncommitted, look at the latest commits:
   `git log --oneline -10`, then the diff of the commits involved.
3. If the scope is ambiguous (several recent commits, mixed topics), ask the
   developer which one to cover before going further. A single question, with
   the options you identified.

Read the whole diff, and open the modified files when the diff alone is not
enough to understand the context (signatures being called, neighboring
classes). You cannot write good questions about code you have not actually
read.

## Step 2 — Calibrate the quiz

Number of questions, proportional to the size of the change:

| Diff size | Questions |
|---|---|
| Small (< ~50 lines, 1-2 files) | 3 |
| Medium (~50-300 lines) | 5 |
| Large (> 300 lines or many files) | 7 |

Announce the format to the developer before starting: how many questions,
and the fact that they come one at a time.

Ask the questions in the language the developer and the project use. This
skill talks to a human being, and this repository being written in English
does not make English the language of the quiz.

## Step 3 — Build the questions

Before asking the first question, build the complete list of questions in
your head (or in a reasoning block). That guarantees coverage of the three
axes and avoids redundancy.

The questions cover **three axes**, to be balanced across the whole quiz:

1. **The WHAT** — structure of the change: which files/modules are touched,
   where a given responsibility lives, what the call flow is.
2. **The WHY** — design choices: why this structure rather than an
   alternative, what problem the choice avoids, what trade-off it makes.
3. **Risks / edge cases** — what breaks if you pass a given input, which case
   is not covered, where the fragile spot is.

Quality rules for the questions:

- **Anchored in the real diff.** Every question must cite its anchor (file,
  function, even line). No general-knowledge question that could be answered
  without having seen the code.
- **4 options (A-D), exactly one correct.** The distractors must be
  *plausible* — typically the design alternatives genuinely on the table, or
  the likely confusions. An absurd distractor is an option handed over for
  free.
- **No trick wording.** The difficulty must come from understanding the
  code, never from a subtlety of phrasing or an insignificant memory detail
  (exact order of the parameters, precise name of a local variable).
- **The WHY wins when you have to choose.** If the question quota forces a
  trade-off, favor design and risk questions: those are the ones that make
  the developer able to maintain the code.

## Step 4 — Run the quiz, one question at a time

This is the cardinal rule of the skill: **one question per message, then wait
for the answer**. Never list several questions ahead of time, never move on
without an answer. Active recall only works if the developer commits to an
answer before seeing the correction.

Presentation format: the question, then the options as a **bullet list** (one
per line, more readable than a paragraph):

```
Question 2/5 — [axis: why]
In `OrderService.cancel()`, the refund is delegated to an asynchronous event
rather than called directly. Why?

- **A.** ...
- **B.** ...
- **C.** ...
- **D.** ...
```

The developer answers with the letter. Only use an interactive choice
mechanism (buttons, selection widget) **if it can display the full question
AND its four options in the same place**. A widget that shows nothing but
A/B/C/D buttons detached from the question makes the developer answer blind —
in that case, plain text is better.

**After a correct answer**: confirm briefly, and add in one or two sentences
the *why* of the right answer (confirmation on its own teaches nothing). Then
the next question.

**After a wrong answer**:

1. Give the right answer with a teaching explanation, pointing at the exact
   spot in the code (`file:function`) so that the developer can go and look.
2. **Note the notion that was missed.** Later in the quiz (not right away —
   leave at least one question in between), ask a **reworded** question on
   the same notion: different angle, different wording, different options. A
   re-question is a fresh test of the notion, not the same question recycled
   — otherwise you are testing short-term memory, not understanding.
3. Re-questions add to the initial quota (a 5-question quiz with 2 mistakes
   can grow to 7). Mention it naturally ("we'll come back to this").

Tone to hold: supportive and factual. A mistake from the developer is useful
information (a fuzzy area detected), never a failure. No condescension, and
no excessive praise either.

## Step 5 — Final wrap-up

At the end of the quiz, in conversation (no file to produce):

1. **Score**: x/n on the first try, plus the result of the re-questions.
2. **Breakdown by area**:
   - *Solid* — the notions answered correctly the first time.
   - *To revisit* — the notions that were missed, even the ones recovered on
     a re-question, each with its code pointer (`file:function`) for targeted
     rereading.
3. **A suggested next step** when relevant: for example "reread the
   try/except block in `retry.py` and ask yourself what happens if X" — an
   active reading instruction beats "reread the file".

Do not turn the wrap-up into a bureaucratic report: a few sentences per area
are enough.

## What this skill does not do

- It does not criticize the code and does not propose refactorings — it is
  not a quality review. If you spot a genuine problem in the diff while
  preparing the questions, raise it *after* the quiz, separately.
- It never triggers on its own. Even at the end of an implementation, you
  may at most *mention* that the skill exists if the context lends itself to
  it, never start the quiz without being asked.
