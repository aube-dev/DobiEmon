import asyncio
import datetime
import json

import emon_magics as dem

# --------------------------------------------------

with open('information.json') as json_file:
    json_data = json.load(json_file)
    SCHEDULE_CHANNEL_ID = int(json_data['schedule_channel_id'])

# --------------------------------------------------


def add_schedule(db, dt, name_str):
    with db:
        cur = db.cursor()
        add_sch_dt = dt.strftime('%Y-%m-%d %H:%M')
        add_sch_db_str = 'INSERT INTO Schedule (Schedule_Name, Datetime) VALUES (?, ?)'
        cur.execute(add_sch_db_str, (name_str, add_sch_dt))
        db.commit()


def del_schedule_by_idx(db, schedule_index):
    with db:
        cur = db.cursor()
        del_sch_db_str = 'DELETE FROM Schedule WHERE id = ?'
        cur.execute(del_sch_db_str, (schedule_index,))
        db.commit()


async def scheduler(db, bot):
    await bot.wait_until_ready()
    while True:
        sch_rows = dem.db_to_list(db, 'Schedule', False)
        for row in sch_rows:
            datetime_tmp = datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M')
            if datetime_tmp <= datetime.datetime.today():
                schedule_channel = bot.get_channel(SCHEDULE_CHANNEL_ID)
                await dem.send_embed(schedule_channel, row[1],
                                     "일정 알림입니다.\n" + datetime_tmp.strftime('%Y-%m-%d %H:%M'))
                del_schedule_by_idx(db, row[0])

        await asyncio.sleep(5)
