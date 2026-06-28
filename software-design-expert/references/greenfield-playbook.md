# Greenfield playbook (new project / feature / service)

For designing something new. The governing rule: **start deep and simple, and keep reversible
decisions cheap.** Greenfield failures rarely come from too little structure up front; they come
from too much speculative structure, an incoherent core, or a domain nobody named precisely.

## Step 1 — Frame it strategically, then size the design effort

- State the actual problem and the one or two requirements that will dominate the design (latency?
  data volume? change frequency? team size?). Design for those; do not gold-plate the rest.
- Decide how reversible each major decision is. Spend up-front design effort only on the expensive-
  to-reverse ones (data model, public API shape, service boundaries, persistence choice). Make the
  cheap-to-reverse ones quickly and late (internal class layout, libraries, naming) — you can change
  them once you know more. (YAGNI + reversibility)

## Step 2 — Name the domain (ubiquitous language)

Before drawing modules, agree on the vocabulary of the problem with whoever owns the domain. Use
exactly those words in code, tests, and conversation. Where the same word means two different things
in two parts of the system, that is the signal for a **bounded context** — split there and translate
explicitly at the boundary. Most tangled systems are tangled because two different concepts shared a
name. (DDD)

## Step 3 — Design it twice

For the core shape (the main module boundaries, the key data model), sketch two genuinely different
designs, not one design and a strawman. Compare them on: how simple is each module's interface, how
much does each hide, what changes are cheap vs expensive under each. The comparison routinely exposes
a flaw in your first instinct. (Ousterhout)

## Step 4 — Draw deep modules and point dependencies inward

- Cut modules so each hides a substantial decision behind a small interface (deep, not shallow). Ask
  of each: "what does a caller have to know to use this?" Minimize that.
- Put the domain/business logic at the center, free of frameworks, database, and I/O. Let the outer
  rings (web, persistence, external services) depend inward on the core, never the reverse, so the
  core stays testable and the volatile edges stay swappable. (Clean Architecture)
- Isolate every external dependency (vendor SDK, third-party API, message broker) behind an interface
  you own, so it can be faked in tests and replaced later. (POODR)

## Step 5 — Build a walking skeleton first

Implement the thinnest possible slice that runs end-to-end through the real architecture — one
request from entry point to storage and back — before fleshing out features. This proves the
integration, surfaces the hard problems early, and gives you a working system to grow rather than a
big-bang integration at the end. (Tracer bullets / walking skeleton)

## Step 6 — Grow it under tests, keep complexity out

- Add features as thin slices on the skeleton, each tested. Tests are part of the design: code that
  is hard to test is usually badly coupled — let the difficulty push you toward better seams.
- Resist premature abstraction. Wait for the third real occurrence before extracting a shared
  abstraction; prefer a little duplication over guessing at the wrong one. (Rule of three; Metz)
- Reach for a design pattern only when you actually have the problem it solves. Don't pre-install
  patterns to look robust.
- Keep conceptual integrity: a newcomer should be able to hold the system's shape in their head. If
  the mental model is fracturing, stop and reconcile it before adding more. (Brooks)

## Step 7 — Make errors rare by design

Shape interfaces so the common case is the easy case and as many error conditions as possible simply
can't arise (idempotent operations, sensible defaults, total functions). Every error path you design
away is complexity removed from every caller. (Ousterhout)

## Anti-patterns to watch for in new code

- **Speculative generality:** layers, config, and plugin points for futures no one has asked for.
- **Framework-first design:** letting the framework's folder structure dictate the domain instead of
  the other way around ("screaming architecture" — the structure should announce the domain, not the
  framework).
- **Second-system effect:** over-engineering the rebuild of something you've done before, larding it
  with every feature the first version lacked. (Brooks)
- **Distributed-by-default:** splitting into many services before you have a reason; network
  boundaries are the most expensive coupling to add and the hardest to remove. Start with a
  well-modularized single deployable; extract a service only when a real force (scaling, team
  ownership, independent release) demands it.

## Sequencing rule of thumb

```
frame problem + rank reversibility
   -> name the domain (ubiquitous language, bounded contexts)
      -> design it twice; pick deep module boundaries
         -> domain core inward, volatile edges outward
            -> walking skeleton end-to-end
               -> grow under tests, defer abstraction, protect conceptual integrity
```

## What to deliver to the user

A short design brief: the dominating requirements, the module/context boundaries and why they fall
where they do, which decisions you deliberately deferred (and how to reverse them cheaply later), and
the walking-skeleton slice to build first. Lead with the decisions, not the diagram.
