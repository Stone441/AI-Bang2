# Quote support versus source-wide review

The dd99b3b live case established a real semantic review miss: selected quote omitted provenance qualifiers even though the full source contained them. Existing reviewer instructions required full-source inspection and whole-claim support but did not sharply separate the support basis from the coverage/contradiction basis.

The shared sectioned generation/review contract now explicitly requires each claim to follow from its own selected quote union, without importing uncited source/title/context facts. Full-source inspection remains mandatory for missing qualifications, contradictions, premises and coverage. Provenance is permitted when requested or necessary to disambiguate/limit the answer, not added merely to display an extra source. No wire schema, parser, acceptance gate, source access or budget logic changed; no post-hoc removal or automatic retry was added.

fixtures/sectioned_quote_scope.json preserves the actual failure and two contrasting cases: properly requested/quoted provenance and misleading short approval quote with an omitted pilot limitation. Expected booleans are human-authored semantic oracle, not observed model judgments; these cases are derived from known failures, not blind data.

85 related tests passed in1.458s. The new boundary test verifies full sources and original selected supports both remain in reviewer input, and either an unsupported or unresponsive verdict rejects the whole draft. It deliberately does not pretend to evaluate model semantics. Two initial test setup errors (date argument type and invalid short dummy key) were fixed; their logs remain alongside the passing log.

Real effect remains unverified. Latest paid run remains the closed dd99b3b failure, and human trialfa88f2f stays untouched. This local prompt refinement cannot establish that the model will now reject the known case or pass all11 questions. No fresh paid grant was created.
