import allure
import grpc
import pytest

from tests.grpc.internal.pb.niffler_currency_pb2 import CalculateRequest, CurrencyValues
from tests.grpc.internal.pb.niffler_currency_pb2_pbreflect import NifflerCurrencyServiceClient

@allure.epic("gRPC")
@allure.feature("Niffler")
class TestCalculateRate:

    def test_calculate_rate(self, grpc_client: NifflerCurrencyServiceClient) -> None:
        resp = grpc_client.calculate_rate(
            request=CalculateRequest(
                spendCurrency=CurrencyValues.EUR,
                desiredCurrency=CurrencyValues.USD,
                amount=100
            )
        )
        assert resp.calculatedAmount == 108

    def test_calculate_rate_negative(self, grpc_client: NifflerCurrencyServiceClient) -> None:
        try:
            resp = grpc_client.calculate_rate(
                request=CalculateRequest(
                    spendCurrency=CurrencyValues.EUR,
                    amount=100.0
                )
            )
        except grpc.RpcError as e:
            assert e.code() == grpc.StatusCode.UNKNOWN
            assert e.details() == 'Application error processing RPC'

    @pytest.mark.parametrize('spend, spend_currency, desired_currency, expected_result',
                             [
                                 (100.0, CurrencyValues.USD, CurrencyValues.RUB, 6666.67),
                                 (100.0, CurrencyValues.RUB, CurrencyValues.USD, 1.5),
                                 (100.0, CurrencyValues.USD, CurrencyValues.USD, 100.0)
                             ])
    def test_currency_conversion(self, grpc_client: NifflerCurrencyServiceClient, spend: float,
                                 spend_currency: CurrencyValues, desired_currency: CurrencyValues,
                                 expected_result: float) -> None:
        resp = grpc_client.calculate_rate(
            request=CalculateRequest(
                spendCurrency=spend_currency,
                desiredCurrency=desired_currency,
                amount=spend
            )
        )
        assert resp.calculatedAmount == expected_result