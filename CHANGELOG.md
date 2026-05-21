# Changelog

All notable changes to this plugin are documented here. The plugin uses an
explicit `version` in `plugin.json`, so users receive updates only when that
field is bumped.

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
