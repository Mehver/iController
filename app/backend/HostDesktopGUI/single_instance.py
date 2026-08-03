# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

"""Single-instance guard for HostDesktopGUI using QLockFile + QLocalServer/Socket.

When a second GUI process is launched while one is already running (e.g. by
clicking the taskbar pinned icon on Windows), the second process notifies the
primary to restore/activate its window and then exits immediately.

CLI (HostDesktopCLI) is completely unaffected — this module is only imported
by HostDesktopGUI.
"""

import logging
import os
import sys
import tempfile
from typing import Optional

from PySide6.QtCore import QLockFile, QObject, Signal, Slot
from PySide6.QtNetwork import QLocalServer, QLocalSocket

logger = logging.getLogger(__name__)

# Well-known server name.  Include a version suffix so a future IPC protocol
# change can use a different name without colliding with older running instances.
_SERVER_NAME = "iController_GUI_Instance_v1"

# Timeout (ms) for synchronous IPC operations in the secondary instance.
_IPC_CONNECT_TIMEOUT = 3000
_IPC_WRITE_TIMEOUT = 1000


def _lock_file_path() -> str:
    """Return the filesystem path for the inter-process lock file.

    Uses the platform-defined temp directory so different OS users get
    separate lock scopes, which is the desired behaviour.
    """
    return os.path.join(tempfile.gettempdir(), "iController_GUI.lock")


# ---------------------------------------------------------------------------
# Primary-instance side: QLocalServer that receives activation requests
# ---------------------------------------------------------------------------


class InstanceServer(QObject):
    """QLocalServer wrapper that listens for activation requests.

    When a secondary instance connects, ``activate_requested`` is emitted on
    the Qt main thread so the window can be safely restored/activated.
    """

    activate_requested = Signal()

    def __init__(
        self,
        parent: Optional[QObject] = None,
        server_name: Optional[str] = None,
    ):
        super().__init__(parent)
        self._server: Optional[QLocalServer] = None
        # Allow overriding the server name (primarily for testing).
        self._server_name = server_name if server_name is not None else _SERVER_NAME

    @property
    def server_name(self) -> str:
        return self._server_name

    def listen(self) -> bool:
        """Start listening on the well-known server name.

        Any stale socket file/pipe from a previously crashed primary is
        removed before listening.

        Returns ``True`` on success, ``False`` if the server cannot listen
        (unlikely, but logged for diagnostics).
        """
        # Clean up a potential stale server from a crashed previous run.
        # (On Windows the OS cleans the named pipe; on Unix the socket file
        # may persist — removeServer handles both.)
        QLocalServer.removeServer(self._server_name)

        self._server = QLocalServer(self)
        self._server.newConnection.connect(self._on_new_connection)

        if not self._server.listen(self._server_name):
            logger.warning(
                "InstanceServer listen failed: %s", self._server.errorString()
            )
            return False
        return True

    def shutdown(self):
        """Gracefully stop listening and release resources."""
        if self._server is not None:
            self._server.close()
            self._server = None

    @Slot()
    def _on_new_connection(self):
        """Handle an incoming connection from a secondary instance.

        Any successful connection is treated as an activation request —
        we do not inspect the payload.
        """
        socket = self._server.nextPendingConnection()
        if socket is None:
            return
        # Qt-idiomatic lifecycle: schedule deletion *before* disconnect so
        # that ``deleteLater`` is reliably called even if the disconnect
        # completes synchronously.
        socket.disconnected.connect(socket.deleteLater)
        socket.disconnectFromServer()
        # We are always called from the Qt main thread (the server lives
        # in the main thread), so it is safe to emit directly.
        self.activate_requested.emit()


# ---------------------------------------------------------------------------
# Lock acquisition
# ---------------------------------------------------------------------------


def attempt_primary(
    lock_path: Optional[str] = None,
) -> "tuple[bool, Optional[QLockFile]]":
    """Attempt to become the primary instance by acquiring a QLockFile.

    This is designed to be called **before** a ``QApplication`` is created so
    that a secondary instance can exit without ever showing a window or
    splash screen.

    Args:
        lock_path: Filesystem path for the lock file.  If ``None`` (the
            default), the platform temp directory is used.

    Returns:
        ``(True, lock)`` – this is the primary instance; the *lock* is a
        successfully acquired ``QLockFile`` that the caller must keep alive
        for the lifetime of the process.

        ``(True, None)`` – the lock could not be acquired due to a non-fatal
        error (permission, unknown); the caller should still proceed as if
        it were the primary.

        ``(False, None)`` – another instance already holds the lock; the
        caller should notify the primary and exit (see
        :func:`notify_primary_and_exit`).

    Important: the *lock* value is ``None`` for any path where the lock was
    **not** actually acquired.  The caller must never treat a ``None`` lock
    as if it were holding the file.
    """
    if lock_path is None:
        lock_path = _lock_file_path()
    lock = QLockFile(lock_path)

    # We intentionally never mark the lock as "stale" based on age — the OS
    # automatically releases file locks when the owning process exits (even
    # on crash), so a lock file from a dead process does not block a new one.
    lock.setStaleLockTime(0)

    if lock.tryLock(200):
        return True, lock

    error = lock.error()
    if error == QLockFile.LockFailedError:
        logger.debug("Another GUI instance is already running (lock held).")
        return False, None

    if error == QLockFile.PermissionError:
        logger.warning(
            "Lock file permission error at %s; continuing as primary "
            "(no lock held — another instance may start concurrently).",
            lock_path,
        )
        return True, None

    # Unknown error — best-effort: continue without a lock.
    logger.warning(
        "Lock file unknown error (%d) at %s; continuing as primary "
        "(no lock held — another instance may start concurrently).",
        error,
        lock_path,
    )
    return True, None


# ---------------------------------------------------------------------------
# Secondary-instance side: notify the primary, then exit
# ---------------------------------------------------------------------------


def notify_primary_and_exit(server_name: Optional[str] = None) -> None:
    """Send an activation request to the primary instance and exit.

    This should only be called when :func:`attempt_primary` returned
    ``(False, None)``, indicating that a primary instance is already running.

    Args:
        server_name: The QLocalServer name to connect to.  If ``None``, the
            default well-known name is used.

    A minimal ``QCoreApplication`` is created temporarily if one does not
    already exist, because ``QLocalSocket`` requires a running Qt event
    system.  The function always ends with ``sys.exit(0)`` — the caller
    should treat this as "return with exit".
    """
    from PySide6.QtCore import QCoreApplication

    if server_name is None:
        server_name = _SERVER_NAME

    # Ensure a QCoreApplication exists.  In the normal second-instance path
    # (HostDesktopGUI called a second time) there is none; during tests one
    # may already be present.
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)

    socket = QLocalSocket()
    try:
        socket.connectToServer(server_name)

        if socket.waitForConnected(_IPC_CONNECT_TIMEOUT):
            # The payload content is irrelevant — the primary treats *any*
            # incoming connection as an activation request.
            socket.write(b"activate")
            if socket.waitForBytesWritten(_IPC_WRITE_TIMEOUT):
                logger.debug("Activation message sent to primary instance.")
            else:
                logger.warning(
                    "Activation message write timed out: %s",
                    socket.errorString(),
                )
            socket.disconnectFromServer()
            # Give the socket a moment to finish disconnecting gracefully.
            if socket.state() != QLocalSocket.UnconnectedState:
                socket.waitForDisconnected(500)
        else:
            # We cannot reach the primary.  Possible causes:
            #  - the primary crashed but left a non-stale lock file behind
            #    (unlikely — OS cleans file locks on process exit)
            #  - a firewall/security product is blocking the local pipe
            #  - the server name changed between versions
            #
            # In any case we must NOT launch a second GUI (that would
            # violate the single-instance contract).
            logger.warning(
                "Could not connect to the running GUI instance: %s.  "
                "The primary instance may have terminated abnormally or "
                "the IPC server is unreachable.  "
                "Exiting without launching a second GUI.",
                socket.errorString(),
            )
            # Explicit abort: we never connected, but Qt may have allocated
            # resources that should be released promptly.
            socket.abort()
    finally:
        # Guard against corner cases where the socket object outlives the
        # function (e.g. an exception propagates).  close() is safe to call
        # on an already-closed socket.
        socket.close()

    # Always exit — we are a secondary instance regardless of whether
    # the IPC message was delivered.
    sys.exit(0)
