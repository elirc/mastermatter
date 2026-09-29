# Architectural Cartographer

This suite is a top-down onboarding guide for Mattermost's core web and server code. It treats the product as a collaboration system where teams, channels, posts, permissions, plugins, and notifications move through one shared delivery pipeline. The codebase basis for that model is the repository README, which identifies Mattermost as a Go and React self-hosted collaboration platform backed by PostgreSQL (`README.md:1-3`).

Use the files in this order:

1. `00-reading-map.md` - build the first mental map before opening many files.
2. `01-junior-engineer.md` - learn setup, folders, entry points, components, routes, and beginner TypeScript.
3. `02-mid-level-engineer.md` - trace the message-posting path across UI, state, API, middleware, app logic, storage, and UI update.
4. `03-senior-engineer.md` - critique the architecture, security, performance, tests, and ownership risks.
5. `04-reference-suite.md` - keep this open during reviews, debugging, feature work, and interviews.

Every checkpoint includes questions and a "How to self-grade" section immediately after it. Do the questions first, then compare against the rubric. The line references are not decoration: they are the habit. When you explain the system, point to code.

