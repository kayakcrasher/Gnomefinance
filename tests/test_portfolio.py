import pytest

from gnomefinance.errors import ValidationError
from gnomefinance.portfolio import Portfolio, parse_amount


def test_new_portfolio_is_empty():
    assert Portfolio().holdings == {}


def test_add_accumulates():
    p = Portfolio()
    p.add("bitcoin", 0.5)
    p.add("bitcoin", "0.25")
    assert p.amount("bitcoin") == 0.75


def test_set_overrides_and_zero_removes():
    p = Portfolio({"solana": 10})
    p.set("solana", 4)
    assert p.amount("solana") == 4
    p.set("solana", 0)
    assert "solana" not in p


def test_holdings_is_a_copy():
    p = Portfolio({"bitcoin": 1})
    p.holdings["bitcoin"] = 999
    assert p.amount("bitcoin") == 1


@pytest.mark.parametrize("bad", ["abc", "-1", -0.1, "nan", "inf", None])
def test_rejects_bad_amounts(bad):
    with pytest.raises(ValidationError):
        parse_amount(bad)


def test_rejects_unknown_asset():
    with pytest.raises(ValidationError):
        Portfolio().add("dogecoin", 1)
