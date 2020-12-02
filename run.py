import discord
from discord.ext import commands
import os
import glob
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
import datetime
import asyncio
import sqlite3

# Token
token_path = os.path.dirname(os.path.abspath(__file__)) + "/token.txt"
t = open(token_path, "r", encoding="utf-8")
token = t.read().split()[0]
print("Token_key : ", token)

# Settings
game = discord.Game("-도움말")
bot = commands.Bot(command_prefix='-', status=discord.Status.online, activity=game)
client = discord.Client()

# Schedule Channel id
schedule_channel_id_path = os.path.dirname(os.path.abspath(__file__)) + "/schedule_channel_id.txt"
sci = open(schedule_channel_id_path, "r", encoding="utf-8")
schedule_channel_id = int(sci.read().split()[0])
print("Schedule Channel ID : ", schedule_channel_id)

# Database
db = sqlite3.connect("dobiemon.db")


def extension_check(filename):
    file_list = glob.glob('./images/*')
    # print(file_list)
    correct_list = [file for file in file_list if file.find(filename) != -1]
    try:
        ext = Path(correct_list[0]).suffix
    except:
        return 'error: not found'
    return ext


@bot.event
async def on_ready():
    print("봇 시작")


@bot.command()
async def 도움말(ctx):
    embed = discord.Embed()
    embed.add_field(name="이모티콘 이미지를 보내려면...",
                    value="-커져라 를 입력하고 한 칸 띄어쓰기 한 뒤, 원하는 이모티콘 이름을 쓰세요.\nEX) -커져라 blob_excited", inline=False)
    embed.add_field(name="레식 오퍼레이터를 랜덤으로 뽑고 싶다면...",
                    value="-오퍼 를 입력하고 한 칸 띄어쓰기 한 뒤, 공격/수비 중 하나를 입력하세요.\nEX) -오퍼 공격", inline=False)
    embed.add_field(name="오늘의 메뉴를 뽑고 싶다면...",
                    value="-메뉴 를 입력하세요.", inline=False)
    embed.add_field(name="오늘의 식당을 뽑고 싶다면...",
                    value="-식당 을 입력하세요.", inline=False)
    embed.add_field(name="알림을 받고 싶은 일정을 추가하려면...",
                    value="-일정 을 입력하고 한 칸 띄어쓰기 한 뒤, YYYYMMDD 형식으로 날짜를 입력하고, "
                          + "한 칸 띄어쓰기 한 뒤, HHMM 형식으로 시각을 입력하고, 한 칸 띄어쓰기 한 뒤, 일정 이름을 입력하세요."
                    + "\nEX) -일정 20201123 1300 검단모임 : 2020년 11월 23일, 13시 00분으로, 검단모임 이라는 이름의 일정 설정", inline=False)
    embed.add_field(name="이미 등록되어 있는 일정을 삭제하려면...",
                    value="-일정삭제 를 입력하고 한 칸 띄어쓰기 한 뒤, 삭제할 일정의 이름을 입력하세요."
                    + "\nEX) -일정삭제 검단모임"
                    + "\n주의) 같은 이름을 가진 다른 일정이 있다면 모두 삭제됩니다.", inline=False)
    embed.add_field(name="둘 중 하나를 랜덤으로 뽑고 싶다면...",
                    value="-소라고둥 을 입력하고 한 칸 띄어쓰기 한 뒤, 뽑고 싶은 것 중 하나를 입력하고, "
                          + "한 칸 띄어쓰기 한 뒤, 나머지 하나를 입력하세요.\n" + "EX) -소라고둥 짜장면 짬뽕", inline=False)
    embed.set_footer(text="by 도비에몽")
    await ctx.send(embed=embed)


@bot.command()
async def 커져라(ctx, arg):
    extension = extension_check(arg)
    if extension == 'error: not found':
        embed = discord.Embed(title="오류가 발생했습니다.",
                              description="해당 이름의 이미지를 찾을 수 없습니다.")
        embed.set_footer(text="by 도비에몽")
        await ctx.send(embed=embed)
    else:
        image_path = "images/" + arg + extension
        image = discord.File(image_path)
        try:
            await ctx.send(file=image)
        except:
            embed_tmp = discord.Embed(title="오류가 발생했습니다.",
                                      description="사진 용량이 너무 큽니다.")
            embed_tmp.set_footer(text="by 도비에몽")
            await ctx.send(embed=embed_tmp)


@bot.command()
async def 오퍼(ctx, arg):
    with db:
        # 0 : Attacker
        # 1 : Defender
        r6_operator = ''
        cur = db.cursor()
        if arg == '공격':
            cur.execute('SELECT * FROM R6_Operator WHERE Type = 0')
            r6_op_a_rows = cur.fetchall()
            r6_op_a = []
            r6_op_a_p = []
            for row in r6_op_a_rows:
                r6_op_a.append(row[1])
                r6_op_a_p.append(row[2])
            r6_operator_rand = np.random.choice(r6_op_a, size=1, p=r6_op_a_p)
            r6_operator = r6_operator_rand[0]
        elif arg == '수비':
            cur.execute('SELECT * FROM R6_Operator WHERE Type = 1')
            r6_op_d_rows = cur.fetchall()
            r6_op_d = []
            r6_op_d_p = []
            for row in r6_op_d_rows:
                r6_op_d.append(row[1])
                r6_op_d_p.append(row[2])
            r6_operator_rand = np.random.choice(r6_op_d, size=1, p=r6_op_d_p)
            r6_operator = r6_operator_rand[0]

        if r6_operator == '':
            embed = discord.Embed(title="올바른 형식이 아닙니다.",
                                  description="도움말을 참조해 다시 입력해 주세요.")
            embed.set_footer(text="by 도비에몽")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="당신께 추천드리는, 이번 게임에 선택할 오퍼레이터는...",
                                  description=r6_operator + "입니다.")
            embed.set_footer(text="by 도비에몽")
            await ctx.send(embed=embed)


@bot.command()
async def 메뉴(ctx):
    with db:
        cur = db.cursor()
        cur.execute('SELECT * FROM Menu')
        menu_rows = cur.fetchall()
        menu = []
        menu_p = []
        for row in menu_rows:
            menu.append(row[1])
            menu_p.append(row[2])
        menu_rand = np.random.choice(menu, size=1, p=menu_p)
        menu_final = menu_rand[0]

        embed = discord.Embed(title="당신께 추천드리는, 오늘의 메뉴는...",
                              description=menu_final + "입니다.")
        embed.set_footer(text="by 도비에몽")
        await ctx.send(embed=embed)


@bot.command()
async def 식당(ctx):
    with db:
        # 0 : Basic
        # 1 : Far
        # 2 : Your House
        cur = db.cursor()
        cur.execute('SELECT * FROM Restaurant')
        res_rows = cur.fetchall()
        restaurant = []
        restaurant_p = []
        for row in res_rows:
            restaurant.append((row[1], row[3]))
            restaurant_p.append(row[2])
        res_rand = np.random.choice(len(restaurant), size=1, p=restaurant_p)
        res_final = restaurant[res_rand[0]][0]
        res_extra_message = ''
        if restaurant[res_rand[0]][1] == 2:
            res_extra_message = "메뉴는 파워에이드 라면만 허용해요."
        elif restaurant[res_rand[0]][1] == 1:
            res_extra_message = "가서 식사만 하고 돌아오는 거에요."

        if bool(res_extra_message):
            res_extra_message = "\n" + res_extra_message

        embed = discord.Embed(title="당신께 추천드리는, 오늘의 식당은...",
                              description=res_final + "입니다." + res_extra_message)
        embed.set_footer(text="by 도비에몽")
        await ctx.send(embed=embed)


def add_schedule(dt, name_str):
    with db:
        cur = db.cursor()
        add_sch_dt = dt.strftime('%Y-%m-%d %H:%M')
        add_sch_db_str = 'INSERT INTO Schedule (Schedule_Name, Datetime) VALUES (?, ?)'
        cur.execute(add_sch_db_str, (name_str, add_sch_dt))
        db.commit()


def del_schedule_by_idx(schedule_index):
    with db:
        cur = db.cursor()
        del_sch_db_str = 'DELETE FROM Schedule WHERE id = ?'
        cur.execute(del_sch_db_str, (schedule_index,))
        db.commit()


async def scheduler():
    await bot.wait_until_ready()
    while True:
        with db:
            cur = db.cursor()
            cur.execute('SELECT * FROM Schedule')
            sch_rows = cur.fetchall()
            for row in sch_rows:
                datetime_tmp = datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M')
                if datetime_tmp <= datetime.datetime.today():
                    embed = discord.Embed(title=row[1],
                                          description="일정 알림입니다.\n" + datetime_tmp.strftime('%Y-%m-%d %H:%M'))
                    embed.set_footer(text="by 도비에몽")
                    del_schedule_by_idx(row[0])
                    message_channel = bot.get_channel(schedule_channel_id)
                    await message_channel.send(embed=embed)

        await asyncio.sleep(5)


@bot.command()
async def 일정(ctx, date_arg, time_arg, schedule_arg):
    schedule_datetime_tmp = datetime.datetime.strptime(date_arg + '-' + time_arg, '%Y%m%d-%H%M')
    add_schedule(schedule_datetime_tmp, schedule_arg)

    embed = discord.Embed(title="일정 알림이 추가되었습니다.",
                          description="일정 이름 : " + schedule_arg + "\n"
                                      + "일정 일시 : " + schedule_datetime_tmp.strftime('%Y-%m-%d %H:%M'))
    embed.set_footer(text="by 도비에몽")
    await ctx.send(embed=embed)


@bot.command()
async def 일정삭제(ctx, schedule_arg):
    with db:
        cur = db.cursor()
        cur.execute('SELECT * FROM Schedule')
        sch_rows = cur.fetchall()
        for row in sch_rows:
            if row[1] == schedule_arg:
                embed = discord.Embed(title="일정 삭제가 완료되었습니다.",
                                      description="삭제한 일정 이름 : " + row[1] + "\n"
                                                  + "삭제한 일정 일시 : " + row[2])
                embed.set_footer(text="by 도비에몽")
                del_schedule_by_idx(row[0])
                await ctx.send(embed=embed)


@bot.command()
async def 소라고둥(ctx, arg1, arg2):
    srgd_list = [arg1, arg2]
    srgd_rand = np.random.choice(srgd_list, size=1)
    srgd = srgd_rand[0]

    embed = discord.Embed(title="둘 중에서...",
                          description=srgd + " 선택해.")
    embed.set_footer(text="by 마법의 소라고둥 in 도비에몽")
    await ctx.send(embed=embed)


@bot.command()
async def 처벌(ctx):
    ban_list = ['2초', '5초', '10초', '1분', '2분', '5분', '10분', '15분', '30분', '1시간', '용서']
    ban_list_p = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05]
    ban_rand = np.random.choice(ban_list, size=1, p=ban_list_p)
    ban_result = ban_rand[0]

    embed = discord.Embed(title="이번 사건은...",
                          description=ban_result + "만큼 처벌해요.")
    embed.set_footer(text="by 도비에몽")
    await ctx.send(embed=embed)

bot.loop.create_task(scheduler())
bot.run(token)
