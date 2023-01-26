import sqlite3 as sq

from telegrambot.creation import bot

base = sq.connect('bars.db')
cur = base.cursor()


def sql_start():

    if base:
        print('Data base connected OK')
    base.execute(
        'CREATE TABLE IF NOT EXISTS places(img TEXT, name TEXT PRIMARY KEY, description TEXT)'
    )
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute(
            'INSERT INTO places VALUES (?, ?, ?)', tuple(data.values())
        )
        base.commit()


async def sql_data_base(message):
    for value in cur.execute('SELECT * FROM places').fetchall():
        await bot.send_message(
            message.from_user.id,
            f'Город: {value[0]}\nИмя заведения:{value[1]}\nОписание:{value[2]}',
        )


async def sql_read():
    return cur.execute('SELECT * FROM places').fetchall()


async def sql_delete_command(data):
    cur.execute('DELETE FROM places WHERE name == ?', (data,))
    base.commit()
