# Block C — Automated doc-gardening

Loaded by `codebase-harness` only if this block was retained in the scoping multiple-choice question (step 2). The other blocks live in the neighbouring `block-*.md` files.

---

## 6.0 — What this block automates, and what it cannot

Doc-gardening does two things of a different nature:

| | Nature | Needs |
|---|---|---|
| **Running the checks** and collecting the violations | Deterministic | A scheduler. That is all. |
| **Interpreting the drift** — an invariant gone stale, an orphan test-case, documentation that no longer describes the code | Judgement | An agent. |

The first part runs anywhere. The second assumes the host knows how to schedule an agent run — which not all of them do.

**By default, ship the first one only.** A weekly mechanical report beats an interpretation that never runs. The second is added if, and only if, the host allows it.

## 6.1 — Cadence

The agent proposes the cadences through a multiple-choice question (see `clarify-with-choices`):

| Cadence | Cron | Use case |
|---------|------|-------------|
| Daily | `0 9 * * *` | Active project, plenty of contributions |
| Weekly (default) | `0 9 * * 1` | Project under normal development |
| Twice a month | `0 9 1,15 * *` | Project in maintenance |
| Monthly | `0 9 1 * *` | Stable project |

## 6.2 — Scheduler: choosing the host

The agent detects what the project has available and proposes **a single** host, in this order of preference:

| Host | Condition | Why this rank |
|---|---|---|
| **Scheduled GitHub Actions** | `.github/` present | Versioned with the code, visible to the team, no secret required |
| **Scheduled GitLab pipeline** | `.gitlab-ci.yml` present | Same; the schedule is configured under *CI/CD → Schedules* |
| **The host agent's scheduler** | The host exposes a scheduled-task mechanism | The only host able to add interpretation (see 6.4) |
| **Local cron** | None of the above | Fallback. Runs only on the machine it was set up on — say so to the user. |

Never install two of them: two reports for the same drift is noise, and noise ends up ignored.

## 6.3 — Mechanical report (portable, the default)

The job runs every script in `tools/harness/` and aggregates their output. They honor the common contract (`--explain`, `--root`, codes 0/1/2), so the aggregation knows nothing about any individual script.

```yaml
# .github/workflows/doc-gardening.yml
name: doc-gardening

on:
  schedule:
    - cron: '0 9 * * 1'   # the cadence retained in the multiple-choice question
  workflow_dispatch:       # manual trigger, to test without waiting

permissions:
  contents: read
  issues: write

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run the harness checks
        id: checks
        run: |
          : > report.md
          for script in tools/harness/*; do
            [ -x "$script" ] || continue
            output=$("$script" --root . 2>&1) || true
            [ -n "$output" ] && printf '## %s\n\n```\n%s\n```\n\n' "$(basename "$script")" "$output" >> report.md
          done
          if [ -s report.md ]; then echo "drift=yes" >> "$GITHUB_OUTPUT"; fi

      # Silence means OK. No issue is opened when everything is green.
      - name: Reporting
        if: steps.checks.outputs.drift == 'yes'
        run: gh issue create --title "Doc-gardening — drift detected" --body-file report.md
        env:
          GH_TOKEN: ${{ github.token }}
```

For GitLab, the same script body in a job whose rule is `if: $CI_PIPELINE_SOURCE == "schedule"`, the schedule itself being defined under *CI/CD → Schedules*.

**Show the file to the user and ask permission before writing it**, as with the other blocks. The issue title and anything else the job says out loud are written in the target project's language.

## 6.4 — Interpretation (optional, depends on the host)

If the host exposes a scheduler able to launch an agent, additionally propose a scheduled task carrying this prompt:

```
Run the codebase-harness skill again in update mode on the project [path].
Do not change any file automatically — produce a consolidated report only:
new invariant violations, stale invariants, drifted test-cases
(covered_broken, or a new test with no test-case), mutation score
regression against the baseline and new surviving mutants, documentation
that may have drifted. If everything is green, say so and send nothing
else. Write the report in the language of the project.
```

The name of the scheduling tool varies from one agent to the next: do not hard-code it, use whichever one the host exposes. If the host exposes none, **do not fake it** — say so, and stick to the mechanical report of 6.3.

Show the prompt and the cadence, **ask for permission explicitly**, and create the task only once confirmed.

## 6.5 — Guardrails

The task must NEVER apply changes without a multiple-choice question, even when it runs with no human at the keyboard. Its job is to produce a signal, not a fix.

If the report is empty (everything green), it produces no message at all — **silence means OK**. A "nothing to report" report sent every week teaches the team to stop opening it.

---
