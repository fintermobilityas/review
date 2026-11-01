# review

The reusable review workflows of fintermobilityas. One file for each kind of review.

| File | What it does | Caller |
|---|---|---|
| `.github/workflows/claude-review.yml` | The Claude review of a pull request: five rounds at most, one summary comment with a head/findings marker, inline comments for each finding | `.github/workflows/claude-review.yml` in each repository |
| | *another kind of review goes here as another file* | |

## Why this repository is public

A public repository may call only a **public** reusable workflow. Several product repositories are public
(`mongomigrations.core`, `surge`, `mongo`), so the workflows they call must be readable from a public
repository. Keeping the files here means one copy of each review instead of a copy in every repository.

No secret lives in this repository. A review that needs one declares it under `on: workflow_call: secrets:`
and reads it from the caller, which passes that one organization secret by name. A caller never uses
`secrets: inherit`, which would hand every repository and organization secret to the called workflow.

## How a repository calls a review

The caller holds the event, the concurrency group and one `uses:` line, and nothing else. The `uses:` line
names a full commit SHA of this repository, never a branch or a tag, so a change here reaches a repository
through its normal reviewed pull request, or a direct default-branch rollout explicitly authorized by the user:

```yaml
jobs:
  review:
    uses: fintermobilityas/review/.github/workflows/claude-review.yml@<40-character commit SHA>
    permissions:
      contents: read
      pull-requests: write
      issues: write
      actions: read
      checks: read
      statuses: read
    # The called workflow reads ANTHROPIC_API_KEY, the organization secret.
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Changing a review

Open a pull request here. A merge changes no repository by itself: each caller runs the commit that its
`uses:` line names. To roll the change out, move each caller to the tested workflow commit through its normal pull request route,
or directly to its existing default branch when the user explicitly authorizes that delivery. Every caller names the same SHA once the rollout is done. The
policy that the review enforces stays in `docs/pull-requests.md` of `fintermobilityas/company`.

A review is tested by a pull request in a repository that calls it: the run must start, post one summary
comment that ends with the marker of that review, and set the status that the caller repository requires. The caller
runs on `pull_request_target`, so a pull request runs the caller of its base branch: the pull request that
moves the SHA still runs the old commit. Merge the move in one repository first, let the next review there
run the new commit, and move the other callers after it passes.

## What is not here

- The policy: `fintermobilityas/company`, `docs/pull-requests.md`.
- The repositories that call these workflows: each has its own caller file.
- The API keys: organization secrets, never written in this repository.

## Review acceptance and follow-up rounds

The first in-repository review starts automatically, including the allowed Upkeep and Dependabot bots.
Within an authorized PR task, the implementing agent may add `claude-review` after addressing findings
or adding missing evidence, up to five completed rounds. Evidence-only corrections can be reviewed on
the same head. A fork's first review still needs explicit maintainer authorization.

Bot approval is the latest genuine summary from a successful shared-workflow run naming the current
head with `findings=0`, with no unresolved feedback. A `COMMENTED` review can satisfy that contract;
a successful check without the matching zero-findings summary cannot. Required human approvals, CI,
smoke evidence and merge authorization remain separate. No Actions approval permission needs enabling.
New commits invalidate earlier-head summaries. Report a failed or missing review, or remaining findings
at the five-round cap; do not bypass the cap or treat failure as acceptance.

## Local verification

`python3 -m unittest discover -s tests -v` executes the workflow's own shell blocks with a file-backed
GitHub double. It covers rounds 1–5, refusal of round 6, label removal, stale heads, author-spoofed or
injected markers, conservative finding counts, API failures, bounded retry and failed/open-feedback gates.
It needs Python 3, Bash and jq; it contacts no GitHub API.

For an explicitly authorized live-model local check, run
`python3 tests/run_real_reviews.py /tmp/review-flow-evidence` with an authenticated Claude CLI.
It makes five read-only calls using the model configured in this workflow. Synthetic arithmetic heads
contain one concrete defect in each of rounds 1–4 and none in round 5. GitHub operations remain local,
and a sixth request is rejected before a model call. No git commit, push or remote comment is created.
This checks the model and local orchestration; a subsequent caller pilot checks GitHub Actions and
the actual inline-comment integration before a broad rollout.

On 2026-11-01, all 12 control checks passed, five real model calls returned finding counts
`1, 1, 1, 1, 0`, and round 6 was refused. The tested workflow commit was
`7a5ba7a3549f568252581dc9007d6fc5b8d6c361`; local execution took 45.82 seconds.
