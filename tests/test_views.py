from datetime import UTC, datetime, timedelta

import pytest

from qrmenu_desktop.api import ApiError, SessionExpiredError
from qrmenu_desktop.ui.calls import CallsView
from qrmenu_desktop.ui.common import table_name, time_ago
from qrmenu_desktop.ui.menu import MenuView, ProductDialog, format_price


def call(i, label="5", note=""):
    return {"id": i, "table_label": label, "note": note, "created_at": f"2026-10-30T12:0{i}:00+00:00"}


class FakeApi:
    def __init__(self):
        self.pending = []
        self.closed = []
        self.fail_close = None
        self.fail_poll = None
        self.updates = []

    def pending_calls(self, slug):
        if self.fail_poll:
            raise self.fail_poll
        return list(self.pending)

    def close_call(self, call_id, action):
        if self.fail_close:
            raise self.fail_close
        self.closed.append((call_id, action))

    def meta(self):
        return {"allergens": [{"code": "milk", "tr": "Süt", "en": "Milk"}]}

    def categories(self, slug):
        return [{"id": 1, "name": "Tatlılar"}]

    def products(self, slug):
        return [
            {
                "id": 9,
                "category": 1,
                "name": "Sütlaç",
                "name_en": "",
                "price": "120.00",
                "description": "",
                "is_active": True,
                "is_popular": False,
                "allergens": ["milk"],
            },
        ]

    def update_product(self, pid, data):
        self.updates.append((pid, data))


@pytest.fixture
def view(qtbot):
    api = FakeApi()
    v = CallsView(api, poll_seconds=60)
    qtbot.addWidget(v)
    v.resize(900, 600)
    return v, api


def test_first_load_is_not_announced_but_later_calls_are(qtbot, view):
    v, api = view
    api.pending = [call(1)]
    announced = []
    v.new_calls.connect(announced.append)
    v.set_business("cafe")
    qtbot.waitUntil(lambda: len(v.tiles) == 1)
    assert announced == []  # açılışta var olan çağrılar için zil çalmaz

    api.pending = [call(1), call(2, "Bahçe 1", "Hesap lütfen")]
    v.poll()
    qtbot.waitUntil(lambda: len(v.tiles) == 2)
    assert [c["id"] for c in announced[0]] == [2]
    assert v.tiles[2].property("fresh") == "true"


def test_closing_is_optimistic(qtbot, view):
    v, api = view
    api.pending = [call(1), call(2)]
    v.set_business("cafe")
    qtbot.waitUntil(lambda: len(v.tiles) == 2)
    with qtbot.waitSignal(v.count_changed) as sig:
        v.close_call(v.calls[0], "complete")
    assert sig.args == [1]
    qtbot.waitUntil(lambda: api.closed == [(1, "complete")])
    # Kapatma isteği sürerken gelen yoklama kartı geri getirmez
    assert 1 not in v.tiles


def test_failed_close_restores_the_tile(qtbot, view, monkeypatch):
    v, api = view
    shown = []
    monkeypatch.setattr("qrmenu_desktop.ui.calls.show_error", lambda parent, exc: shown.append(exc))
    api.pending = [call(1)]
    v.set_business("cafe")
    qtbot.waitUntil(lambda: len(v.tiles) == 1)
    api.fail_close = ApiError(500)
    v.close_call(v.calls[0], "complete")
    qtbot.waitUntil(lambda: len(v.tiles) == 1 and bool(shown))


def test_conflict_means_already_closed(qtbot, view, monkeypatch):
    v, api = view
    shown = []
    monkeypatch.setattr("qrmenu_desktop.ui.calls.show_error", lambda parent, exc: shown.append(exc))
    api.pending = [call(1)]
    v.set_business("cafe")
    qtbot.waitUntil(lambda: len(v.tiles) == 1)
    api.fail_close = ApiError(409, {"detail": "Bu çağrı zaten kapatılmış."})
    v.close_call(v.calls[0], "complete")
    qtbot.wait(200)
    assert not v.tiles and not shown


def test_connection_problem_shows_banner_and_session_end_is_signalled(qtbot, view):
    v, api = view
    api.fail_poll = ApiError(0)
    v.set_business("cafe")
    qtbot.waitUntil(lambda: not v.banner.isHidden())
    assert "ulaşılamadı" in v.banner.text()

    api.fail_poll = SessionExpiredError()
    with qtbot.waitSignal(v.session_expired):
        v.poll()
    assert not v.poll_timer.isActive()


def test_menu_toggle_sends_patch(qtbot):
    api = FakeApi()
    v = MenuView(api)
    qtbot.addWidget(v)
    v.set_business("cafe")
    qtbot.waitUntil(lambda: v.table.rowCount() == 1)
    from PySide6.QtWidgets import QCheckBox

    v.table.cellWidget(0, 2).findChild(QCheckBox).setChecked(False)
    qtbot.waitUntil(lambda: api.updates == [(9, {"is_active": False})])


def test_product_dialog_validates_price(qtbot):
    product = FakeApi().products("x")[0]
    dialog = ProductDialog(product, FakeApi().meta())
    qtbot.addWidget(dialog)
    dialog.price.setText("abc")
    dialog._validate()
    assert not dialog.error.isHidden()
    dialog.price.setText("95,50")
    dialog._validate()
    assert dialog.values()["price"] == "95.50"
    assert dialog.values()["allergens"] == ["milk"]


def test_helpers():
    assert table_name("5") == "Masa 5"
    assert table_name("Bahçe 1") == "Bahçe 1"
    now = datetime(2026, 10, 30, 12, 10, tzinfo=UTC)
    assert time_ago((now - timedelta(minutes=3)).isoformat(), now) == "3 dk önce"
    assert time_ago(now.isoformat(), now) == "az önce"
    assert format_price("1250.50") == "₺1.250,50"
    assert format_price("95.00") == "₺95"
