# Google Drive delegated pilot

## Actual coverage — 2026-10-05

The reader and loopback operator support exact allowlisted UTF-8 `text/plain` files in personal Drive. All current Drive results are **mock source HTTP / fake model**. No Google Cloud project, OAuth grant, token or real source read has been configured or verified. Do not run the live command until explicit source/scope authorization and verified mappings exist.

`brain/drive.py` checks `about.get` user `permissionId` and `me` before each read. It uses fixed Google endpoints, exact file IDs, an expected parent and selected metadata fields. Current native file read plus `capabilities.canDownload` is authoritative; it does not reconstruct group/domain/inherited permission lists locally. A readable parent never implies a readable file. Each file is separately checked. Native 403/404, trash or disabled download returns deny; timeout, 401/429, malformed metadata and unsupported objects return unknown. Both prevent usable model evidence.

A successful read validates native version, head revision, timezone-aware modified time, byte length and MD5 checksum, retrieves the current body, and rechecks metadata/access before returning it. MD5 is only the native transport consistency check; evidence also records SHA-256. The shared Engine then repeats current permission/content checks before model dispatch, answer delivery and history/citation/export. Current readable content does not authorize arbitrary historical revisions. Native version fits SQLite signed int64; the reader does not fetch old revisions.

Files moved outside their configured parent are unknown pending explicit remapping. This parent is an application scope boundary, not an inferred ACL. Google Docs/Sheets/Slides exports, PDF/OCR, shortcuts, shared drives, encrypted files and permission propagation matrices are unsupported / not_run. No list/search, files write, permission mutation or redirects are implemented. No pages/line numbers are invented: locator identifies the full text file and real head revision.

## Approved real setup; native acceptance pending

Prepare a competition-only folder containing D-01/D-02/D-03 synthetic `.txt` files matching the fixture truth. Use a reader identity separate from the owner for real share removal; owners cannot demonstrate revocation by removing their own direct share. Test direct and inherited grants separately: removing one grant may leave another valid path. Native API results determine effective access.

The proposed read-only OAuth scope is `https://www.googleapis.com/auth/drive.readonly`. It potentially covers all files readable by the authorizing account; the application only requests the fixed synthetic whitelist and identity fields. AUTH-009 approved this exact scope for the personal Google account on 2026-10-05. A dedicated test Google identity reduces account-wide exposure. The narrower `drive.file` requires app-authorized selection/creation and also grants write capability; it is not silently equivalent to read-only access. Picker and persistent OAuth refresh are not implemented. The dedicated Cloud project/API/testing-consent preparation is authorized; final Google authorization is performed by the user. New policy agreements or credential creation still require their specific review. Do not enable billing.

After approval and native setup, replace every invalid placeholder in `config/drive-pilot.example.json` into ignored `.runtime/drive-pilot.json` (0600). Store only file/parent IDs, tenant, verified requesting-user permissionId and the credential env reference, never tokens. Mapping verification and safe token acquisition are outstanding prerequisites; no discovery CLI is supplied yet.

```sh
python3 -m brain.operator_web --source drive --config .runtime/drive-pilot.json --actor eng_a --port 8085 --live
```

This is a prepared command, not currently runnable live. It asks for a Drive OAuth access token once with hidden TTY input, no email, then validates native identity before serving. The token stays only in process memory; browser token-free one-use bootstrap attaches the existing operator session. No refresh token or keychain extraction is performed. Expiration stops access instead of cached allow. This is not Google employee SSO. Runtime state is `.runtime/drive-web.sqlite`; model remains fake-extractive.

## Reproducible local checks

```sh
PYTHONPATH=tests python3 -m unittest test_drive test_drive_operator
make test-report
```

22 new tests cover reader/configuration/local HTTP, source identity, native errors, downloaded bytes, unsupported content, body/metadata races, editing, revocation, persistent browser credentials and the combined four-source Engine. The four-source test verifies that Drive revocation removes Drive model evidence, leaves other authorized sources usable and blocks the old mixed answer. These are mock platform results, not four-source real API acceptance.

Official contracts checked: [about.get](https://developers.google.com/workspace/drive/api/reference/rest/v3/about/get), [User](https://developers.google.com/workspace/drive/api/reference/rest/v3/User), [File](https://developers.google.com/workspace/drive/api/reference/rest/v3/files), [download guide](https://developers.google.com/workspace/drive/api/guides/manage-downloads). Live source/rate/permission propagation behavior remains to be measured.

AUTH-009 setup increment: the Google Cloud console confirmed successful creation of `AI-Bang2 Drive Read-only Pilot`, project ID `outstanding-box-510619-h9`, under the approved Google account and No organization. No Billing activation was requested. Drive API/consent/client/token/source reads remain pending; no personal files have been read.

Native setup checkpoint: Drive API now shows Enabled in the dedicated project. OAuth branding is prepared as External/testing but not submitted: the Google API Services User Data Policy checkbox remains unchecked for user review. No OAuth client, token, real file IDs or Drive content query has been created/read. See `evidence/runs/live-drive/setup-progress.json`; next resume point is user-confirmed branding creation, then read-only data-access/test-user/client preparation.

OAuth configuration checkpoint: user completed policy/Create, verified by the native success notification. The single configured scope is drive.readonly (saved); Audience is External/Testing with one approved test user. A Desktop client named `AI-Bang2 Drive read-only desktop pilot` is prepared with the native AI-agent classification, but not created. User must Create, Download JSON locally, close the secret modal and return to the Clients list. The agent must not capture or inspect that modal. Credential acquisition/PKCE callback integration is still to implement; no token/file content was read, and live Drive acceptance remains not_run.
