# Execution and reconciliation

## Preflight

1. Verify the reviewed source/render bytes and exact platform variant.
2. Validate the platform manifest, copy, disclosures, destination identity,
   visibility, schedule, and current authorization evidence.
3. Check the destination ledger and authoritative remote state for an existing
   operation using the same source, account, variant, copy, and schedule.
4. Run the repository's dry-run or local validator before opening an
   authenticated publisher.

## API execution

Use the official adapter when it is configured and appropriate for the owned
account. Reserve the operation before upload, persist the observed remote ID,
poll processing to a terminal state, and read back visibility and the canonical
URL. A timeout after an upload begins is an ambiguous write, not permission to
upload again.

## Browser/CDP execution

Use the exact named Chrome profile or loopback CDP session selected by the
operator. Confirm the visible account before the write, use a dedicated task
tab, select the exact local file, populate the reviewed copy and schedule, and
record the attempt immediately before the final Post or Schedule action.

Do not export browser storage or attach a second browser to an active profile
directory. Relocate controls after navigation instead of reusing stale
selectors. Clean any owned temporary profile snapshot or CDP session after
reconciliation.

## Evidence

Prefer an official API readback or public structured endpoint. For a browser
post, capture enough authoritative page state to prove the account, exact copy,
native video presence, schedule or publish state, remote ID, and canonical URL.
Keep receipts free of credentials and machine-specific profile paths.

If the result is uncertain, retain the original operation identity and stop.
Reconcile before any retry. Never invent a public URL for a scheduled or
unverified post.
