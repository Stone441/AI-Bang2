# Premise explanation contract · candidate, not yet live validated

An optional `explained` source-review model extends structured-v2's one-call selection with `premise_status` and `premise_sources` (passage aliases). Existing structured-v2 and its frozen evidence remain unchanged.

Statuses: `not_applicable` (no material assumed assertion to assess), `supported`, `not_established` (the selected current evidence does not establish an assumed assertion), `contradicted` (selected evidence explicitly establishes an incompatible state). Missing approval is not rejection; absence is not contradiction. Unknown global latest ordering alone uses the existing chronology notice. Mixed or ambiguous premises use `not_established`, not a blanket contradiction.

No new model-authored factual prose is accepted. The application renders fixed explanatory wording with the exact original question and retained source quotations. Non-applicable requires zero premise sources; other statuses require nonempty, unique aliases that are all retained by the original selection. IDs/quotes, safety, coverage, required actions, actual settled review receipt and final authorization checks remain mandatory. The assessment and supporting evidence IDs are included in the final response and audit; History uses the same current checks.

This is a fallible semantic model judgment, not an independent fact verifier or access grant. Only the exact trusted explained model class may supply this metadata to Engine. Unknown/malformed statuses or unsupported aliases reject the output without a paid retry. No question-ID or keyword-specific answer mapping is used.

Acceptance: reject malformed/missing metadata, alias not selected, duplicate aliases, absence labelled as an arbitrary new status, unsafe/incomplete original selections; preserve one call, retained exact source quotes, final authorization, audit, History. Live cases must distinguish withdrawn/accepted facts from unsupported rejection, plus ordinary Q1/Q2 behavior. Do not adopt this candidate based on mock tests alone.
