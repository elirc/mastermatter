# User Story Build Path

This suite is a progressive ticket ladder. Each story is a realistic feature or product improvement grounded in Mattermost's channel, post, sidebar, notification, and access-control domain. It is independent from the other documentation suites.

How to use these stories:

1. Pick the next story in order.
2. Read the likely files and line ranges before editing.
3. Write your own implementation plan in a scratch note.
4. Implement in the smallest coherent slice.
5. Run focused checks for the area you touched.
6. Review your own diff using the acceptance criteria.

Difficulty progression:

- Stories 1-3 are easy UI changes touching one or two files.
- Stories 4-5 add UI behavior from existing data across a few files.
- Stories 6-7 add a new endpoint or new state path.
- Stories 8-9 are full-stack and include persistence.
- Story 10 is expert-level and asks you to design around caching/security/performance.

A story is done when every acceptance criterion is independently verifiable, the UI behavior works in the relevant channel state, TypeScript/Go contracts still line up, and focused tests or manual verification cover the main path. Frontend scripts live in `webapp/channels/package.json:172-180`; server run and test targets live in `server/Makefile:481-529` and `server/Makefile:602-690`.

Use AI to get unstuck without outsourcing the work. Prompt:

```text
I'm working on Story X. I'm stuck on Y. Here is what I've tried: Z.
Don't give me the solution. Ask me questions that help me figure it out.
Use the relevant Mattermost files and line ranges if you need to point me somewhere.
```

