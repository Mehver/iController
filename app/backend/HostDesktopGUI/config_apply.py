# SPDX-License-Identifier: BSD-3-Clause
"""Listening-address application on the GUI thread; IO stays in ServerWorker.

Only a changed Config HOST/PORT can request an automatic restart. One latest
target and one old-listener rollback are retained, without polling or blocking.
"""


class ServiceApply:
    def __init__(self, start, stop, complete, log):
        self.start, self.stop, self.complete, self.log = start, stop, complete, log
        self.phase = 'stopped'
        self.wanted = False
        self.attempt = self.live = None
        self.request_id = 0
        self.restart = None
        self.degraded = None

    def _launch(self, bind):
        self.attempt, self.phase = bind, 'starting'
        self.log(f'[info] starting listener on {bind[0]}:{bind[1]}\n')
        self.request_id = self.start(*bind)

    def _stop(self):
        self.phase = 'stopping'
        self.log('[info] stopping listener...\n')
        self.stop()  # Direct, thread-safe stop; never queued to a blocked Qt worker.

    def _cancel(self, reason):
        if self.restart is not None:
            self.complete(self.restart['operation'], reason)
        self.restart = None

    def manual_start(self, host, port):
        if self.phase != 'stopped':
            return
        self._cancel('Automatic service application was replaced by a manual start.')
        self.wanted, self.degraded = True, None
        self.live = None  # A listener from a previously stopped session is not a rollback target.
        self._launch((host, port))

    def manual_stop(self):
        self.wanted, self.degraded = False, None
        self._cancel('Automatic service application was cancelled by a manual stop.')
        if self.phase not in ('stopped', 'failed'):
            self._stop()

    def quit(self):
        self.wanted = False
        self.restart = None
        self.stop()

    def apply(self, previous, target, operation):
        if self.phase == 'failed':
            self.complete(operation, dict(message='Service worker could not close its event loop; application restart required.', restart=True))
            return
        if not self.wanted:
            self.complete(operation, None)  # Stopped means update parameters only.
            return
        if previous == target:
            if self.restart is not None:
                self.restart['operation'] = operation  # Wait for the already requested change.
            else:
                error = self.degraded[1] if self.degraded and self.degraded[0] == target else None
                self.complete(operation, error)
            return
        if self.phase == 'running' and self.attempt == target:
            self.degraded = None
            self.complete(operation, None)
            return
        old = self.restart['old'] if self.restart else self.live
        self.log(f'[info] listener configuration changed to {target[0]}:{target[1]}; clients may disconnect and the old URL may no longer work; follow listener logs and QR\n')
        self.restart = dict(target=target, old=old, operation=operation, restoring=False, error='')
        if self.phase == 'starting' and self.attempt == target:
            return  # The accepted start already targets the new Config; await readiness.
        if self.phase == 'stopped':
            self._launch(target)
        else:
            self._stop()

    def _failed(self, detail, *, restart_required=False):
        request = self.restart
        self.restart = None
        self.wanted = False
        result = dict(message=detail, restart=True) if restart_required else detail
        self.degraded = (request['target'], result)
        self.log(f'[error] configuration retained, but service application failed: {detail}\n')
        self.complete(request['operation'], result)

    def on_state(self, state):
        if state.request_id != self.request_id:
            return
        self.phase = state.phase
        request = self.restart
        if state.phase == 'failed':
            self.wanted = False
            if request:
                self._failed(state.error, restart_required=True)
            else:
                self.log(f'[error] service health failure after configuration operation: {state.error}\n')
            return
        if state.running:
            self.live = self.attempt
            if request and not request['restoring'] and request['old'] is None and self.attempt != request['target']:
                request['old'] = self.attempt  # Ready arrived after the save requested a stop.
            if not self.wanted:
                self._stop()
            elif request is not None:
                if request['restoring']:
                    detail = request['error'] + f'; old service restored on {self.attempt[0]}:{self.attempt[1]}; new configuration remains saved'
                    self.degraded = (request['target'], detail)
                    self.restart = None
                    self.log(f'[warn] {detail}\n')
                    self.complete(request['operation'], detail)
                elif self.attempt == request['target']:
                    self.restart, self.degraded = None, None
                    self.complete(request['operation'], None)
                else:
                    self._stop()
            return
        if state.phase == 'starting':
            if not self.wanted or (request and not request['restoring'] and self.attempt != request['target']):
                self._stop()
            return
        if state.phase != 'stopped':
            return
        if not self.wanted:
            return
        if request is None:
            self.wanted = False
            if state.error:
                self.log(f'[error] listener stopped after readiness: {state.error}\n')
            return
        if state.error and (request['restoring'] or self.attempt == request['target']):
            if request['restoring']:
                self._failed(request['error'] + f'; old service recovery also failed: {state.error}; service stopped')
            else:
                request['error'] = f'Failed to listen on {self.attempt[0]}:{self.attempt[1]}: {state.error}'
                if request['old'] and request['old'] != request['target']:
                    request['restoring'] = True
                    self.log('[warn] new listener failed; restoring the old listener once\n')
                    self._launch(request['old'])
                else:
                    self._failed(request['error'] + '; service stopped')
        else:
            self._launch(request['old'] if request['restoring'] else request['target'])
