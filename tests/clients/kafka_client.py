import json
import logging
from typing import Dict, Any

from confluent_kafka import TopicPartition
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import Consumer, Producer

from tests.models.userdata import UserName
from tests.utils.waiters import wait_until_timeout


class KafkaClient:
    def __init__(self, envs, client_id: str = 'tester', group_id: str = 'tester'):
        self.server = envs.kafka
        self.admin = AdminClient({"bootstrap.servers": self.server})
        self.producer = Producer({"bootstrap.servers": self.server})
        self.consumer = Consumer({
            "bootstrap.servers": self.server,
            "group.id": group_id,
            "client.id": client_id,
            "auto.offset.reset": "latest",
            "enable.auto.commit": False
        })

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.consumer.close()
        self.producer.flush()

    def produce_message(self, topic: str, key: str, value: Dict[str, Any]):
        """Отправка сообщения в Kafka"""
        def delivery_callback(err, msg):
            if err:
                logging.error(f"Message delivery failed: {err}")
            else:
                logging.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

        try:
            json_value = json.dumps(value)
            self.producer.produce(
                topic=topic,
                key=key,
                value=json_value,
                callback=delivery_callback
            )
            self.producer.poll(0)
        except Exception as e:
            logging.error(f"Failed to produce message: {e}")
            raise

    def produce_user_data(self, user_data: Dict[str, Any]):
        """Отправка userdata в соответствующий топик"""
        user_id = user_data.get('id', user_data.get('username', 'unknown'))
        self.produce_message('userdata', str(user_id), user_data)

    def list_topics_names(self, attempts: int = 5):
        """Вернуть список доступных топиков"""
        try:
            topics = self.admin.list_topics(timeout=attempts).topics
            return [topics.get(item).topic for item in topics]
        except RuntimeError:
            logging.error("no topics in kafka")

    @wait_until_timeout
    def consume_message(self, partitions, **kwargs):
        """Вернуть последнее после определенной позиции сообщение"""
        self.consumer.assign(partitions)
        try:
            message = self.consumer.poll(1.0)
            logging.debug(f'{message.value()}')
            return message.value()
        except AttributeError:
            pass

    def get_last_offset(self, topic: str = "", partition_id=0):
        """Вернуть последнюю позицию партиции"""
        partition = TopicPartition(topic, partition_id)
        try:
            low, high = self.consumer.get_watermark_offsets(partition, timeout=10)
            return high
        except Exception as err:
            logging.error("probably no such topic: %s: %s", topic, err)

    def log_msg_and_json(self, topic_partitions):
        msg = self.consume_message(topic_partitions, timeout=25)
        logging.info(msg)
        return msg

    def subscribe_listen_new_offsets(self, topic):
        self.consumer.subscribe([topic])
        p_ids = self.consumer.list_topics(topic).topics[topic].partitions.keys()
        partitions_offsets_event = {k: self.get_last_offset(topic, k) for k in p_ids}
        logging.info(f'{topic} offsets: {partitions_offsets_event}')
        topic_partitions = [TopicPartition(topic, k, v) for k, v in partitions_offsets_event.items()]
        return topic_partitions

    def delivery_report(self, err, msg):
        if err is not None:
            logging.info(f"Ошибка при отправке сообщения: {err}")
        else:
            print(f"Сообщение отправлено в {msg.topic()} [{msg.partition()}] с смещением {msg.offset()}")

    def send_message(self, topic: str, username: str):
        self.producer.produce(topic,
                              json.dumps(UserName(username=username).model_dump()).encode("utf-8"),
                              on_delivery=self.delivery_report,
                              headers={"__TypeId__": "guru.qa.niffler.model.UserJson"},
                              )
        self.producer.flush()
