import json

from gnomefinance.storage import Storage


def test_missing_file_loads_empty(tmp_path):
    assert Storage(tmp_path / "nope.json").load() == {"holdings": {}, "wallets": []}


def test_round_trip(tmp_path):
    storage = Storage(tmp_path / "sub" / "p.json")
    wallets = [{"id": "x", "chain": "solana", "address": "a", "label": "l"}]
    storage.save({"bitcoin": 0.5}, wallets)
    assert storage.load() == {"holdings": {"bitcoin": 0.5}, "wallets": wallets}
    assert not list((tmp_path / "sub").glob("*.tmp"))


def test_reads_old_flat_format(tmp_path):
    path = tmp_path / "p.json"
    path.write_text(json.dumps({"bitcoin": 0.065, "solana": 5.4}))
    assert Storage(path).load() == {
        "holdings": {"bitcoin": 0.065, "solana": 5.4},
        "wallets": [],
    }
