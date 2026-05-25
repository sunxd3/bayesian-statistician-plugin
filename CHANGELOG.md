# Changelog

Notable changes to this plugin. It is distributed via git without an explicit
`version` in `plugin.json`, so marketplace users receive each pushed commit as
an update; the milestones below summarize the significant changes.

## Unreleased

### Added
- `/bayesian-workflow:setup` command — one-time bootstrap for the Python
  environment (copies `shared_utils`, creates `pyproject.toml`, runs `uv sync`
  and `cmdstanpy.install_cmdstan`).
- `/bayesian-workflow:eda <data_path> [output_dir] [--focus=<area>]` command —
  run EDA standalone, without the full workflow pipeline. Wraps the
  `eda-analyst` subagent so it can be invoked directly by the user.
- `validation-protocol` skill — the shared two-step input-validation
  protocol used by every subagent (argument check, filesystem check,
  single-line `[EXCEPTION]` output on failure). Each agent's `Input
  Validation` section now declares only its specific args and filesystem
  checks, eliminating the boilerplate that had drifted across agents.
- `statistical-diagnostics` split into per-shape references
  (`references/{distribution,regression,time-series,count,missing-and-hierarchical}.md`).
  SKILL.md trimmed to a pointer index plus the thresholds table, so the
  EDA analyst preloads ~28 lines instead of ~119 and reads relevant
  references on demand.
- `statistical-diagnostics` renamed and expanded to `eda`. The new skill
  consolidates EDA process content (data semantics audit, data quality
  checks, timestamp handling, visualization, modeling handoff) with the
  existing diagnostic-test library under `references/process/` and
  `references/tests/`. `eda-analyst`'s body slimmed from ~179 lines to
  ~55: role, interface, 8-step procedure with pointers, and the agent's
  principles. The bulk of operational detail now lives in the skill and
  is read on demand.

### Changed
- Renamed plugin from `bayesian-statistician` to `bayesian-workflow` —
  matches the canonical name of the methodology (Gelman et al., 2020).
  Install command is now `/plugin install bayesian-workflow@sunxd3-plugins`.
- Renamed orchestrator skill `bayesian-workflow` to `run`. Invoke as
  `/bayesian-workflow:run`.
- `python-environment` skill trimmed to reference-only content
  (`shared_utils` API, script structure). Setup steps moved to the new
  `setup` command. The bundled `shared_utils/` library now lives at the
  plugin root and is referenced via `${CLAUDE_PLUGIN_ROOT}/shared_utils`.
- Consolidated Stan skills via progressive disclosure: `stan-coding`
  renamed to `stan`; `stan-ode-modeler` and `horseshoe-prior` folded in
  as `skills/stan/references/ode.md` and `skills/stan/references/horseshoe.md`.
  Subagent skill lists updated. Net: 12 modeling skills → 10, with the
  previously-orphaned ODE and horseshoe guides now discoverable from the
  umbrella `stan` skill.

## 0.2.0 — 2026-05-21

Full sync with the upstream `bayesian-statistician` agent.

### Added
- Six skills: `bayesian-model-diagnostics`, `bayesian-model-selection`,
  `generative-model-design`, `horseshoe-prior`, `inferencedata-handling`,
  `statistical-diagnostics`.
- `critique` agent — a single integrated review covering statistical health,
  domain validity, and framework appropriateness.

### Changed
- All 9 carried-over subagents (`eda-analyst`, `model-designer`, `model-fitter`,
  `model-refiner`, `model-selector`, `posterior-predictive-checker`,
  `prior-predictive-checker`, `recovery-checker`, `report-writer`) updated to
  upstream parity.
- `bayesian-workflow` orchestrator skill updated: structural-question-driven
  search loop, per-experiment/per-stage task pool, discovery-driven questions.
- `stan-coding`, `visual-predictive-checks`, `artifact-guidelines`,
  `convergence-diagnostics` skills updated to upstream parity.
- Bundled `shared_utils` replaced with the current package, which adds the
  `fit_and_summarize` / `FitResult` pipeline, `to_arviz_prior`, `NumpyEncoder`,
  and `cleanup_csv_files`.
- `python-environment` skill rewritten with a concrete, plugin-local setup
  flow (no sandbox-specific paths).
- `plugin.json` gains `$schema`, `displayName`, `keywords`, and `homepage`.

### Removed
- `model-critique` and `decision-auditor` agents — folded into `critique` and
  `model-selector` respectively.
- Plugin hooks — the skills already instruct `uv`-only execution.

## 0.1.0

- Initial release: orchestrator skill, subagents, and core Stan/ArviZ skills.
