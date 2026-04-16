# Contributing

Thanks for improving `task-handoff`.

## What Good Contributions Look Like

We especially welcome contributions that improve:

- handoff clarity
- prompt structure
- support for more task types
- examples that improve actionability
- better fact-boundary labeling (`confirmed / unverified / pending`)

## Before You Open a PR

Please make sure your change keeps the core design intact:

1. Optimize for the next executor, not for full historical replay
2. Keep prompts concise and directly reusable
3. Preserve exact paths, branches, IDs, service names, and commands when relevant
4. Clearly separate completed work from recommended next steps
5. Avoid adding generic filler text

## Suggested Contribution Areas

- Better templates for bug handoff
- Better templates for multi-worktree continuation
- Remote ops / acceptance handoff refinements
- English wording improvements
- Chinese wording improvements
- Real-world example prompts

## Pull Requests

When submitting a PR, please include:

- what problem you observed
- what you changed
- a short before/after example if wording changed

## Security

Please do **not** report vulnerabilities publicly in issues.
See [SECURITY.md](SECURITY.md).
