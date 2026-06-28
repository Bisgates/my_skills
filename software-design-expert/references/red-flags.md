# Red-flag catalog (diagnosis -> meaning -> fix)

A field guide for reviewing code and architecture. Each entry: the observable signal, which root
cause it points to (dependency or obscurity — see SKILL.md), and the standard fix. When you cite a
flag in a review, name it and point at the specific location as evidence.

Use this catalog to *rank*, not just to list. A flag in hot, frequently-changed code matters far
more than the same flag in a stable corner nobody touches.

## Structural / module flags

| Flag | What it signals | Cause | Fix |
|---|---|---|---|
| Shallow module | Interface nearly as complex as the implementation; the wrapper hides nothing | obscurity (no real abstraction) | Merge it away, or deepen it so it hides real work behind a simpler interface |
| Information leakage | Same design decision (format, order, protocol) duplicated across modules | dependency | Encapsulate the decision in one module; others go through it |
| Temporal decomposition | Code structured by *order of execution* (read-then-process-then-write) instead of by knowledge, so each step half-knows the others | dependency | Re-cut modules around information hidden, not around time |
| Pass-through method | A method only forwards to another with essentially the same signature | obscurity (layer earns nothing) | Remove the layer, or give it a real, different abstraction |
| Overexposure | Using the API forces callers to learn rarely-used features first | obscurity | Make the common path simple; push the rare config out of the main interface |
| Conjoined methods | Two methods only understandable by reading both together | dependency | Re-draw the boundary so each is independently comprehensible |
| Special-general mixture | A general mechanism polluted with one special case's details | dependency | Lift the special case out to a caller; keep the general core clean |

## Dependency / architecture flags

| Flag | What it signals | Cause | Fix |
|---|---|---|---|
| Domain depends on framework/DB/UI | Business logic imports the web framework, ORM, or I/O directly | dependency (wrong direction) | Invert it: define an interface in the core, implement it in the outer layer |
| God object / class | One class knows and does everything | dependency + obscurity | Split by responsibility; extract collaborators |
| Feature envy | A method uses another object's data far more than its own | dependency | Move the method to the data it envies |
| Shotgun surgery | One conceptual change requires edits in many files | dependency (change amplification) | Consolidate the scattered knowledge into one module |
| Cyclic dependency | Modules A and B import each other | dependency | Extract the shared abstraction into a third module both depend on |
| Hidden global / singleton coupling | Components communicate through shared mutable global state | dependency (invisible) | Make the dependency explicit; inject it |

## Readability / obscurity flags

| Flag | What it signals | Cause | Fix |
|---|---|---|---|
| Name needs a comment to be understood | The name is wrong or the concept is muddy | obscurity | Rename to something precise and intuitive; if you can't, the design is unclear |
| Comment restates the code | Noise that will drift out of date | (none — it's clutter) | Delete it; if intent is missing, write the *why* instead |
| Vague/temporary name (`data`, `tmp`, `manager`, `do`, `handle`) | The author hadn't decided what it is | obscurity | Name the actual role/responsibility |
| Magic number/string | Meaning lives only in the author's head | obscurity | Name the constant; document the unit |
| Inconsistency (two ways to do the same thing) | Reader can't predict the system | obscurity | Pick one convention and apply it everywhere |

## Process / change flags

| Flag | What it signals | Cause | Fix |
|---|---|---|---|
| No tests around code you're about to change | Refactors can silently change behavior | risk | Write characterization tests first (see legacy-playbook.md) |
| Mixed refactor + feature in one diff | Un-reviewable, un-revertable change | risk | Split: one PR refactors, the next adds behavior |
| "We'll clean it up later" | Tactical debt with no payback plan | accruing complexity | Budget a steady design fraction now; later never comes |
| Premature abstraction / framework | Generality no caller needs yet | accidental complexity | Inline it until the third real use appears (rule of three) |
| Proposed big-bang rewrite | High chance of late, regressed delivery | risk | Propose an incremental strangler plan instead |

## How to weight what you find

For each flag, estimate **return on change = future cost removed / risk of the fix**.

- High return: hot path, high obscurity or change-amplification, cheap and well-tested fix -> do first.
- Low return: isolated, stable, low-traffic, risky to touch -> list under "leave alone for now".

A clean review ends with both a fix list *and* an explicit leave-alone list. Telling the user what
not to destabilize is part of the expertise.
