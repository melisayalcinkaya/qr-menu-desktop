"""Ağ isteklerini arayüzü dondurmadan arka planda çalıştırma.

Qt arayüzü tek bir iş parçacığında çalışır; orada beklenen bir HTTP isteği pencereyi
dondurur. İstekler QThreadPool'da çalışır, sonuç sinyalle arayüz iş parçacığına
döner (Qt sinyalleri iş parçacıkları arasında güvenle kuyruklanır).
"""

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


class _Signals(QObject):
    done = Signal(object)
    failed = Signal(object)


class _Task(QRunnable):
    def __init__(self, fn, args, kwargs):
        super().__init__()
        self.fn, self.args, self.kwargs = fn, args, kwargs
        self.signals = _Signals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as exc:  # noqa: BLE001 - hata arayüze iletilir
            self.signals.failed.emit(exc)
        else:
            self.signals.done.emit(result)


_alive: set = set()


def run_async(fn, *args, on_done=None, on_error=None, **kwargs):
    """`fn(*args)` arka planda çalışır; sonuç `on_done`, hata `on_error` ile gelir."""
    task = _Task(fn, args, kwargs)
    task.setAutoDelete(False)
    _alive.add(task)  # sinyaller gelene kadar nesne çöp toplanmasın

    def finish(callback, value):
        _alive.discard(task)
        if callback:
            callback(value)

    task.signals.done.connect(lambda r: finish(on_done, r))
    task.signals.failed.connect(lambda e: finish(on_error, e))
    QThreadPool.globalInstance().start(task)
    return task
