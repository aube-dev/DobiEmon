import discord
from discord.ext import commands
import os  # 이미지 접근
import glob  # 이미지 접근
from pathlib import Path  # 이미지 접근
import random  # 레식 오퍼 돌림판
import numpy as np
from openpyxl import load_workbook

# Token
token_path = os.path.dirname(os.path.abspath(__file__)) + "/token.txt"
t = open(token_path, "r", encoding="utf-8")
token = t.read().split()[0]
print("Token_key : ", token)

# channel id
channel_id_path = os.path.dirname(os.path.abspath(__file__)) + "/afk_channel_id.txt"
c = open(channel_id_path, "r")
afk_channel_id = c.read().split()[0]
print("AFK_channel_id : ", afk_channel_id)

# Settings
game = discord.Game("-도움말")
bot = commands.Bot(command_prefix='-', status=discord.Status.online, activity=game)
client = discord.Client()


r6_operator_attacker = ['AMARU', 'BLITZ', 'MONTAGNE', 'THATCHER', 'RECRUIT']
r6_operator_defender = ['CLASH', 'ORYX', 'TACHANKA', 'CAVEIRA', 'RECRUIT']
# menu = ['피자', '삼겹살', '치킨', '국밥', '중국음식', '돈가스', '김밥', '냉면', '칼국수', '김치찌개', '뼈해장국', '닭갈비', '굶기', '라면', '파워에이드 라면', '파스타']
# menu_p = [0.008, 0.01, 0.01, 0.1, 0.1, 0.1, 0.1, 0.1, 0.02, 0.1, 0.05, 0.1, 0.001, 0.1, 0.001, 0.1]

load_wb = load_workbook('./Menu.xlsx', data_only=True)
load_ws = load_wb['Menu']
menu = []
menu_p = []
menu_num = load_ws['E2'].value
for i in range(2, menu_num+2):
    menu.append(load_ws['A'+str(i)].value)
    menu_p.append(load_ws['B'+str(i)].value)


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
                    value="-메뉴 를 입력하세요.", inline=True)
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

# ---- 여기까지 이미지 크게 하는 기능

@bot.command()
async def 오퍼(ctx, arg):
    r6_operator = ''
    if arg == '공격':
        r6_operator = random.choice(r6_operator_attacker)
    elif arg == '수비':
        r6_operator = random.choice(r6_operator_defender)

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


bot.run(token)
