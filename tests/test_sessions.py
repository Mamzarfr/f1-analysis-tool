from backend.app.models import Lap
from backend.app.models import Session as SessionModel


def _get_session_id(db):
    return db.query(SessionModel).first().id


def test_session_drivers(client, db):
    sid = _get_session_id(db)
    resp = client.get(f"/sessions/{sid}/drivers")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert "code" in data[0]
    assert "name" in data[0]
    assert "team" in data[0]


def test_list_laps(client, db):
    sid = _get_session_id(db)
    resp = client.get(f"/sessions/{sid}/laps")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    lap = data[0]
    assert "lap_number" in lap
    assert "driver_code" in lap
    assert "compound" in lap


def test_laps_filter1(client, db):
    sid = _get_session_id(db)
    lap = db.query(Lap).filter(
        Lap.session_id == sid
    ).first()
    code = lap.driver.code

    resp = client.get(
        f"/sessions/{sid}/laps",
        params={"driver": code},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert all(l["driver_code"] == code for l in data)


def test_laps_filter2(client, db):
    sid = _get_session_id(db)
    resp = client.get(
        f"/sessions/{sid}/laps",
        params={"lap_min": 5, "lap_max": 10},
    )
    assert resp.status_code == 200
    data = resp.json()
    for lap in data:
        assert 5 <= lap["lap_number"] <= 10


def test_wrong_sessino_l(client):
    resp = client.get("/sessions/67676767/laps")
    assert resp.status_code == 404


def test_wrong_session_d(client):
    resp = client.get("/sessions/67676767/drivers")
    assert resp.status_code == 404
