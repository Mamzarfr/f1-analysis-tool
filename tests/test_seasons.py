def test_seasons(client):
    resp = client.get("/seasons")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert "year" in data[0]


def test_seasons_order(client):
    resp = client.get("/seasons")
    assert resp.status_code == 200
    data = resp.json()
    years = [s["year"] for s in data]
    assert years == sorted(years)


def test_events(client):
    resp = client.get("/seasons/2025/events")
    assert resp.status_code == 200
    data = resp.json()
    first = data[0]
    assert first["season_year"] == 2025
    assert first["round_number"] == 1


def test_events_order(client):
    resp = client.get("/seasons/2025/events")
    data = resp.json()
    rounds = [e["round_number"] for e in data]
    assert rounds == sorted(rounds)


def test_drivers(client):
    resp = client.get("/seasons/2025/drivers")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 20
    assert "code" in data[0]
    assert "team" in data[0]


def test_wrong_season(client):
    resp = client.get("/seasons/1900/events")
    assert resp.status_code == 404
