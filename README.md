# review

The reusable review workflows of fintermobilityas. One file for each kind of review.

| File | What it does | Caller |
|---|---|---|
| `.github/workflows/claude-review.yml` | The Claude review of a pull request: two rounds at most, one summary comment with a head/findings marker, inline comments for each finding | `.github/workflows/claude-review.yml` in each repository |
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
only through a reviewed pull request in that repository:

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
`uses:` line names. To roll the change out, open a pull request in each repository that calls the review and
move the SHA to the merge commit on `main`. Every caller names the same SHA once the rollout is done. The
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
