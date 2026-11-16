# Official draw announcements

`competition.json.draw_announcements` records the draw event and ball list before
fixtures exist. It never advances `source_round`, creates opponents or changes
results/custody. Existing draw/result importers retain this additive metadata.

Import an official FA announcement with the CLI (dry run by default):

```sh
python updater/import_draw_announcement.py \
  https://www.thefa.com/news/2026/oct/16/emirates-fa-cup-first-round-draw-to-be-broadcast-on-tnt-sports-20261610 \
  --round 'First Round Proper' --at 2026-10-19T18:35:00+01:00 --expected-balls 80
```

After reviewing the output, repeat with `--publish`, then refresh generated copies:

```sh
python updater/refresh_clubfinder_embedded_snapshot.py
python updater/refresh_beta_embedded_snapshot.py
```

Use the new official article, round, announced time (including its UTC offset) and
expected number of balls for later rounds. The importer checks the source domain,
round, date/time and a complete consecutively numbered list. Unsupported source
layouts fail without publication. This is a separate explicit CLI operation;
the scheduled fixtures watcher continues to import confirmed opponents normally.

Both Clubfinders show the draw in Europe/London time and match the custodian to
its ball number, including conditional list entries. After the announced time,
the display says it is awaiting the confirmed draw. A confirmed fixture always
takes precedence over the announcement. Missing announcements retain the existing
fallback; a date or ball number is never guessed.
