import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import mapper, sessionmaker


class ClientDatabase:
    class KnownUsers:
        def __init__(self, username):
            self.id = None
            self.username = username

        def __repr__(self):
            return f"id: #{self.id}, username: {self.username}"

    class MessageHistory:
        def __init__(self, from_user, to_user, message):
            self.id = None
            self.from_user = from_user
            self.to_user = to_user
            self.message = message
            self.date = datetime.datetime.now()

        def __repr__(self):
            time_format = "%Y-%m-%d %H:%M:%S"
            return f"date: #{self.date:{time_format}}, " \
                   f"from: {self.from_user}, " \
                   f"to: {self.to_user}, " \
                   f"message: {self.message[0:20]}..."

    class Contacts:
        def __init__(self, username):
            self.id = None
            self.username = username
            self.creation_date = datetime.datetime.now()

        def __repr__(self):
            time_format = "%Y-%m-%d %H:%M:%S"
            return f"id: #{self.id}, " \
                   f"username: {self.username}, " \
                   f"created: {self.creation_date:{time_format}}"

    def __init__(self, username):
        # Creating engine of database
        self.database_engine = create_engine(f'sqlite:///client_{username}.db3',
                                             echo=False,
                                             pool_recycle=1800,
                                             connect_args={'check_same_thread': False})
        self.metadata = MetaData()

        # Creating Database Tables
        known_users = Table('known_users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('username', String)
                            )
        message_history = Table('message_history', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('from_user', String),
                                Column('to_user', String),
                                Column('message', Text),
                                Column('date', DateTime)
                                )
        contacts = Table('contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('username', String),
                         Column('creation_date', DateTime)
                         )

        self.metadata.create_all(self.database_engine)

        # Creating Views
        mapper(self.KnownUsers, known_users),
        mapper(self.MessageHistory, message_history),
        mapper(self.Contacts, contacts)

        # Creating Session
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # Cleaning Contact Tables
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_new_contact(self, username):
        if not self.session.query(self.Contacts).filter_by(username=username).count():
            new_contact = self.Contacts(username)
            self.session.add(new_contact)
            self.session.commit()
        else:
            print(f"Contact with name {username} is already exist in database")

    def delete_contact(self, username):
        self.session.query(self.Contacts).filter_by(username=username).delete()

    def add_new_users(self, users_list):
        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            new_user = self.KnownUsers(user)
            self.session.add(new_user)
        self.session.commit()

    def save_message(self, from_user, to_user, message):
        new_message = self.MessageHistory(from_user, to_user, message)
        self.session.add(new_message)
        self.session.commit()

    def get_contacts(self):
        return [contact for contact in self.session.query(self.Contacts).all()]

    def get_users(self):
        return [user for user in self.session.query(self.KnownUsers).all()]

    def check_user(self, username):
        if self.session.query(self.KnownUsers).filter_by(username=username).count():
            return True
        else:
            return False

    def chech_contact(self, username):
        if self.session.query(self.Contacts).filter_by(username=username).count():
            return True
        else:
            return False

    def get_history(self, from_who=None, to_who=None):
        query = self.session.query(self.MessageHistory)
        if from_who:
            query = query.filter_by(from_user=from_who)
        if to_who:
            query = query.filter_by(to_user=to_who)
        return [f"{history_row}" for history_row in query.all()]


if __name__ == '__main__':
    test_db = ClientDatabase('test_1')
    # for i in ['test_1', 'test_2', 'test_3']:
    #     test_db.add_new_contact(i)
    # test_db.add_new_contact('test_4')
    # test_db.add_new_users(['test_1', 'test_2', 'test_3', 'test_4', 'test_5'])
    test_db.save_message('test_1', 'test_2', f"Привет, я тестовое сообщение")
    # print(test_db.get_contacts())
    # print(test_db.get_users())
    print(test_db.get_history())
