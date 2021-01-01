import asyncio
import datetime
import json

import emon_magics as dem

# --------------------------------------------------

with open('information.json') as json_file:
    json_data = json.load(json_file)
    SCHEDULE_CHANNEL_ID = int(json_data['schedule_channel_id'])
    SCHEDULE_NOTI_CHANNEL_ID = int(json_data['schedule_noti_channel_id'])

# --------------------------------------------------


async def add_schedule(db, dt, name_str, repeat, reaction_message, bot):
    repeat_str = ''
    if repeat:
        repeat_str += '\n' + '반복 주기 : ' + str(repeat) + '일'

    message_id = 0
    if reaction_message:
        message_id += reaction_message
    else:
        schedule_channel = bot.get_channel(SCHEDULE_CHANNEL_ID)
        message = await dem.send_embed(schedule_channel, name_str,
                                       "일정이 추가되었습니다.\n\n" +
                                       "일정 일시 : " + dt.strftime('%Y-%m-%d %H:%M') +
                                       repeat_str +
                                       "\n\n이 일정의 알림을 받고 싶다면 이 메시지에 반응을 달아 주세요.")
        message_id += message.id

    with db:
        cur = db.cursor()
        add_sch_dt = dt.strftime('%Y-%m-%d %H:%M')
        add_sch_db_str = 'INSERT INTO Schedule (Schedule_Name, Datetime, Message, Repeat) VALUES (?, ?, ?, ?)'
        cur.execute(add_sch_db_str, (name_str, add_sch_dt, message_id, repeat))
        db.commit()


async def del_schedule_by_idx(db, schedule_index, message_id, bot):
    with db:
        cur = db.cursor()
        del_sch_db_str = 'DELETE FROM Schedule WHERE id = ?'
        cur.execute(del_sch_db_str, (schedule_index,))
        db.commit()

    schedule_channel = bot.get_channel(SCHEDULE_CHANNEL_ID)
    message = await schedule_channel.fetch_message(message_id)
    await message.delete()


def modify_schedule_by_idx(db, schedule_index, after_name, after_datetime, after_repeat):
    modify = {'name': True, 'datetime': True, 'repeat': True}
    if after_name == '그대로':
        modify['name'] = False
    if after_datetime == '그대로':
        modify['datetime'] = False
    if after_repeat == '그대로':
        modify['repeat'] = False

    with db:
        cur = db.cursor()
        modify_sch_db_str = 'UPDATE Schedule SET '
        if modify['name']:
            cur.execute(modify_sch_db_str + "Schedule_Name = '" + after_name + "' WHERE id = ?",  (schedule_index,))
        if modify['datetime']:
            cur.execute(modify_sch_db_str + "Datetime = '" + after_datetime + "' WHERE id = ?",  (schedule_index,))
        if modify['repeat']:
            cur.execute(modify_sch_db_str + "Repeat = " + after_repeat + " WHERE id = ?",  (schedule_index,))
        db.commit()

    return modify


async def scheduler(db, bot):
    await bot.wait_until_ready()
    while True:
        sch_rows = dem.db_to_list(db, 'Schedule', False)
        for row in sch_rows:
            datetime_tmp = datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M')
            if datetime_tmp <= datetime.datetime.today():
                # check reactions
                schedule_channel = bot.get_channel(SCHEDULE_CHANNEL_ID)
                message = await schedule_channel.fetch_message(row[3])
                users_list = await dem.check_reaction_users(message)

                mention_users_str = ''
                for user in users_list:
                    mention_users_str += '<@' + str(user) + '> '

                # send notification
                schedule_noti_channel = bot.get_channel(SCHEDULE_NOTI_CHANNEL_ID)
                await dem.send_embed(schedule_noti_channel, row[1],
                                     "일정 알림입니다.\n" + datetime_tmp.strftime('%Y-%m-%d %H:%M'))
                if mention_users_str:
                    await schedule_noti_channel.send(mention_users_str)

                # check if it should be repeated
                if row[4] == 0:
                    await del_schedule_by_idx(db, row[0], row[3], bot)
                else:
                    next_datetime = datetime_tmp + datetime.timedelta(days=row[4])
                    await add_schedule(db, next_datetime, row[1], row[4], reaction_message=row[3], bot=bot)
                    await del_schedule_by_idx(db, row[0], row[3], bot)

        await asyncio.sleep(5)
