import requests

from tests.models.config import Envs
from tests.models.profile import ProfilePayload, ProfileResp
from tests.models.spend import SpendAdd, SpendResp, Category, SpendSearchPayload, SpendSearchResp
from tests.utils.sessions import BaseSession


class SpendsHttpClient:
    session: requests.Session
    base_url: str

    def __init__(self, envs: Envs, token: str):
        self.session = BaseSession(base_url=envs.api_url)
        self.session.headers.update({'Accept': 'application/json',
                                     'Authorization': f'Bearer {token}',
                                     'Content-Type': 'application/json'})


    def get_categories(self) -> list[Category]:
        response = self.session.get("/api/categories/all", params={'excludeArchived': 'true'})
        # self.raise_for_status(response)
        return [Category.model_validate(item) for item in response.json()]

    def add_category(self, name: str, expect_error: bool = False):
        if expect_error:
            response = self.session.post("/api/categories/add", json={"name": name},
                                         skip_status_check=True)
            return response
        else:
            response = self.session.post("/api/categories/add", json={
                "name": name
            })
            return Category.model_validate(response.json())

    def edit_category(self, category: Category) -> Category:
        response = self.session.patch("/api/categories/update", json={
            'archived': category.archived,
            'id': str(category.id),
            'name': category.name,
            'username': category.username
        })
        return Category.model_validate(response.json())

    def get_spends(self) -> list[SpendResp]:
        response = self.session.get("/api/spends/all")
        res = []
        for item in response.json():
            item['category_id'] = item['category']['id']
            res.append(item)
            SpendResp.model_validate(item)
        return res

    def add_spend(self, spend: SpendAdd, expect_error: bool = False):
        if expect_error:
            response = self.session.post("/api/spends/add", json=spend.model_dump(), skip_status_check=True)
            return response
        else:
            response = self.session.post("/api/spends/add", json=spend.model_dump())
            data = response.json()
            data['category_id'] = data['category']['id']
            return SpendResp.model_validate(data)

    def edit_spend(self, spend: SpendAdd) -> SpendResp:
        response = self.session.patch("/api/spends/edit", json=spend.model_dump())
        data = response.json()
        data['category_id'] = data['category']['id']
        return SpendResp.model_validate(data)

    def remove_spends(self, ids: list[str]):
        response = self.session.delete("/api/spends/remove", params={"ids": ','.join(ids)})
        return response

    def edit_profile(self, profile: ProfilePayload) -> ProfileResp:
        resp = self.session.post("/api/users/update", json=profile.model_dump())
        return ProfileResp.model_validate(resp.json())

    def search_spend(self, payload: SpendSearchPayload) -> SpendSearchResp:
        resp = self.session.get("/api/v2/spends/all", params=payload.model_dump())
        return SpendSearchResp.model_validate(resp.json())
