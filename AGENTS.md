# AGENTS.md

## Scope
This repository contains Windows-first Python GUI applications for CESU, Banque, and LBP workflows. The main entry points are [CESU.pyw](CESU.pyw) and [moulinette_LBP.pyw](moulinette_LBP.pyw).

## How To Work Here
- Prefer review comments that focus on concrete regressions, hidden dependencies, brittle browser selectors, and Windows-only path or process assumptions.
- Keep changes aligned with the existing split between framework code in [Monitor/](Monitor) and domain logic in [Cesu/](Cesu), [Banque/](Banque), and [LBP/](LBP).
- Treat [Monitor/core/monitor.py](Monitor/core/monitor.py) as the orchestration boundary for GUI/thread/queue behavior.
- Treat [Cesu/metier_CESU.py](Cesu/metier_CESU.py) and similar `metier_*` modules as the main business-logic surfaces when reviewing behavior.

## Review Checklist
- Check for missing dependencies and packaging gaps in [pyproject.toml](pyproject.toml); this project currently declares no runtime dependencies there.
- Watch for brittle Selenium or XPath-driven automation in the extraction modules, especially around site-specific selectors and timing assumptions.
- Verify thread, queue, and callback interactions carefully before approving changes in the monitor layer.
- Be alert to file-output side effects under [Cesu/Résultats/](Cesu/Résultats) and error dumps such as [ftrace.txt](ftrace.txt).
- Remember that validation is mostly manual here; the repo includes standalone scripts like [testChrome.py](testChrome.py) and [testGuiInput.py](testGuiInput.py) rather than a formal automated test suite.

## Documentation
Link to existing files instead of repeating their contents here. If a task needs deeper project context, point to the relevant source file first.