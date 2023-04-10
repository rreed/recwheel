### Recwheel

A small Sunday afternoon scale Discord bot, implementing a "recommendation wheel" based on a random conversation with one of my metamours.

This should be considered a work in progress, but it works well enough for a small server. :)

### The Impetus

```
[redacted]:
I know what they mean, but the way I immediately interpreted this as “I would participate in the polycule discord”

Amdusias:
hahaha I mean we joke about how we already have a video chat service and a graphing tool, we may as well

[redacted]:
This would be an album recommendation roulette wheel thing

Amdusias:
yeah, that's a neat idea

[redacted]:
Currently a bot on telegram in a music chat I’m in

Amdusias:
so how does this work?
if your slot comes up you have an album ready to go?

[redacted]:
When the wheel is spun it pairs you with a random other user on the wheel
And you ask them what kind of album they’re feeling, gage their taste
Snaking, not pairs

Amdusias:
ah cool!

[redacted]:
It’s a cool way to share music

Amdusias:
yeah! that's actually cool for sure
sounds like something [redacted] would like too

[redacted]:
Could easily work with any other medium too (film, books, etc)

Amdusias:
and it's also like
god I do *not* need another project hahaha
but writing the discord bot to do that is actually easy
```

### Participation

Users may have one of four participation levels:
- `ALWAYS`: they will be included in all future spins of the wheel
- `ONCE`: they will be included in the next spin of the wheel
- `INTERESTED`: they will be notified before the wheel is spun, but not actually included in the spin itself unless they re-tag to `ALWAYS` or `ONCE`
- `NEVER`: not a real level, as this is just "not actually in the user database"; `remove me` deletes oneself from the database because that makes the API simpler ;)

### Using It

First, install it as a Discord bot. The exact steps to doing this are outside the scope of this README, but [here](https://discord.com/developers/docs/getting-started) is Discord's documentation for doing so at time of writing.

The API, once it's installed, is as follows (all requests must be directed to the bot with `@recwheel`, or whatever else you named it):
- `add me once`: sign up for participating the next time the wheel is spun
- `add me always`: sign up for participating in all future spins
- `remove me`: no longer particpate in future wheel spins
- `prespin`: notifies users that the wheel is about to be spun, tags all users registered as "interested"
- `spin`: spins the wheel
- `help`: prints this menu

When `prespin` is run, all participants at all levels are notified. This gives users a chance to opt in before the wheel is spun.

When `spin` is run, all users tagged `ALWAYS` or `ONCE` are put into a list and then shuffled. Each user in this list is pointed to the next user, and the last pointed to the first. Each user should then discuss the chosen topic with the user that their arrow points to.

After `spin` is run, all users tagged as `ONCE` are moved back to `INTERESTED`.

### Copyright

(c) 2023 Ammy I guess.
