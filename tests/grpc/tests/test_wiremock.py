import grpc

from tests.grpc.internal.pb.niffler_currency_pb2 import CalculateRequest, CurrencyValues
from tests.grpc.internal.pb.niffler_currency_pb2_pbreflect import NifflerCurrencyServiceClient

class TestWiremockCurrencies:
    def test_calculate_rate_eur_to_eur(self, grpc_client: NifflerCurrencyServiceClient) -> None:
        try:
            resp = grpc_client.calculate_rate(
                request=CalculateRequest(
                    spendCurrency=CurrencyValues.EUR,
                    desiredCurrency=CurrencyValues.EUR,
                    amount=100.0
                )
            )
        except grpc.RpcError as e:
            assert e.code() == grpc.StatusCode.NOT_FOUND

    def test_calculate_rate_without_amount(self, grpc_client: NifflerCurrencyServiceClient) -> None:
        try:
            resp = grpc_client.calculate_rate(
                request=CalculateRequest(
                    spendCurrency=CurrencyValues.EUR,
                    desiredCurrency=CurrencyValues.USD
                )
            )
        except grpc.RpcError as e:
            assert e.code() == grpc.StatusCode.NOT_FOUND

    def test_calculate_rate_without_currencies(self, grpc_client: NifflerCurrencyServiceClient) -> None:
        try:
            resp = grpc_client.calculate_rate(
                request=CalculateRequest(
                    amount=100.0
                )
            )
        except grpc.RpcError as e:
            assert e.code() == grpc.StatusCode.NOT_FOUND
