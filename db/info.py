from __future__ import annotations
import aiosqlite
from collections import namedtuple


class Info:
    conn: aiosqlite.Connection
    cur: aiosqlite.Cursor

    async def setup(self) -> None:
        self.conn = await aiosqlite.connect("./dbs/info.db")
        self.cur = await self.conn.cursor()
        await self.cur.execute('''CREATE TABLE IF NOT EXISTS info(id INTEGER PRIMARY KEY NOT NULL, kick_thresh INTEGER, ban_thresh INTEGER)''')
        await self.conn.commit()
        self.named_tuple = namedtuple("guild", ["id", "kick_thresh", "ban_thresh"])
    
    async def all_records(self):
        _data = await self.cur.execute("SELECT * FROM warnings")
        return await _data.fetchall()

    async def read(self, guild_id: int) -> namedtuple[...]:
        u_data = await self.cur.execute('''SELECT * FROM info WHERE id = ?''', (guild_id,))
        _user_data = await u_data.fetchone()

        if not _user_data: return None

        return self.named_tuple(_user_data[0], _user_data[1], _user_data[2],)
    
    async def create_acc(self, guild_id: int, kick_thresh: int, ban_thresh: int) -> namedtuple[...]:
        _check = await self.read(guild_id)
        if _check:
            return self.named_tuple(_check[0], _check[1], _check[2])
        await self.cur.execute('''INSERT INTO info(id, kick_thresh, ban_thresh) VALUES(?, ?, ?)''', (guild_id, kick_thresh, ban_thresh))
        await self.conn.commit()
        return self.named_tuple(guild_id, kick_thresh, ban_thresh)
    
    async def update(self, guild_id: int, *, kick_thresh: int=None, ban_thresh: int=None) -> bool:
        if kick_thresh:
            await self.cur.execute("UPDATE info SET kick_thresh = ? WHERE id = ?", (kick_thresh, guild_id))
            await self.conn.commit()
            return True            
        if ban_thresh:
            await self.cur.execute("UPDATE info SET ban_thresh = ? WHERE id = ?", (ban_thresh, guild_id))
            await self.conn.commit()
            return True