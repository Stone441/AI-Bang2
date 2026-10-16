# Demonstration entry and version boundaries

The local human trial is frozen at fa88f2f. On this Mac only, the modified launcher in the original AI-Bang2 directory routes to the semantic workspace private entry. The launcher included in a fresh source checkout uses the standard local deployment configuration; it is not a portable copy of that running trial.

For a credential-free reproduction, run `python3 -m scripts.reviewer_demo` from the extracted source directory. It binds loopback and uses synthetic fixtures with a fake model. Do not present its answers as live semantic synthesis.

Use the [seven-minute walkthrough](../2026-10-16-submission-closeout/DEMO.md) with these corrected entry boundaries. Saved answers must be labelled historical; opening them rechecks access but does not generate a new answer. The isolated quotation-review experiment remains opt-in and is not silently enabled in the human trial. No video is claimed.
