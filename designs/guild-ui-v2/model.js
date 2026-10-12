/* Five Elements Tales guild interaction model. All rules and data are local demos. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.GuildModel = factory();
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const MAX_VALUE = 1000000000;
  const roles = Object.freeze(['帮主', '长老', '精英', '帮众']);
  const donationTiers = Object.freeze({
    small: Object.freeze({ id: 'small', label: '诚心捐献', coins: 10000, contribution: 200, funds: 10000, construction: 200, limit: 5 }),
    large: Object.freeze({ id: 'large', label: '倾力捐献', coins: 30000, contribution: 600, funds: 30000, construction: 600, limit: 3 })
  });
  const inventoryLabels = Object.freeze({ pill: '清灵丹', scroll: '修行心得', talisman: '护身灵符', chest: '帮会珍宝匣' });
  const clone = value => JSON.parse(JSON.stringify(value));
  const isRecord = value => value !== null && typeof value === 'object' && !Array.isArray(value);
  const integer = (value, fallback, max = MAX_VALUE) => Number.isSafeInteger(value) && value >= 0 && value <= max ? value : fallback;
  const readDate = value => {
    const date = value instanceof Date ? new Date(value.getTime()) : new Date(value);
    if (!Number.isFinite(date.getTime())) throw new TypeError('演示时钟必须返回有效日期。');
    return date;
  };
  function dateKey(value) {
    const date = readDate(value);
    return date.getFullYear() + '-' + String(date.getMonth() + 1).padStart(2, '0') + '-' + String(date.getDate()).padStart(2, '0');
  }
  function validDateKey(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const date = new Date(value + 'T12:00:00');
    return Number.isFinite(date.getTime()) && dateKey(date) === value;
  }
  function announcementIsValid(value) {
    if (typeof value !== 'string') return false;
    const length = Array.from(value.trim()).length;
    return length >= 8 && length <= 180 && !/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(value);
  }
  function createInitialState(now = new Date()) {
    const memberData = [
      ['self', '青云小道', 68, '精英', true, 1280, 1],
      ['m2', '云隐真人', 79, '帮主', true, 2860, 2],
      ['m3', '月下清铃', 75, '长老', true, 2420, 3],
      ['m4', '竹间听风', 72, '长老', false, 2150, 4],
      ['m5', '桃夭小仙', 66, '精英', true, 1800, 5],
      ['m6', '逍遥一剑', 70, '精英', true, 1660, 2],
      ['m7', '桂影疏疏', 64, '帮众', false, 980, 3],
      ['m8', '执灯归人', 62, '帮众', true, 820, 4],
      ['m9', '半壶云气', 59, '帮众', false, 720, 1],
      ['m10', '鹿鸣山涧', 65, '帮众', true, 1080, 5],
      ['m11', '南山有鹤', 61, '帮众', false, 600, 4],
      ['m12', '星河渡月', 57, '帮众', false, 480, 3]
    ];
    return {
      schemaVersion: 1,
      currentUser: { id: 'self', name: '青云小道', contribution: 3280, coins: 80000, role: '精英' },
      guild: {
        id: '10086', name: '青云道盟', level: 5, funds: 128600, construction: 8600,
        constructionTarget: 12000, memberCapacity: 50,
        announcement: '同修相聚，仙途不孤。欢迎各位道友加入青云道盟！每日记得签到、完成帮会委托；花灯夜游活动已开放演示报名，愿与诸位共赏月色，同修大道。'
      },
      members: memberData.map(([id, name, level, role, online, weeklyContribution, avatar]) => ({ id, name, level, role, online, weeklyContribution, avatar: 'avatar-' + avatar + '.png' })),
      dailyDate: dateKey(now), signedInDate: null,
      donationCounts: { small: 0, large: 0 },
      tasks: [
        { id: 'herbs', name: '采药济世', description: '为帮会药房筹集清灵草。', progress: 5, target: 5, claimed: false, reward: { contribution: 180, coins: 5000, items: { pill: 2 } }, icon: 'icon-pill.png' },
        { id: 'patrol', name: '山门巡守', description: '完成山门巡守，护佑一方安宁。', progress: 3, target: 3, claimed: false, reward: { contribution: 220, coins: 8000, items: { talisman: 1 } }, icon: 'icon-talisman.png' },
        { id: 'practice', name: '同门论道', description: '与同门完成三次论道。演示进度固定。', progress: 1, target: 3, claimed: false, reward: { contribution: 260, coins: 10000, items: { scroll: 1 } }, icon: 'icon-scroll.png' }
      ],
      events: [
        { id: 'lantern', name: '花灯夜游', description: '结伴赏灯，同游青云山。', dateLabel: '演示场次 · 周六 20:00', status: 'open', joined: false, participants: 18, capacity: 30, icon: 'round_badge_lotus.png' },
        { id: 'trial', name: '镇妖试炼', description: '同门携手，探访镇妖古塔。', dateLabel: '演示场次 · 尚未开放', status: 'upcoming', joined: false, participants: 0, capacity: 20, icon: 'round_badge_pagoda.png' },
        { id: 'moon', name: '月下论道', description: '桂香满庭，月下共话修行。', dateLabel: '演示场次 · 已结束', status: 'ended', joined: false, participants: 24, capacity: 30, icon: 'round_badge_compass.png' }
      ],
      shop: [
        { id: 'pill', itemId: 'pill', name: '清灵丹', description: '修行常备的温润丹药。', cost: 180, stock: 10, purchased: 0, icon: 'icon-pill.png' },
        { id: 'scroll', itemId: 'scroll', name: '修行心得', description: '同门整理的一卷修行札记。', cost: 480, stock: 5, purchased: 0, icon: 'icon-scroll.png' },
        { id: 'talisman', itemId: 'talisman', name: '护身灵符', description: '寄托平安心愿的护身符箓。', cost: 360, stock: 6, purchased: 0, icon: 'icon-talisman.png' },
        { id: 'chest', itemId: 'chest', name: '帮会珍宝匣', description: '帮会准备的精致珍宝礼匣。', cost: 1600, stock: 2, purchased: 0, icon: 'icon-chest.png' }
      ],
      inventory: { pill: 0, scroll: 0, talisman: 0, chest: 0 }
    };
  }

  // Restore only known, validated mutable fields. Definitions and asset paths stay canonical.
  function normalizeState(raw, now = new Date()) {
    const state = createInitialState(now);
    if (!isRecord(raw) || raw.schemaVersion !== 1) return state;
    if (isRecord(raw.currentUser)) {
      state.currentUser.contribution = integer(raw.currentUser.contribution, state.currentUser.contribution);
      state.currentUser.coins = integer(raw.currentUser.coins, state.currentUser.coins);
      if (roles.includes(raw.currentUser.role)) state.currentUser.role = raw.currentUser.role;
    }
    if (isRecord(raw.guild)) {
      state.guild.funds = integer(raw.guild.funds, state.guild.funds);
      state.guild.construction = integer(raw.guild.construction, state.guild.construction);
      if (announcementIsValid(raw.guild.announcement)) state.guild.announcement = raw.guild.announcement.trim();
    }
    if (validDateKey(raw.signedInDate)) state.signedInDate = raw.signedInDate;
    if (raw.dailyDate === state.dailyDate && isRecord(raw.donationCounts)) {
      for (const key of Object.keys(donationTiers)) state.donationCounts[key] = integer(raw.donationCounts[key], 0, donationTiers[key].limit);
    }
    if (Array.isArray(raw.members)) {
      const self = raw.members.find(member => isRecord(member) && member.id === 'self');
      if (self) state.members[0].weeklyContribution = integer(self.weeklyContribution, state.members[0].weeklyContribution);
    }
    state.members[0].role = state.currentUser.role;
    if (Array.isArray(raw.tasks)) {
      for (const task of state.tasks) {
        const saved = raw.tasks.find(item => isRecord(item) && item.id === task.id);
        if (saved && task.progress >= task.target) task.claimed = saved.claimed === true;
      }
    }
    if (Array.isArray(raw.events)) {
      for (const event of state.events) {
        const saved = raw.events.find(item => isRecord(item) && item.id === event.id);
        if (saved && event.status === 'open' && saved.joined === true) {
          event.joined = true;
          event.participants += 1;
        }
      }
    }
    if (Array.isArray(raw.shop)) {
      for (const product of state.shop) {
        const saved = raw.shop.find(item => isRecord(item) && item.id === product.id);
        if (saved) {
          product.purchased = integer(saved.purchased, 0, product.stock);
          product.stock -= product.purchased;
        }
      }
    }
    if (isRecord(raw.inventory)) {
      for (const key of Object.keys(state.inventory)) state.inventory[key] = integer(raw.inventory[key], 0);
    }
    return state;
  }

  function createStore(options = {}) {
    const now = typeof options.now === 'function' ? options.now : () => new Date();
    let state = normalizeState(options.state, now());
    const listeners = new Set();
    function refreshDay() {
      const today = dateKey(now());
      if (state.dailyDate === today) return false;
      state.dailyDate = today;
      state.donationCounts = { small: 0, large: 0 };
      return true;
    }
    function publish(action) {
      for (const listener of Array.from(listeners)) listener(clone(state), action);
    }
    function addReward(target, reward) {
      const contribution = target.currentUser.contribution + (reward.contribution || 0);
      const coins = target.currentUser.coins + (reward.coins || 0);
      const weekly = target.members[0].weeklyContribution + (reward.contribution || 0);
      if ([contribution, coins, weekly].some(value => !Number.isSafeInteger(value) || value > MAX_VALUE)) return false;
      for (const [id, quantity] of Object.entries(reward.items || {})) {
        if (!Object.hasOwn(target.inventory, id) || target.inventory[id] + quantity > MAX_VALUE) return false;
      }
      target.currentUser.contribution = contribution;
      target.currentUser.coins = coins;
      target.members[0].weeklyContribution = weekly;
      for (const [id, quantity] of Object.entries(reward.items || {})) target.inventory[id] += quantity;
      return true;
    }
    function dispatch(action) {
      const dayChanged = refreshDay();
      const next = clone(state);
      const fail = message => {
        if (dayChanged) publish({ type: 'DAY_CHANGED' });
        return { ok: false, message, state: clone(state) };
      };
      if (!isRecord(action) || typeof action.type !== 'string') return fail('操作无效，请重新选择。');
      let message;
      switch (action.type) {
        case 'SIGN_IN':
          if (next.signedInDate === next.dailyDate) return fail('今日已经签到，请明日再来。');
          if (!addReward(next, { contribution: 100 })) return fail('演示数值已达上限，请重置演示。');
          next.signedInDate = next.dailyDate;
          message = '签到成功，获得 100 帮会贡献。';
          break;
        case 'DONATE': {
          if (typeof action.tier !== 'string' || !Object.hasOwn(donationTiers, action.tier)) return fail('请选择有效的捐献档位。');
          const tier = donationTiers[action.tier];
          if (next.donationCounts[tier.id] >= tier.limit) return fail('此档位今日捐献次数已用完。');
          if (next.currentUser.coins < tier.coins) return fail('铜钱不足，无法完成捐献。');
          if (next.guild.funds + tier.funds > MAX_VALUE || next.guild.construction + tier.construction > MAX_VALUE || !addReward(next, { contribution: tier.contribution })) return fail('演示数值已达上限，请重置演示。');
          next.currentUser.coins -= tier.coins;
          next.guild.funds += tier.funds;
          next.guild.construction += tier.construction;
          next.donationCounts[tier.id] += 1;
          message = '捐献成功，获得 ' + tier.contribution + ' 帮会贡献。';
          break;
        }
        case 'CLAIM_TASK': {
          const task = next.tasks.find(item => item.id === action.id);
          if (!task) return fail('未找到此帮会委托。');
          if (task.claimed) return fail('该委托奖励已经领取。');
          if (task.progress < task.target) return fail('委托尚未完成，暂时不能领取。');
          if (!addReward(next, task.reward)) return fail('演示数值已达上限，请重置演示。');
          task.claimed = true;
          message = '已领取「' + task.name + '」奖励，道具已放入演示背包。';
          break;
        }
        case 'TOGGLE_EVENT': {
          const event = next.events.find(item => item.id === action.id);
          if (!event) return fail('未找到此帮会活动。');
          if (event.joined) {
            event.joined = false;
            event.participants = Math.max(0, event.participants - 1);
            message = '已取消「' + event.name + '」演示报名。';
          } else {
            if (event.status !== 'open') return fail(event.status === 'ended' ? '此演示场次已经结束。' : '此演示场次尚未开放报名。');
            if (event.participants >= event.capacity) return fail('此演示场次报名人数已满。');
            event.joined = true;
            event.participants += 1;
            message = '已报名「' + event.name + '」演示场次。';
          }
          break;
        }
        case 'EXCHANGE': {
          const product = next.shop.find(item => item.id === action.id);
          if (!product) return fail('未找到此帮会商品。');
          if (!Number.isSafeInteger(action.quantity) || action.quantity < 1) return fail('兑换数量必须为正整数。');
          if (action.quantity > product.stock) return fail('兑换数量超过本次演示剩余限购数量。');
          const cost = product.cost * action.quantity;
          if (next.currentUser.contribution < cost) return fail('帮会贡献不足，暂时无法兑换。');
          if (next.inventory[product.itemId] + action.quantity > MAX_VALUE) return fail('演示背包已达上限，请重置演示。');
          next.currentUser.contribution -= cost;
          product.stock -= action.quantity;
          product.purchased += action.quantity;
          next.inventory[product.itemId] += action.quantity;
          message = '已兑换 ' + action.quantity + ' 份「' + product.name + '」，已放入演示背包。';
          break;
        }
        case 'UPDATE_ANNOUNCEMENT':
          if (!['帮主', '长老'].includes(next.currentUser.role)) return fail('仅帮主或长老可以编辑帮会公告。');
          if (!announcementIsValid(action.text)) return fail('公告请输入 8–180 个字，且不能包含无效控制字符。');
          next.guild.announcement = action.text.trim();
          message = '帮会公告已保存到本地演示。';
          break;
        case 'SET_DEMO_ROLE':
          if (!roles.includes(action.role)) return fail('请选择有效的演示身份。');
          next.currentUser.role = action.role;
          next.members[0].role = action.role;
          message = '已切换为「' + action.role + '」演示身份。';
          break;
        default:
          return fail('暂不支持此操作。');
      }
      state = next;
      publish(action);
      return { ok: true, message, state: clone(state) };
    }
    return {
      getState() { refreshDay(); return clone(state); },
      dispatch,
      reset() {
        state = createInitialState(now());
        publish({ type: 'RESET' });
        return { ok: true, message: '演示数据已恢复初始状态。', state: clone(state) };
      },
      subscribe(listener) {
        if (typeof listener !== 'function') throw new TypeError('订阅者必须是函数。');
        listeners.add(listener);
        return () => listeners.delete(listener);
      }
    };
  }
  return Object.freeze({ createStore, createInitialState, normalizeState, dateKey, donationTiers, roles, inventoryLabels });
}));
