import pytest
from functools import lru_cache
from mimesis import Person
import copy

person = Person()


class UserData:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_hash = hash(file_path) % 10000
        self._initial_users = self._generate_initial_users()
        self._current_users = copy.deepcopy(self._initial_users)

    def _generate_initial_users(self):
        users = [{
            'login': f'aboba_{self.file_hash}',
            'password': '12345',
            'categories': [],
            'spendings': []
        }]

        for i in range(10):
            users.append({
                "login": f"{person.username()}_{self.file_hash}_{i}",
                "password": person.password(),
                "categories": [],
                "spendings": []
            })

        return users

    def get_users(self):
        return self._current_users

    def get_user(self, user_id):
        return self._current_users[user_id]

    def update_user(self, user_id, **updates):
        if 0 <= user_id < len(self._current_users):
            self._current_users[user_id].update(updates)

    def add_category(self, user_id, category):
        if 0 <= user_id < len(self._current_users):
            self._current_users[user_id]['categories'].append(category)

    def remove_category(self, user_id, category):
        if 0 <= user_id < len(self._current_users):
            self._current_users[user_id]['categories'].remove(category)

    def add_spending(self, user_id, spending):
        if 0 <= user_id < len(self._current_users):
            self._current_users[user_id]['spendings'].append(spending)

    def remove_spending(self, user_id, spending):
        if 0 <= user_id < len(self._current_users):
            if spending in self._current_users[user_id]['spendings']:
                self._current_users[user_id]['spendings'].remove(spending)

    def remove_all_spendings(self, user_id):
        if 0 <= user_id < len(self._current_users):
            self._current_users[user_id]['spendings'].clear()

    def reset(self):
        self._current_users = copy.deepcopy(self._initial_users)


@lru_cache(maxsize=None)
def get_user_data(file_path: str):
    return UserData(file_path)


@pytest.fixture(scope="module")
def user_data(request):
    file_path = str(request.fspath)
    return get_user_data(file_path)


@pytest.fixture(scope="module")
def users(user_data):
    return user_data.get_users()