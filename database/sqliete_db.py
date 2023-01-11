import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect(('bars.db'))
    cur = base.cursor()
    if base:
        print('Data base connected OK')
    base.execute('CREATE TABLE IF NOT EXISTS places(img TEXT, name TEXT PRIMARY KEY, description TEXT, price TEXT')
    base.commit()

    async def sql_add_command(state):
        async with state.proxy() as data:
            cur.execute('INSERT INTO places VALUES (?, ?, ?, ?)', tuple(data.valuest()))
            base.commit()
