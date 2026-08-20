# GameMonetize HTML5 publication

Use this reference for GameMonetize developer-game preparation, upload, hosted
SDK verification, activation review, and reconciliation. Recheck current
first-party documentation before every new submission:

- <https://gamemonetize.com/sdk>
- <https://github.com/MonetizeGame/GameMonetize.com-SDK>

`Developer → Add Game` distributes a developer-owned game. `Publisher → Add
Website` registers a website that embeds catalog games; it is a separate flow
and is not required to submit or activate a developer game.

## Prepare the platform build

1. Create or identify the intended dashboard draft and read its public
   `GameId` from the visible editor.
2. Bind that public ID to a canonical platform config containing no account,
   cookie, token, or credential data.
3. Generate a GameMonetize-only output. Keep other marketplace and canonical
   builds free of the GameMonetize loader.
4. Configure `SDK_OPTIONS` before loading
   `https://api.gamemonetize.com/sdk.js`.
5. Handle `SDK_GAME_PAUSE` by pausing gameplay and muting audio. Handle
   `SDK_GAME_START` by restoring the prior gameplay/audio state.
6. Call `sdk.showBanner()` only at an appropriate user-visible break and from a
   genuine user gesture when browser autoplay policy requires it.
7. Package `index.html` at ZIP root using a conventional deterministic Deflate
   ZIP. Verify integrity, file inventory, compression method, runtime paths,
   injected GameId, loader, callbacks, and checksum.

Treat the dashboard GameId as public configuration, not authentication. Never
put dashboard session material into the build or receipt.

## Upload and listing sequence

Keep these as separate actions:

1. Upload the exact reviewed ZIP and wait for the uploader to finish.
2. Open the uncached hosted URL and confirm that the intended game renders.
3. Save and reload the title, description, controls, categories, tags,
   dimensions, orientation/mobile setting, and required JPG images.
4. Confirm whether the editor preserves external links. Some text filters may
   remove protocol prefixes; read back the saved value instead of assuming it
   persisted.
5. Open the editor's own **Verify Game** modal. A direct hosted-game tab does
   not replace the platform verification surface.
6. Trigger one legitimate advertisement from the hosted game, let it finish
   naturally, then close the modal and reload the editor.
7. Treat verification as successful only when the editor enables **Request
   activation**.

Do not click advertisement creative. Do not intercept or mock advertisement
traffic to manufacture success.

## Verification evidence

Confirm as many layers as the browser exposes:

- The hosted game uses the matching GameId and exposes the expected SDK object.
- The SDK reaches ready state.
- A real advertisement media request succeeds, normally with a successful 2xx
  or ranged `206` response.
- The game receives pause/mute before playback and resume afterward.
- No `AD_CANCELED`, IMA loader failure, or video-play failure remains.
- After a clean editor reload, **Request activation** is enabled.

The enabled dashboard control is the final gate. Network success alone is not
enough.

## Failure matrix

### Hosted preview says `Game not found`

Check in order:

1. `index.html` is directly at ZIP root.
2. The ZIP has no wrapper directory, nested ZIP, symlink, or undeclared file.
3. Archive integrity and content checksums match the reviewed release.
4. The draft contains the matching GameId.

If those pass, perform at most one explicitly authorized upload retry with the
same reviewed files in a conventional Deflate ZIP. If it still fails, stop and
contact platform support with sanitized draft identity, timestamp, and ZIP
checksum. Do not keep uploading variants.

### SDK or IMA loader fails

In an owned temporary browser-profile snapshot only, disable advertisement
blocking and page-translation extensions that inject into the verification
iframe. Reload from a clean editor state. Do not change extensions in the
user's real source profile.

### `AD_CANCELED` before playback

Inspect read-only network evidence. Ensure the proxy permits the SDK, VAST, and
tracking domains. Common domain families include:

```text
doubleclick.net
googlesyndication.com
2mdn.net
```

Do not switch off the user's system proxy when other work depends on it.

### VAST succeeds but IMA reports video playback failure

If the VAST and tracking requests return `200` but the media request fails or
routes to an unusable regional edge, send all Google video CDN domains through
the same working outbound proxy group:

```yaml
- DOMAIN-SUFFIX,gvt1.com,US_PROXY_GROUP
- DOMAIN-SUFFIX,gvt1-cn.com,US_PROXY_GROUP
- DOMAIN-SUFFIX,googlevideo.com,US_PROXY_GROUP
- DOMAIN-SUFFIX,2mdn.net,US_PROXY_GROUP
- DOMAIN-SUFFIX,doubleclick.net,US_PROXY_GROUP
- DOMAIN-SUFFIX,googlesyndication.com,US_PROXY_GROUP
```

Replace `US_PROXY_GROUP` with the actual policy-group name. Put these rules
before broad `REJECT`, `DIRECT`, and `MATCH` rules. With `DOMAIN-SUFFIX`, omit
the `*.` prefix.

Recreate the temporary profile snapshot after changing routing so the final
test has clean browser and network state. A successful retry should show the
media on the intended outbound edge and return `206` or another successful
response without `videoplayfailed` tracking.

### Advertisement finishes but activation is still disabled

Close the verification modal, reload the editor, and read the controls again.
Do not trigger another advertisement until canonical state proves the first
verification failed.

## Request activation

Treat **Request activation** as a separate review submission:

1. Require explicit authorization for this game and draft.
2. Confirm account, title, draft ID, GameId, listing, media, and enabled review
   control immediately before clicking.
3. Click exactly one enabled **Request activation** control.
4. Stop on any new rights, ownership, exclusivity, payout, tax, or legal
   declaration and obtain a human decision.
5. Reconcile in **My Games**. A visible `IN REVIEW` state or an editor action
   such as **Cancel review** proves submission, not publication.
6. Never click **Cancel review** unless the user separately requests it.

Record the result as `submitted_pending` until the platform approves it.
