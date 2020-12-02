import discord
import numpy as np


async def send_embed(channel, title, description, footer='by 도비에몽'):
    embed = discord.Embed(title=title, description=description)
    embed.set_footer(text=footer)
    await channel.send(embed=embed)


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
