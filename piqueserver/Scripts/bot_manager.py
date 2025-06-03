import random
from piqueserver.commands import command
from piqueserver.core import player_joined, player_left

BOT_PREFIX = "Bot "
MAX_BOTS = 9
bots = []
players = []


def is_bot(name):
    return name.startswith(BOT_PREFIX)


def get_unused_bot_name():
    for i in range(1, MAX_BOTS + 1):
        name = f"{BOT_PREFIX}{i}"
        if name not in bots and name not in players:
            return name
    return None


def add_bot(server):
    bot_name = get_unused_bot_name()
    if bot_name:
        bots.append(bot_name)
        server.send_chat(f"{bot_name} has joined the battle!")
    return bot_name


def remove_bot(server):
    if bots:
        bot_name = bots.pop()
        server.send_chat(f"{bot_name} has left the battle!")


@player_joined
def on_player_join(player, **kwargs):
    players.append(player.name)
    remove_bot(player.protocol.server)  # Remove a bot when a real player joins


@player_left
def on_player_leave(player, **kwargs):
    if player.name in players:
        players.remove(player.name)


@command("add_bot")
def add_bot_command(player, *args):
    bot_name = add_bot(player.protocol.server)
    if bot_name:
        return f"Added {bot_name}"
    return "Max bots reached!"


@command("remove_all_bots")
def remove_all_bots_command(player, *args):
    global bots
    bots = []
    return "All bots removed!"


@command("balance_teams")
def balance_teams_command(player, *args):
    server = player.protocol.server
    team1_count = sum(1 for p in players if p.team.id == 0) + sum(1 for b in bots if "1" in b)
    team2_count = sum(1 for p in players if p.team.id == 1) + sum(1 for b in bots if "2" in b)

    while abs(team1_count - team2_count) > 1:
        if team1_count > team2_count:
            remove_bot(server)
            team1_count -= 1
        else:
            add_bot(server)
            team2_count += 1

    return "Teams balanced!" 
