from config import (
    FAUNA_KEY,
)
from faunadb.client import FaunaClient
from faunadb import query as q
from faunadb.errors import NotFound
from datetime import datetime

# fauna client config
client = FaunaClient(secret=FAUNA_KEY, domain='db.eu.fauna.com', schema='https')


class BotDB:
    def __init__(self):
        """Инициализация соединения с бд"""
        self.client = FaunaClient(secret=FAUNA_KEY, domain='db.eu.fauna.com', schema='https')

    def user_exists(self, user_id):
        """Проверка, есть ли юзер в бд"""
        try:
            self.client.query(
                q.get(
                    q.match(
                        q.index("user_by_id"),
                        user_id
                    )
                )
            )
            res = True
        except NotFound:
            res = False
        return res

    def add_user(self, user_id, user_name, is_admin=False):
        """Добавляем юзера в бд"""
        return self.client.query(
            q.create(q.collection('Users'), {
                "data": {
                    "name": user_name,
                    "is_admin": is_admin,
                    "user_id": user_id
                }
            })
        )

    def get_rooms(self):
        res = []
        try:
            temp_res = []
            temp_res.append((self.client.query(
                q.map_(
                    lambda x: q.get(x),
                    q.paginate(
                        q.match(
                            q.index("all_rooms")
                        )
                    )
                )
            ))['data'])

            for el in temp_res[0]:
                res.append(el['data'])

        except NotFound:
            res = []
        return res

    def get_room_id(self, room_name):
        """"Получаем room_id комнаты в базе по ее имени"""
        try:
            res = self.client.query(
                q.get(
                    q.match(
                        q.index("room_by_name"),
                        room_name
                    )
                )
            )['data']['room_id']
        except NotFound:
            res = ""
        return res

    def get_room_name(self, room_id):
        """"Получаем room_name комнаты в базе по ее id"""
        try:
            res = self.client.query(
                q.get(
                    q.match(
                        q.index("room_by_id"),
                        room_id
                    )
                )
            )['data']['name']
        except NotFound:
            res = ""
        return res

    def get_user_name(self, user_id):
        try:
            res = self.client.query(
                q.get(
                    q.match(
                        q.index("user_by_id"),
                        user_id
                    )
                )
            )['data']['name']
        except NotFound:
            res = False
        return res

    def get_entries(self):
        res = []
        try:
            temp_res = []
            temp_res.append((self.client.query(
                q.map_(
                    lambda x: q.get(x),
                    q.paginate(
                        q.match(
                            q.index("all_entries")
                        )
                    )
                )
            ))['data'])

            for el in temp_res[0]:
                res.append(el['data'])

        except NotFound:
            res = []
        return res

    def add_entry(self, user_id, room_name, date, time):
        """Добавляем запись на аренду"""
        e_list = self.get_entries()

        e_id = [0]
        for el in e_list:
            e_id.append(int(el['entry_id']))

        return self.client.query(
            q.create(q.collection('Entries'), {
                "data": {
                    "entry_id": max(e_id)+1,
                    "date": date,
                    "time": time,
                    "room_name": room_name,
                    "room_id": self.get_room_id(room_name),
                    "user_id": user_id,
                }
            })
        )

    def delete_entry(self, entry_id):
        """Удаляем запись на аренду"""
        refEntry = self.client.query(
            q.get(
                q.match(
                    q.index("entry_by_id"),
                    entry_id
                )
            )
        )['ref']
        return self.client.query(
            q.delete(
                refEntry
            )
        )

    def get_user_entries(self, user_id):
        """Получаем записи юзера"""
        res = []
        try:
            temp_res = []
            temp_res.append((self.client.query(
                q.map_(
                    lambda x: q.get(x),
                    q.paginate(
                        q.match(
                            q.index("entries_by_user"),
                            user_id
                        )
                    )
                )
            ))['data'])

            for el in temp_res[0]:
                if datetime.strptime(el['data']['date'], '%d/%m/%Y') >= datetime.today():
                    res.append(el['data'])

        except NotFound:
            res = []

        return res

    def get_room_entries(self, room_id):
        """Получаем записи в комнату"""
        res = []
        try:
            temp_res = []
            temp_res.append((self.client.query(
                q.map_(
                    lambda x: q.get(x),
                    q.paginate(
                        q.match(
                            q.index("entries_by_room"),
                            room_id
                        )
                    )
                )
            ))['data'])

            for el in temp_res[0]:
                if datetime.strptime(el['data']['date'], '%d/%m/%Y') >= datetime.today():
                    res.append(el['data'])

        except NotFound:
            res = []
        return res

    def get_room_entries_dates(self, room_name):
        """Получаем все даты записи в комнату"""
        res = []
        tempRes = self.get_room_entries(self.get_room_id(room_name))

        for el in tempRes:
            if datetime.strptime(el['date'], '%d/%m/%Y') >= datetime.today():
                res.append(el['date'])
        return res

    def get_rooms_names(self):
        """Получаем имена всех комнат"""
        res = []
        for el in self.get_rooms():
            res.append(el['name'])
        return res

    def add_room(self, room_name):
        r_list = self.get_rooms()

        r_id = [0]
        for el in r_list:
            r_id.append(int(el['room_id']))

        return self.client.query(
            q.create(q.collection('Rooms'), {
                "data": {
                    "name": room_name,
                    "room_id": max(r_id)+1
                }
            })
        )

    def delete_room(self, room_id):
        refRoom = self.client.query(
            q.get(
                q.match(
                    q.index("room_by_id"),
                    room_id
                )
            )
        )['ref']
        return self.client.query(
            q.delete(
                refRoom
            )
        )


