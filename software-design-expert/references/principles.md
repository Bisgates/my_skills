# Principles library

The distilled, de-duplicated principle set behind this skill. Grouped by the problem each group
solves. Each entry names its primary source so you can trace and trust the lineage, and states *why*
it matters so you can apply it with judgment instead of by rote.

## Table of contents
1. Managing complexity (the core)
2. Modules, interfaces, and abstraction
3. Dependencies and coupling
4. Errors and edge cases
5. Change, refactoring, and legacy
6. Naming, comments, and readability
7. New-system design and process
8. Genuine disputes (resolve with judgment)

---

## 1. Managing complexity (the core)

- **Complexity is the lifetime cost, not an aesthetic.** It is whatever makes the system hard to
  understand or change. Its symptoms: change amplification (one change forces many edits), high
  cognitive load (you must know too much to make a change), and unknown unknowns (you can't tell
  what to change). Its causes reduce to two: dependencies and obscurity. (*A Philosophy of Software
  Design*, Ousterhout)
- **Complexity is incremental; it accrues like debt.** No single decision dooms a system; a thousand
  small "good enough for now" choices do. So fight it continuously, and spend a steady fraction of
  effort (Ousterhout suggests ~10–20%) on design improvement rather than saving it for a cleanup
  that never comes. This is *strategic* programming; the opposite, just-make-it-work, is *tactical*
  programming and it compounds against you. (Ousterhout)
- **Essential vs accidental complexity.** Some complexity is inherent to the problem and cannot be
  removed by any tool, language, or pattern; the rest is accidental and is yours to eliminate.
  Distrust silver-bullet claims. (*The Mythical Man-Month* / "No Silver Bullet", Brooks)

## 2. Modules, interfaces, and abstraction

- **Deep modules over shallow ones.** A module's value is the functionality it hides relative to the
  interface it exposes. Deep = small interface, large hidden implementation (e.g. Unix file I/O:
  `open/read/write/close/lseek` over an ocean of buffering, scheduling, permissions). Shallow = the
  interface is nearly as complex as the implementation; a class that just forwards calls adds
  interface cost while hiding nothing. (Ousterhout)
- **Information hiding.** Each module should encapsulate a design decision so that decision lives in
  exactly one place. The reverse — *information leakage* — is the same decision baked into several
  modules; it is the most common avoidable source of dependency. (Parnas; Ousterhout)
- **Pull complexity downward.** Given a choice, make the implementation absorb complexity so the
  interface stays simple. The module has one author and many users; let the one suffer. (Ousterhout)
- **Different layer, different abstraction.** Adjacent layers should offer different abstractions. A
  method that passes its arguments straight through to another method of the same signature (a
  *pass-through*) signals a layer that isn't pulling its weight. (Ousterhout)
- **General-purpose tends to be deeper than special-purpose.** Slightly general interfaces are often
  simpler *and* more reusable than a pile of narrow ones. But don't over-generalize speculatively —
  generality that no caller needs is just unused surface area. (Ousterhout, tempered by YAGNI)
- **Program to an interface, not an implementation; favor composition over inheritance; encapsulate
  what varies.** The three foundational moves behind most design patterns. They all isolate the
  parts likely to change. (*Design Patterns*, GoF)
- **Patterns are vocabulary, not goals.** Use a pattern when you already have the problem it solves.
  Applying patterns to look sophisticated ("pattern-itis") creates the complexity you meant to
  avoid. (GoF, as commonly mis-applied)

## 3. Dependencies and coupling

- **The Dependency Rule.** Source-code dependencies should point toward higher-level, more-stable
  policy. The domain/business core should not depend on the database, the web framework, or the UI;
  those should depend on it. Keep the core testable in isolation. (*Clean Architecture*, Martin)
- **Depend on things less likely to change than you are.** Inject dependencies; depend on
  abstractions; isolate the volatile parts (external services, formats, vendors) behind seams you
  control. (*POODR*, Metz)
- **Orthogonality / decoupling.** Independent components let you change one thing without disturbing
  others. Coupling is what turns a one-line change into a week. (*The Pragmatic Programmer*)
- **Bounded contexts.** In a large domain, the same word means different things in different parts.
  Draw a boundary where the language changes; inside each boundary keep one consistent model, and
  translate explicitly at the seams. (*Domain-Driven Design*, Evans)

## 4. Errors and edge cases

- **Define errors out of existence.** The cheapest exception is the one that can't happen. Redesign
  interfaces so the error case becomes a normal case (e.g. a delete that is idempotent rather than
  throwing if the item is gone). Fewer error paths = less complexity everywhere. (Ousterhout)
- **When errors must exist, reduce where they're handled.** Mask them low, aggregate handling high,
  rather than forcing every caller to cope. (Ousterhout)
- **Design by contract / fail fast.** State preconditions and invariants; crash early and loudly on
  a violated invariant rather than limping on with corrupt state. (*The Pragmatic Programmer*)

## 5. Change, refactoring, and legacy

- **Make the change easy, then make the easy change.** Refactor to create room for the feature
  *first*; then the feature is small. (Kent Beck)
- **Two hats.** Separate "adding behavior" from "refactoring structure"; never do both in one edit.
  (Fowler)
- **Refactor under a green test bar, in small steps.** Each step preserves behavior and keeps tests
  passing. The discipline is what makes large restructurings safe. (*Refactoring*, Fowler)
- **Legacy code is code without tests.** Before changing untested code, pin its current behavior with
  characterization tests; find *seams* (places to substitute behavior without editing in place) to
  break dependencies; add new code via *sprout* (new method/class) or *wrap* rather than surgery on
  the tangle. (*Working Effectively with Legacy Code*, Feathers)
- **Don't rewrite a working system wholesale.** A rewrite discards hard-won edge-case knowledge and
  reliably ships late; strangle the old system incrementally instead. (Industry consensus; Fowler's
  "Strangler Fig")
- **Rule of three.** Duplicate once freely; on the third occurrence, consider abstracting. Abstracting
  on the first hint guesses at a pattern you haven't seen yet. (Fowler)
- **Don't live with broken windows.** Fix small visible decay promptly; tolerated rot signals that
  rot is acceptable and accelerates it. (*The Pragmatic Programmer*)

## 6. Naming, comments, and readability

- **Names are design.** A name that needs a comment to explain it is a design smell. Precise,
  consistent, intuitive names cut cognitive load more than almost anything else. (Clean Code;
  Ousterhout)
- **Comment the non-obvious; write key comments first.** Code states *what*; comments must carry the
  *why*, the invariants, the units, and the rejected alternatives — things code cannot express.
  Writing the interface comment before the code is a design check: if it's hard to describe simply,
  the design is probably too complex. Delete comments that merely restate code. (Ousterhout)
- **Code is obvious or it isn't.** If a reader has to pause and reconstruct intent, the obscurity is
  a defect, not their failing. Optimize for the next reader. (Ousterhout)

## 7. New-system design and process

- **Conceptual integrity above feature count.** A system that reflects one coherent set of ideas is
  easier to use and extend than one with more features but no unifying model. Concentrate the core
  design in few hands. (Brooks)
- **Walking skeleton / tracer bullets.** Build the thinnest possible end-to-end slice that runs in
  the real architecture first; flesh it out once the path is proven. Beats big up-front design that
  meets reality late. (*The Pragmatic Programmer*)
- **Good-enough software, on purpose.** Engineer quality to the requirement, not to perfection;
  make the trade-offs explicit and let stakeholders weigh in. (*The Pragmatic Programmer*)
- **Software engineering is programming integrated over time.** Code lives for years across many
  hands; design for the people who will maintain it, invest in tests and readability, and plan for
  deprecation and change. ("If you liked it you shoulda put a test on it.") (*Software Engineering
  at Google*)

## 8. Genuine disputes (resolve with judgment, per codebase)

- **Function length.** Clean Code: very small functions. Ousterhout: over-decomposition scatters
  logic and breeds pass-throughs. Resolution: minimize a reader's total cognitive load; a longer
  cohesive function can beat five fragments that must be read together.
- **Comment density.** "Self-documenting code" advocates vs Ousterhout's "comments capture what code
  can't". Resolution: no comments that restate code; yes to comments carrying intent/invariants.
- **Inheritance.** Classical OO leans on it; POODR and GoF both warn it couples tightly. Resolution:
  prefer composition; use inheritance only for genuine is-a with stable hierarchies.
- **Abstraction timing.** DRY pressure vs "wrong abstraction is worse than duplication" (Metz).
  Resolution: rule of three; de-duplicate knowledge, tolerate coincidental similarity.
