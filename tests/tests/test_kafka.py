import json
import mimesis
import allure

from faker import Faker

from tests.models.userdata import UserName

person = mimesis.Person()


class TestKafkaUserData:
    @allure.title("KAFKA: Сообщение НЕ публикуется при регистрации с невалидным username")
    @allure.tag("KAFKA")
    @allure.tag("NEGATIVE")
    def test_no_message_on_failed_registration(self, auth_client, kafka, envs):
        with allure.step("Попытка регистрации"):
            username = ""
            password = Faker().password(special_chars=False)
            topic_partitions = kafka.subscribe_listen_new_offsets("users")
            result = auth_client.register(username, password, envs=envs, expect_error=True)

        with allure.step("Проверить, что регистрация завершилась ошибкой"):
            assert result.status_code != 201

        with allure.step("Убедиться, что сообщение НЕ было отправлено в Kafka"):
            event = kafka.log_msg_and_json(topic_partitions)
            assert event is None or event == '' or event == b''

    @allure.title("KAFKA: Сообщение НЕ публикуется при невалидном пароле")
    @allure.tag("KAFKA")
    @allure.tag("NEGATIVE")
    def test_no_message_on_invalid_password(self, auth_client, kafka, envs):
        with allure.step("Попытка регистрации"):
            username = Faker().user_name()
            password = "a"
            topic_partitions = kafka.subscribe_listen_new_offsets("users")
            result = auth_client.register(username, password, envs=envs, expect_error=True)

        with allure.step("Проверка ошибки валидации пароля"):
            assert result.status_code != 201

        with allure.step("Проверка, что сообщение НЕ было отправлено в Kafka"):
            event = kafka.log_msg_and_json(topic_partitions)
            assert event is None or event == '' or event == b''

    @allure.title("KAFKA: Полный цикл регистрация")
    @allure.tag("KAFKA")
    @allure.tag("E2E")
    def test_full_registration_flow_to_database(self, auth_client, kafka, userdata_db, envs):
        with allure.step("Генерация данных"):
            username = Faker().user_name()
            password = Faker().password(special_chars=False)

        with allure.step("Подписка на топик users перед регистрацией"):
            topic_partitions = kafka.subscribe_listen_new_offsets("users")

        with allure.step("Выполнение регистрации"):
            result = auth_client.register(username, password, envs=envs)
            assert result.status_code == 201

        with allure.step("Получение сообщения из Kafka"):
            event = kafka.log_msg_and_json(topic_partitions)
            assert event != '' and event != b''

        with allure.step("Валидация структуры сообщения"):
            message_data = json.loads(event.decode('utf8'))
            UserName.model_validate(message_data)
            assert message_data['username'] == username

        with allure.step(f"Проверка наличия записи {username} в БД"):
            user_from_db = userdata_db.get_user_by_username(username=username)
            assert user_from_db is not None
            assert user_from_db.username == username

    @allure.title("KAFKA: Прямая отправка сообщения топик")
    @allure.tag("KAFKA")
    def test_direct_message_to_userdata_topic(self, kafka, userdata_db):
        with allure.step("Отправка сообщения"):
            name = Faker().user_name()
            kafka.send_message("users", name)

        with allure.step(f"Проверка наличия в БД записи {name}"):
            user_from_db = userdata_db.get_user_by_username(name)
            assert user_from_db is not None
            assert user_from_db.username == name
