# Demo onboarding and query activity · 16 October 2026

User requested all-English event wording, explicit Team AI Bang2, compact member cards with mail icons, discoverable credentials, query auto-scroll/progress improvements and a scenario introduction. User explicitly authorized public sharing of the three existing demo accounts, shared history and allowance, then separately authorized the scoped auditor account.

## Delivery

- English event name and Team AI Bang2; compact member cards and email icons.
- Workspace explains the fictional payment-service / payment-retry scenario, four source roles, open-ended question directions and account-dependent evidence. This background does not enumerate restricted resources or reveal their content.
- Login page offers four shared demo identities with fill-then-sign-in and optional displayed credentials. README links to the current page. Passwords remain outside Git and are supplied through an explicitly enabled same-origin runtime endpoint. Startup validates each supplied password against the existing registry and limits the auditor to the three demo identities and payment-service scope. Registry, permissions, expiry and budget are not changed.
- Submitted queries scroll to the progress panel once; runtime polling does not steal scroll. Current stage, explanation, elapsed time and actual stage outcomes are displayed as a continuous timeline. No fabricated percentage, inferred completion or model draft is shown. Examples are hidden while a request is running.

## Checks

Frontend login/admission, refresh/recovery, saved-history stage states and sectioned rendering pass. Nine HTTP and ten reviewer-access tests pass. Public credential validation rejects mismatched passwords, expired accounts and expanded auditor scope. Short 1100×620 browser checked with an isolated 15-second delayed fake model: progress becomes visible after submission and actual reported stages update. No paid model question is used. Public login verification follows deployment; successful configuration is not full semantic acceptance.
