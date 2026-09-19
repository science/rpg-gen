# Concept sketches — making the Tomb of the Sphinx less of a crawl
### Design review of `scenarios/ashes-at-the-sphinx.md`, written after session 4

*These are sketches, not a rewrite. Nothing here retcons anything played in session 4, and
every one of them can be switched on mid-dungeon, from the hallway the party is standing in
right now. Take them in any combination; they're ordered so that each later one is stronger
if you've adopted the earlier ones, but none of them requires the others.*

---

## 1. The diagnosis — why it reads as a crawl

It isn't your adaptation. It's the bones of the source. "Death at the Oasis" was written for
Castles & Crusades in a deliberately old-school idiom, and the tomb is a *pure* example of
the form. Counted out:

- **Sixteen keyed rooms. Twelve of them contain a guardian.** Of those twelve, **eleven are
  explicitly stated not to leave the room** — "will not chase," "cannot follow," "won't
  wander." The gargoyle in 9j is the sole exception, and even it stops at the end of its own
  hallway.
- **No room's outcome changes any other room.** There is no state in this dungeon. Clearing
  9d does not alter 9e. You could shuffle the rooms into any order and nothing would break.
- **There is nothing to learn.** Every room has frescoes, lovingly described — and not one
  of them contains a fact the party can act on. They are wallpaper. This is the biggest
  single waste in the module, and it's also the easiest thing in the world to fix (§3).
- **There is nobody to talk to.** Every occupant is mindless, cursed, or a construct. The
  one thing with a mind is the Dark Creeper in 9n, whose entire behavior is to steal a torch
  and run away.
- **There is nothing to decide.** The only genuine decisions in sixteen rooms are "do we take
  the obviously cursed scarab" and "do we push the obviously suspicious statue." Everything
  else is *fight or don't*.
- **There is nothing to navigate toward.** The party has no map, no named objective, and no
  reason to prefer any door over any other. Movement is undirected, which means it reads as
  a treadmill regardless of how good the individual rooms are.
- **The clock does not bind.** The source's 24 hours is invisible to the party, entirely
  external to the dungeon, and long enough to permit two long rests. *Your session 4 already
  fixed this one* — see §2.
- **The reward is poisoned and the party knows it.** 30,000 gp of unsellable relic, ~8,000 gp
  of grave goods, and an NPC companion who will hate them for taking any of it. That's a good
  moral problem and a terrible incentive: it gives the party no reason to go deeper.

Put plainly: the tomb has no pressure, no information, no negotiation, no navigation, and a
prize nobody can spend. Sixteen rooms of "roll initiative" is what's left.

---

## 2. What's already good — don't throw these out

Four things in this dungeon are genuinely excellent, and every sketch below is built out of
them rather than around them.

**The aesthetic is unusually strong.** A desert god with a pyramid for a hat, worshipped in
frescoes in every single room, with dog-headed attendants flanking his temple. It is coherent,
it is strange, and it is *everywhere* in the text. That density is an asset.

**"Praise Doorne the All-Knowing and live."** The 9e safe-phrase is the one moment where the
dungeon stops being a fight and becomes a test. Sketch 2 is nothing more than taking this
seriously and applying it consistently.

**Doorne's Ember is your invention and it's the best idea in the packet.** Right now it's a
prologue (why the raid worked) and an epilogue (relight it for a bonus). Sketch 4 moves it
into the middle, where it can do work.

**The cult's barrier is now a solved problem.** As of session 4 you have a concrete,
source-grounded answer to why a full raiding party bounced off a tomb that a level-2 party
strolled into: undying statues in 9a, a guardian in 9e that scimitars and arrows essentially
cannot hurt, and a safe phrase that requires praising the wrong god. That single explanation
does more for this dungeon than any new content would — it makes the party's advantage real,
narrow, and *earned by an NPC's piety rather than plot armor*. See `ashes-at-the-sphinx.md` →
*Doorne's rules at the table* for the full rule and the room-by-room coverage table.

**Session 4 already replaced the clock with a better one.** The interrogated guards said the
main body left to fetch *magical items needed to penetrate the tomb* and returns in 1-2 days.
That is strictly better than the source's timer in three ways: it's shorter, it's information
the party *earned* rather than GM fiat, and — the important one — **it asserts that there is
something down there the cult could not get past.** A full raiding party sat on this site for
a week and went home empty-handed. Whatever stopped them is the party's one structural
advantage over the enemy, and it is sitting there waiting to be named. Sketches 2 and 5 name
it.

---

## 3. Sketch one — the frescoes are the interface

**The idea.** Stop describing the wall art as scenery. Make it the only source of information
in the dungeon, and make that information *load-bearing*: threat-typing and navigation.
Nothing new gets added. This is a reinterpretation of text the module already wrote.

**The threat taxonomy.** Sort every occupant of the tomb into four kinds, and give each kind
a wall-symbol that announces it *before the door opens*:

| Kind | Who | The tell on the walls | Can it be passed without a fight? |
|---|---|---|---|
| **Doorne's servants** — the only things checking credentials | Caryatid Columns (9a), Stone Guardian (9e) | Clean pyramid. Worship, harvests, labor honored. | **Yes** — this is what they're *for*, and it's what Jiyloo's pendant already did in 9a. Note the two want **different** keys: 9a wants a symbol worn, 9e wants words spoken. |
| **Doorne's punished** — undead | Skeletons (9d), Ghouls (9i), Zombies (9k), Coffer Corpse (9g), Ogre (9h), Sia himself (9p) | **A skull on the side of the pyramid.** Sacrifice scenes, bodies clawing out of the ground, the dakhma. | **No.** These are not guards; they're a sentence being served. They do not care who you are. |
| **The machinery** — beasts and traps | Giant Ants (9b), Scarab Swarm (9l), the collapsing floor (9o) | The room depicts *the thing itself*: 9b's walls show ants eating people staked out in the desert; 9l's floor is the bait. | **No, but they can be avoided entirely** — these rooms are marked "do not enter," not "prove yourself." |
| **The personal curse** | An-Zefful (9f) | **The frescoes are smashed, and the north wall is blood-stained.** The only room in the tomb where the record was destroyed. | **No** — and this is the sharpest line in the taxonomy. Doorne cursed him *personally*. Doorne's servants check credentials; Doorne's sentences don't. It's also the one room where **no blessing is available**, because somebody smashed the record. Nobody is covered in there. |
| **Squatters** — nothing to do with any of this | Gargoyle (9j), Dark Creeper (9n) | Nothing. They're hiding *among* the art, not depicted in it. | **No.** The source makes both of these Chaotic/Neutral Evil outsiders to the tomb's whole logic — a predator that learned to look like statuary, and a thief who wants your torch. They're the reminder that a four-hundred-year-old hole in the ground accumulates tenants. |

Teach the symbol in **9c, the Hall of the Great God**, which the source has already set up
perfectly: the pyramid appears there in every form — struck by lightning, sun on its pinnacle,
wheat growing from its top — *and some of them have a skull on the side.* One Investigation
or Religion check, or just a player paying attention, and the party has a rule they can use
for the rest of the dungeon: **skull means the dead are in there.**

> **⚑ This is now a full system, and it's in the packet rather than here.** See
> `ashes-at-the-sphinx.md` → **Rule three — reading the doors**. Steve took the skull symbol
> and gave it the thing it was missing: *what those rooms are for.* The marks aren't warnings
> about an infestation, they're **labels on a filing system** — the tomb's primary function is
> holding the dead and the damned, either **sealed** (held forever) or **washing** (being
> purified toward release), and the priests never entered either kind. They kept them. That
> resolves the question this dungeon otherwise can't answer — why is a holy site full of
> undead — and it flips the frame: *the party thinks it's robbing a king's tomb; it's walking
> through a prison with a king buried in it.*
>
> Two consequences worth knowing here, because they change other sketches:
> - **9p has no mark.** In a building that labels everything it condemns, nobody labelled the
>   room with the wight in it — because Doorne didn't put him there, his high priest did. That
>   is physical evidence of the murder, findable with no roll, and it walks straight into
>   Sketch 5's trial.
> - **The marks label rooms, not objects.** 9l (the scarab) is a *clean* room with a cursed
>   thing in it, and the gargoyle and the Dark Creeper squat in unmarked rooms because they
>   moved in later. The system fails in exactly the right places, so it's a map and not a
>   guarantee. *(This replaces the earlier "leave 9g and 9h unmarked" suggestion — those are
>   both sealed rooms and they get marks. The useful imperfection moved somewhere better.)*

**The chronology.** Read in the right order, the frescoes are a story with a hole in it. The
source wrote this without meaning to; all you do is notice it out loud:

- **9c** — the good reign. Harvests, bounty, worship, the god given his due. *Some* pyramids
  already bear the skull.
- **9l** — the height. A bright sun, a green stone floor, people dancing with hands joined.
- **9j** — the turn. Humans working in mines and building mighty tombs, each overseer in a
  pyramid hat. The labor is now the worship.
- **9o** — the corruption. A man whipping slaves, waging war, lounging with women. *And every
  treasure in this room is fake — thin ivory over birch, gold leaf over worm-eaten wood.*
  The room that depicts his vices is the room where nothing is real. That's not a coincidence
  you need to invent; it's already on the page.
- **9d / 9i** — the atrocity and its price. People sacrificed before a skull-pyramid; then the
  dakhma, and four who "died accursed of Doorne."
- **9k** — the dead clawing out of the ground while the pyramid-hatted man smiles down.
- **9f** — the erasure. Somebody smashed this room's record and bled on the wall doing it.
- **9g / 9h** — the end. Sunrises to floods; then black walls with points of light.

**What it buys you.** Exploration starts producing something other than XP. A party that
reads walls can route around three fights, spot two secret doors, and — critically — walk into
9p knowing what Sia actually was. That last one is what makes Sketch 5 possible.

**What it costs.** It only works on a table that will engage with description. Tath'Shar
(educated, rich family, rogue's eye) and Gereon are your natural ins; hand the first reading
to one of them unprompted so the table learns that looking is rewarded. And back it with
hard currency at least once: make one reading the location of the secret door in 9c, so the
first payoff is treasure, not lore.

**Bolt-on from where they are?** Immediately. 9b's walls *already* show ants eating people
staked out in the desert. That's the read they can make right now, mid-fight, and it tells
them the truth: this room was never on the route.

---

## 4. Sketch two — the tomb can be passed, not only fought

> **⚑ Partly superseded, and improved on, by the rule Steve built after session 4.** The
> *Unwelcome* blessing (`ashes-at-the-sphinx.md` → *Rule two*) does the job of observances 1-2
> better than this sketch did, for one reason I hadn't found: **it resolves per character
> instead of per party.** My version gated a door for everybody, which makes it a puzzle the
> party solves once. Steve's version makes each PC answer for themselves, in front of the
> others, and then *keep* answering for it every room — which produces intra-party friction, a
> grumbling holdout, and a running cost, all of which are worth more than a solved door.
> What survives below and is still worth taking: **observances 3, 4 and 5** (come wet, come
> empty, come clean), which the blessing doesn't cover and which is where the loot gets priced.


**The idea.** Generalize the two rules the source already gives you into one system the party
can discover and exploit. In 9a the Caryatid Columns stand down for anyone openly displaying
a pyramid of Doorne. In 9e the Stone Guardian stands down for anyone who speaks praise. Those
aren't two quirks. They're two-fifths of a rite.

**The Pilgrim's Observances.** Five, in ascending order of what they cost:

1. **Bear the sign.** Wear a pyramid of Doorne openly. Cheap — the temple above ground is
   carved with them; any of them can be taken or copied.
2. **Speak the praise.** Name him aloud on entering: the All-Knowing, the Mighty, the
   Omnipotent, the Creator.
3. **Come wet.** Wash hands and face in the pools of 9a before going deeper. The water is his;
   a dry pilgrim reads as a robber. *This is the one that makes 9a a hub instead of a
   vestibule* — the party has to go back, which gives that room a permanent function.
4. **Come empty.** Carry nothing taken from inside the tomb. The instant someone pockets the
   citrines from 9h or the scarab from 9l, the observances stop working **for that person
   specifically.** Everyone else walks; the thief fights alone.
5. **Come clean.** Carry no unavenged killing done on the god's own ground.

**Observance 5 is the one your table already broke.** They executed a bound prisoner on the
sphinx's plinth in session 4. One of Doorne's four names is *the All-Knowing*. Tath'Shar reads
as unclean from the moment they descend, no matter what else they do — and nothing announces
it. The party just has to notice that the statues track one of them and not the others. That
is a far better consequence than a lecture, and it's recoverable: the god wants the body
buried, or the name spoken, or the survivor released. Your call which; pick before session 5.
Tracked as `thread:the-prisoner-on-the-plinth`.

**Jiyloo already taught them observance 1, out loud, and it was better than a reveal.** She
led down the stair, saw 9a, pulled her Doornian pendant out from under her robes and said
*"This area is holy for believers of Doorne."* The Caryatid Columns never moved. So the party
isn't carrying a secret they have to earn — they watched a woman produce a piece of jewelry and
turn off two statues, in the first room. **The interesting thing is what they do with a fact
they already have.**

Three consequences worth playing for, none of which need a word of explanation from you:

- **They will eventually ask why they walked in when a whole cult had to retreat and regroup.**
  You have the real answer and it's entirely source-grounded: the Columns are *undying* (the
  cult knocked them down repeatedly and got nowhere), the Stone Guardian in 9e is functionally
  immune to scimitars and arrows, and the safe phrase that would open it requires praising a
  rival god — which the Black Water Cult will not do. **The door was open the whole time and
  they went shopping for a magic item instead.** Full write-up and the Ashiq question in
  `ashes-at-the-sphinx.md` → *Doorne's rules at the table*.
- **The pendant will fail, and it should fail somewhere instructive.** 9e is the place: a party
  grown confident in "wear the pyramid, walk through" strolls in wearing pyramids and gets hit
  by something that wanted a *sentence* instead of a symbol. By then they'll have taken the oath
  in 9a and may assume that covers it. It doesn't — the oath is about *them*, the praise is
  about *him*. That's the moment they learn the
  rite has grammar — and it's much better than a fight they lose for no reason.
- **Marching order suddenly matters.** The pendant has to be visible and in front. Downed,
  rear-ranked, sent back up the stair with the prisoner, cut off by a door — and 9a is hostile
  ground again. Don't announce it. Just track where she is.

And the opening it leaves you: **anyone can wear one.** 9a checks the symbol, not the faith;
9e checks the words, not the meaning. Doorne's credentials are cheap and Jiyloo was simply the
only one who thought to bring them. Temple al Sia above ground is carved with pyramids and the
party has never set foot in it. A trip back up to equip everybody is the smart play, it's
available right now, and it converts them from *dependent on Jiyloo* to *self-sufficient* —
which is a much healthier place for the campaign to end up. Let them find it; don't offer it.

**What it buys you.** A competence curve instead of an attrition curve. The party fights 9b
and 9d because they didn't know. Somewhere around 9e they work it out. By 9j and 9k they're
walking through rooms that would have been fights, and *that feels like mastery* in a way that
winning the fights doesn't. Then they reach the treasure rooms and observance 4 prices the
loot in safety — the gold or the free passage, not both. The dungeon starts asking them
questions.

**What it costs.** Fights. Fewer encounters, less XP, a shorter combat night. If your table
came to roll dice, this is the sketch to take in half-measures — keep the undead rooms as
straight fights (they're immune to the rite anyway, per Sketch 1) and let the rite only turn
off the two rooms that already check credentials — 9a and 9e. That's still a real system, it's
the one the party has already met, and it costs you almost nothing.

**Bolt-on from where they are?** Yes, and elegantly. The ants don't answer to the rite —
they're machinery. So the party's first experiment with it *fails*, which is the right way
to learn a rule that has exceptions.

---

## 5. Sketch three — somebody else is already down here

**The idea.** The cult is currently a timer that lives outside the dungeon. Put some of it
inside, already failing.

Your session-4 interrogation says the main body left a week ago. It does not say they left
*nobody*. Put a four-person advance team below, sent in to scout and soften while the
leadership went shopping, and let the party find them in the order they died:

- **In 9b, among the ants** — a cultist's body, mostly gone. *This is why the door was shut
  and why the ants were already awake when the party opened it.* It explains the session-4
  cliffhanger with no retcon at all, and it's the first hard evidence that the party is
  walking a route somebody else already lost people on.
- **On the spikes in 9o** — a second one, ten feet down on the collapsed floor. Which
  telegraphs the trap to anyone who looks before stepping, exactly the way the packet already
  asks you to telegraph it.
- **Somewhere behind a barred door, alive** — the fourth. Four days without water, no way
  past what's between him and the stair, and entirely willing to trade.

**The living one is the point.** He is the first thing in this tomb that can be talked to. He
knows two rooms the party hasn't seen and is confidently wrong about a third. He knows what
the leadership went to fetch, or thinks he does. He is harmless, useful, and cornered.

**And the party executed exactly this man, upstairs, three hours ago.** Same choice, stakes
inverted: this time killing him costs them the only source of information in the dungeon, and
Tath'Shar's player has to make the call in front of a table that now knows what they do with
prisoners. You don't have to editorialize. Just run it and let the silence do the work.

**And he now has four weeks of context behind him.** With *The cult's high-water mark* in play
(`ashes-at-the-sphinx.md`), the survivor isn't a lone scout — he's the last man of a month-long
expedition that lost nineteen people, watched seven of them be eaten by a wall on somebody's
repeated orders, and was left behind when the rest marched out. He is the voice for all that
physical evidence, and he is extremely willing to be bitter about it. That's a much better
interrogation than "what's down the next corridor."

**Optionally, a third faction.** The Griffon Blades (see Sketch 6) are a *living* order whose
honored dead are in 9n. One of their number, or a Doornian pilgrim, or a surviving Talifan
guard from area 7 — someone in this hole who has a claim on it that isn't the party's and
isn't the cult's. Two sides is a fight; three sides is a situation.

**What it costs.** Prep. This is the sketch with the most new content in it — you need a
name, a voice, and a page of what he knows and what he has wrong. Budget twenty minutes.

**Bolt-on from where they are?** The dead one in the ant room, yes, this instant. The living
one can wait until they're two rooms deeper.

---

## 6. Sketch four — the Coal is a key that rings a dinner bell

**The idea.** Doorne's Ember is currently bookends: smothered before the adventure, relit
after it. Move it into the middle and make it a resource the party carries.

**Setup (already in your packet).** The Ember in Temple al Sia is out — Ashiq smothered it,
which blinded the tomb's guardians to anything happening outside their own walls and is why
the raid worked. Sia was entombed with a live fragment of the original hearth-flame: **Sia's
Coal**, the golden pyramid on the altar in 9p, still lit after centuries.

**The change.** Make the Coal portable, lit, and *loud*.

- **Carried openly, it satisfies the rite absolutely.** Every construct in the tomb stands
  down in its presence — the Columns in 9a and the Stone Guardian in 9e, with no symbol worn and
  no words spoken. Doors that were closed to the party open. For as long as they hold it, they
  are Doorne's, and they don't need Jiyloo standing in front to prove it.
- **And every undead thing in the tomb comes off its leash.** The zombies in 9k, the ghouls
  in 9i, the coffer corpse, the ogre — the ones who are down here as a *punishment*, who have
  been in the dark since the Great Destruction, all feel the fire move. They stop being room
  guardians and start hunting it. The one rule the source leaned on for balance —
  "won't chase past this room" — breaks, once, deliberately, and only for the dead.

So the Coal is a key that also rings a dinner bell. Take it and the tomb opens in front of
you and closes behind you.

**The climax that falls out of this.** The run from 9p back to the surface with the Coal:
constructs opening the way ahead, the dead pouring in from behind, and Ashiq's returning
column arriving at the sphinx's mouth at the top of the stair, carrying whatever they went to
fetch. Three forces converge at one door. That's a climax. A wight in a sealed room is not.

It also converts the clock from something the GM tracks into something the party starts
themselves, on purpose, at a moment of their choosing. That's the difference between pressure
and a timer.

**What it costs.** You lose the source's per-room containment, which was doing real work at
level 2. Contain it: only the undead unleash, only while the Coal is out of its altar, and a
party that puts it *back* gets the quiet tomb again — which is itself an interesting decision
to be able to make while bleeding.

**Bolt-on from where they are?** Not yet — it needs the party to reach 9p. But decide now,
because it changes what 9p is for.

---

## 7. Sketch five — Sia wants a verdict, not a fight

**The idea.** As written, the climax of sixteen rooms is a 28 HP wight that throws off a lid
and swings. Give him a mouth.

**What he is.** Sia's own high priest poisoned him and raised him as a wight to guard the tomb
from robbers — then intended to come back, turn the wight, and take everything. The Great
Destruction came first. So the priest was a murderer *and* a thief, and the king has been
alone in the dark for centuries with the Scepter of Ice, which grants telepathy — which is
how the tomb's guardians still work. He has been talking to his own statues since the empire
fell.

**What he wants, in the order he'll ask for it:**
1. To know whether the empire survived. (It didn't. The party has to decide whether to say so.)
2. To know where his priest went. (Nowhere. He died in the Destruction — and one of the two
   canopic jars beside the sarcophagus is his, three feet from a wight who has never been able
   to reach it.)
3. His fire back. He can feel that the Ember above is out.

**And he will not talk to the blessed as equals.** This is where the *Unwelcome* rule cashes
out. Sia was a god-king. Anyone who knelt in a doorframe and took Doorne into their heart is,
to him, a **subject** — he'll address them the way a king addresses a petitioner, and he'll
expect to be obeyed rather than argued with. The PCs who refused the blessing all the way down
are the only people in the room he has to *negotiate* with, and he knows it. Six rooms of
eating a −1d4 and grumbling about it turn into the one character who gets to conduct the trial.
That's the payoff that makes the refusal a character arc rather than a tax — and Tath'Shar's
player should get it without being told it was coming.

**Three endings, all available, none of them a dice-roll:**

- **Condemn him.** The party lays out what they read on the walls — the slaves, the war, the
  skull-pyramids, the sacrifices — and names him a king who fed his people to a god. He agrees.
  The fight happens anyway, but it's a fight he *chose*, and he thanks them on the way down.
- **Absolve him.** They argue that a priest who poisons his king is no judge. He gives up the
  Scepter and the Coal willingly and finally dies. They walk out with everything and no fight.
  This should only be reachable if they did the reading in Sketch 1 — otherwise they're just
  guessing, and it feels unearned.
- **Rob him.** Open the sarcophagus without speaking first. Run the fight exactly as written,
  nothing lost. **Keep this available.** A party that wants a boss fight should get one.

**What it buys you.** Every fresco they read three hours ago becomes evidence in a trial
they're now conducting. That's the payoff that makes Sketch 1 worth doing, and it's the moment
the dungeon stops being a crawl retroactively, all the way back to the first room.

**What it costs.** It's a talky climax after a long night of combat. Read the room; if the
table's energy wants a fight at 11pm, take the third ending and don't apologize.

---

## 8. Sketch six — three prizes, one clock

**The idea.** Give the party named objectives in different parts of the tomb, so movement
becomes triage instead of wandering.

**Hand them a map, early and wrong.** The dead cult scout in 9b is carrying a charcoal sketch
of what the advance team got through: partial, with the ant room crossed out, one corridor
mislabeled, and two rooms they never reached left blank. Now the party is navigating rather
than groping, and the blanks are the interesting part.

**Three prizes, three directions:**

- **Sia's Coal** — the Ember, the ward, the trade route, Jiyloo's stake. *Move it out of 9p.*
  Put it in **9m, the Temple of the Sphynx** — a temple room with a podium is the obvious home
  for a hearth-relic, and it means the party's three goals aren't all in the same box.
- **The Scepter of Ice** — 9p, with Sia. The one everybody wants and nobody can spend:
  30,000 gp, unfenceable locally, burns the unfaithful, and Jiyloo will turn on them for it.
  Keep it exactly that poisoned; it's a much better object as a temptation than as a payday.
- **The Griffon Blades' honors** — 9n. Five knights of an elite order that **still exists and
  is honored across the desert**, in a tomb whose location the order has forgotten. The source
  hands you this and does nothing with it. Returning one knight's blade and sigil to the living
  order is worth more than the grave goods and costs nothing but the carrying.

**That third one is the point.** Your party stood in Elmingwed's compound in session 4 and
chose **reputation over gold**, deliberately, as a strategy. This dungeon currently answers
that choice with 30,000 gp they can't sell. Give them a reputation economy instead — the
Griffon Blades, the reopened route, a relit Ember, a family pulled out of a pit, slaves brought
home — and the tomb starts rewarding the decision they actually made.

**The cost that makes it triage.** With 1-2 days on the clock and a party at level 2, there's
time for two of the three if they fight everything, and all three if they use the rite. Let
them feel that arithmetic.

---

## 9. Free material you already have

Three things sitting in the text, costing nothing:

**The dog.** 9m's temple is flanked by large seated statues of **dog-headed men in pyramid
hats**. The splint mail in 9p has **a dog's head for a helm**. Doorne's attendants are
dog-headed — and the party adopted a dog in the ruins above, three hours before walking in
here. Nobody has to say anything. Just describe the statues, then describe the dog going quiet
when it sees them, and let the table draw its own conclusion. If you want to go further: the
dog is the one member of the party the tomb never challenges.

**The slaves.** The raiders took the oasis's people into the desert days ago, and not one
person at the table has mentioned them. They are recoverable, they are the part of this job
that isn't about gold, and they're the natural next adventure whether the party remembers or
not. If they never come up, that's an answer too — and the world should be allowed to notice
it (`thread:missing-caravans`).

**The El-Alouph family.** Still alive in a covered pit near the pond. The party has their dog.
The dog knows where they are. This is the best scene in the module and it is currently sitting
unplayed, ten feet from where the party was standing.

---

## 10. If you only do one thing

**Sketch 1.** It's free, it's already written on the walls, and it converts the dungeon's
single most wasted resource into its interface. Everything else here gets better if you do it
and is still fine if you don't.

**If you do two:** add Sketch 2 at half-strength — the rite turns off the three construct
rooms, nothing else. The two together give you information *and* something to do with it,
which is the whole difference between a crawl and a dungeon.

---

## 11. Session 5, concretely

You're opening in a narrow hallway with the 9b door forced open. In order:

1. **Run the ant fight the way you planned it.** Your instinct in the session-4 notes is
   correct on both counts: let a braced or spiked door work if they invent one, and let a
   party that chooses to brawl in a five-foot corridor find out why that's a choice. The
   doorway-into-9a chokepoint should visibly, mechanically pay off.
2. **Mid-fight, give them the walls.** "The bas-reliefs in there show giant ants eating people
   staked out in the sand." One line. They now know this room was never on the route — which
   is Sketch 1 arriving as a free action.
3. **In the wreckage, the dead cultist** (Sketch 3), and on him the charcoal map with the ant
   room crossed out (Sketch 6). Somebody else lost people here, and they knew enough to mark
   it.
4. **When they go back to the unopened south door**, mention the floor: the gold-flecked black
   marble of 9a's hall runs south and stops dead at the east door they opened. They've been
   off the pilgrim road since they turned. That's the navigation rule, delivered by the
   architecture instead of a check.
5. **Say nothing about Jiyloo's pendant.** She already announced it in 9a; the fact is theirs.
   Let them ask why they got in when a cult had to retreat — and when they do, you have the
   real answer (undying columns, a guardian their scimitars can't scratch, and four words of
   praise they refuse to say).
6. **The ant fight has a way out, and it turns 9a into the classroom for the whole dungeon.**
   Jiyloo realises the problem is their *feet*, slams and braces the door, and sends them back
   to the pools to wash — including bringing water back for hers, which somebody has to kneel
   and do. The ants settle in stages as each person comes clean. Then the party goes back and
   reads 9a properly, and finds all five observances sitting in a room they'd crossed twice:
   the statues' pendants, a decodable inscription, pilgrims washing their feet at those exact
   pools, gold poured *into* the floor, and four carved doors. Full staging in
   `ashes-at-the-sphinx.md` → *Session 5 opens here*.
7. **The oath is taken in 9a, at one of four doors, and the door chosen gives a boon.**
   East/Creator, West/All-Knowing, North/Mighty, South/Omnipotent — the source gives the god
   exactly four names and the room has exactly four doors. Decline all four and you're
   *Unwelcome*, which now applies **only in Doornian conflicts** — the holdout fights the cult
   at full strength. Same file, *Rule two*. Ask **once**; the choice rides, and 9m is the only
   place to change it.
8. **Then don't mention it again.** Apply the −1d4 quietly and let the holdout be the one who
   brings it up. The mechanic is supposed to grind, not to be argued about at every door.
9. **9e is where the choice bites, and it's staged over the cult's dead.** A guardian that wants
   *spoken words* rather than a worn symbol — so the pendant that has carried them this far
   stops working — standing on a plinth ringed with mummified cultists and snapped scimitars,
   under an inscription telling them exactly how to pass that they chiselled at, defaced, and
   left perfectly legible. Full staging, plus the camp, the dig and the door, in
   `ashes-at-the-sphinx.md` → *The cult's high-water mark*.
10. **Give Jiyloo her one free line about doors whenever it first comes up:** *"You don't go
    through a skull door."* She can't explain it — her grandmother told her. The safety rule is
    free; the understanding still has to be earned (`ashes-at-the-sphinx.md` → *Rule three*).

---

*Cross-refs: `campaign/sessions/04.md` · `campaign/threads.yaml` → `thread:sia-tomb`,
`thread:missing-caravans`, `thread:the-prisoner-on-the-plinth` · `scenarios/ashes-at-the-sphinx.md`
· source room key `assets/_raw/Oasis of Sia .../Death_at_the_Oasis_(Levels_2_4).pdf` pp. 5-11.*
