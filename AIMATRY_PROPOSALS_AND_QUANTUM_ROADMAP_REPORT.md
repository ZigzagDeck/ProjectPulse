# AIMATRY Capability, Research-Proposal, and Quantum-Computing Roadmap

## Executive summary

AIMATRY has moved beyond a visual concept into a functioning computational research prototype. According to the supplied presentation, it can accept fibre and formulation choices, estimate multiple textile properties with simplified physics, rank or optimize candidate designs, ingest laboratory sheets, store experimental records, recommend informative follow-up experiments, screen molecular candidates, and export technical dossiers. These are meaningful software capabilities. They do not yet demonstrate that the predicted textile performance is accurate in the physical world.

The project's central gap is therefore not another dashboard feature or a more complex algorithm. It is a traceable, statistically defensible measured-data loop. AIMATRY needs laboratory measurements linked to specimen identity, preparation history, test method, instrument, environmental conditions, raw values, derived values, model version, and uncertainty. The presentation correctly frames the next milestone as measured calibration rather than broader product or compliance claims.

The three proposals are complementary, but they should not start simultaneously:

1. **Proposal 1 - Aramid thermal-comfort calibration** should be the first programme. It creates the common data schema, laboratory workflow, validation method, uncertainty reporting, and active-learning loop needed by everything else.
2. **Proposal 2 - Wash-durability modelling** should follow as a longitudinal extension of calibrated baseline fabrics. It answers whether initially promising fabrics retain performance after use-related conditioning.
3. **Proposal 3 - Coating add-on trade-off** should follow after coating chemistry, preparation, curing, adhesion, and environmental controls are defined. It is the most natural extension of AIMATRY's current multi-objective optimization capability, but it has more uncontrolled process variables.

Quantum computing can provide a research edge in two places: constrained selection from a very large formulation or experiment space, and electronic-structure calculations for shortlisted coating or monomer chemistry. It is not justified for the current 12-combination aramid pilot, three-to-four-fabric wash study, or three-to-four-level coating study. Those spaces are small enough for classical design of experiments, Bayesian optimization, Gaussian processes, mixed-effects models, NSGA-II, integer programming, or exhaustive evaluation. AIMATRY should build a quantum-ready benchmark layer now, but should claim quantum advantage only if a controlled comparison later demonstrates better solution quality, time-to-solution, sample efficiency, or cost than strong classical baselines.

---

## 1. Scope and evidence basis

This report interprets the first three research proposals in the supplied AIMATRY presentation:

- Proposal 1: aramid thermal-comfort calibration.
- Proposal 2: wash-durability model for protective fabrics.
- Proposal 3: coating add-on versus protection and comfort.

The current capability assessment is based on statements in that presentation. The underlying AIMATRY source code, database, tests, model artefacts, and exported dossiers were not supplied in the current workspace and were therefore not independently audited for this report. Phrases such as "implemented" and "available" mean "reported as implemented in the presentation," not independently validated laboratory performance.

The presentation itself makes an important distinction:

- **Implemented and demonstrable:** interactive formulation workflows, deterministic physics calculations, TOPSIS, inverse search, NSGA-II, lab-sheet ingestion, database storage, random-forest and Gaussian-process pipelines, RDKit structure checks, and dossier export.
- **Not established:** accuracy against physical fabric tests, generalization across fibres and constructions, certified compliance, reliable economic/environmental performance, a proprietary experimental dataset, and a production deployment at NITRA or in industry.

This boundary should remain visible in every proposal, demonstration, model card, publication, and stakeholder discussion.

---

## 2. What AIMATRY is currently capable of

### 2.1 Formulation and design-space definition

AIMATRY can reportedly represent candidate textile formulations using variables such as:

- fibre identity and blend ratio;
- fabric mass or GSM;
- weave architecture;
- finish or coating-related attributes;
- user-defined target specifications;
- curated use-case scenarios.

The presentation identifies 12 fibre records and supports both curated and user-defined formulations. This makes the platform a structured pre-screening environment: it can turn an informal material concept into a machine-readable candidate and pass it through repeatable calculations and decision rules.

### 2.2 Simplified physics-based estimation

The current computation layer reportedly combines rule-of-mixtures calculations, simplified transport equations, and weave-related adjustments to estimate:

- density;
- tensile properties;
- limiting oxygen index (LOI);
- thermal resistance (Rct);
- evaporative resistance (Ret);
- total heat loss (THL);
- cost indicators;
- environmental indicators.

This layer is valuable for early screening because it imposes structure and consistency before physical samples are manufactured. However, its output is a model estimate, not evidence of protection, comfort, durability, certification, or field performance. Its coefficients and correction factors require calibration against traceable measurements.

### 2.3 Multi-criteria decision support and optimization

AIMATRY reportedly provides three distinct decision mechanisms:

1. **TOPSIS** ranks a predefined set of candidates according to stakeholder-weighted criteria.
2. **NSGA-II** searches for Pareto-optimal compromises among competing goals such as protection, comfort, strength, cost, and manufacturability.
3. **Inverse design** begins with a target specification and searches backward for candidate blend ratios and GSM values.

These mechanisms support different questions. TOPSIS answers "Which of these known candidates best fits the chosen priorities?" NSGA-II answers "Which non-dominated trade-offs exist in a broader model-derived design space?" Inverse design answers "What formulation might achieve this target?" None of them proves physical performance unless the forward model has been calibrated and validated.

### 2.4 Laboratory-data and measured-learning infrastructure

The presentation reports the following building blocks:

- CSV and Excel import;
- SQLite persistence;
- correction factors for THL, LOI, and tensile predictions;
- random-forest and Gaussian-process pipelines;
- Gaussian-process recommendations for the next informative experiment;
- a fabricate-test-update-select cycle.

This means the software can support an active-learning loop in principle. Its present database, however, contains demonstration records rather than verified NITRA measurements. The immediate objective is to make the loop scientifically operational by adding approved protocols, specimen-level provenance, quality checks, replicate handling, uncertainty propagation, and held-out validation.

### 2.5 Molecular and chemical pre-screening

The presentation reports rule-based scaffold combinations, RDKit validity checks, descriptors, and similarity comparison against ten curated monomers. This module can help organize chemical candidate exploration and remove invalid or obviously unsuitable structures before deeper analysis.

The module should be described as chemical pre-screening, not toxicity clearance, synthesis validation, coating compatibility proof, or regulatory approval. Those require specialist review, reliable source data, and physical or accredited testing.

### 2.6 Standards-oriented pre-screening

AIMATRY reportedly checks candidates against six standards families at a simplified pre-screening level. This can identify which tests or thresholds may be relevant and can flag obvious gaps in a technical dossier. It cannot provide certification. Compliance claims require the exact edition of each standard, controlled specimen preparation, accredited testing where applicable, acceptance criteria, and authorized interpretation.

### 2.7 Research outputs and reporting

Current outputs reportedly include:

- ranked candidate formulations;
- estimated properties;
- pre-screening flags;
- trade-off or Pareto views;
- experiment recommendations;
- a downloadable technical dossier;
- machine-readable specification data;
- an optional language-model explanation with an offline scripted fallback.

These outputs make AIMATRY useful as a research coordination and decision-support instrument. Their credibility will ultimately depend on the provenance, calibration status, and uncertainty attached to each number.

---

## 3. How AIMATRY achieves these capabilities

### 3.1 End-to-end computational path

The current architecture can be understood as a seven-stage path:

1. **Design input:** the user chooses a curated scenario, target specification, or custom formulation.
2. **Feature construction:** fibre, blend, GSM, weave, finish, and other descriptors are converted into model inputs.
3. **Physics estimation:** deterministic equations produce baseline property estimates.
4. **Data-driven correction:** where data exist, correction factors or surrogate models adjust the simplified estimates.
5. **Decision layer:** TOPSIS, NSGA-II, or inverse design ranks or searches candidates.
6. **Research output:** the system presents predicted properties, uncertainty or flags, candidate rankings, and a technical dossier.
7. **Measured-learning loop:** laboratory results are imported, linked to a specimen, used to recalibrate the model, and used by active learning to select the next experiment.

Stages 1-6 are reported as operational in software. Stage 7 has software components but lacks the verified dataset and approved laboratory programme required for scientific validation.

### 3.2 Hybrid physics and data-driven modelling

The most appropriate technical identity for AIMATRY is a **hybrid physics-guided decision-support system**. Simplified physical relationships provide interpretable priors and enforce sensible trends. Data-driven models learn residual errors or more complex interactions after laboratory data become available.

A robust implementation should use the relationship:

```text
measured response = physics estimate + learned residual + measurement error
```

This is preferable to discarding the physics layer and training an opaque model on a small dataset. It allows the project to:

- remain useful before a large dataset exists;
- show which assumptions produced a prediction;
- learn correction factors from measurements;
- quantify epistemic and measurement uncertainty separately;
- detect when a new candidate is outside the calibrated domain.

### 3.3 Active-learning mechanism

The Gaussian-process component is suited to small experimental datasets because it can provide both a predicted response and a model uncertainty. A candidate experiment can be selected using an acquisition function such as expected improvement, upper confidence bound, probability of improvement, or integrated variance reduction.

For multi-response textile design, the acquisition function should also include:

- constraint satisfaction, such as minimum LOI or tensile strength;
- diversity, to avoid testing near-duplicate formulations;
- test cost and specimen availability;
- laboratory batch capacity;
- expected information gain across Rct, Ret, LOI, and tensile response.

### 3.4 Auditability required for scientific use

Every measurement should be traceable through a specimen identifier and immutable provenance chain:

```text
material lot -> yarn/fabric construction -> preparation -> conditioning ->
test method and standard edition -> instrument and calibration -> raw readings ->
quality-control decision -> derived response -> dataset version -> model version ->
prediction or recommendation
```

Raw measurements must remain separate from corrected, normalized, imputed, or model-derived values. A model result should always expose its training-dataset version, feature schema, hyperparameters, code commit, validation metrics, and boundary of use.

---

## 4. Shared foundation required before all three proposals

### 4.1 Governance and experimental ownership

Assign clear responsibilities:

- **Textile scientist:** scientific scope, factor ranges, physical interpretation, exclusion criteria.
- **Laboratory mentor:** preparation, conditioning, methods, instruments, replicates, quality control.
- **AIMATRY team:** schema, software, model code, provenance, validation, reporting.
- **Data steward:** identifiers, data dictionary, access, versioning, corrections, release approval.
- **Principal reviewer:** approves protocol deviations, model cards, external wording, and publication claims.

### 4.2 Common data model

Create linked tables or equivalent objects for:

- material and supplier lot;
- fibre and blend composition;
- yarn and fabric construction;
- GSM, thickness, weave, finish, and coating;
- specimen and parent fabric identifiers;
- preparation and conditioning history;
- wash or ageing exposure;
- coating chemistry, add-on, cure, and adhesion conditions;
- test method, standard edition, instrument, operator, timestamp, and environment;
- replicate-level raw readings;
- accepted/rejected result with reason;
- derived response and units;
- dataset release, model version, prediction, and uncertainty.

Use controlled vocabularies and explicit SI or declared conventional units. Never store an unqualified value such as `25` without a variable definition, unit, method, and specimen.

### 4.3 Data-quality controls

Before model training, enforce:

- required fields and unit validation;
- unique specimen and test identifiers;
- replicate completeness;
- physically plausible ranges;
- instrument calibration status;
- protocol-deviation flags;
- missingness reason codes;
- duplicate detection;
- raw-file checksums;
- reviewer sign-off.

### 4.4 Validation policy

Use a locked validation policy before examining results:

- Keep true hold-out samples untouched until final evaluation.
- Split by physical specimen, fabric lot, or batch, not by duplicated readings.
- Report MAE and RMSE for continuous responses and calibration coverage for uncertainty intervals.
- Compare against simple baselines: mean predictor, linear model, physics-only estimate, and nearest-neighbour formulation.
- Report confidence or prediction intervals and residual plots.
- Use bootstrap intervals when sample size is small.
- Document failure cases and out-of-domain inputs.
- Do not select the best model solely from training or cross-validation performance and then report that same score as final proof.

---

## 5. Proposal 1 - Aramid thermal-comfort calibration

### 5.1 Research objective

Determine how accurately blend ratio, GSM, and weave construction predict Rct, Ret, LOI, flame behaviour, and tensile response for a narrowly defined para-aramid/meta-aramid woven-fabric family.

### 5.2 Why this should be first

Proposal 1 has very high institutional fit and moderate pilot complexity in the presentation. More importantly, it creates the first defensible measured dataset and calibrates the exact response family already present in AIMATRY. It is the minimum viable scientific programme that can convert the prototype from model demonstration to validated decision support within a declared domain.

### 5.3 Experimental design

The illustrative design is three blend ratios x two GSM bands x two weave constructions, producing 12 design combinations before replicates. NITRA or the laboratory partner should finalize the exact levels.

Recommended additions:

- Include at least independent specimen replicates per design point, with the number set by expected test variance and resource constraints.
- Randomize test order where practical.
- Block by manufacturing or laboratory batch and record that block.
- Include repeated or reference-control specimens to estimate repeatability and drift.
- Reserve entire design points or independently manufactured specimens for hold-out evaluation.
- Predefine handling of failed tests, censoring, and outliers.

### 5.4 Response set

Minimum proposed responses:

- Rct;
- Ret;
- LOI;
- defined flame-behaviour outputs;
- tensile strength and elongation in declared directions;
- GSM and thickness as measured covariates.

If THL is calculated from measured comfort variables, store the raw inputs and formula version rather than only the derived THL value.

### 5.5 Modelling sequence

1. Fit and document a physics-only baseline.
2. Fit transparent statistical baselines, such as linear or response-surface models with interaction terms.
3. Fit a Gaussian-process residual model with uncertainty.
4. Fit random forest only as a comparison, with care because 12 design combinations are too small for unrestricted complexity.
5. Evaluate physics-only, statistical, hybrid, and machine-learning models on the same hold-out policy.
6. Use active learning only after the initial model passes data and uncertainty checks.
7. Select a small follow-up batch based on uncertainty and expected information gain.
8. Freeze a first dataset release and model card after follow-up testing.

### 5.6 Software changes

- Replace demonstration records with a versioned measured-data namespace while retaining demo data separately.
- Add specimen, batch, method, instrument, replicate, and source-file provenance.
- Add response-specific calibration objects instead of global undocumented correction factors.
- Add model registry, dataset version, training run, and validation-result tables.
- Add uncertainty intervals and domain-of-applicability flags to every prediction.
- Add a laboratory-review state before records become training-eligible.
- Add an experiment-selection screen that explains why each next coupon was recommended.

### 5.7 12-week execution plan

| Period | Work | Gate or output |
| --- | --- | --- |
| Weeks 1-2 | Confirm fabric family, factor levels, methods, sample size, schema, and acceptance criteria | Signed pilot protocol and data dictionary |
| Weeks 3-5 | Source or manufacture coupons, condition specimens, perform baseline tests | Traceable initial dataset with QC disposition |
| Weeks 6-7 | Clean data, calibrate physics, train transparent and GP models | Baseline comparison and provisional model card |
| Weeks 8-9 | Select and test a small active-learning follow-up batch | Measured information gain and updated model |
| Weeks 10-12 | Evaluate locked hold-out set, freeze dataset and code, write report | MAE/RMSE, uncertainty coverage, reproducible release |

### 5.8 Success criteria

- Traceable raw and derived test data.
- Predeclared hold-out MAE/RMSE for each response.
- Uncertainty intervals with measured empirical coverage.
- Performance compared with simple baselines and physics-only estimates.
- Repeatable code and a frozen dataset release.
- Model card stating fabric family, factor ranges, exclusions, and intended use.
- Quantified information gain or error reduction from the active-learning batch.
- No claim beyond the calibrated aramid family.

### 5.9 Principal risks and controls

| Risk | Control |
| --- | --- |
| Fibre sourcing or manufacture limits the 12-point matrix | Use a reduced, statistically balanced design approved by the textile scientist |
| Too few independent samples | Prioritize replication and hold-out integrity over model complexity |
| Batch effects dominate formulation effects | Randomize, block, and record batches; use hierarchical analysis |
| Multiple responses give conflicting recommendations | Use constraints and Pareto analysis instead of one opaque weighted score |
| Model extrapolates beyond tested ranges | Enforce domain-of-applicability warnings |

---

## 6. Proposal 2 - Wash-durability model for protective fabrics

### 6.1 Research objective

Identify which starting properties and construction or finish variables best predict retention of flame, comfort, dimensional, and mechanical performance after repeated laundering.

### 6.2 Dependency on Proposal 1

Proposal 2 should reuse the specimen identity, method, uncertainty, provenance, and model-registry infrastructure established in Proposal 1. At least one baseline fabric family should have repeatable initial measurements before ageing curves are modelled. Otherwise, the project will confound baseline measurement noise with true degradation.

### 6.3 Experimental design

The presentation proposes three or four defined fabrics or finishes measured at baseline and agreed intervals such as 5, 10, and 20 wash cycles.

Recommended structure:

- Define the laundering standard, machine, detergent, water chemistry, load, temperature, drying method, and conditioning procedure.
- Use matched specimens from the same fabric lot across intervals where destructive testing prevents repeated measurement on one specimen.
- Include an unwashed control stored and conditioned with the test set.
- Separate inherently flame-resistant fibres from flame-retardant finishes in analysis and claims.
- Record finish chemistry, application route, cure, add-on, and initial property values.
- Include replicates at each fabric x wash-interval point.
- Consider an intermediate early interval if preliminary data show nonlinear initial loss.

### 6.4 Measurements

- dimensional change;
- mass/GSM and thickness change;
- tensile response;
- LOI and/or defined flame-behaviour metrics;
- Rct and Ret;
- visual or microscopy-supported damage rating if standardized;
- optional chemical or surface measurements where finish loss is central.

### 6.5 Modelling approach

Model both absolute response and retention:

```text
retention at cycle c = response at cycle c / baseline response
```

Recommended methods:

- nonlinear or spline retention curves;
- mixed-effects models with fabric or lot as a random effect;
- monotonic Gaussian processes when domain knowledge supports non-increasing behaviour;
- survival or threshold-crossing analysis for the cycle at which a minimum requirement is no longer met;
- uncertainty bands that include specimen and measurement variability.

Do not force all properties to degrade monotonically if the measurement can initially improve due to shrinkage, consolidation, or conditioning. Encode monotonicity only where physically justified.

### 6.6 Software changes

- Add exposure-event and wash-cycle tables.
- Preserve one baseline parent fabric linked to all conditioned specimens.
- Add longitudinal plots with confidence bands.
- Add a retention-threshold alert and estimated cycle-to-threshold.
- Add a factor that distinguishes fibre-inherent performance from finish-dependent performance.
- Add protocol versioning so results from different laundering standards are never pooled silently.
- Add an ageing-module model card with valid cycle range and fabric-family scope.

### 6.7 Stage gates

| Gate | Required evidence |
| --- | --- |
| P2-G0: protocol ready | Approved laundering method, intervals, materials, and response set |
| P2-G1: baseline stable | Repeatability acceptable for baseline response measurements |
| P2-G2: degradation detectable | Signal across cycles exceeds measurement noise for at least one response |
| P2-G3: model validated | Held-out fabric or batch performance reported with uncertainty |
| P2-G4: operational module | Retention curves, warnings, provenance, and model card integrated |

### 6.8 Principal risks and controls

| Risk | Control |
| --- | --- |
| Finish loss and fibre behaviour are confounded | Stratify designs and include appropriate controls |
| Different standards or wash conditions are pooled | Treat protocol version as a first-class variable and block incompatible data |
| Destructive tests create pseudo-longitudinal data | Use matched specimens and hierarchical models |
| Too few cycle points for a reliable curve | Prefer a simple interpretable model and report uncertainty |
| A threshold warning is treated as certification | Label it as model-based screening pending accredited testing |

---

## 7. Proposal 3 - Coating add-on versus protection and comfort

### 7.1 Research objective

For one controlled base fabric, determine the coating add-on range that gives the best defensible trade-off between thermal or protective performance and physiological comfort while maintaining acceptable mechanical behaviour.

### 7.2 Why it should follow Proposal 1

Proposal 3 aligns strongly with AIMATRY's NSGA-II and Pareto-front capability, but coating performance depends on more than nominal add-on. Chemistry, solids content, viscosity, application route, wet pickup, cure time and temperature, adhesion, fabric structure, and ambient handling can all affect outcomes. The project needs the provenance and uncertainty discipline established in Proposal 1 before it adds this process complexity.

### 7.3 Experimental design

The presentation proposes one defined base fabric and three or four controlled coating add-on levels. Recommended controls are:

- one uncoated base control;
- three or four measured dry add-on levels;
- fixed coating formulation or explicitly designed chemistry factor;
- fixed application route and equipment settings;
- documented wet pickup, drying, cure profile, and conditioning;
- independent replicates across preparation batches;
- randomized test order;
- retained specimen for adhesion or failure analysis.

### 7.4 Measurements

- actual dry add-on, not only target add-on;
- thickness and GSM;
- thermal conductivity;
- DSC/TGA response where scientifically relevant;
- Rct and Ret;
- tensile or other agreed mechanical change;
- adhesion and coating integrity;
- defined flame or heat-transfer responses relevant to the intended safety question;
- optional air permeability and moisture-management response if comfort interpretation requires them.

### 7.5 Modelling and decision logic

1. Fit dose-response relationships against measured add-on.
2. Report uncertainty and batch effects.
3. Define hard safety and manufacturability constraints with the textile/coating expert.
4. Construct a Pareto front for protection, comfort, mechanical retention, and optionally cost or environmental indicators.
5. Use TOPSIS only after stakeholders agree on weights; preserve the unweighted Pareto set in the dossier.
6. Validate the selected region with an independently prepared batch.

The output should be a screened operating window, not a claim that one coating level is universally optimal.

### 7.6 Software changes

- Add coating formulation, chemistry, batch, process, cure, and measured-add-on entities.
- Add adhesion and integrity observations.
- Extend the optimization layer to support hard constraints and Pareto uncertainty.
- Allow users to distinguish nominal settings from measured post-process values.
- Add a process-window view that highlights calibrated, uncertain, and excluded regions.
- Connect RDKit candidates only as pre-screened chemistry hypotheses, with explicit source and hazard-review fields.

### 7.7 Stage gates

| Gate | Required evidence |
| --- | --- |
| P3-G0: process frozen | Base fabric, coating chemistry, application, cure, and handling approved |
| P3-G1: add-on controlled | Target versus measured add-on repeatability quantified |
| P3-G2: response characterized | Thermal, comfort, mechanical, and integrity measurements complete |
| P3-G3: Pareto region validated | Independent batch confirms the candidate operating window |
| P3-G4: screening module released | Constraints, uncertainty, provenance, and model card integrated |

### 7.8 Principal risks and controls

| Risk | Control |
| --- | --- |
| Nominal add-on does not equal retained dry add-on | Measure dry add-on for every specimen |
| Cure or adhesion drives performance more than add-on | Freeze or explicitly design process variables |
| Too many chemistry variables for the sample budget | Start with one chemistry and one base fabric |
| Comfort and protection have no single optimum | Preserve the Pareto front and define decision weights transparently |
| Chemical or environmental hazards are understated | Require expert safety review and source-backed handling data |

---

## 8. Integrated programme sequence

### Phase A - Research infrastructure, 4-6 weeks

- Finalize common schema and identifiers.
- Implement raw/derived separation, source traceability, and QC states.
- Add dataset and model versioning.
- Define validation and model-card templates.
- Agree NITRA or laboratory roles, data rights, and approval wording.

### Phase B - Proposal 1 pilot, 12 weeks

- Execute the aramid calibration study.
- Release dataset v1, calibrated models, hold-out results, and active-learning evidence.
- Decide whether accuracy and repeatability justify expansion.

### Phase C - Proposal 2 feasibility and pilot, approximately 12-20 weeks

- Select a small subset of calibrated or well-characterized fabrics.
- Run controlled wash intervals.
- Build retention curves and threshold-screening functions.

### Phase D - Proposal 3 feasibility and pilot, approximately 12-20 weeks

- Freeze one base fabric and coating process.
- Characterize add-on response.
- Validate a Pareto operating region.

### Phase E - Integrated decision support

- Combine baseline performance, durability, coating trade-offs, uncertainty, and cost.
- Prevent cross-study comparison where standards, methods, or domains differ.
- Publish a consolidated model card and technical dossier.

Proposal 2 and Proposal 3 can overlap only after Phase A is complete and laboratory capacity, specimen identity, protocol ownership, and analysis ownership are unambiguous.

---

## 9. Quantum computing: where it may provide an edge

### 9.1 Honest position

Quantum computing should not be presented as necessary for AIMATRY's first three pilots. Proposal 1 has only 12 nominal factor combinations before replication; Proposals 2 and 3 are also intentionally narrow. Classical enumeration and statistically designed experiments will be faster, cheaper, easier to validate, and easier to explain.

IBM describes QAOA as a hybrid quantum-classical method for combinatorial problems that can be written as a QUBO and mapped to a cost Hamiltonian. IBM also explicitly cautions that quantum machine learning is exploratory, that high-dimensional quantum feature spaces do not automatically yield advantage, and that it is unrealistic to expect speed-up for tasks that classical ML already solves well. These cautions fit AIMATRY's current small-data setting.

Quantum work becomes defensible only when AIMATRY has:

- a much larger discrete design space;
- clearly expressed constraints and objectives;
- a strong classical benchmark;
- reproducible measured data;
- a cost or quality bottleneck not already solved by existing methods.

### 9.2 Opportunity A - Constrained experiment and formulation selection

This is the most practical near-term quantum research track.

As AIMATRY expands across many fibres, blend increments, GSM bands, weaves, finishes, coating chemistries, add-on levels, cure schedules, wash intervals, suppliers, and test bundles, the number of possible experiments can grow combinatorially. The selection problem can be expressed using binary variables:

```text
x_i = 1 if candidate experiment i is selected, otherwise 0
```

A useful objective could maximize:

```text
expected information gain
+ design-space diversity
+ predicted Pareto improvement
- experiment cost
- lead time
- penalties for violating batch, material, or laboratory constraints
```

After suitable scaling, pairwise terms and penalties can form a QUBO for QAOA or quantum annealing. IBM's QAOA documentation provides the standard QUBO-to-Hamiltonian workflow, and its multi-objective tutorial demonstrates how objective weights can trace a Pareto front. A materials-design precedent also exists in quantum-annealing-assisted lattice optimization, where a surrogate model, active-learning loop, and quantum optimizer are combined.

**Potential edge:** better sampling of diverse, high-value experiment batches from an enormous constrained candidate pool.

**Current limitation:** the three proposed pilots are far below the scale where this is likely to beat classical mixed-integer optimization, constraint programming, Bayesian optimization, or greedy information-gain selection.

### 9.3 Opportunity B - Multi-objective formulation search

Proposal 3 can eventually create a large multi-objective optimization problem when multiple base fabrics, coating chemistries, add-ons, cure conditions, comfort responses, protection responses, mechanical constraints, cost, and environmental indicators are combined.

A quantum or quantum-inspired optimizer could sample candidate Pareto regions. The appropriate comparison is not "quantum result versus no result." It is:

- QAOA or quantum annealing;
- NSGA-II currently used by AIMATRY;
- exact or mixed-integer optimization where feasible;
- Bayesian multi-objective optimization;
- random and Latin-hypercube baselines.

**Potential edge:** diversity or quality of candidate solutions under complex discrete constraints.

**Required proof:** hypervolume, feasibility rate, best objective value, diversity, wall-clock time, QPU time, and total cost across repeated runs.

### 9.4 Opportunity C - Quantum chemistry for coating and monomer candidates

AIMATRY's RDKit module can generate or screen chemical structures, but RDKit descriptors do not calculate full electronic structure. Quantum chemistry is a longer-term opportunity for shortlisted molecules or coating components where electronic effects matter.

The VQE was introduced as a hybrid quantum-classical method and demonstrated on a small quantum-chemistry problem. IBM's current learning material shows the practical pattern: map a molecular Hamiltonian, optimize the circuit, execute through quantum primitives, and post-process the result. This makes VQE a relevant research interface for small active-space calculations, not a replacement today for classical DFT or established chemistry packages on industrial coating systems.

Possible future questions include:

- relative ground-state energies of small coating or monomer fragments;
- reaction or curing-path hypotheses in tightly reduced active spaces;
- electronic descriptors for adhesion or thermal stability models;
- comparison of shortlisted chemistries after classical pre-screening.

**Potential edge:** more accurate treatment of strongly correlated electronic structures when fault-tolerant quantum computing and suitable algorithms mature.

**Near-term action:** build a classical quantum-chemistry baseline first; use tiny molecules and active spaces to test reproducibility on simulators and available hardware; never infer bulk fabric performance directly from a molecular energy calculation.

### 9.5 Opportunity D - Quantum kernels for nonlinear surrogate modelling

Quantum kernels map classical features into a quantum feature space and then use the resulting kernel matrix in a classical learning algorithm. They can be tested on AIMATRY response prediction only after a sufficiently large, clean, independently split dataset exists.

For the proposed pilots, quantum kernels are low priority because:

- the dataset will be small;
- the features are classical and low-dimensional;
- Gaussian processes and classical kernels are naturally suited to small data;
- circuit noise and repeated kernel estimation add variance and cost;
- data encoding can remove an apparent computational advantage.

A defensible future experiment would compare a quantum kernel against linear, polynomial, RBF, Matérn-GP, random-forest, and physics-guided residual baselines using identical nested cross-validation and a locked external hold-out set.

**Potential edge:** a useful feature map for a specific nonlinear structure-property relationship.

**Required proof:** statistically significant and reproducible improvement in held-out prediction or calibration, including total training and inference cost. Do not use training accuracy or a simulator-only result as evidence of quantum advantage.

### 9.6 Opportunity E - Quantum amplitude estimation and simulation

Longer-term fault-tolerant algorithms may accelerate Monte Carlo-style uncertainty estimation or high-accuracy molecular simulation. These are not near-term implementation targets for AIMATRY. They should remain on a technology watchlist until hardware, error correction, input preparation, and end-to-end resource estimates show relevance to a defined bottleneck.

---

## 10. Quantum implementation roadmap

### Step 1 - Finish the classical scientific foundation

Complete Proposal 1 data provenance, calibration, hold-out validation, uncertainty, and model cards. Quantum algorithms cannot compensate for untraceable or biased measurements.

### Step 2 - Define one quantum-amenable bottleneck

Choose one explicit problem, preferably constrained experiment-batch selection. State the number of candidate experiments, binary variables, constraints, objective terms, and operational value.

### Step 3 - Establish strong classical baselines

Implement and tune:

- exhaustive search for small instances;
- mixed-integer programming or CP-SAT;
- greedy information gain;
- Bayesian optimization;
- NSGA-II for multi-objective cases.

Archive solver version, parameters, seeds, hardware, time, solution quality, and feasibility.

### Step 4 - Formulate the QUBO or Hamiltonian

Normalize objectives, encode hard constraints where possible, add penalties only when necessary, and verify that the ground-state solution of small instances matches the exact classical answer.

### Step 5 - Run simulator studies

Use small controlled instances to assess circuit depth, qubit count, penalty sensitivity, optimizer stability, and sampling requirements. Reject formulations that do not reproduce exact small-instance solutions.

### Step 6 - Execute a limited hardware benchmark

Run matched instances on an available QAOA or annealing platform. Record queue time separately from compute time, include repeated seeds or anneals, and retain raw measurement distributions.

### Step 7 - Compare end-to-end value

Evaluate:

- best feasible objective;
- Pareto hypervolume where applicable;
- feasibility rate;
- diversity of returned candidates;
- probability of finding the best-known solution;
- wall-clock and QPU time;
- monetary or credit cost;
- reproducibility across runs;
- downstream laboratory information gain.

### Step 8 - Apply a continuation gate

Continue quantum work only if it provides at least one demonstrated benefit on a meaningful instance:

- better feasible solution quality under a fixed budget;
- comparable quality with materially lower time or cost;
- higher diversity of valuable candidates;
- measurable improvement in information gained per laboratory test;
- access to a chemistry calculation not tractable at required accuracy classically.

Otherwise, keep the quantum module as a reproducible research benchmark and retain the classical production path.

### Step 9 - Integrate as an optional solver plug-in

Use a solver abstraction:

```text
candidate set + objectives + constraints
                 |
        solver interface
       /        |        \
classical   quantum    quantum-inspired
       \        |        /
      common evaluated result
```

The dashboard should show the solver, version, parameters, run time, cost, feasibility, objective values, and comparison baseline. A quantum result must pass the same scientific and operational review as a classical result.

### Step 10 - Review annually against hardware and evidence

Revisit qubit requirements, circuit depth, error rates, classical competitor performance, cloud cost, and scientific relevance. Do not place proposal delivery dates on a forecast of future fault-tolerant hardware.

---

## 11. Recommended architecture changes

### 11.1 Data layer

- Separate demonstration, raw laboratory, curated analytical, and released datasets.
- Add immutable source and transformation lineage.
- Add units, uncertainty, method edition, instrument, and QC metadata.
- Add study, batch, specimen, exposure, coating, and replicate entities.

### 11.2 Model layer

- Treat simplified physics as a versioned model.
- Implement residual learning rather than undocumented global correction.
- Provide a common estimator API for linear models, Gaussian processes, random forests, and future quantum kernels.
- Provide a common optimizer API for TOPSIS, NSGA-II, Bayesian optimization, integer programming, QAOA, and annealing.
- Add prediction intervals, applicability checks, and calibration diagnostics.

### 11.3 Workflow layer

- Add protocol approval and deviation states.
- Add training-eligibility review for measurements.
- Add experiment recommendation, scientific approval, fabrication, test, ingestion, and closure states.
- Prevent an algorithm from directly authorizing a compliance claim.

### 11.4 Interface layer

- Mark every output as demonstration, uncalibrated, calibrated, validated, or out of domain.
- Show the source dataset and model version beside each result.
- Explain the reason for each candidate recommendation.
- Show raw measurements before derived scores.
- Preserve the Pareto front instead of displaying only one winner.
- Add a quantum benchmark tab only after a reproducible classical baseline exists.

---

## 12. Decision matrix

| Workstream | Scientific value | Current readiness | Complexity | Recommended priority |
| --- | --- | --- | --- | --- |
| Shared provenance and validation foundation | Critical | Partial | Moderate | Start immediately |
| Proposal 1: aramid calibration | Very high | Highest | Moderate | First research pilot |
| Proposal 2: wash durability | High | Depends on stable baseline | Moderate and time-dependent | Second |
| Proposal 3: coating trade-off | Very high | Needs process controls | Moderate to high | Third |
| Quantum experiment selection benchmark | Exploratory | Not needed at pilot scale | Moderate | Parallel research after P1 baseline |
| Quantum kernel surrogate | Exploratory | Dataset not ready | Moderate to high | Defer |
| Quantum chemistry for coatings | Long-term strategic | Small-molecule benchmark only | High | Technology watch and scoped experiments |

---

## 13. Immediate 30-day action list

1. Hold a two-hour scoping session with the textile scientist and laboratory mentor.
2. Freeze the Proposal 1 research question and narrow fabric family.
3. Agree factor levels, response definitions, methods, standards editions, replicates, and hold-out policy.
4. Build the specimen-level data dictionary and identifier convention.
5. Separate demonstration records from future measured data.
6. Implement raw-value provenance and training-eligibility status.
7. Add dataset and model versioning.
8. Create the physics-only and simple statistical baselines before new data arrive.
9. Pre-register success metrics and failure criteria.
10. Cost and schedule the 12-week pilot.
11. Create a small synthetic QUBO notebook for experiment selection, clearly labelled as a benchmark rather than a production capability.
12. Agree external wording: no NITRA validation or compliance claim without written institutional approval.

---

## 14. Final recommendation

AIMATRY's strongest path is to become a calibrated, auditable research instrument for protective-textile pre-screening. The present software already contains many of the correct computational components, but credibility will come from measured data, disciplined validation, transparent uncertainty, and textile-expert control.

Proposal 1 should be funded and executed first as the foundation study. Proposal 2 should extend that foundation into performance retention. Proposal 3 should then use the same evidence infrastructure to identify a validated coating operating window through multi-objective analysis. Quantum computing should be developed as an optional benchmark and future capability, initially focused on large constrained experiment-selection problems and, later, carefully scoped molecular electronic-structure calculations. It should not be used as a substitute for laboratory evidence or as a marketing claim before measurable advantage is demonstrated.

---

## References

### Project source

1. AIMATRY, *A Roadmap from Computational Prototype to Laboratory Validation*, research discussion presentation, 2026. Supplied PDF, especially slides 1-18 and proposal slides 12-14.

### Quantum-computing sources

2. IBM Quantum, [Quantum approximate optimization algorithm](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm). Official documentation for QUBO mapping, cost Hamiltonians, and hybrid QAOA execution.
3. IBM Quantum, [Quantum approximate multi-objective optimization](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-multi-objective-optimization). Official tutorial on multi-objective QAOA and Pareto-front sampling.
4. IBM Quantum Learning, [Introduction to quantum machine learning](https://quantum.cloud.ibm.com/learning/en/courses/quantum-machine-learning/introduction). Official discussion of QML scope, data loading, and the absence of a general shortcut to advantage.
5. IBM Quantum, [Quantum kernel training](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-kernel-training). Official implementation pattern for training a quantum kernel.
6. Peruzzo, A. et al., [A variational eigenvalue solver on a photonic quantum processor](https://doi.org/10.1038/ncomms5213), *Nature Communications* 5, 4213 (2014). Original VQE demonstration.
7. IBM Quantum Learning, [Quantum chemistry with VQE](https://quantum.cloud.ibm.com/learning/en/courses/quantum-chem-with-vqe/index). Official VQE chemistry course and workflow.
8. Huang, H.-Y. et al., [Power of data in quantum machine learning](https://www.nature.com/articles/s41467-021-22539-9), *Nature Communications* 12, 2631 (2021). Analysis of when data and model choice limit or enable QML advantage.
9. [Quantum annealing-assisted lattice optimization](https://www.nature.com/articles/s41524-024-01505-1), *npj Computational Materials* (2024). A materials-design example combining a surrogate model, active learning, and quantum annealing.

