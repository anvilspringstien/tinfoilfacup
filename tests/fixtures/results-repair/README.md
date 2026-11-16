# Results repair source captures

Fetched during the 18 October 2026 investigation. These are public source HTML
captures for offline parser and metadata regressions, not canonical competition
patches and not the lost 17 October runner candidate.

- `fourth-qualifying-round.html`: https://www.footballwebpages.co.uk/fa-cup/fixtures-results/fourth-qualifying-round
  SHA-256: `8cbf4d7286214edf8385003b03e8c8a97c156fe4186f26debebfad8b538db059`
- `20261006.html`: https://www.footballwebpages.co.uk/fa-cup/20261006
  SHA-256: `51c249b704de20a448eb772d4f44534e012e808b72313fd2d0bb38ee38466c8d`
- `atherton-trafford.html`: https://www.footballwebpages.co.uk/match/2026-2027/emirates-fa-cup/atherton-collieries/trafford/594362
  SHA-256: `f881a2cefc72b2d3d7ba66e00ba5c6799125a6478c4c3e665bff4523f8ddba8e`

`verified-milestones.json` is a test fixture generated from the source parser's
Fylde result and a historical Atherton replay scenario matching the canonical
result and captured full-time match page, enriched through
the exact replay match page. The match page calls the ground "The Dreams2Reality
Stadium"; this repair consumes its kick-off only. It retains the existing verified
Clubfinder ground identity, Dreams2Remember Stadium, M46 9EY.

Independent authoritative result corroboration:
https://www.thefa.com/news/2026/oct/17/20261017-fac4qr-wrap
The FA reports AFC Fylde ending Atherton Collieries' run with a 5-0 win.

The frozen candidate input `competition-input.json.gz` contains the exact canonical
`competition.json` from commit `13d0e1f97951281cdc91bf0eb1b128c06e5bc89c` (before Results publication).
Uncompressed SHA-256: `d10c824122c0cbb3762501d0f0f64bf66980b3bef9222643e627eb9bc7ecbfa5`.
This keeps the captured 32-tie FRQ scenario independent of later live imports and
round promotion. The runner still verifies that the actual checkout input remains
unchanged. The unit test separately proves new-result and duplicate classification.
