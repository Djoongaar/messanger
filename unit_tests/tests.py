import os
import re
import sys
import time
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from client import make_presence_message, process_answer
from common.settings import DEFAULT_IP_ADDRESS, DEFAULT_PORT, MAX_PACKAGE_LENGTH, ACTION, PRESENCE, TIME, USER, \
    ACCOUNT_NAME, RESPONSE
from server import process_client_message


class GetMessageTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_def_make_presence_message(self):
        test = make_presence_message()
        test[TIME] = 1.1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_isinstance_message(self):
        """ Test for type of received message encoding """
        test = make_presence_message(account_name='Guest')
        self.assertIsInstance(test, dict)

    def test_200_OK_ans(self):
        """ Test encoding from bytes to dict class """
        self.assertEqual(process_answer({RESPONSE: 200}), '200: OK')


class ProcessClientMessageTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_return_200(self):
        MSG_TO_SERV = make_presence_message(account_name='Guest')
        response = process_client_message(MSG_TO_SERV)
        self.assertEqual(response['response'], 200)

    def test_return_400(self):
        MSG_TO_SERV = {
            # ACTION: PRESENCE,  # Закомментируем чтобы выдавало ошибку
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }
        response = process_client_message(MSG_TO_SERV)
        self.assertEqual(response['response'], 400)


class PresenceMessageTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_return_presence(self):
        presence_message = make_presence_message(account_name='Guest')
        # print(f"сообщение о присутствии: {presence_message}")
        self.assertEqual(presence_message['action'], 'presence')

    def test_return_time(self):
        presence_message = make_presence_message(account_name='Guest')
        # print(f"сообщение о присутствии: {presence_message}")
        self.assertIsNotNone(presence_message['time'])

    def test_return_name(self):
        """ Использую assertTrue вместо assertIsNotNone чтобы нельзя было вставить пустое значение """
        presence_message = make_presence_message(account_name='Guest')
        # print(f"Имя гостя для сравнения с регулярным выражением: {presence_message['user']['account_name']}")
        self.assertTrue(re.match('[0-9a-zA-Z_]+', presence_message['user']['account_name']))


if __name__ == '__main__':
    unittest.main()
