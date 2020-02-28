import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker


class ServerDatabase:
    class Users:
        def __init__(self, username):
            self.id = None
            self.username = username
            self.last_login = datetime.datetime.now(tz=None)

        def __repr__(self):
            time_format = "%Y-%m-%d %H:%M:%S"
            return f"id: #{self.id}, username: {self.username}, last_login: {self.last_login:{time_format}}"

    class ActiveUser:
        def __init__(self, user_id, ip_address, port):
            self.id = None
            self.user_id = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = datetime.datetime.now()

        def __repr__(self):
            time_format = "%Y-%m-%d %H:%M:%S"
            return f"id: #{self.user_id}, " \
                   f"from IP: {self.ip_address}:{self.port}, " \
                   f"login_time: {self.login_time:{time_format}}"

    class LoginHistory:
        def __init__(self, user_id, ip_address, port):
            self.id = None
            self.user_id = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = datetime.datetime.now()

        def __repr__(self):
            time_format = "%Y-%m-%d %H:%M:%S"
            return f"id: #{self.user_id}, " \
                   f"from IP: {self.ip_address}:{self.port}, " \
                   f"login_time: {self.login_time:{time_format}}"

    class UsersContacts:
        def __init__(self, user_id, contact):
            self.id = None
            self.user_id = user_id
            self.contact = contact

    class UsersHistory:
        def __init__(self, user_id):
            self.id = None
            self.user_id = user_id
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):
        # CREATE DATABASE ENGINE
        self.database_engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=1800,
                                             connect_args={'check_same_thread': False})
        self.metadata = MetaData()

        all_users_table = Table('all_users', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('username', String, unique=True),
                                Column('last_login', DateTime)
                                )

        active_users_table = Table('active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user_id', Integer, index=True, unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime)
                                   )
        login_history_table = Table('login_history', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user_id', Integer),
                                    Column('ip_address', String),
                                    Column('port', Integer),
                                    Column('login_time', DateTime)
                                    )
        contacts_table = Table('contacts', self.metadata,
                               Column('id', Integer, primary_key=True),
                               Column('user', ForeignKey('all_users.id')),
                               Column('contact', ForeignKey('all_users.id'))
                               )
        users_history_table = Table('history', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('all_users.id')),
                                    Column('sent', Integer),
                                    Column('accepted', Integer)
                                    )
        # CREATE DATABASE TABLES
        self.metadata.create_all(self.database_engine)
        mapper(self.Users, all_users_table),
        mapper(self.ActiveUser, active_users_table),
        mapper(self.LoginHistory, login_history_table),
        mapper(self.UsersContacts, contacts_table),
        mapper(self.UsersHistory, users_history_table)

        # CREATE SESSION
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        self.session.query(self.ActiveUser).delete()
        self.session.commit()

    def login_user(self, username, ip_address, port):
        new_user = self.session.query(self.Users).filter_by(username=username).first()
        if new_user:
            new_user.last_login = datetime.datetime.now()
        else:
            new_user = self.Users(username)
            self.session.add(new_user)
            self.session.commit()
        new_active_user = self.ActiveUser(new_user.id, ip_address, port)
        self.session.add(new_active_user)
        new_login_history = self.LoginHistory(new_user.id, ip_address, port)
        self.session.add(new_login_history)
        self.session.commit()

    def logout_user(self, username):
        user = self.session.query(self.Users).filter_by(username=username).first()
        self.session.query(self.ActiveUser).filter_by(user_id=user.id).delete()
        self.session.commit()

    # Добавил получение юзера по id, думаю пригодится
    def get_user_by_id(self, user_id):
        return self.session.query(self.Users).get(user_id)

    def all_users(self):
        return self.session.query(self.Users).all()

    def all_active_users(self):
        return self.session.query(self.ActiveUser).all()

    def all_history(self):
        return self.session.query(self.LoginHistory).all()


if __name__ == '__main__':
    test_db = ServerDatabase()
    test_db.login_user('client_1', '192.168.1.4', 8888)
    test_db.login_user('client_2', '192.168.1.5', 7777)

    # Чтобы сработала logout_user из main нужно закомментировать строки 65 и 66
    # test_db.logout_user('client_1')
    # test_db.logout_user('client_2')

    print('all_users:', test_db.all_users())
    print('all_active_users:', test_db.all_active_users())
    print('all_history:', test_db.all_history())
