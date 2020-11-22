import discord
from discord.ext import commands
import os
import glob
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
import datetime
import asyncio

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

# Load Menu
load_wb_menu = load_workbook('./Menu.xlsx', data_only=True)
load_ws_menu = load_wb_menu['Menu']
menu = []
menu_p = []
menu_num = load_ws_menu['E2'].value
for i in range(2, menu_num+2):
    menu.append(load_ws_menu['A'+str(i)].value)
    menu_p.append(load_ws_menu['B'+str(i)].value)

# Load Restaurant
load_wb_res = load_workbook('./Restaurant.xlsx', data_only=True)
load_ws_res = load_wb_res['Restaurant']
restaurant = []
restaurant_p = []
restaurant_num = load_ws_res['E2'].value
for i in range(2, restaurant_num+2):
    restaurant.append(load_ws_res['A'+str(i)].value)
    restaurant_p.append(load_ws_res['B'+str(i)].value)

# Load Schedule
load_wb_sch = load_workbook('./Schedule.xlsx', data_only=True)
load_ws_sch = load_wb_sch['Schedule']

# Load R6 Operators - Attackers
wb_r6_a = load_workbook('./r6_operator_attackers.xlsx', data_only=True)
ws_r6_a = wb_r6_a['Attackers']
r6_operator_attacker = []
r6_operator_attacker_p = []
r6_op_a_num = ws_r6_a['M3'].value
for i in range(1, r6_op_a_num+1):
    r6_operator_attacker.append(ws_r6_a['A'+str(i)].value)
    r6_operator_attacker_p.append(ws_r6_a['J'+str(i)].value)

# Load R6 Operators - Defenders
wb_r6_d = load_workbook('./r6_operator_defenders.xlsx', data_only=True)
ws_r6_d = wb_r6_d['Defenders']
r6_operator_defender = []
r6_operator_defender_p = []
r6_op_d_num = ws_r6_d['M3'].value
for i in range(1, r6_op_d_num+1):
    r6_operator_defender.append(ws_r6_d['A'+str(i)].value)
    r6_operator_defender_p.append(ws_r6_d['J'+str(i)].value)


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
    r6_operator = ''
    if arg == '공격':
        r6_operator_rand = np.random.choice(r6_operator_attacker, size=1, p=r6_operator_attacker_p)
        r6_operator = r6_operator_rand[0]
    elif arg == '수비':
        r6_operator_rand = np.random.choice(r6_operator_defender, size=1, p=r6_operator_defender_p)
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
    menu_rand = np.random.choice(menu, size=1, p=menu_p)
    menu_final = menu_rand[0]

    embed = discord.Embed(title="당신께 추천드리는, 오늘의 메뉴는...",
                          description=menu_final + "입니다.")
    embed.set_footer(text="by 도비에몽")
    await ctx.send(embed=embed)


@bot.command()
async def 식당(ctx):
    res_rand = np.random.choice(restaurant, size=1, p=restaurant_p)
    res_final = res_rand[0]
    res_extra_message = ''
    if res_final == '당신의 집':
        res_extra_message = "메뉴는 파워에이드 라면만 허용해요."
    elif res_final.find('(') != -1:
        res_extra_message = "가서 식사만 하고 돌아오는 거에요."

    if bool(res_extra_message):
        res_extra_message = "\n" + res_extra_message

    embed = discord.Embed(title="당신께 추천드리는, 오늘의 식당은...",
                          description=res_final + "입니다." + res_extra_message)
    embed.set_footer(text="by 도비에몽")
    await ctx.send(embed=embed)


def check_schedule(num):
    if num < 1:
        return False
    else:
        return bool(load_ws_sch.cell(row=num, column=1).value)


def add_schedule(dt, name):
    idx_add_schedule = 2
    while check_schedule(idx_add_schedule):
        idx_add_schedule = idx_add_schedule + 1

    write_ws = load_wb_sch.active
    write_ws['A' + str(idx_add_schedule)] = dt.strftime('%Y-%m-%d %H:%M')
    write_ws['B' + str(idx_add_schedule)] = name

    load_wb_sch.save('./Schedule.xlsx')


def del_schedule_by_idx(schedule_index):
    del_ws = load_wb_sch.active
    del_ws['A' + str(schedule_index)] = None
    del_ws['B' + str(schedule_index)] = None
    load_wb_sch.save('./Schedule.xlsx')


async def scheduler():
    await bot.wait_until_ready()
    while True:
        idx_scheduler = 2
        while check_schedule(idx_scheduler):
            datetime_tmp = datetime.datetime.strptime(load_ws_sch['A' + str(idx_scheduler)].value, '%Y-%m-%d %H:%M')
            if datetime_tmp <= datetime.datetime.today():
                embed = discord.Embed(title=load_ws_sch['B' + str(idx_scheduler)].value,
                                      description="일정 알림입니다.\n" + datetime_tmp.strftime('%Y-%m-%d %H:%M'))
                embed.set_footer(text="by 도비에몽")
                del_schedule_by_idx(idx_scheduler)
                message_channel = bot.get_channel(schedule_channel_id)
                await message_channel.send(embed=embed)
            idx_scheduler = idx_scheduler + 1

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
    j = 2
    while check_schedule(j):
        if load_ws_sch['B' + str(j)].value == schedule_arg:
            embed = discord.Embed(title="일정 삭제가 완료되었습니다.",
                                  description="삭제한 일정 이름 : " + load_ws_sch['B' + str(j)].value + "\n"
                                              + "삭제한 일정 일시 : " + load_ws_sch['A' + str(j)].value)
            embed.set_footer(text="by 도비에몽")
            del_schedule_by_idx(j)
            await ctx.send(embed=embed)
        j = j + 1

bot.loop.create_task(scheduler())
bot.run(token)
