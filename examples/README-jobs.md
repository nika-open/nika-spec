# Jobs · industry workflows, simplest → epic

> Complete, spec-correct workflows (the count lives in [`manifest.yaml`](manifest.yaml)) that answer one question per
> industry · **« what would MY Monday look like with this? »** Every
> file passes the same conformance gate as the foundation examples
> (`python conformance/runner.py all`) — schema + DAG cross-refs +
> stdlib surface. Together with the foundation set they exercise
> **every stdlib builtin** (verified by the conformance + coverage sweep).

The [foundation examples](README.md) teach the *language*
construct-by-construct. The jobs teach the *life* — real work, ordered
simplest → epic so a newcomer climbs from a 4-task starter to a
multi-agent swarm without ever leaving validated ground.

---

## The workflows

| File | Industry | The wow | Key constructs |
|---|---|---|---|
| [`standup-digest`](standup-digest.nika) | engineering | the standup note writes itself from real commits | parallel start · `nika:date` · exec→infer |
| [`meeting-actions`](meeting-actions.nika) | every office | transcript → tracker-ready typed action items | `infer.schema:` · input `default:` vs literal permit |
| [`price-watch`](price-watch.nika) | e-commerce / personal | a price alert with **zero** model calls | `extract:` jq · CEL `when:` · `egress:` **and** `net.http` |
| [`social-repurpose`](social-repurpose.nika) | marketing / creators | one post → thread + LinkedIn + newsletter, in parallel | diamond DAG · `with:` aliasing |
| [`og-images`](og-images.nika) | marketing / content | brief in → OG PNG + provenance manifest out, one task | `nika:image_generate` · dir-writing permit |
| [`image-fx-batch`](image-fx-batch.nika) | creators / media | a folder of photos → deterministic art, byte-identical forever | `nika:glob` · jq-derived paths · `nika:image_fx` ops chain |
| [`image-compose-sheet`](image-compose-sheet.nika) | creators / media | photos and their variants → one contact sheet, with no image program to install | `nika:image_fx` · `nika:image_compose` row + grid · `scale: fit` |
| [`release-notes`](release-notes.nika) | engineering / devrel | git log → typed notes → a CHANGELOG copy edited in place | `exec` `recover:` · `nika:edit` · gated notify |
| [`seo-content-brief`](seo-content-brief.nika) | SEO / content | a brief that beats the competitor's best page | chained fetch modes · `recover:` · CEL indexing |
| [`invoice-chaser`](invoice-chaser.nika) | finance / freelance | overdue reminders drafted · NOTHING sent without a yes | `nika:convert` · `nika:prompt` gate · `size()` |
| [`support-triage`](support-triage.nika) | customer support | the overnight queue triaged before coffee | schema-over-list · jq post-filter · `nika:uuid` |
| [`contract-guard`](contract-guard.nika) | legal / compliance | the contract **never leaves the machine** (local model) | `ollama/…` · `nika:validate` + `nika:assert` |
| [`etl-quarantine`](etl-quarantine.nika) | data engineering | bad batches degrade to quarantine · the pipeline lives | `on_error: { recover: … }` · `nika:validate` · jq group_by |
| [`model-bench`](model-bench.nika) | engineering / model selection | the same question, three local models, one MEASURED table | per-task `infer.model:` · `duration_ms` as data · jq fan-in |
| [`release-radar`](release-radar.nika) | devops / dependencies | only the NEW ships reach you — human-gated since it crosses the trifecta | `mode: feed` · state-file diff · RFC 6902 |
| [`csv-chart-report`](csv-chart-report.nika) | data → picture | paste the spreadsheet, get the slide — offline, deterministic | `nika:convert` · jq group_by · `nika:chart` |
| [`transcript-shownotes`](transcript-shownotes.nika) | podcasts / meetings | raw transcript → typed show-notes, ONE bounded infer | `infer.schema:` strict · typed→markdown |
| [`bookmark-triage`](bookmark-triage.nika) | personal / research | the bookmark pile triaged — dead links survive the batch | `mode: metadata` · resilient `for_each` · recover |
| [`competitor-radar`](competitor-radar.nika) | strategy / PMM | everything they shipped last week, one brief | `for_each` · `for_each.max_parallel` · retry · fan-in |
| [`localization-factory`](localization-factory.nika) | product / i18n | the whole docs tree translated, voice intact | chained fan-outs · jq `transpose` zip |
| [`config-drift-sentinel`](config-drift-sentinel.nika) | SRE / platform | only UNSANCTIONED prod drift wakes anyone | RFC 7396 merge + RFC 6902 diff · blake3 |
| [`pr-review-fanout`](pr-review-fanout.nika) | engineering | one read-only review agent **per changed file** | `for_each`+`agent:` swarm · default-deny tools |
| [`resume-screener`](resume-screener.nika) | HR / recruiting | one local-model rubric per candidate · PII stays home | `ollama/…` · `for_each` · schema enums · jq sort_by |
| [`programmatic-seo-pages`](programmatic-seo-pages.nika) | SEO / growth | a services × cities sheet becomes landing pages that ship only when the rules pass | `nika:convert` · `infer.schema:` fan · QA law in `const:` · `nika:glob` mirror |
| [`seo-site-audit`](seo-site-audit.nika) | SEO / growth | the monthly audit says what REGRESSED · only failing pages cost a model call | `mode: sitemap` · jq regex facts · `nika:json_diff` state · root gate |
| [`source-to-45-locales`](source-to-45-locales.nika) | product / i18n | one page, 45 locales, a translation memory · a rerun pays only for what changed | `nika:hash` memory · 45-way `for_each` · QA law · back-translation |
| [`subscription-renewal-radar`](subscription-renewal-radar.nika) | admin / finance | every renewal sorted keep / downgrade / cancel / negotiate, plus a calendar to import | `nika:decide` · `nika:date` windows · RFC 6902 + 7396 state · `.ics` in jq |
| [`deep-research-brief`](deep-research-brief.nika) | research / VC | plan → budgeted agent → thinking synthesis | plan-then-execute · budgets · `thinking:` |
| [`incident-war-room`](incident-war-room.nika) | SRE / on-call | the postmortem drafts itself — after recovery is PROVEN | `nika:wait` settle · assert · `after: {…: terminal}` always-pattern |
| [`ceo-monday-brief`](ceo-monday-brief.nika) | founders / execs | the Monday brief assembles itself — and the human decision sits at the ROOT of the lethal trifecta | 3-branch gather · root `nika:prompt` gate · capped synthesis |
| [`release-train`](release-train.nika) | devops / release | gates → human GO → hold until the window → ship · verify | `nika:wait until:` · `nika:date diff` · `nika:prompt` |
| [`inbox-triage`](inbox-triage.nika) | every office | the shared inbox sorted run after run · only new mail reaches the model | `nika:hash` + `nika:json_diff` state · cost assert · confirm gate before the send |
| [`receipt-ledger`](receipt-ledger.nika) | finance / small business | the month close · receipts typed, reconciled with the bank, a double charge becomes a refund claim | `infer.schema:` + `nika:validate` · reconciliation join in jq · `nika:chart` |
| [`lead-enrichment`](lead-enrichment.nika) | sales | inbound leads deduped, looked up and scored by const weights · only the qualified reach the CRM | `nika:hash` dedupe · `retry:` lookups · ICP law in jq · `formula_guard` CSV |
| [`feed-digest`](feed-digest.nika) | research / newsletters | topic feeds with stale and seen entries dropped, near duplicates folded, the best few kept | `nika:date` window · Jaccard in jq · token budget · keyed POST |
| [`docs-answer-desk`](docs-answer-desk.nika) | support / knowledge | chat with your docs, where every quote is searched for in the passage it cites | chunking in jq · zero-call abstain · `nika:grep` verification · `nika:json_merge_patch` log |
| [`comfyui-image-chain`](comfyui-image-chain.nika) | creative / local images | a brief → seeds → a local ComfyUI graph built as a value → a graded contact sheet | graph as a value · `retry.on_codes` poll · `nika:image_fx` · `nika:image_compose` |
| [`ci-failure-triage`](ci-failure-triage.nika) | engineering | a red CI board sorted by failure signature · rules first, a model only for the unknown | `group_by` signatures · `nika:decide` flake law · keyed POST behind a confirm gate |
| [`workflow-watchdog`](workflow-watchdog.nika) | operations | your automations watched · a page only when something is actually wrong, and only once | epoch math in jq · `nika:notify` branches · alert state with `nika:json_diff` |
| [`listing-link-audit`](listing-link-audit.nika) | growth / SEO | every public listing scored, and what REGRESSED since the last run · no model | `mode: raw` fan · jq regex · `nika:json_diff` state · root gate over a trifecta |
| [`qr-art-forge`](qr-art-forge.nika) | creators / marketing | a batch of art QR codes → the poster set, every export proven to scan | `exec:` qrscan as the judge · jq law · `nika:image_compose` + `nika:image_fx` |
| [`launch-campaign-forge`](launch-campaign-forge.nika) | marketing | one brief → typed copy per locale, tracked links, art QR codes, a hero image, one manifest | `run.access` ACP seat · `images.save` · credit budget assert · keyed POST |
| [`quote-compare-decide`](quote-compare-decide.nika) | procurement / operations | three supplier quotes compared by rules · a person picks · the order is sent once | extract then law · `nika:prompt` `mode: choice` · idempotency key + state |
| [`refund-chaser`](refund-chaser.nika) | admin / finance | the money owed back, chased on schedule · polite first, firmer after 30 days | root confirm gate · `nika:date` ages · keyed POST fan · `nika:json_merge_patch` register |

## Clone and run

Every T1 and T2 file runs from the repo root with **no arguments and no
setup**. Run them exactly as their `Run ·` header line says — paths resolve
from your working directory, not from the file's, so the repo root is the
contract:

```bash
nika check examples/csv-chart-report.nika --native-strict   # 0 findings, 0 hints
nika run   examples/csv-chart-report.nika                   # artifacts land in out/
rm -rf out                                                                    # back to clean
```

- **Fixtures are committed.** `fixtures/` holds the sample data these files
  read — a sales CSV, a dirty orders batch, a meeting transcript, two PNGs, a
  contract, a ticket queue, a changelog. A header with **no `Needs ·` line
  needs nothing**: clone, run, watch it work. A `Needs ·` line names the one
  effect that is genuinely external (a git repo, a network host, ollama seats).
- **Every write lands under `out/`.** Nothing in this corpus writes into your
  source tree, so `rm -rf out` always restores a clean checkout. Reads point
  at `fixtures/`; repoint the `const:` at your own data and move the matching
  `permits.fs.read` literal with it — `permits:` cannot interpolate
  (`NIKA-AUTH-007`), and that is the point: a boundary you can read is a
  boundary a reviewer can check.
- **The mock model by default, not offline.** Any `infer:` file rehearses with
  `--model mock/echo`: zero keys, no model call, deterministic. The mock
  replaces the model, not the network: a fetch step still reaches its host.
  A step that only READS the network (a fetch, a feed, a sitemap) carries an
  `on_error: { recover: … }` sample so the run stays green with no network
  at all; a recovery stands in for the RAW response, so the `extract:` jq
  bindings run over it unchanged.
- **An effect never recovers into a success.** A step that changes something
  elsewhere (a POST, a send, a notify) is not a read: a recovered task
  settles `success` with the recovery value as its output, so every step
  after it reads a send that never happened as done (measured on 0.125.0).
  Give an effect `on_error: { skip: true }`, which settles `skipped` and
  keeps the error at `tasks.<id>.error`, and let what follows test
  `tasks.<id>.status`. If it must recover, the value says it was not sent
  (`{ sent: false, … }`) and every later step tests that before it records
  anything as done.
- **Every job checks green — including `release-radar`.** It crosses the
  lethal trifecta (private read + feed ingress + state-file write), so it
  carries the canonical human gate (`after: {approve: success}` at the head
  of the flow · NEP-0002 v2.2) instead of shipping red. The always-red
  SEC-009 witness the conformance lane still needs lives beside the other
  conformance inputs at
  `conformance/envelope/trifecta-realized-flow-ungated.nika` — an
  attack shape stays an attack shape; a TEACHING page checks green.

## Conventions (same gate as the foundation set)

- `# SPDX-License-Identifier: Apache-2.0` header + schema hint line
- `ollama/qwen3.5:4b` is the showcase model: every file leads local,
  zero key, recorded-as-run. It is a THINKING model — the think block
  and the JSON both count against `max_tokens` (engine#428), so schema
  showcases carry ceilings sized for think + answer, never the answer
  alone. Cloud providers appear only as per-task overrides or swap
  hints, never as the envelope default. Where the
  data is sensitive the local model is the point: sovereignty is a
  feature, show it
- the network story, honestly: `nika check` needs zero network on every
  file, and any `infer:` showcase rehearses with `--model mock/echo`
  (deterministic, zero keys, no model call; a fetch step still reaches its
  host) — see **Clone and run** above. The `agent:`
  showcases (`pr-review-fanout` · `deep-research-brief`) are the
  exception — mock echoes text and never *calls* a tool, so the ReAct loop
  does zero rounds under it: exercising the agent needs a real tool-calling
  model (the pinned local `qwen3.5` qualifies). `launch-campaign-forge`
  does not rehearse at all: its Codex seat over ACP refuses
  `--model mock/echo` (NIKA-1801, exit 3), so `nika check` is its offline
  proof
- every file is a conformance input · `python conformance/runner.py all`
  MUST stay green · one verb per task · snake_case ids · every
  `${{ tasks.X }}` reference at the `with:` boundary (the binding IS the edge)
- these files are the **single source** for the YAML shown in the
  public docs (`nika-docs` examples pages) and the website use-cases
  explorer — projected, never hand-copied
  (`scripts/showcase-projector.py` · `--check` is the drift gate)

🦋 *The jobs pack · ordered simplest → epic · every stdlib builtin exercised across the example corpus · manifest = the contract.*
