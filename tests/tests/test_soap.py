import allure
import mimesis

from tests.templates.xml_readers import current_user, send_invite, accept_invite, decline_invite, remove_friend
from tests.utils.helpers import parse_xml_string

person = mimesis.Person()

@allure.feature("SOAP")
class TestSoap:
    @allure.story("Получение информации о пользователе")
    def test_user_info(self, soap_session, sign_up):
        with allure.step("Регистрация пользователя"):
            login = person.username()
            sign_up({'login': login, 'password': person.password()})
        with allure.step("Получение информации о пользователе"):
            resp = soap_session.request(data=current_user(login))
        with allure.step("Проверка полученной информации"):
            user = parse_xml_string(resp.text)['Envelope']['Body']['userResponse']['user']
            assert user['id']
            assert user['username'] == login

    @allure.story("Отправка запроса на добавление в друзья")
    def test_send_invite(self, soap_session, sign_up_many_users, userdata_db):
        with allure.step("Регистрация пользователей"):
            user_inviter, user_addressed = sign_up_many_users(2)
        with allure.step("Получение информации о пользователях"):
            inviter = userdata_db.get_user_by_username(user_inviter)
            addressed = userdata_db.get_user_by_username(user_addressed)
        with allure.step("Отправка запроса на добавление в друзья"):
            resp = soap_session.request(data=send_invite(user_inviter, user_addressed))
        with allure.step("Проверка статуса запроса на добавление в друзья"):
            status = userdata_db.get_friend(inviter.id.__str__(), addressed.id.__str__())
            assert status.status == 'PENDING'

    @allure.story("Принятие запроса на добавление в друзья")
    def test_accept_invite(self, soap_session, sign_up_many_users, userdata_db):
        with allure.step("Регистрация пользователей"):
            user_inviter, user_addressed = sign_up_many_users(2)
        with allure.step("Получение информации о пользователе"):
            inviter = userdata_db.get_user_by_username(user_inviter)
            addressed = userdata_db.get_user_by_username(user_addressed)
        with allure.step("Отправка запроса на добавление в друзья"):
            resp = soap_session.request(data=send_invite(user_inviter, user_addressed))
        with allure.step("Проверка статуса запроса на добавление в друзья"):
            status = userdata_db.get_friend(inviter.id.__str__(), addressed.id.__str__())
            assert status.status == 'PENDING'
        with allure.step("Отправка запроса с согласием на добавления в друзья"):
            resp = soap_session.request(data=accept_invite(user_addressed, user_inviter))
        with allure.step("Проверка статуса запроса"):
            status_inviter = userdata_db.get_friend(inviter.id.__str__(), addressed.id.__str__())
            status_addressed = userdata_db.get_friend(addressed.id.__str__(), inviter.id.__str__())
            assert status_inviter.status == 'ACCEPTED' and status_addressed.status == 'ACCEPTED'

    @allure.story("Отклонение запроса на добавление в друзья")
    def test_decline_invite(self, soap_session, sign_up_many_users, userdata_db):
        with allure.step("Регистрация пользователей"):
            user_inviter, user_addressed = sign_up_many_users(2)
        with allure.step("Получение информации о пользователе"):
            inviter = userdata_db.get_user_by_username(user_inviter)
            addressed = userdata_db.get_user_by_username(user_addressed)
        with allure.step("Отправка запроса на добавление в друзья"):
            resp = soap_session.request(data=send_invite(user_inviter, user_addressed))
        with allure.step("Проверка статуса запроса на добавление в друзья"):
            status = userdata_db.get_friend(inviter.id.__str__(), addressed.id.__str__())
            assert status.status == 'PENDING'
        with allure.step("Отправка запроса с отклонением запроса на добавления в друзья"):
            resp = soap_session.request(data=decline_invite(user_addressed, user_inviter))
        with allure.step("Проверка статуса запроса"):
            status = userdata_db.get_friend(inviter.id.__str__(), addressed.id.__str__())
            assert status is None

    @allure.story("Удаление из друзей")
    def test_remove_friend(self, soap_session, sign_up_many_users, userdata_db):
        with allure.step("Регистрация пользователей"):
            user_inviter, user_addressed = sign_up_many_users(2)
        with allure.step("Получение информации о пользователе"):
            inviter = userdata_db.get_user_by_username(user_inviter)
            addressed = userdata_db.get_user_by_username(user_addressed)
        with allure.step("Отправка запроса на добавление в друзья"):
            resp = soap_session.request(data=send_invite(user_inviter, user_addressed))
        with allure.step("Проверка статуса запроса на добавление в друзья"):
            status = userdata_db.get_friend(inviter.id.__str__(), addressed.id.__str__())
            assert status.status == 'PENDING'
        with allure.step("Отправка запроса на согласие на добавления в друзья"):
            resp = soap_session.request(data=accept_invite(user_addressed, user_inviter))
        with allure.step("Проверка добавления в друзья"):
            status_inviter = userdata_db.get_friend(inviter.id.__str__(), addressed.id.__str__())
            status_addressed = userdata_db.get_friend(addressed.id.__str__(), inviter.id.__str__())
            assert status_inviter.status == 'ACCEPTED' and status_addressed.status == 'ACCEPTED'
        with allure.step("Отпрвка запроса на удаление из друзей"):
            resp = soap_session.request(data=remove_friend(user_inviter, user_addressed))
        with allure.step("Проверка статуса запроса на удаление из друзей"):
            status_inviter = userdata_db.get_friend(inviter.id.__str__(), addressed.id.__str__())
            status_addressed = userdata_db.get_friend(addressed.id.__str__(), inviter.id.__str__())
            assert status_inviter is None and status_addressed is None

