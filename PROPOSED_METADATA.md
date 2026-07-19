# Proposed GitHub Repository Metadata

This repo's GitHub-side settings (description, topics, homepage) are configured
in the GitHub UI, not in git. Below are proposed values for a maintainer to
apply under Settings > General (description/homepage) and the gear icon next
to "About" on the repo page (topics).

## Description

Deterministic orchestration primitives for AI agent workflows: a PLAN, SPEC,
and EXECUTE pipeline that gives Claude Code (or any coding agent) durable,
file-based state to resume work across sessions.

## Topics

- claude-code
- ai-agents
- agentic-workflows
- python
- cli

## Homepage

Leave unset, or point it at this repo's GitHub URL.

pyproject.toml names the package `orchestrator-toolkit` and lists PyPI upload
prep docs (PACKAGE_SUMMARY.md, PYPI_UPLOAD_GUIDE.md), but checking the PyPI
JSON API (`https://pypi.org/pypi/orchestrator-toolkit/json`) on 2026-07-19
returns `{"message": "Not Found"}`. No package named `orchestrator-toolkit`
(or close variants) is published on PyPI. Only a TestPyPI upload was
prepared, which does not count as a public homepage. Do not set the
homepage to a PyPI URL until the package is actually published there.
