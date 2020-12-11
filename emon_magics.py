import discord
import numpy as np
import asyncio


async def send_embed(channel, title, description, footer='by 도비에몽'):
    embed = discord.Embed(title=title, description=description)
    embed.set_footer(text=footer)
    message = await channel.send(embed=embed)
    return message


def db_to_list(db, table, is_random, query_str=''):
    with db:
        cur = db.cursor()
        if bool(query_str):
            query_str = ' ' + query_str
        execute_str = 'SELECT * FROM ' + table + query_str
        cur.execute(execute_str)
        rows = cur.fetchall()

        if is_random:
            result = []
            result_p = []
            for row in rows:
                result.append(row[1])
                result_p.append(row[2])
            return result, result_p
        else:
            return rows


def random(list1d, probability):
    rand = np.random.choice(list1d, size=1, p=probability)
    return rand[0]


def run_coroutine(coroutine: asyncio.coroutine, bot):
    fut = asyncio.run_coroutine_threadsafe(coroutine, bot.loop)
    return fut.result()


async def check_reaction_users(message, reaction_emoji=None):
    users_list = []
    if not reaction_emoji:
        print('case 1')
        for reaction in message.reactions:
            async for user in reaction.users():
                users_list.append(user.id)
    else:
        print('case 2')
        for reaction in message.reactions:
            if str(reaction.emoji) == reaction_emoji:
                async for user in reaction.users():
                    users_list.append(user.id)
    # deduplication
    users_set = set(users_list)
    users_list = list(users_set)
    return users_list
