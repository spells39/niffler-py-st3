from urllib.parse import urljoin

import requests
from fastapi_pagination import response

from tests.models.spend import Category, Spend, SpendAdd, SpendResp


class SpendsHttpClient:
    session: requests.Session
    base_url: str

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.session = requests.session()
        self.session.headers.update({'Accept': 'application/json',
                                     'Authorization': f'Bearer {token}',
                                     'Content-Type': 'application/json'})

    def get_categories(self) -> list[Category]:
        response = self.session.get(urljoin(self.base_url, "/api/categories/all"), params={'excludeArchived': 'true'})
        self.raise_for_status(response)
        return [Category.model_validate(item) for item in response.json()]

    def add_category(self, name: str) -> Category:
        response = self.session.post(urljoin(self.base_url, "/api/categories/add"), json={
            "name": name
        })
        self.raise_for_status(response)
        return Category.model_validate(response.json())

    def edit_category(self, category: Category) -> Category:
        response = self.session.patch(urljoin(self.base_url, "/api/categories/update"), json={
            'archived': category.archived,
            'id': str(category.id),
            'name': category.name,
            'username': category.username
        })
        self.raise_for_status(response)
        return Category.model_validate(response.json())

    def get_spends(self) -> list[SpendResp]:
        url = urljoin(self.base_url, "/api/spends/all")
        response = self.session.get(url)
        self.raise_for_status(response)
        res = []
        for item in response.json():
            item['category_id'] = item['category']['id']
            res.append(item)
            SpendResp.model_validate(item)
        return res

    def add_spend(self, spend: SpendAdd) -> SpendResp:
        url = urljoin(self.base_url, "/api/spends/add")
        response = self.session.post(url, json=spend.model_dump())
        self.raise_for_status(response)
        data = response.json()
        data['category_id'] = data['category']['id']
        return SpendResp.model_validate(data)

    def edit_spend(self, spend: SpendAdd) -> SpendResp:
        url = urljoin(self.base_url, "/api/spends/edit")
        response = self.session.patch(url, json=spend.model_dump())
        self.raise_for_status(response)
        data = response.json()
        data['category_id'] = data['category']['id']
        return SpendResp.model_validate(data)

    def remove_spends(self, ids: list[str]):
        url = urljoin(self.base_url, "/api/spends/remove")
        response = self.session.delete(url, params={"ids": ids})
        self.raise_for_status(response)

    @staticmethod
    def raise_for_status(response: requests.Response):
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 400:
                e.add_note(response.text)
                raise
