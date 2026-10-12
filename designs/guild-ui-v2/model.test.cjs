'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { createStore, createInitialState, normalizeState } = require('./model.js');
const fixed = () => new Date(2026, 8, 13, 12);
const store = state => createStore({ state, now: fixed });

test('a donation updates the wallet, guild resources, daily allowance and member ranking together', () => {
  const guild = store();
  const before = guild.getState();
  const result = guild.dispatch({ type: 'DONATE', tier: 'large' });
  assert.equal(result.ok, true);
  assert.equal(result.state.currentUser.coins, before.currentUser.coins - 30000);
  assert.equal(result.state.currentUser.contribution, before.currentUser.contribution + 600);
  assert.equal(result.state.guild.funds, before.guild.funds + 30000);
  assert.equal(result.state.guild.construction, before.guild.construction + 600);
  assert.equal(result.state.members[0].weeklyContribution, before.members[0].weeklyContribution + 600);
  assert.equal(result.state.donationCounts.large, 1);
});

test('insufficient coins reject a donation without partial rewards or consumed allowance', () => {
  const guild = store();
  assert.equal(guild.dispatch({ type: 'DONATE', tier: 'large' }).ok, true);
  assert.equal(guild.dispatch({ type: 'DONATE', tier: 'large' }).ok, true);
  const before = guild.getState();
  assert.match(guild.dispatch({ type: 'DONATE', tier: 'large' }).message, /铜钱不足/);
  assert.deepEqual(guild.getState(), before);
});

test('each donation tier enforces its own daily allowance even when the wallet has enough coins', () => {
  const initial = createInitialState(fixed());
  initial.currentUser.coins = 1000000;
  const guild = store(initial);
  for (let count = 0; count < 5; count++) assert.equal(guild.dispatch({ type: 'DONATE', tier: 'small' }).ok, true);
  let before = guild.getState();
  assert.equal(guild.dispatch({ type: 'DONATE', tier: 'small' }).ok, false);
  assert.deepEqual(guild.getState(), before);
  for (let count = 0; count < 3; count++) assert.equal(guild.dispatch({ type: 'DONATE', tier: 'large' }).ok, true);
  before = guild.getState();
  assert.equal(guild.dispatch({ type: 'DONATE', tier: 'large' }).ok, false);
  assert.deepEqual(guild.getState(), before);
});

test('sign in is once per local calendar day and a live store resets daily donations at midnight', () => {
  let time = new Date(2026, 8, 13, 23, 59);
  const guild = createStore({ now: () => time });
  guild.dispatch({ type: 'DONATE', tier: 'small' });
  assert.equal(guild.dispatch({ type: 'SIGN_IN' }).ok, true);
  const balance = guild.getState().currentUser.contribution;
  assert.equal(guild.dispatch({ type: 'SIGN_IN' }).ok, false);
  assert.equal(guild.getState().currentUser.contribution, balance);
  time = new Date(2026, 8, 14, 0, 1);
  assert.deepEqual(guild.getState().donationCounts, { small: 0, large: 0 });
  assert.equal(guild.dispatch({ type: 'SIGN_IN' }).ok, true);
  assert.equal(guild.getState().currentUser.contribution, balance + 100);
});

test('completed tasks grant all rewards once; incomplete tasks never grant rewards', () => {
  const guild = store();
  let before = guild.getState();
  assert.equal(guild.dispatch({ type: 'CLAIM_TASK', id: 'practice' }).ok, false);
  assert.deepEqual(guild.getState(), before);
  assert.equal(guild.dispatch({ type: 'CLAIM_TASK', id: 'herbs' }).ok, true);
  assert.equal(guild.getState().currentUser.coins, before.currentUser.coins + 5000);
  assert.equal(guild.getState().currentUser.contribution, before.currentUser.contribution + 180);
  assert.equal(guild.getState().inventory.pill, 2);
  before = guild.getState();
  assert.equal(guild.dispatch({ type: 'CLAIM_TASK', id: 'herbs' }).ok, false);
  assert.deepEqual(guild.getState(), before);
  const restored = store(JSON.parse(JSON.stringify(before)));
  assert.equal(restored.dispatch({ type: 'CLAIM_TASK', id: 'herbs' }).ok, false);
});

test('task rewards and purchases share one inventory while purchases do not reduce weekly contribution', () => {
  const guild = store();
  guild.dispatch({ type: 'CLAIM_TASK', id: 'herbs' });
  const before = guild.getState();
  assert.equal(guild.dispatch({ type: 'EXCHANGE', id: 'pill', quantity: 3 }).ok, true);
  const after = guild.getState();
  assert.equal(after.inventory.pill, 5);
  assert.equal(after.currentUser.contribution, before.currentUser.contribution - 540);
  assert.equal(after.shop[0].stock, 7);
  assert.equal(after.shop[0].purchased, 3);
  assert.equal(after.members[0].weeklyContribution, before.members[0].weeklyContribution);
});

test('stock and contribution both prevent overbuying without partial changes', () => {
  const guild = store();
  assert.equal(guild.dispatch({ type: 'EXCHANGE', id: 'chest', quantity: 2 }).ok, true);
  const before = guild.getState();
  assert.equal(guild.dispatch({ type: 'EXCHANGE', id: 'chest', quantity: 1 }).ok, false);
  assert.deepEqual(guild.getState(), before);
  assert.match(guild.dispatch({ type: 'EXCHANGE', id: 'pill', quantity: 1 }).message, /贡献不足/);
  assert.deepEqual(guild.getState(), before);
});

test('invalid quantities and unknown identifiers are rejected without changing state', () => {
  const guild = store();
  const before = guild.getState();
  for (const quantity of [0, -1, 1.5, '1', NaN, Infinity, Number.MAX_SAFE_INTEGER + 1, null, undefined]) {
    assert.equal(guild.dispatch({ type: 'EXCHANGE', id: 'pill', quantity }).ok, false);
    assert.deepEqual(guild.getState(), before);
  }
  for (const action of [null, {}, { type: 'UNKNOWN' }, { type: 'DONATE', tier: '__proto__' }, { type: 'DONATE', tier: 'toString' }, { type: 'CLAIM_TASK', id: 'missing' }, { type: 'EXCHANGE', id: 'missing', quantity: 1 }, { type: 'TOGGLE_EVENT', id: 'missing' }]) {
    assert.equal(guild.dispatch(action).ok, false);
    assert.deepEqual(guild.getState(), before);
  }
});

test('only an open demo event accepts signups and canceling restores the participant count', () => {
  const guild = store();
  const initial = guild.getState();
  assert.equal(guild.dispatch({ type: 'TOGGLE_EVENT', id: 'trial' }).ok, false);
  assert.equal(guild.dispatch({ type: 'TOGGLE_EVENT', id: 'moon' }).ok, false);
  assert.deepEqual(guild.getState(), initial);
  assert.equal(guild.dispatch({ type: 'TOGGLE_EVENT', id: 'lantern' }).ok, true);
  assert.equal(guild.getState().events[0].participants, 19);
  const reloaded = store(guild.getState());
  assert.equal(reloaded.getState().events[0].participants, 19);
  assert.equal(reloaded.dispatch({ type: 'TOGGLE_EVENT', id: 'lantern' }).ok, true);
  assert.equal(reloaded.getState().events[0].participants, 18);
  assert.equal(reloaded.getState().events[0].joined, false);
});

test('announcement permissions apply in the model and persisted demo roles stay in sync with members', () => {
  const guild = store();
  const action = { type: 'UPDATE_ANNOUNCEMENT', text: '同门道友相约山门，一起赏灯论道。' };
  assert.equal(guild.dispatch(action).ok, false);
  guild.dispatch({ type: 'SET_DEMO_ROLE', role: '长老' });
  assert.equal(guild.dispatch(action).ok, true);
  assert.equal(guild.getState().guild.announcement, action.text);
  const restored = store(guild.getState());
  assert.equal(restored.getState().members[0].role, '长老');
  restored.dispatch({ type: 'SET_DEMO_ROLE', role: '帮众' });
  assert.equal(restored.dispatch(action).ok, false);
  assert.equal(restored.dispatch({ type: 'SET_DEMO_ROLE', role: '管理员' }).ok, false);
});

test('announcements validate length and control characters before saving', () => {
  const guild = store();
  guild.dispatch({ type: 'SET_DEMO_ROLE', role: '帮主' });
  const before = guild.getState();
  for (const text of ['', '     ', '短公告', '长'.repeat(181), '同门道友相聚山门\u0000赏灯', null, 123]) {
    assert.equal(guild.dispatch({ type: 'UPDATE_ANNOUNCEMENT', text }).ok, false);
    assert.deepEqual(guild.getState(), before);
  }
});

test('restoring malformed storage validates mutable fields and ignores injected rules or paths', () => {
  for (const bad of [null, [], 'bad', { schemaVersion: 99 }]) assert.deepEqual(normalizeState(bad, fixed()), createInitialState(fixed()));
  const raw = createInitialState(fixed());
  raw.currentUser.coins = -500;
  raw.currentUser.role = '管理员';
  raw.currentUser.contribution = '999999';
  raw.guild.funds = Infinity;
  raw.guild.announcement = 'bad';
  raw.members[0].avatar = 'javascript:alert(1)';
  raw.shop[0].cost = 0;
  raw.shop[0].stock = 99999;
  raw.shop[0].purchased = -1;
  raw.events[1].status = 'open';
  raw.events[1].joined = true;
  raw.tasks[2].progress = 3;
  raw.tasks[2].claimed = true;
  raw.tasks[0].reward.coins = 999999999;
  raw.inventory = { pill: -1, chest: 1.5, attacker: 999 };
  raw.donationCounts.small = 100;
  raw.signedInDate = '2026-02-30';
  assert.deepEqual(normalizeState(raw, fixed()), createInitialState(fixed()));
});

test('a saved session preserves transactions but a later day resets only daily allowances', () => {
  const guild = store();
  guild.dispatch({ type: 'SIGN_IN' });
  guild.dispatch({ type: 'DONATE', tier: 'small' });
  guild.dispatch({ type: 'CLAIM_TASK', id: 'patrol' });
  guild.dispatch({ type: 'EXCHANGE', id: 'pill', quantity: 2 });
  const saved = JSON.parse(JSON.stringify(guild.getState()));
  assert.deepEqual(store(saved).getState(), saved);
  const nextDay = createStore({ state: saved, now: () => new Date(2026, 8, 14, 12) }).getState();
  assert.deepEqual(nextDay.donationCounts, { small: 0, large: 0 });
  assert.equal(nextDay.signedInDate, '2026-09-13');
  assert.deepEqual(nextDay.inventory, saved.inventory);
  assert.deepEqual(nextDay.tasks, saved.tasks);
  assert.deepEqual(nextDay.shop, saved.shop);
});

test('snapshots cannot mutate the store and subscribers can be removed; reset restores all demo state', () => {
  const guild = store();
  let notifications = 0;
  const unsubscribe = guild.subscribe(snapshot => {
    notifications++;
    snapshot.currentUser.coins = 0;
  });
  const detached = guild.getState();
  detached.currentUser.contribution = 999999;
  assert.equal(guild.getState().currentUser.contribution, 3280);
  guild.dispatch({ type: 'SIGN_IN' });
  assert.equal(notifications, 1);
  assert.equal(guild.getState().currentUser.coins, 80000);
  guild.dispatch({ type: 'SIGN_IN' });
  assert.equal(notifications, 1);
  unsubscribe();
  guild.dispatch({ type: 'DONATE', tier: 'small' });
  assert.equal(notifications, 1);
  assert.deepEqual(guild.reset().state, createInitialState(fixed()));
});

test('numeric overflow rejects the entire operation rather than corrupting a saved balance', () => {
  const initial = createInitialState(fixed());
  initial.currentUser.contribution = 1000000000;
  const guild = store(initial);
  const before = guild.getState();
  assert.equal(guild.dispatch({ type: 'DONATE', tier: 'small' }).ok, false);
  assert.deepEqual(guild.getState(), before);
  assert.equal(guild.dispatch({ type: 'CLAIM_TASK', id: 'herbs' }).ok, false);
  assert.deepEqual(guild.getState(), before);
});
