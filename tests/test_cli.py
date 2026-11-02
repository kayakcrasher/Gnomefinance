from gnomefinance.cli import main


def test_set_and_show_portfolio(service, capsys):
    assert main(["set", "BTC", "0.5"], service=service) == 0
    assert main(["portfolio"], service=service) == 0
    out = capsys.readouterr().out
    assert "BTC" in out and "$50,000.00" in out


def test_prices(service, capsys):
    assert main(["prices"], service=service) == 0
    assert "$100,000.00" in capsys.readouterr().out


def test_bad_amount_returns_error(service, capsys):
    assert main(["set", "BTC", "lots"], service=service) == 1
    assert "error" in capsys.readouterr().err
