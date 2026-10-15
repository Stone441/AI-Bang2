# Requested information and grounded gap explanations · local v3 candidate

## Problem and resulting behavior

The fourth real run's partial question contained a true, cited statement that no release date was confirmed. v2 inferred `supported` from nonempty claims, so both generator and reviewer accepted the wrong completeness category. That failed result remains unchanged in compact-wire-results.json.

The v3 candidate represents the distinction explicitly. A part has `resolution:answered` or `resolution:unavailable`. An unavailable part may carry exact-cited explanations of its gap. The server places those claims in `gap_claim_indices` and keeps `status:insufficient`; `claim_indices` remain empty. An answered part must contain answer claims and cannot contain gap claims. All claims must be assigned exactly once, with the same quote, identifier, current-permission and version checks.

Independent review now supplies an explicit completeness verdict for every part, even for legacy generation formats. Review disagreement with the draft rejects the entire draft; no automatic relabeling, filtering or JSON repair occurs. Missing, malformed, duplicate, extra-field or unknown verdicts reject. Existing global coverage, premise, conflict and claim support checks remain mandatory. The model name changes to `deepseek-flash-grounded-synthesis-by-part-v3`.

The UI keeps the partial/insufficient state while displaying the grounded gap explanation and citation button. History and audit render the same claims after existing authorization checks. Existing three-field historical parts remain readable; the legacy insufficient-with-answer-indices error remains invalid. No question-string or fixture-ID logic enters runtime classification.

## Evidence and limits

- Full regression: 780 Python tests pass in 59.217s (value-completeness-tests.log). The final prompt wording adjustment also passed 33 sectioned/challenge tests. Existing ResourceWarning and intentional negative-fixture output remain in the log.
- 27 sectioned-model tests pass, including new gap citation/history/revocation, independent completeness disagreement, old-wire bypass denial, malformed per-part verdicts, invalid gap mappings and forged gap quotations.
- 14 frontend DOM suites pass. Partial and wholly unavailable answers retain their correct labels even with cited gap explanations.
- Chrome fixture/mock observation: submitted the authored multipart sample, saw Partial answer and the cited unavailable date, opened its original source drawer, closed with Escape, and reopened historical answer after access checks. Screenshot: value-gap-mock.png. This is authored mock output, not real model quality or human acceptance.
- Initial full regression failed 12 challenge subcases because their authored mock reviewer responses lacked the new mandatory fields. The old log is preserved; updated only mock protocol payloads, retaining original claims, rubrics and assertions. These protocol fixtures do not establish semantic accuracy.

## Remaining uncertainty and rollback

Neither typed resolution nor a granular reviewer proves correct semantic judgment. The reviewer may still agree with a wrong classification, and extra required fields may increase output failure. No new live model/provider/source operation is authorized or performed here; all four previous grants remain closed. Do not reopen the paid loop under this local change. Goal remains incomplete until actual quality meets the frozen business oracle under an independently authorized direction.

Local rollback is the parent candidate 64266a0 (runtime b21f953), which has a known failed real business gate and is not an accepted release. No production switch occurred. New gap-bearing records require v3 for display; any future deployment rollback must preserve the candidate index/audit separately as already required by DEPLOYMENT_AND_DEMO.md. No database migration is needed for the additive JSON field.
