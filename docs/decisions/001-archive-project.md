# ADR-001: Archive starlette-flask

- **Date:** 2026-01-31
- **Status:** Accepted
- **Decision Makers:** Hasan Sezer Tasan (author)

## Context

`starlette-flask` is a Python library providing a Flask-compatible `SessionMiddleware` for Starlette/FastAPI applications. It enables session data sharing between Flask and FastAPI apps mounted together, solving a real problem during Flask-to-FastAPI migrations.

The project was created in 2023, published as v0.0.1, and has been inactive since. The core functionality is complete - it does exactly what it set out to do.

## Problem Statement

Should the project continue to be maintained, or should it be archived?

## Factors

### In Favor of Archiving

1. **Goal achieved.** The middleware works. The problem is solved and documented.
2. **Low maintenance burden, but nonzero.** Dependencies evolve. Starlette, Flask, and itsdangerous may introduce breaking changes. Maintaining compatibility requires ongoing effort for a project the author no longer actively uses.
3. **AI-generated code is now viable.** The middleware is ~100 lines of well-defined ASGI middleware. Given the problem description and Flask's signing internals, any modern coding agent can produce an equivalent implementation. A maintained package adds overhead without proportional value.
4. **Low adoption.** ~100 PyPI downloads/month, 2 GitHub dependents. Archiving has minimal community impact.
5. **The knowledge is more valuable than the package.** Understanding _why_ Flask and Starlette sessions are incompatible (different `itsdangerous` signing configurations, Starlette's eager re-signing) is more useful than a pip-installable dependency.

### Against Archiving

1. **Existing users.** The 2 dependent repositories and ~100 monthly downloaders would need to vendor the code or find alternatives.
2. **Discoverability.** A published PyPI package is easier to find than a README explanation.

## Decision

Archive the project on GitHub. Do not delete the PyPI package. Update the README to:

- Clearly state the project is archived and why
- Preserve the technical knowledge (the signing configuration details)
- Provide a self-contained code snippet so users can vendor the solution
- Link to related discussions and the inspiration project

## Consequences

- The PyPI package remains installable at v0.0.1 indefinitely
- No further releases or bug fixes
- The README becomes the primary artifact - a document explaining the problem, the solution, and the key technical insight
- Users needing this functionality can copy the ~100 lines of middleware or ask an AI to generate it from the documented specification

## Alternatives Rejected

### Convert to "whenwords-style" code-free library

Provide only a specification (SPEC.md), language-agnostic tests (tests.yaml), and an AI prompt (INSTALL.md). Rejected because the middleware is Python-specific and framework-specific - there is only one implementation target, making the abstraction unnecessary.

### Convert to blog post

Write the solution as educational content. Not rejected outright - the author may do this in the future. But the archived README with preserved knowledge serves a similar purpose with less effort.
