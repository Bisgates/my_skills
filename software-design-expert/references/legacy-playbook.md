# Legacy / messy-project playbook

For existing code that is tangled, under-tested, or risky to touch. The governing rule: **stabilize
before you reshape.** Most damage to legacy systems comes from confident refactoring of code whose
behavior nobody had actually pinned down.

This is a procedure, not a menu. Do the steps roughly in order.

## Step 0 — Resist the rewrite urge

The instinct on seeing a mess is "let's rewrite it clean." Don't, by default. A rewrite discards
years of embedded bug fixes and undocumented edge cases, takes far longer than estimated, and leaves
you with two systems to maintain during the (long) transition. Choose incremental improvement unless
the system genuinely cannot meet a hard new requirement *and* you can deliver the replacement in
shippable slices. Even then, strangle rather than replace (Step 6).

## Step 1 — Understand before you change

- Find the *change point*: the specific place new behavior is needed or the bug lives.
- Trace what depends on it and what it depends on. Note where it reaches global state, I/O, the
  clock, randomness, the network — those are the things that make it hard to test.
- Don't try to understand the whole system. Understand the neighborhood around the change point.

## Step 2 — Get behavior under test (characterization tests)

You usually can't trust untested legacy code, so pin down what it *currently* does — bugs and all —
before touching it. These are *characterization* tests: they document actual behavior, not intended
behavior.

- Pick the smallest unit you can call around the change point.
- Feed representative inputs, capture the actual outputs, and assert on them. If an output looks
  wrong, still capture it for now and flag it — the goal here is a safety net, not correctness.
- If the unit won't run in a test because of a hard dependency (DB, network, clock), proceed to
  Step 3 to create a seam.

This net is what lets every later step be verified. Without it you are editing blind.

## Step 3 — Break dependencies at seams

A *seam* is a place where you can change behavior without editing in place — by passing in a
collaborator, subclassing a method, or swapping an implementation. Use seams to replace the
hard-to-test dependency (real database, real HTTP, real time) with a controllable fake, so the code
becomes testable without rewriting it.

Common dependency-breaking moves (Feathers):
- **Extract and inject:** pull a hidden `new`/global into a parameter or constructor argument.
- **Subclass and override:** in languages that allow it, override the awkward method in a test
  subclass.
- **Wrap the dependency:** put a thin interface in front of the external thing and depend on the
  interface.

Make the dependency explicit and substitutable — that alone removes a large fraction of the
"untouchable" feeling.

## Step 4 — Add new behavior without entangling it

When adding to a messy area, avoid surgery inside the tangle. Prefer:
- **Sprout method / class:** write the new logic as a fresh, clean, tested method or class, and call
  into it from the old code with a one-line hook. The new code is born clean even though its host
  isn't.
- **Wrap method:** rename the old method, write a new one with the original name that calls the old
  plus the new behavior. Lets you add a step (logging, validation) without editing the original
  body.

This keeps the clean/dirty boundary visible and stops the mess from spreading into your new work.

## Step 5 — Refactor in small, green, single-hat steps

Now, and only now, improve structure:
- One hat at a time: this PR refactors *or* adds behavior, never both.
- After every small step, run the tests; keep the bar green; commit.
- Apply the highest return-on-change fixes from references/red-flags.md first: kill information
  leakage, deepen shallow modules near the change point, fix the worst names.
- Use the Boy Scout Rule: improve the file you're in; resist expanding scope to the whole repo.

## Step 6 — For large replacements, strangle don't rewrite

When a subsystem really must go, apply the Strangler Fig pattern:
1. Put a routing layer (facade, proxy, or feature flag) in front of the old subsystem.
2. Build the replacement for one slice of behavior; route just that slice to the new code.
3. Verify in production, expand slice by slice, shrinking the old system.
4. Delete the old code only when no traffic reaches it.

Every step ships and is reversible. You never have a months-long branch that has to land at once.

## Sequencing rule of thumb

```
understand the change point
   -> characterize current behavior with tests
      -> break dependencies at seams (to make tests possible)
         -> sprout/wrap new behavior in clean code
            -> refactor the neighborhood in small green steps
               -> (only if necessary) strangle the subsystem slice by slice
```

## What to tell the user at the end

Deliver: the change made, the safety net you added (which tests now exist), the small refactors you
did *and why*, and an explicit list of nearby messes you deliberately left alone with the reason
(stable / low-traffic / not worth the risk). The leave-alone list prevents the user from over-reaching.
