import discord
import os
import sqlite3
import random

from dotenv import load_dotenv
from enum import IntEnum

DB_NAME = os.environ.get("DB_PATH") or "/data/recs.db"

HELP_TEXT = """
Hi! Please choose from one of the following:

- `add me once`: sign up for participating the next time the wheel is spun
- `add me always`: sign up for participating in all future spins
- `remove me`: no longer particpate in future wheel spins
- `prespin`: notifies users that the wheel is about to be spun, tags all users registered as "interested"
- `spin`: spins the wheel
- `help`: prints this menu
"""

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

class ParticipationLevel(IntEnum):
    # we don't actually need a `never` because `remove me` just deletes you from the database
    ONCE = 1
    ALWAYS = 2
    INTERESTED = 3

@client.event
async def on_ready():
    print(f"Authenticated as {client.user}")

@client.event
async def on_message(message):
    # some no-ops first, let's try to avoid infinite recursions here :)
    # don't bother logging in either case because they're never really meaningful logs
    if message.author == client.user:
        return

    if not client.user.mentioned_in(message):
        return

    bot_id = client.user.id
    actual_content = message.content.replace(f"<@{bot_id}>", "").strip()
    author_id = message.author.id

    conn = sqlite3.connect(DB_NAME)
    match actual_content:
        case "help":
            await message.channel.send(HELP_TEXT)
        case "add me once":
            # upsert so users can trivially switch between participation levels without needed to delete themselves
            conn.execute("INSERT OR REPLACE INTO users (user_id, participation) VALUES (?, ?)", (author_id, ParticipationLevel.ONCE.value))
            print(f"Added user {author_id} once")
            await message.channel.send(f"Okay, <@{author_id}>, I have added you for the next spin")
        case "add me always":
            conn.execute("INSERT OR REPLACE INTO users (user_id, participation) VALUES (?, ?)", (author_id, ParticipationLevel.ALWAYS.value))
            print(f"Added user {author_id} always")
            await message.channel.send(f"Okay, <@{author_id}>, I have added you to all future spins")
        case "add me interested":
            conn.execute("INSERT OR REPLACE INTO users (user_id, participation) VALUES (?, ?)", (author_id, ParticipationLevel.INTERESTED.value))
            print(f"Added user {author_id} interested")
            await message.channel.send(f"Okay, <@{author_id}>, I have marked you as interested")
        case "remove me":
            conn.execute("DELETE FROM users WHERE user_id = ?", (author_id,))
            print(f"Deleted user {author_id}")
            await message.channel.send(f"Okay, <@{author_id}>, I have removed you from all future spins")
        case "prespin":
            always = []
            once = []
            interested = []
            cursor = conn.execute("SELECT user_id, participation FROM users")
            for row in cursor.fetchall():
                user_id = row[0]
                participation = ParticipationLevel(row[1])
                if participation == ParticipationLevel.ONCE:
                    once.append(user_id)
                elif participation == ParticipationLevel.ALWAYS:
                    always.append(user_id)
                else: #interested
                    interested.append(user_id)
            # maybe it'd be nice to sort the names alphabetically here but shrug
            # everyone's going to get pinged anyway so ¯\_(ツ)_/¯
            await message.channel.send(f"Always: {' '.join(['<@' + s + '>' for s in always])}")
            await message.channel.send(f"Once: {' '.join(['<@' + s + '>' for s in once])}")
            await message.channel.send(f"Interested: {' '.join(['<@' + s + '>' for s in interested])}")
        case "spin":
            # we don't actually need a filter on participation levels but we need the field
            # we're just grabbing every user after all
            # so we can distinguish how to act on the two types later
            cursor = conn.execute("SELECT user_id, participation FROM users")
            always = []
            once = []
            for row in cursor.fetchall():
                user_id = row[0]
                participation = ParticipationLevel(row[1])
                if participation == ParticipationLevel.ONCE:
                    once.append(user_id)
                elif participation == ParticipationLevel.ALWAYS:
                    always.append(user_id)
                # interested users are irrelevant here, they didn't opt in for this round
            all_participants = once + always
            # don't let anyone get past here if there's no one in either list
            if len(all_participants) == 0:
                print("There are no participants, will not spin")
                return
            random.shuffle(all_participants)

            # we've shuffled everyone, we can now point everyone at the next person
            msg = ""
            for participant in all_participants:
                msg += f"<@{participant}> -> "
            # point the last participant back to the first to complete the circle
            # we already added a trailing arrow so we can just append
            # this probably gets extremely gross if there are a million people but shrug
            msg += f"<@{all_participants[0]}>"
            await message.channel.send(msg)

            # okay, we're done, let's move the "once" participants back to "never"
            for participant in once:
                conn.execute("UPDATE users SET participation = ? WHERE user_id = ?", (ParticipationLevel.INTERESTED, author_id,))
                print(f"Moving user {author_id} back to INTERESTED")
        case _:
            await message.channel.send(f"Sorry, <@{author_id}>, I don't understand. Have you tried asking for `help`?")
    conn.commit()
    conn.close()

def maybe_init_db():
    if not os.path.exists(DB_NAME):
        print("No database found, initializing one...")
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        conn.execute('''CREATE TABLE users
             (user_id TEXT PRIMARY KEY,
              participation INTEGER);''')
        conn.commit()
        conn.close()
        print("DB initialized")

if __name__ == "__main__":
    load_dotenv()
    print("Environment loaded...")
    maybe_init_db()
    print("Database initialized, if necessary...")
    client.run(os.getenv('BOT_TOKEN'))
