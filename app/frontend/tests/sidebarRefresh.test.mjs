// SPDX-License-Identifier: BSD-3-Clause
// Execute the actual TSX class/lifecycle code, omitting only JSX render and
// replacing external imports. No React/MUI install or algorithm copy is needed.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {stripTypeScriptTypes} from 'node:module';
import vm from 'node:vm';

const settle = async () => { for (let i = 0; i < 20; i++) await Promise.resolve(); };
const deferred = () => {
    let resolve, reject;
    const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
    return {promise, resolve, reject};
};

function loadMenu(name, open = false, expanded = true) {
    const key = name === 'VolumeMenu' ? 'volume' : 'brightness';
    const source = readFileSync(new URL(`../src/components/SideBar/${name}.tsx`, import.meta.url), 'utf8');
    const render = source.indexOf('    render() {');
    assert.notEqual(render, -1);
    const lifecycle = source.slice(0, render).replace(/^import[^\n]*\n/gm, '') +
        `\n}\nglobalThis.MenuUnderTest = ${name};`;
    const reads = [], writes = [], updates = [];
    class Component {
        constructor(props) { this.props = props; }
        setState(update) { this.state = {...this.state, ...update}; updates.push(update); }
    }
    const debounce = callback => {
        let pending;
        const invoke = (...args) => { pending = args; };
        invoke.cancel = () => { pending = undefined; };
        invoke.flush = () => {
            if (pending === undefined) return;
            const args = pending; pending = undefined;
            return callback(...args);
        };
        return invoke;
    };
    const context = {Component, debounce, Context: {}, console: {log() {}, error() {}}};
    context[`api_${key}_get`] = () => { const d = deferred(); reads.push(d); return d.promise; };
    context[`api_${key}_set`] = value => { const d = deferred(); writes.push({...d, value}); return d.promise; };
    vm.runInNewContext(stripTypeScriptTypes(lifecycle, {mode: 'strip'}), context, {filename: name + '.tsx'});
    const menu = new context.MenuUnderTest({drawerOpen: open, expanded});
    const toggle = (drawerOpen, expanded = menu.props.expanded) => {
        const previous = menu.props;
        menu.props = {drawerOpen, expanded};
        menu.componentDidUpdate(previous);
    };
    return {menu, toggle, reads, writes, updates, reply: value => ({[key]: value})};
}

for (const name of ['VolumeMenu', 'BrightnessMenu']) {
    test(`${name}: both Collapse edges refresh; simultaneous drawer/open edge is deduplicated`, async () => {
        const x = loadMenu(name, false, false);
        x.menu.componentDidMount(); await settle();
        x.toggle(true, true); await settle();
        assert.equal(x.reads.length, 1); // Two changes, one lifecycle refresh.
        x.reads[0].resolve(x.reply(50)); await settle();
        x.toggle(true, false); await settle();
        x.toggle(true, true); await settle();
        assert.equal(x.reads.length, 3);
        x.reads[2].resolve(x.reply(80)); await settle();
        x.reads[1].resolve(x.reply(20)); await settle();
        assert.equal(x.menu.state.value, 80);
        x.toggle(false, false); x.toggle(false, true); await settle();
        assert.equal(x.reads.length, 3); // Hidden drawer transitions do not query.
        x.toggle(true, false); await settle();
        assert.equal(x.reads.length, 4);
        x.menu.componentWillUnmount();
    });

    test(`${name}: Collapse close cancels drafts, waits for writes, and open protects edits`, async () => {
        const x = loadMenu(name, true, true);
        x.menu.componentDidMount(); await settle();
        x.reads[0].resolve(x.reply(50)); await settle();
        x.menu.handleChange(null, 20); x.menu.debouncedHandleCommit.flush();
        x.menu.handleChange(null, 40);
        x.toggle(true, false); await settle();
        x.menu.debouncedHandleCommit.flush();
        assert.equal(x.writes.length, 1);
        assert.equal(x.reads.length, 1);
        x.writes[0].resolve(); await settle();
        assert.equal(x.reads.length, 2);
        x.reads[1].resolve(x.reply(20)); await settle();
        x.toggle(true, true); await settle();
        x.menu.handleChange(null, 25);
        x.reads[2].resolve(x.reply(60)); await settle();
        assert.equal(x.menu.state.value, 25);
        x.menu.componentWillUnmount();
    });

    test(`${name}: closed mount is idle; each sidebar reopen reads current server value`, async () => {
        const x = loadMenu(name);
        x.menu.componentDidMount(); await settle();
        assert.equal(x.reads.length, 0);
        x.toggle(true); await settle();
        x.reads[0].resolve(x.reply(60)); await settle();
        assert.equal(x.menu.state.value, 60);
        x.toggle(false); x.toggle(true); await settle();
        assert.equal(x.reads.length, 2);
        x.reads[1].resolve(x.reply(100)); await settle(); // e.g. a restarted server.
        assert.equal(x.menu.state.value, 100);
        x.menu.componentWillUnmount();
    });

    test(`${name}: open mount reads, stale GET cannot override a new open or drag`, async () => {
        const x = loadMenu(name, true);
        x.menu.componentDidMount(); await settle();
        assert.equal(x.reads.length, 1);
        x.toggle(false); x.toggle(true); await settle();
        x.reads[1].resolve(x.reply(70)); await settle();
        x.reads[0].resolve(x.reply(5)); await settle();
        assert.equal(x.menu.state.value, 70);
        const refresh = name === 'VolumeMenu' ? x.menu.fetchVolume : x.menu.fetchBrightness;
        void refresh(); await settle();
        x.menu.handleChange(null, 45);
        x.reads[2].resolve(x.reply(80)); await settle();
        assert.equal(x.menu.state.value, 45);
        x.menu.componentWillUnmount();
        x.menu.debouncedHandleCommit.flush();
        assert.equal(x.writes.length, 0);
    });

    test(`${name}: close/open cancels unsent drafts and waits for ALL already sent writes`, async () => {
        const x = loadMenu(name, true);
        x.menu.componentDidMount(); await settle();
        x.reads[0].resolve(x.reply(60)); await settle();
        x.menu.handleChange(null, 20); x.menu.debouncedHandleCommit.flush();
        x.menu.handleChange(null, 30); x.menu.debouncedHandleCommit.flush();
        assert.equal(x.writes.length, 2);
        x.menu.handleChange(null, 40); // Not yet sent: must never reach the restarted server.
        x.toggle(false); x.toggle(true); await settle();
        x.menu.debouncedHandleCommit.flush();
        assert.equal(x.writes.length, 2);
        assert.equal(x.reads.length, 1);
        x.writes[1].resolve(); await settle(); // The last sent request is NOT the last to finish.
        assert.equal(x.reads.length, 1);
        x.toggle(false); x.toggle(true); await settle();
        x.writes[0].resolve(); await settle();
        assert.equal(x.reads.length, 2); // Only the latest open survives the barrier.
        x.reads[1].resolve(x.reply(20)); await settle();
        assert.equal(x.menu.state.value, 20);
        x.menu.componentWillUnmount();
    });

    test(`${name}: rejected POST still releases read barrier; unmount ignores late reads`, async () => {
        const x = loadMenu(name, true);
        x.menu.componentDidMount(); await settle();
        x.reads[0].resolve(x.reply(50)); await settle();
        x.menu.handleChange(null, 25); x.menu.debouncedHandleCommit.flush();
        x.toggle(false); x.toggle(true);
        x.writes[0].reject(Error('network failed')); await settle();
        assert.equal(x.reads.length, 2);
        const count = x.updates.length;
        x.menu.componentWillUnmount();
        x.reads[1].resolve(x.reply(90)); await settle();
        assert.equal(x.updates.length, count);
    });

    test(`${name}: unmount cancels drafts and prevents sent POST callbacks from updating state`, async () => {
        const x = loadMenu(name, true);
        x.menu.componentDidMount(); await settle();
        x.reads[0].resolve(x.reply(50)); await settle();
        x.menu.handleChange(null, 25); x.menu.debouncedHandleCommit.flush();
        x.menu.handleChange(null, 35);
        const count = x.updates.length;
        x.menu.componentWillUnmount();
        x.menu.debouncedHandleCommit.flush();
        x.writes[0].resolve(); await settle();
        assert.equal(x.writes.length, 1);
        assert.equal(x.updates.length, count);
    });
}

test('sidebar retains keepMounted and passes drawerOpen only to the two controls', () => {
    const source = readFileSync(new URL('../src/components/SideBar/index.tsx', import.meta.url), 'utf8');
    assert.match(source, /keepMounted:\s*true/);
    assert.match(source, /<VolumeMenu drawerOpen=\{this\.context\.drawerOpen\}/);
    assert.match(source, /<BrightnessMenu drawerOpen=\{this\.context\.drawerOpen\}/);
    assert.match(source, /in=\{volumeExpanded\}/);
    assert.match(source, /in=\{brightnessExpanded\}/);
    assert.match(source, /expanded=\{volumeExpanded\}/);
    assert.match(source, /expanded=\{brightnessExpanded\}/);
});

test('actual parent expressions cover autoCollapse/openMenuSW and independent booleans', async () => {
    const source = readFileSync(new URL('../src/components/SideBar/index.tsx', import.meta.url), 'utf8');
    const menuIndex = source.match(/const MenuIndex = \{[\s\S]*?\};/)[0];
    const volume = source.match(/const volumeExpanded = [^;]+;/)[0];
    const brightness = source.match(/const brightnessExpanded = [^;]+;/)[0];
    const compute = vm.runInNewContext(`(function () { ${menuIndex} ${volume} ${brightness} return {volumeExpanded, brightnessExpanded}; })`);
    const v = loadMenu('VolumeMenu'), b = loadMenu('BrightnessMenu');
    v.menu.componentDidMount(); b.menu.componentDidMount();
    const update = context => {
        const state = compute.call({context});
        v.toggle(context.drawerOpen, state.volumeExpanded);
        b.toggle(context.drawerOpen, state.brightnessExpanded);
        return [state.volumeExpanded, state.brightnessExpanded];
    };
    const context = {drawerOpen: true, autoCollapse: true, openMenuSW: 4, sidebarVolumeMenu: false, sidebarBrightnessMenu: true};
    assert.deepEqual(update(context), [true, false]); await settle();
    assert.equal(v.reads.length, 1); assert.equal(b.reads.length, 1);
    assert.deepEqual(update({...context, openMenuSW: 8}), [false, true]); await settle();
    assert.equal(v.reads.length, 2); assert.equal(b.reads.length, 2);
    assert.deepEqual(update({...context, autoCollapse: false, openMenuSW: 8, sidebarVolumeMenu: true, sidebarBrightnessMenu: false}), [true, false]);
    await settle();
    assert.equal(v.reads.length, 3); assert.equal(b.reads.length, 3);
    assert.deepEqual(update({...context, autoCollapse: false, sidebarVolumeMenu: true, sidebarBrightnessMenu: true}), [true, true]);
    await settle();
    assert.equal(v.reads.length, 3); assert.equal(b.reads.length, 4); // Only brightness changed.
    update({...context, drawerOpen: false, openMenuSW: 0}); await settle();
    assert.equal(v.reads.length, 3); assert.equal(b.reads.length, 4);
    v.menu.componentWillUnmount(); b.menu.componentWillUnmount();
});
