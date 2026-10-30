# House style

## Voice and script
- One study per episode. 2-4 minutes. A host who is curious, a little irreverent, and fair.
- Arc: cold open hook -> show open (music-only montage + sonic logo) -> the story with real numbers -> "hold on" turn (the
  biggest honest caveat) -> the fundamentals (why it could or could not work, sourced) -> verdict (what to do with it,
  with a confidence) -> sources end card.
- Short spoken sentences (8-20 words). Say numbers the way a person would ("forty-nine minutes").
- Never overstate: "at least N" for citation counts, PREPRINT for preprints, "same-day test" when it was one.
- Optional viewer greeting: config `viewer_name` fills `{VIEWER_NAME}` in a line; `notes_name` fills `{NOTES_NAME}`.
- Mild profanity is allowed only if the configured audience allows it; a `bleep` can cut a word to true silence.

## Visuals
- Something moves at all times: no hold longer than 1.5 s (qa.py checks).
- Every beat is keyed to a spoken word and every visual hit emits a cue (so a sound lands on it).
- Text on screen stays at least 1.2 s; at most ~8 words per card; accent words in *asterisks*.
- Charts use only numbers from the sources, with units and labels. No invented data, no decorative fake charts.
- Real images only (licensed, credited). Voxel models are illustrations, never evidence.

## Sound
- The voice always wins: music ducks under it (mix.py). -14 LUFS integrated, true peak <= -1 dBTP.
- Original score only (scripts/music), CC0 / public-domain samples only. Credit sample packs in the end card or description.
- Risers and reverse swells END on their cue; hits START on it (within 40 ms; sfx_align.py reports it).

## Process
- Accuracy audit BEFORE voice; harsh review AFTER render. Fixes always go into a new version folder.
- Status every 50 minutes during a build. Cut scope before accuracy.
