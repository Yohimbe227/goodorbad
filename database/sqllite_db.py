import sqlite3 as sq

from creation import bot


def sql_start():
    global base, cur
    base = sq.connect('bars.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK')
    base.execute(
        'CREATE TABLE IF NOT EXISTS places(img TEXT, name TEXT PRIMARY KEY, description TEXT)')
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO places VALUES (?, ?, ?)',
                    tuple(data.values()))
        base.commit()


async def sql_data_base(message):
    for ret in cur.execute('SELECT * FROM places').fetchall():
        await bot.send_photo(message.from_user.id, ret[0],
                             f'{ret[1]}\nГорода: {ret[2]}\nИмя заведения {ret[-1]}')


async def sql_read():
    return cur.execute('SELECT * FROM place').fetchall()


async def sql_delete_command(data):
    cur.execute('DELETE FROM place WHERE name == ?', (data,))
    base.commit()
