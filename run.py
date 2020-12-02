import discord
from discord.ext import commands

import glob
from pathlib import Path

import sqlite3
import json

import datetime

import emon_magics as dem
import emon_schedule as sch

# --------------------------------------------------

# Information
with open('information.json') as json_file:
    json_data = json.load(json_file)
    token = str(json_data['token'])
    schedule_channel_id = int(json_data['schedule_channel_id'])

# Settings
game = discord.Game("-도움말")
bot = commands.Bot(command_prefix='-', status=discord.Status.online, activity=game)
client = discord.Client()

# Database
db = sqlite3.connect("dobiemon.db")

# --------------------------------------------------


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


# --------------------------------------------------


def extension_check(filename):
    file_list = glob.glob('./images/*')
    correct_list = [file for file in file_list if file.find(filename) != -1]
    try:
        ext = Path(correct_list[0]).suffix
    except:
        return 'error: not found'
    return ext


@bot.command()
async def 커져라(ctx, arg):
    extension = extension_check(arg)
    if extension == 'error: not found':
        await dem.send_embed(ctx, "오류가 발생했습니다.", "해당 이름의 이미지를 찾을 수 없습니다.")
    else:
        image_path = "images/" + arg + extension
        image = discord.File(image_path)
        try:
            await ctx.send(file=image)
        except:
            await dem.send_embed(ctx, "오류가 발생했습니다.", "사진 용량이 너무 큽니다.")


@bot.command()
async def 오퍼(ctx, arg):
    # 0 : Attacker / 1 : Defender
    r6_operator = ''
    if arg == '공격':
        r6_op_a, r6_op_a_p = dem.db_to_list(db, 'R6_Operator', True, 'WHERE Type = 0')
        r6_operator = dem.random(r6_op_a, r6_op_a_p)
    elif arg == '수비':
        r6_op_d, r6_op_d_p = dem.db_to_list(db, 'R6_Operator', True, 'WHERE Type = 1')
        r6_operator = dem.random(r6_op_d, r6_op_d_p)

    if r6_operator == '':
        await dem.send_embed(ctx, "올바른 형식이 아닙니다.", "도움말을 참조해 다시 입력해 주세요.")
    else:
        await dem.send_embed(ctx, "당신께 추천드리는, 이번 게임에 선택할 오퍼레이터는...", r6_operator + "입니다.")


@bot.command()
async def 메뉴(ctx):
    menu, menu_p = dem.db_to_list(db, 'Menu', True)
    menu_final = dem.random(menu, menu_p)
    await dem.send_embed(ctx, "당신께 추천드리는, 오늘의 메뉴는...", menu_final + "입니다.")


@bot.command()
async def 식당(ctx):
    # 0 : Basic / 1 : Far / 2 : Your House
    res_rows = dem.db_to_list(db, 'Restaurant', False)
    restaurant = []
    restaurant_p = []
    for row in res_rows:
        restaurant.append((row[1], row[3]))
        restaurant_p.append(row[2])
    res_rand = dem.random(len(restaurant), restaurant_p)
    res_final = restaurant[res_rand[0]][0]
    res_extra_message = ''
    if restaurant[res_rand[0]][1] == 2:
        res_extra_message = "메뉴는 파워에이드 라면만 허용해요."
    elif restaurant[res_rand[0]][1] == 1:
        res_extra_message = "가서 식사만 하고 돌아오는 거에요."

    if bool(res_extra_message):
        res_extra_message = "\n" + res_extra_message

    await dem.send_embed(ctx, "당신께 추천드리는, 오늘의 식당은...", res_final + "입니다." + res_extra_message)


@bot.command()
async def 일정(ctx, date_arg, time_arg, schedule_arg):
    schedule_datetime_tmp = datetime.datetime.strptime(date_arg + '-' + time_arg, '%Y%m%d-%H%M')
    sch.add_schedule(db, schedule_datetime_tmp, schedule_arg)
    await dem.send_embed(ctx, "일정 알림이 추가되었습니다.",
                         "일정 이름 : " + schedule_arg + "\n"
                         + "일정 일시 : " + schedule_datetime_tmp.strftime('%Y-%m-%d %H:%M'))


@bot.command()
async def 일정삭제(ctx, schedule_arg):
    sch_rows = dem.db_to_list(db, 'Schedule', False)
    for row in sch_rows:
        if row[1] == schedule_arg:
            await dem.send_embed(ctx, "일정 삭제가 완료되었습니다.",
                                 "삭제한 일정 이름 : " + row[1] + "\n"
                                 + "삭제한 일정 일시 : " + row[2])
            sch.del_schedule_by_idx(db, row[0])


@bot.command()
async def 소라고둥(ctx, arg1, arg2):
    srgd = dem.random([arg1, arg2], [0.5, 0.5])
    await dem.send_embed(ctx, "둘 중에서...", srgd + " 선택해.", "by 마법의 소라고둥 in 도비에몽")


@bot.command()
async def 처벌(ctx):
    ban_list = ['2초', '5초', '10초', '1분', '2분', '5분', '10분', '15분', '30분', '1시간', '용서']
    ban_list_p = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05]
    ban_result = dem.random(ban_list, ban_list_p)
    await dem.send_embed(ctx, "이번 사건은...", ban_result + ".")

# --------------------------------------------------

bot.loop.create_task(sch.scheduler(db, bot))
bot.run(token)
