import allure
from google.protobuf import empty_pb2

from tests.grpc.internal.pb.niffler_currency_pb2_pbreflect import NifflerCurrencyServiceClient

@allure.epic("gRPC")
@allure.feature("Niffler")
class TestGetAllCurrencies:
    def test_get_all_currencies(self, grpc_client: NifflerCurrencyServiceClient) -> None:
        resp = grpc_client.get_all_currencies(empty_pb2.Empty())
        assert len(resp.allCurrencies) == 4