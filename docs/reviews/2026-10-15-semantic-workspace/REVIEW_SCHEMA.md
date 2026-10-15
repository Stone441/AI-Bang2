# Complete review schema follow-up · 2026-10-16

Local prompt inspection found the sectioned reviewer inherited a leading JSON example containing only question_covered, filtered_answer_complete and verdicts. The later paragraphs required parts_supported, premise_handled, conflicts_handled and part_verdicts. Although the prose extended the format, no complete example showed the actual required response.

The reviewer now overrides a shared output_instructions hook with one complete seven-field example, explicitly distinguishes claim versus part array cardinality, and documents the zero-claim case. Ordinary EvidenceReview keeps its exact previous prompt text. No parsing, acceptance, quote, permission or rejection rule changed.84 sectioned/synthesis/DeepSeek tests passed in1.496s. This is a proven prompt inconsistency correction, not a proven explanation of historical failures or a real quality pass.

No live calls were made. Prior closed grants remain closed. The current human trial was not modified. Next decisive evidence must come from an authorized new run using granular partition/reviewer diagnostics, followed by actual source/oracle assessment; repeated green fixture tests cannot establish model reliability.
