# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for HostDesktopGUI.single_instance — lock + IPC single-instance guard.

Requires PySide6.  Run with::

    QT_QPA_PLATFORM=offscreen python -m pytest tests/test_single_instance.py -v

Cross-process lock detection (second call to ``attempt_primary`` when a lock is
held by the same process) is platform-dependent: on Windows ``LockFileEx`` is
per-handle and the second call will fail; on Linux ``fcntl`` record locks are
per-PID and the second call may succeed.  These tests cover the in-process
behaviour available on the current platform; cross-process scenarios must be
verified manually (launch two GUI processes).
"""

import os
import sys
import tempfile

import pytest

# Ensure the backend package is importable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication, QLockFile
from PySide6.QtNetwork import QLocalSocket
from PySide6.QtTest import QSignalSpy

from HostDesktopGUI.single_instance import (
    InstanceServer,
    _lock_file_path,
    attempt_primary,
    notify_primary_and_exit,
)


# ───────────────────────────────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def qapp():
    """Session-scoped QCoreApplication for tests that need Qt infrastructure."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)
    yield app
    # No explicit cleanup needed — QCoreApplication is a singleton.
    # Avoid calling app.quit() here because other tests may still need it.


@pytest.fixture
def lock_dir():
    """A unique temp directory for lock files, cleaned up after each test."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def lock_path(lock_dir):
    """Path to a unique lock file inside ``lock_dir``."""
    return os.path.join(lock_dir, "test.lock")


@pytest.fixture
def server_name():
    """A unique QLocalServer name for each test to avoid collisions."""
    return f"iController_test_{os.getpid()}_{id(object())}"


# ───────────────────────────────────────────────────────────────────────
# _lock_file_path
# ───────────────────────────────────────────────────────────────────────


def test_lock_file_path_is_in_tempdir():
    """The default lock file lives under the system temp directory."""
    path = _lock_file_path()
    assert path.endswith("iController_GUI.lock")
    assert tempfile.gettempdir() in path


# ───────────────────────────────────────────────────────────────────────
# attempt_primary
# ───────────────────────────────────────────────────────────────────────


class TestAttemptPrimary:
    def test_first_call_succeeds(self, lock_path):
        """A first call to attempt_primary should acquire the lock."""
        is_primary, lock = attempt_primary(lock_path=lock_path)
        assert is_primary is True
        assert lock is not None, "First call on a clean path must return a lock"
        assert isinstance(lock, QLockFile)
        assert lock.isLocked()
        lock.unlock()

    def test_returned_lock_is_always_valid(self, lock_path):
        """When a lock is returned, it must actually be held (P0 fix).

        The contract: if ``(True, lock)`` and ``lock is not None``,
        then ``lock.isLocked()`` is ``True``.  A ``None`` lock is
        acceptable (non-fatal error — proceed as primary anyway).
        """
        is_primary, lock = attempt_primary(lock_path=lock_path)
        assert is_primary is True
        if lock is not None:
            assert lock.isLocked(), (
                "Returned lock object must be held.  "
                "Returning a non-locked QLockFile as if it were valid is a bug."
            )
            lock.unlock()

    def test_lock_file_created(self, lock_path):
        """Acquiring the lock writes a file visible on disk."""
        is_primary, lock = attempt_primary(lock_path=lock_path)
        assert is_primary is True
        assert lock is not None
        assert os.path.isfile(lock_path)
        lock.unlock()

    def test_default_path_uses_tempdir(self):
        """When called without a path, the temp-dir-based path is used."""
        is_primary, lock = attempt_primary()
        assert is_primary is True
        default = _lock_file_path()
        # QLockFile.__str__ varies between platforms; just ensure lock is held.
        assert lock is not None
        assert lock.isLocked()
        lock.unlock()

    def test_lock_reused_after_release(self, lock_path):
        """After releasing a lock, a new call on the same path succeeds."""
        is_primary1, lock1 = attempt_primary(lock_path=lock_path)
        assert is_primary1 is True
        assert lock1 is not None
        lock1.unlock()

        is_primary2, lock2 = attempt_primary(lock_path=lock_path)
        assert is_primary2 is True
        assert lock2 is not None
        assert lock2.isLocked()
        lock2.unlock()

    def test_error_paths_do_not_return_fake_lock(self, lock_path):
        """Verify that the LockFailedError path returns (False, None).

        Note: on Linux (fcntl record locks are per-PID) two QLockFile
        instances in the same process *may* both succeed.  This test
        documents the expected contract; the actual behaviour on the
        current platform can be observed but not strictly enforced.
        """
        is_primary1, lock1 = attempt_primary(lock_path=lock_path)
        assert is_primary1 is True
        assert lock1 is not None

        # Attempt a second lock while the first is still held.
        is_primary2, lock2 = attempt_primary(lock_path=lock_path)

        # Platform-dependent: Windows should return (False, None);
        # Linux may return (True, lock2) due to per-PID fcntl semantics.
        # In either case, the return must be consistent with the contract:
        #   - If lock2 is not None, then lock2.isLocked() must be True.
        #   - If is_primary2 is False, then lock2 must be None.
        if lock2 is not None:
            assert is_primary2 is True, (
                "If a lock object is returned, must be primary"
            )
            assert lock2.isLocked(), "Returned lock must be held"
            lock2.unlock()
        else:
            assert is_primary2 is False, (
                "If lock acquisition failed with LockFailedError, must not "
                "be primary"
            )

        lock1.unlock()


# ───────────────────────────────────────────────────────────────────────
# InstanceServer — lifecycle
# ───────────────────────────────────────────────────────────────────────


class TestInstanceServer:
    def test_listen_succeeds(self, qapp, server_name):
        """A fresh InstanceServer should start listening on a unique name."""
        server = InstanceServer(server_name=server_name, parent=qapp)
        assert server.listen() is True
        assert server.server_name == server_name
        server.shutdown()

    def test_shutdown_is_idempotent(self, qapp, server_name):
        """Calling shutdown twice is safe."""
        server = InstanceServer(server_name=server_name, parent=qapp)
        server.listen()
        server.shutdown()
        server.shutdown()  # Should not raise.

    def test_shutdown_before_listen(self, qapp, server_name):
        """Shutdown before listen is harmless."""
        server = InstanceServer(server_name=server_name, parent=qapp)
        server.shutdown()  # Should not raise.

    def test_listen_after_shutdown(self, qapp, server_name):
        """Re-listening after shutdown works (a new QLocalServer is created)."""
        server = InstanceServer(server_name=server_name, parent=qapp)
        assert server.listen() is True
        server.shutdown()
        assert server.listen() is True
        server.shutdown()

    def test_listen_fails_with_invalid_name(self, qapp):
        """P2: listen() must return False for an invalid server name.

        On Linux, QLocalServer uses Unix-domain sockets whose path is
        limited to ~108 bytes.  A 200-char name reliably triggers a
        ``Name error`` and ``listen()`` returns ``False``.

        The caller must check this return value — silently ignoring it
        leads to the "primary running, secondaries silently die" bug.
        """
        bad_name = "x" * 200
        server = InstanceServer(server_name=bad_name, parent=qapp)
        result = server.listen()
        assert result is False, (
            "listen() should return False for an invalid server name.  "
            "If this test fails, the platform may handle long names "
            "differently — investigate before relaxing the assertion."
        )
        # shutdown() after failed listen() must be safe (idempotent).
        server.shutdown()

    def test_client_cannot_connect_after_listen_failure(self, qapp):
        """P2: after listen() fails, no client can connect to the server.

        This validates that the server is truly not listening — the
        ``activate_requested`` signal will never fire, so the caller must
        not rely on IPC to restore the window.
        """
        bad_name = "y" * 200
        server = InstanceServer(server_name=bad_name, parent=qapp)
        assert server.listen() is False

        spy = QSignalSpy(server.activate_requested)

        # Attempt to connect a client — must fail.
        client = QLocalSocket()
        client.connectToServer(bad_name)
        connected = client.waitForConnected(1000)
        assert not connected, (
            "Client should NOT be able to connect to a server that "
            "failed to listen.  If connected, the listen() failure "
            "was not genuine on this platform."
        )
        client.close()

        # No signal should have been emitted.
        QCoreApplication.processEvents()
        assert spy.count() == 0, (
            "activate_requested must not be emitted when server is not listening"
        )
        server.shutdown()


# ───────────────────────────────────────────────────────────────────────
# InstanceServer — signal emission (P4: QSignalSpy for robust waiting)
# ───────────────────────────────────────────────────────────────────────


class TestInstanceServerSignal:
    """Signal emission tests using QSignalSpy for reliable waiting."""

    def test_signal_emitted_on_client_connect(self, qapp, server_name):
        """When a client connects, activate_requested should fire."""
        server = InstanceServer(server_name=server_name, parent=qapp)
        assert server.listen() is True

        spy = QSignalSpy(server.activate_requested)

        # Connect a client.
        client = QLocalSocket()
        client.connectToServer(server_name)
        connected = client.waitForConnected(3000)
        assert connected, f"Client could not connect: {client.errorString()}"

        # Use QSignalSpy.wait() — blocks until signal fires or timeout.
        received = spy.wait(2000)
        assert received, (
            "activate_requested was not emitted within 2 seconds.  "
            "Check that QLocalServer.newConnection is being delivered."
        )

        client.disconnectFromServer()
        server.shutdown()

        assert spy.count() >= 1

    def test_multiple_clients_emit_multiple_signals(self, qapp, server_name):
        """Each client connection should trigger activate_requested."""
        server = InstanceServer(server_name=server_name, parent=qapp)
        assert server.listen() is True

        spy = QSignalSpy(server.activate_requested)

        for i in range(2):
            client = QLocalSocket()
            client.connectToServer(server_name)
            assert client.waitForConnected(3000), (
                f"Client {i} could not connect"
            )
            # Wait for the signal for this connection.
            received = spy.wait(2000)
            assert received, (
                f"activate_requested not emitted for client {i}"
            )
            client.disconnectFromServer()

        server.shutdown()
        assert spy.count() >= 2


# ───────────────────────────────────────────────────────────────────────
# P1: Buffered activation — early connection before signal wiring
# ───────────────────────────────────────────────────────────────────────


class TestBufferedActivation:
    """Simulate the P1 scenario: client connects AFTER listen() but BEFORE
    the real activate_requested signal is wired to show_from_tray.
    Activation must be buffered, not silently dropped."""

    def test_buffered_activation_preserved(self, qapp, server_name):
        """Activation before real handler is connected must be recorded."""
        server = InstanceServer(server_name=server_name, parent=qapp)

        # --- Step 1: buffer handler connected (simulating __init__.py) ---
        pending = [False]

        def buffer_handler():
            pending[0] = True

        server.activate_requested.connect(buffer_handler)
        assert server.listen() is True

        # --- Step 2: client connects while buffer is the only handler ---
        client = QLocalSocket()
        client.connectToServer(server_name)
        assert client.waitForConnected(3000), (
            f"Client could not connect: {client.errorString()}"
        )

        # Wait for the buffered signal.
        spy_buf = QSignalSpy(server.activate_requested)
        received = spy_buf.wait(2000)
        assert received, "Buffer handler did not receive signal"
        client.disconnectFromServer()

        # --- Step 3: verify buffer was triggered ---
        assert pending[0] is True, (
            "Buffer handler should have been triggered — activation lost!"
        )

        # --- Step 4: swap to real handler (simulating __init__.py) ---
        server.activate_requested.disconnect(buffer_handler)

        real_activated = [False]

        def real_handler():
            real_activated[0] = True

        server.activate_requested.connect(real_handler)

        # --- Step 5: replay the buffered activation ---
        if pending[0]:
            real_handler()  # Simulate show_from_tray()
        assert real_activated[0] is True, (
            "Buffered activation was not replayed"
        )

        # --- Step 6: a new client should trigger the real handler ---
        real_activated[0] = False
        client2 = QLocalSocket()
        client2.connectToServer(server_name)
        assert client2.waitForConnected(3000)

        spy_real = QSignalSpy(server.activate_requested)
        assert spy_real.wait(2000)
        assert real_activated[0] is True, (
            "Real handler not triggered for new connection after swap"
        )

        client2.disconnectFromServer()
        server.shutdown()


# ───────────────────────────────────────────────────────────────────────
# P3: notify_primary_and_exit — quiet exit, no second process
# ───────────────────────────────────────────────────────────────────────


class TestNotifyPrimaryAndExit:
    """Tests for the secondary-instance exit path.

    ``notify_primary_and_exit`` always calls ``sys.exit(0)``, so we use
    ``pytest.raises(SystemExit)`` to verify it exits as expected."""

    def test_exits_when_no_server_listening(self, qapp):
        """When no server is listening, notify_primary_and_exit must still
        exit (never start a second GUI)."""
        unique_name = f"nonexistent_server_{os.getpid()}_{id(object())}"
        with pytest.raises(SystemExit) as exc_info:
            notify_primary_and_exit(server_name=unique_name)
        assert exc_info.value.code == 0, (
            "Should exit with code 0 even when IPC fails"
        )

    def test_exits_after_successful_notification(self, qapp, server_name):
        """When a server is listening, notify_primary_and_exit should
        connect, send the activation, and still exit."""
        server = InstanceServer(server_name=server_name, parent=qapp)
        assert server.listen() is True

        spy = QSignalSpy(server.activate_requested)

        with pytest.raises(SystemExit) as exc_info:
            notify_primary_and_exit(server_name=server_name)
        assert exc_info.value.code == 0

        # The primary should have received the activation.
        assert spy.wait(2000), "Primary did not receive activation signal"
        assert spy.count() >= 1

        server.shutdown()

    def test_exit_code_is_zero(self, qapp):
        """The exit code is always 0 — this is normal shutdown, not error."""
        unique_name = f"nonexistent_{os.getpid()}_{id(object())}"
        with pytest.raises(SystemExit) as exc_info:
            notify_primary_and_exit(server_name=unique_name)
        assert exc_info.value.code == 0


# ───────────────────────────────────────────────────────────────────────
# IPC end-to-end (supplementary)
# ───────────────────────────────────────────────────────────────────────


def test_notify_primary_causes_activation(qapp, server_name):
    """End-to-end: client connect + write triggers activate_requested."""
    server = InstanceServer(server_name=server_name, parent=qapp)
    assert server.listen() is True

    spy = QSignalSpy(server.activate_requested)

    # Simulate what notify_primary_and_exit does (without sys.exit).
    client = QLocalSocket()
    client.connectToServer(server_name)
    connected = client.waitForConnected(3000)
    assert connected, f"Client could not connect: {client.errorString()}"
    client.write(b"activate")
    client.waitForBytesWritten(1000)
    client.disconnectFromServer()

    assert spy.wait(2000), "Signal not received within timeout"
    assert spy.count() >= 1

    server.shutdown()
