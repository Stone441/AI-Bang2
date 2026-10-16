# Homepage context and first-query experience · 16 October 2026

User requested explicit Singapore/Tencent event identification, removal of member initial circles and the secondary how-it-works jump, clearer question entry/example interactions, fewer disclosure arrows and appropriate budget messaging. Follow-up requests Aspire and Tencent logos/context.

The homepage now names 腾讯云 AI CAN DO IT 新加坡黑客松 2026 and introduces the Aspire Internal Brain challenge. Logos identify Tencent Cloud as a hackathon co-host (with AI Singapore) and Aspire as FinTech challenge provider. Member cards retain full names without initials. The main workspace CTA remains; the secondary jump is removed.

Official sources checked:
- https://tch.tencentcloud.com/contest/44 confirms event name, co-hosts and Aspire challenge.
- https://aspireapp.com/en-sg/ provides https://cdn.aspireapp.com/brand/v2/aspire-logo.svg
- The official competition site header provides https://staticintl.cloudcachetci.com/yehe/backend-news/VYt5270_qc-topnav-logo.svg
- Both SVGs are local same-origin copies with original colours, rendered on white. No remote tracking or relaxed content policy is needed.

The composer has a distinct bordered input, label/help and visible focus. Example cards explicitly say Use this question and show selected state; clicking fills/focuses the input and announces the result without submitting. Native disclosure semantics remain keyboard-accessible; triangle markers are replaced by restrained context-specific controls.

Normal admission is visually quiet; usage counts and precise trial dollars are omitted from the user-facing banner. Paused admission still disables submission and explains available next steps. Backend budgets, call limits and unknown-usage safeguards are unchanged. Tests now assert hidden healthy status, visible paused status and disabled submission rather than obsolete budget prose.

Validation: frontend reviewer login/admission, refresh/recovery, sectioned answer rendering and history tests pass; 9 HTTP tests pass. Desktop and 390px mobile browser inspected; example click verified filled text, input focus, live feedback and empty answer area. No horizontal overflow. No paid/live-model query. Deployment retains sectioned-synthesis and existing account/permission/budget configuration.
