# Domain Assessment

Identify the scientific domain from the EDA report, experiment plan, and data. State it explicitly:

> **Domain identification**: [e.g., "Psychophysics — signal detection / classification under multisensory stimulation"]

If the domain is not recognizable (purely synthetic data, generic business metrics with no established domain theory), state "No strong domain conventions identified" and skip to framework questioning.

Read the Stan model file. Compare the code against both the Domain Context stated in the experiment plan AND your independent knowledge of the field. Flag discrepancies in either direction:

- The plan specified a domain component that the code omits → implementation regression.
- The plan itself missed a standard domain convention → plan blind spot.

Assess each dimension below. Be specific — cite the model's actual code and contrast it with what domain practice would dictate. Skip dimensions that are genuinely not applicable.

## Link function and response model

Is the functional form domain-standard? Examples of domain-canonical choices:

- Psychophysics: probit (cumulative normal) or Weibull for psychometric functions
- Dose-response: log-logistic or Hill equation
- Survival analysis: hazard-based models (Cox, Weibull, exponential)
- Population ecology: Lotka-Volterra, Beverton-Holt, Ricker
- Pharmacokinetics: compartmental models with first-order kinetics

A logistic link may work statistically but miss the theoretical foundation. State whether the model's choice is domain-standard, a defensible alternative, or a mismatch.

## Missing domain-standard model components

Most scientific domains have known structural components that competent domain modelers include as baseline expectations. Examples:

- Psychophysics: lapse rates (stimulus-independent error floor/ceiling), guessing rates for forced-choice
- Epidemiology: exposure offsets, reporting delays, age-period-cohort structure
- Ecology: detection probability, abundance vs occupancy, carrying capacity
- Pharmacology: saturation kinetics (Michaelis-Menten), receptor binding curves
- Cognitive science: contaminant processes (fast guesses, attentional lapses)

Identify missing components and explain why they matter (e.g., missing lapse rate forces the sigmoid to reach 0/1 asymptotes, inflating slope estimates).

## Parameterization and mechanistic interpretability

Does the parameterization map to scientifically meaningful quantities, or does it capture the right shape for the wrong reason?

- Are parameters interpretable as domain quantities (threshold, sensitivity, capacity, rate constant) or generic regression coefficients?
- Would a different parameterization preserve statistical fit while enabling domain-meaningful inference?
- Does the parameterization align with the analysis purpose?

## Predictor selection and causal structure

- Does the model use the scientifically causal variable, or a correlated proxy?
- Are there known confounds in this domain that the model does not control for?
- Is the direction of influence correct?

## Model structure and known domain phenomena

- Are there nonlinearities, saturation effects, or threshold effects known in this domain that the model assumes away with linearity?
- Are there known interaction patterns?
- Does the hierarchical structure respect the natural grouping?
