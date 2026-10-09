---
name: prompt-pictures
description: Make a ~25-second vertical, story-driven animated film entirely in code with Claude Code. Every frame is drawn in HTML canvas or Three.js and rendered with HyperFrames; every note and sound effect is synthesised in Node and locked to the frame. No image or video models, no stock, no samples. Use when someone describes an idea for a short animated film, ad or brand story.
---

# Prompt Pictures

**Describe an idea, and Claude makes a finished short film from it, entirely in code.**

This kit is how the [VoiceDumps](https://voicedumps.qwee.ai) films *Buy Milk*, *47 Tabs*, *The Talkies* and *The Race*
were made with Claude:
- Every frame is drawn by code.
- Every note of music and every sound effect is synthesised by code.
- There are no image or video models, no stock footage and no sample libraries.

You bring the idea. Claude writes the story, draws it, animates it, scores it, mixes it and
renders the MP4.

It has three parts:
1. **The method**: the production rules every film follows. Always include it.
2. **Four styles**: templates you fill in with your own idea. Each one comes with the film
   we made from it, as a worked example.
3. **Lessons**: what we learned the hard way.

### Two reference files (recipes)

This file works on its own. Two companion files make the sound and the animation much
better on the first try:
- **`references/sound.md`**: a runnable synth and mix engine core, instrument and
  sound-effect recipes with real parameters, the mix chain and its numbers, scoring
  patterns, and the commands that measure loudness, silence and sync.
- **`references/animation.md`**: the HyperFrames page skeleton (2D and Three.js), spring
  and easing code, pose blending, an acting cheat sheet with frame counts, timing styles
  (smooth, on twos, hand-cranked), camera grammar, composition and type rules, material
  recipes, and the review checklist.

**Claude: before drawing, read `references/animation.md`. Before writing the score, read
`references/sound.md`.** If they're not next to this file, fetch them first:
- https://raw.githubusercontent.com/heynaavi/prompt-pictures/main/skills/prompt-pictures/references/animation.md
- https://raw.githubusercontent.com/heynaavi/prompt-pictures/main/skills/prompt-pictures/references/sound.md

---

## What you need

- **Claude Code**, in the terminal or the desktop app. The films need a real computer to
  render on, so a chat window alone isn't enough.
- **Node.js 20+**, **ffmpeg** and **Google Chrome**.
- **HyperFrames**, which turns an HTML page into a video. It runs through `npx`, so there's
  nothing to install. These films were made with `hyperframes@0.8.71`.
- **Patience.** A film is a long working session: about an hour for a 2D film, several
  hours for a 3D one. Much of that is drawing, reviewing frames and rendering.

## How to use it

**Option 1: paste.** Open Claude Code in an empty folder. Paste *The method*, then one
*Style* with the brackets filled in.

**Option 2: as a skill.** Save this file as `~/.claude/skills/prompt-pictures/SKILL.md`, and
the two reference files beside it in `references/` (optional: Claude fetches them if
they're missing). Then type:

```
/prompt-pictures a 25-second film about [your idea]
```

**Quick start, if you only have an idea:**

```
I want to make a short film. My idea: [one or two sentences].
It's for: [your product, cause, event or just yourself].
The one thing it should make people feel or understand: [ ].

Follow the Prompt Pictures method. Pick the style that fits best (Era Montage, Overload →
Release, Medium Shift, Live Broadcast) or propose a new one. Pitch me 3 different concepts
in 4–5 lines each and wait for my pick. Then write the bar map, show it to me, and only
then build.
```

---

## Part 1: The method

```
Make a short film entirely in code. These are the production rules. Follow all of them.

FORMAT
- 1080×1920 (9:16), 30 fps, 24–27 seconds, sound on. It's for Reels, TikTok and Shorts.
- Zero generation: no image, video or music models, no stock, no samples. Every frame is
  drawn by code and every sound is synthesised by code.

STORY FIRST
- One relatable truth, told as a story with a character who wants something, physical
  comedy, and a turn where [the product / the point] changes everything.
- The emotion is EXCITEMENT and a SMILE. Never mean, never sad at the end. The old way
  gets a warm ending, not a humiliation.
- One idea per film. One gag per beat. Every second must earn its place.
- Before building, pitch 3 distinct concepts and wait for a pick.

THE BAR MAP (write it before drawing anything)
- Pick a tempo where one beat is a whole number of frames at 30 fps. For example:
  90 BPM = 20 f, 100 = 18 f, 112.5 = 16 f, 120 = 15 f, 128.57 = 14 f.
- Write a table: bar → frame range → what happens on each beat.
- The picture and the music are made to this grid in parallel. Once it's agreed, an action
  may move a frame or two inside its beat, but never to another beat.
- Put the turn on a downbeat. Put the payoff on the biggest downbeat.

THE TIMING FILE (shared by picture and sound)
- `scripts/lib/timing.mjs` exports FPS, BPM, BEAT, BAR, BARS, TOTAL, an at(bar, beat)
  helper, and EVENTS.
- EVENTS is a list of { frame, kind, x, detail } for EVERY sound-worthy action: every step,
  pop, blink, key press and card. x is the on-screen position, 0 to 1, and is used for
  stereo pan.
- The picture reads its cue frames from this file, so picture and sound cannot drift.

PICTURE  (recipes: references/animation.md)
- An HTML page rendered by HyperFrames. First read `npx hyperframes@0.8.71 --help` and its
  docs, and follow its composition contract: a root element with the composition id and
  duration, and a paused GSAP timeline registered when the build is ready.
- Draw with canvas 2D, or Three.js for 3D.
- Determinism: every frame is a pure function of the frame number. Use a seeded RNG
  (mulberry32). Never use Math.random, Date or requestAnimationFrame. Reset canvas state
  on every frame.
- Performance: pre-render static art and textures once, and keep per-frame work light.
  Render with `--workers 4`; headless Chrome can be killed if a single worker runs too long.
- Craft:
  - Motion is clean, springy and confident: spring easing with overshoot, never linear or
    floaty.
  - The acting is Pixar-style: anticipation, squash and stretch, follow-through and
    overlapping action, arcs, moving holds, blinks and eye darts, and reactions that land.
  - Characters read at thumbnail size: strong silhouette, big eyes, one signature feature.
  - Every shot has one focal point and a clean composition.
  - Material and texture sell the look: paper grain, clay fingerprints, film grain, gold
    leaf.
  - Keep all essential text and gags between y 220 and y 1600, because the app's UI covers
    the edges.
  - Use no real brands, logos or interfaces unless they're yours. Original characters only.
  - Prefer open-licence (OFL) fonts.

SOUND (a score, not a cue list; recipes: references/sound.md)
- Write a small deterministic synth and mix engine in Node (48 kHz, 24-bit WAV), with:
  - Instruments made by synthesis: FM (bells, electric piano), modal (marimba, vibes, steel
    pan), Karplus-Strong (plucks, harp, upright bass, harpsichord), additive piano with
    detuned strings (honky-tonk), formant voices (vocal chops, chants, cartoon "speech"),
    filtered saw (brass, sax), and noise sweeps (whooshes, brushes).
  - Instruments that "talk": a muted trumpet or clarinet following a pitch contour can say
    a word without words.
  - A mix: buses with high- and low-pass filters, a real reverb (Freeverb), a tempo-synced
    delay, a sidechain pump from the kick, a glue compressor and a look-ahead limiter.
- Compose the music to the bar map. The music should tell the story: changes of band, key
  or tempo feel happen on the bar lines where the story turns.
- Place every sound effect from EVENTS on its exact frame, panned by x.
- Give the product (or the hero) ONE signature sound that plays on the exact frame it's
  used.
- Designed silence must be true digital zero. Kill effect tails at the cut rather than
  fading them.
- The payoff is the loudest moment. Measure loudness per bar to prove it.
- Master to about −14 LUFS integrated, with true peak at −1 dBTP or lower.

REVIEW (nothing ships unseen)
- Snapshot every bar line and every gag at full size, and LOOK at them. A passing build
  check proves nothing.
- Check every hand pose at phone size, because small hands can read as rude gestures.
- Verify sync by measuring: the frame of the action against the onset of the sound.

DELIVER
- Mux: ffmpeg -i out/film-silent.mp4 -i out/score.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest out/film.mp4
- Social: -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -profile:v high -movflags +faststart
- Grainy films: add -tune grain -maxrate 20M -bufsize 40M (plain CRF balloons on grain).
- Write a short story doc covering the treatment, the bar map as built and the sound
  handoff, plus resume notes, so the work can be paused and picked up again.
```

---

## Part 2: The styles

Fill in the brackets, then paste the style after *The method*. Each style lists the
example we made, so Claude can see the bar we're aiming for.

### Style A: Era Montage *(Buy Milk)*

**Use it when** the problem is old and universal, and your product is the latest answer to
it. One person, the same task, every era of history. They fail in each era's own way, then
today it just works.

```
STYLE: ERA MONTAGE

The task: one person keeps trying to [THE SAME SMALL, RELATABLE TASK] across history.
The eras, one per bar: [6–8 ERAS, e.g. "Sumer 3200 BC, Egypt, a medieval monastery,
Gutenberg 1455, an 1866 telegraph, a 1995 PC, a 2012 phone, NOW"].
How each era fails: [OPTIONAL; otherwise invent a gag specific to each era's tool].
Today: [HOW YOUR PRODUCT DOES IT IN ONE GESTURE].
End line: [YOUR LINE, e.g. "5,000 years of writing it down. Now just say it."]

FORM
- One locked composition: the character sits at the same place in frame in every era.
  Every cut is a hard cut on the bar line.
- Recast the SAME character in each era's art style. Same soul, recognisable at a glance:
  round head, one signature feature (a tuft of hair, a big nose).
- Each era gets its own real art style, with materials: carved relief, Egyptian painting
  on papyrus, illuminated gold leaf, woodcut, a Victorian poster, 16-colour pixel art, a
  flat phone UI, a clean modern look.
- A place/date caption sits in the same spot every era, in small tracked caps.
- One gag per era, readable in under 2 seconds at phone size.
- Running gags across eras: an animal that keeps ruining it (a goat, a cat), and a payoff
  callback on the end card.

SOUND
- One tempo for the whole film, with a NEW BAND ON EVERY BAR LINE that fits the era: frame
  drum and reed pipe, harp and sistrum, plainchant, harpsichord, music-hall piano, a 90s
  drum machine, trap, then a warm modern pop drop for "now".
- Hide one musical joke in the score. In ours, the printing-press bar plays its phrase
  backwards while the press prints the words backwards.
- The "now" bar is a hush, then the drop: the loudest moment of the film.

GRID: 120 BPM (15 frames per beat), 12 bars = 720 frames (24.0s).
Bars 1–2 establish the first era. Bars 3–8 are one era each. Bars 9–10 are now.
Bars 11–12 are the end card.
```

**Our example: *Buy Milk*.** One man tries to write down "BUY MILK" for 5,000 years. The
earliest writing really was mostly lists of goods.
- **Uruk:** a goat eats the clay tablet.
- **Thebes:** a cat walks through the wet ink and sits on the list.
- **Kells:** a monk spends the whole bar gilding one perfect B.
- **Mainz:** the press prints KLIM YUB.
- **1866:** the telegraph taps MILK in Morse and fries his hair.
- **1995:** he's buried in pop-ups.
- **2012:** a cat video eats 40 minutes.
- **Now:** the cat sleeps on the keyboard, he holds one key, says "buy milk", and it's
  written.

The goat bites the end card and gets the last word.

**Why it works:** the premise fits in one sentence, the eras turn a history lesson into
eye candy, and the cat and goat keep people rewatching.

---

### Style B: Overload → Release *(47 Tabs)*

**Use it when** your product relieves a feeling everyone knows. You make the feeling
physical, count it up until it's unbearable, then release it one piece at a time.

```
STYLE: OVERLOAD → RELEASE

The feeling: [A RELATABLE OVERLOAD, e.g. "47 mental tabs open at 11:52 pm"].
What it looks like: [THE PHYSICAL METAPHOR, e.g. "the worries are browser tabs that pile
up on your head in bed"].
The items: [10–20 SPECIFIC, FUNNY, TRUE EXAMPLES, e.g. "reply to Sam (2)", "dentist?",
"why did I walk in here", "startup idea", "buy milk"].
The release: [HOW YOUR PRODUCT TAKES THEM AWAY, ONE BY ONE].
End line: [e.g. "Empty your head."]

FORM
- One character, one place, one night. A big round head and huge expressive eyes: the
  face does the acting.
- A counter on screen rolls up like an odometer: 4 → 12 → 47. The pile-up accelerates,
  one per beat, then two, then four, then each pop multiplies. The pile teeters, wobbles
  and squashes the character.
- At the peak: eyes squeezed shut, then STILLNESS. Hold identical frames, with digital
  silence underneath.
- One eye opens. They reach for the product (its signature glow, in one accent colour).
- The release: each item plucks off the pile, flips, and snaps into one tidy list. Each
  snap is one beat, then faster.
- One last item hesitates. A shrug, and it goes in too.
- The light arc carries the emotion: cold navy night warms to lamp gold as the head
  empties. They smile, turn over and sleep. One small star becomes the full stop of the
  end line.
- Look: soft flat geometry, rounded shapes, gentle gradients, film grain. The items are
  the only colour.

SOUND
- Anxiety you can count: a clock ticking on every eighth, a quickening heartbeat, and a
  minor pad whose filter creeps open.
- Every item pops in on the next note of a CLIMBING minor pentatonic, so the pile-up
  literally rises.
- The stillness is digital zero.
- The product's signature sound plays on the exact frame it's pressed.
- The release turns to the major key, and every item that snaps into the list plays the
  next note of a melody. The emptying is a melody you can hear.

GRID: 100 BPM (18 frames per beat), 11 bars = 792 frames (26.4s).
Bars 1–4 are the pile-up, accelerating. Bar 5 is the peak, the stillness and the reach.
Bars 6–9 are the release, accelerating. Bar 10 is the last item, the shrug and sleep.
Bar 11 is the end card.
```

**Our example: *47 Tabs*.** It's 11:52 pm and 47 thoughts pile onto a head in bed as
browser tabs, until the tower squashes it into the pillow. Silence. One eye opens. They
hold the key and just say it all, and each phrase plucks a tab off the tower and snaps it
into one note. The room warms from navy to gold. "Why did I walk in here" gets a shrug and
goes in too. They sleep. *Empty your head.*

**Why it works:** everyone has had that night, the counter makes it measurable, and the
release is physically satisfying to watch.

---

### Style C: Medium Shift *(The Talkies)*

**Use it when** your product feels like a leap, not an upgrade. Set the story in an old
medium whose limitation IS the problem, and make your product the moment the medium
changes.

```
STYLE: MEDIUM SHIFT

The old medium: [e.g. "a 1927 silent film", "black-and-white TV", "an 8-bit game",
"a crackly radio serial"].
Why it's the problem: [WHAT THE CHARACTER CAN'T DO IN IT, e.g. "you can only talk in typed
title cards"].
The story: [A SMALL, HUMAN WANT, e.g. "a shy clerk wants to ask the girl across the street
to dinner"].
How the old way fails, comically: [e.g. "his typed letter grows into a scroll that crosses
the street and buries her"].
The shift: [THE GESTURE THAT CHANGES THE MEDIUM, e.g. "a key on his desk glows; he presses
it and sound arrives"].
The first moment in the new medium: [ONE WORD OR ONE ACTION, e.g. "Dinner?"].
End line: [e.g. "Welcome to the talkies."]

FORM
- Make the old medium a convincing artefact:
  - For silent film: warm black-and-white, heavy grain, gate weave, flicker, dust and
    scratches, iris wipes, intertitle cards with an art-deco border, and motion stepped to
    ~15 fps.
  - Make it TRUE to the old medium. In black and white, red prints dark.
- At the shift, EVERYTHING changes at once: colour blooms outward from the moment
  (designed, petal-edged, not a flat fade), motion becomes smooth 30 fps, the grain calms
  and the gate stops weaving.
- Original characters, with pantomime acting that reads with no words.

SOUND
- The old medium's sound and nothing else. For silent film: projector clatter and a
  honky-tonk pit piano playing ragtime, with slide-whistle and glockenspiel "pit effects".
- NO VOICES in the old medium, not even a snore. Keep that rule sacred.
- At the shift the old sound stops DEAD on the exact frame. A breath, then about 0.3s of
  TRUE digital silence.
- The first word is played by an instrument that talks: a muted trumpet for him, a
  clarinet for her.
- The new world arrives in full: a harp glissando with the colour, then a swing big band
  a whole step higher. The loudest part of the film is the new world.

GRID: 100 BPM (18 frames per beat), 11 bars = 792 frames (26.4s).
Bar 1 is the leader and title. Bars 2–5 are the old medium and its comic failure. Bar 6 is
the despair, the glow, the press and the silence. Bar 7 is the first word and the colour
bloom. Bars 8–9 are the answer and the celebration. Bars 10–11 are the end card and an
iris close.
```

**Our example: *The Talkies*.** In a 1927 silent film, a clerk's typed love letter grows
into a scroll that crosses the street and puts Mabel to sleep. A key glows. He presses it,
the piano stops dead, and in the silence he leans out and says "Din-ner?" on a muted
trumpet. Colour pours out of his mouth and floods the street. "Yes!" on a clarinet, then
the big band.

**Why it works:** the silence before the first word is the most attention-grabbing moment
in the feed, and the colour bloom is the payoff people share.

---

### Style D: Live Broadcast *(The Race)*

**Use it when** your product beats the old way at something measurable: speed, effort or
quality. Stage the comparison as a ridiculous live sports event.

```
STYLE: LIVE BROADCAST

The event: [A RIDICULOUS CHAMPIONSHIP, e.g. "THE 100-WORD MESSAGE FINAL"].
Lane 1, the old way: [CHARACTERS WHO TRY SO HARD, e.g. "twin thumbs in sweatbands, very
serious"].
Lane 2, your product: [A CHARACTER WHO BARELY TRIES, e.g. "a chill speech bubble in
sunglasses with a juice box"].
The hazards on the old way's lane: [3 GAGS ABOUT THE REAL PAIN, e.g. "an AUTOCORRECT
hurdle, a BACKSPACE sand pit, a TYPO banana peel"].
The warm ending: [HOW THE WINNER IS KIND, e.g. "Voice brings the exhausted thumbs a juice
box; they give a huge thumbs-up"].
End line: [e.g. "Say it. It's faster."]

FORM
- Full TV-sports grammar: a swooping establishing shot, a LIVE scorebug, lane intros with
  lower-thirds, ON YOUR MARKS / GET SET / BANG, a word-count ticker, a split screen, a
  PHOTO FINISH freeze, a SLOW-MO REPLAY with a telestrator, and a freeze-frame.
- Bold flat broadcast graphics, halftone, and saturated stadium colour.
- The comedy is contrast. The old way's legs are a blur but the track barely moves. The
  product lounges, yet the stands streak past.
- Each hazard is a gag with anticipation, a payoff and a reaction to camera.
- The ending is warm, never cruel. Check the final hand gestures at phone size.

SOUND
- A stadium that breathes: a crowd walla bed whose energy follows the race, and applause
  swells.
- A brass fanfare for the intros, a held breath at GET SET, and the starting pistol.
- Then a driving anthem: four on the floor, toms and brass hits, with a stinger on every
  gag.
- The finish is the loudest moment: a crash, a roar and camera flashes.
- The replay drops everything to underwater slow motion.

GRID: 128.57 BPM (14 frames per beat), 14 bars = 784 frames (26.1s).
Bars 1–2 are the stadium and lane intros. Bar 3 is marks and set. Bar 4 is the bang.
Bars 5–8 are the chase and the hazards. Bar 9 is the finish. Bar 10 is the replay.
Bars 11–12 are the warm ending. Bars 13–14 are the end card.
```

**Our example: *The Race*.** It's the 100-Word Message Final: twin Thumbs against Voice,
a chill speech bubble in sunglasses. The Thumbs hit an autocorrect hurdle (it shouts
"*ducking*"), sink in a BACKSPACE sand pit, and slip on a TYPO banana peel. Voice glides
over everything waving to the crowd, and wins the photo finish 100 to 14. It comes back
with a juice box, and the Thumbs give the only answer a thumb has: 👍. *Say it. It's
faster.*

**Why it works:** sports grammar is instantly readable, and the hazards are pains everyone
has felt.

---

## Part 3: Lessons we learned the hard way

**Concept**
- Check every new concept against your earlier films on mechanic, palette and sound. If
  any one repeats, change it. Repeating a concept reads as "average", however well it's
  made.

**Picture**
- A frame that "passes" can still be wrong. Look at the pixels at full size, every bar
  line and every gag. A small thumbs-up once read as a middle finger.
- If a render dies around 30 seconds in, suspect the headless browser's lifetime before
  you suspect your film, and render with 4 workers.
- A film that ends on pure black can make the renderer fall back to one worker. Force
  `--workers 4`.

**Sound**
- The limiter should catch peaks, not set the level. Leave headroom before the master, or
  every dynamic in the film flattens.
- Designed silence must be digital zero, and reverb tails must not resume after it.
  Choke the effects at the cut.
- Make the product's sound play on the frame the key bottoms out, not the frame the finger
  starts moving. Derive it from the animation curve.

**Delivery**
- Grain and boil are expensive to encode. Use `-tune grain` with a bitrate cap.

---

*Made with Claude Code. If you make something with this, the most important rule is the
first one: story first, and make people smile.*
