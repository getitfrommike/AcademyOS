# BUILD. DO. HAVE.™ — Milestone 1

## Included

- `/academy` Discovery Intake™ experience prefilled with the Thug Coding® example
- live intake completion progress
- `/api/knowledge-profile` server route
- strict structured-output schema for the Knowledge Engine™
- demo-mode results when no API key is configured
- live OpenAI Responses API mode when `OPENAI_API_KEY` is present
- Knowledge Profile, readiness assessment, Opportunity Map™, scoring, and direction selection
- landing-page actions connected to `/academy`
- public-facing AcademyOS wording removed from the landing-page entry points

## Run

1. Copy `.env.example` to `.env.local`.
2. Add `OPENAI_API_KEY` to enable live analysis. Leave it empty to use the built-in demonstration.
3. Run `npm install`.
4. Run `npm run dev`.
5. Open `http://localhost:3000/academy`.

## Verified

`npm run build` completed successfully with `/`, `/academy`, and `/api/knowledge-profile`.
