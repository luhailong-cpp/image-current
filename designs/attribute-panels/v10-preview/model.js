/*
 * 五行奇谈 · 人物与宝宝属性面板交互演示。
 * 基础数值源于页面参考及明确的演示数据；收益系数仅用于预览交互，
 * 不代表游戏服务端公式。所有操作仅改变当前页面内存中的分配记录。
 */
(function (root, factory) {
  'use strict';
  var model = factory();
  if (typeof module === 'object' && module.exports) module.exports = model;
  if (root) root.AttributeModel = model;
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';

  var attributes = Object.freeze(['体质', '灵力', '力量', '敏捷']);
  var statKeys = Object.freeze(['hp', 'mp', 'patk', 'matk', 'speed', 'def']);
  var previewNotice = '加点收益为交互演示，实际数值以游戏规则为准。';
  var previewCoefficients = [
    { hp: 42, mp: 0, patk: 0, matk: 0, speed: 0, def: 3 },
    { hp: 0, mp: 28, patk: 0, matk: 18, speed: 0, def: 0 },
    { hp: 6, mp: 0, patk: 20, matk: 0, speed: 0, def: 0 },
    { hp: 0, mp: 0, patk: 0, matk: 0, speed: 3, def: 1 }
  ];
  previewCoefficients.forEach(Object.freeze);
  Object.freeze(previewCoefficients);

  var entities = [
    {
      id: 'hero', name: '清玄', level: 85, kind: 'hero',
      subtitle: '云游小道童', element: '金', role: '物攻', image: 'hero.png',
      base: [126, 125, 371, 177], available: 20,
      stats: { hp: 10786, mp: 7017, patk: 13188, matk: 4463, speed: 680, def: 2944 },
      dataSource: '参考人物数值；剩余属性点为演示设置。'
    },
    {
      id: 'lingyue', name: '灵玥', level: 85, kind: 'pet',
      subtitle: '九尾灵狐', element: '水', role: '法攻', image: 'lingyue.png',
      base: [85, 425, 85, 85], available: 12,
      stats: { hp: 39066, mp: 22818, patk: 3003, matk: 42336, speed: 744, def: 10663 },
      dataSource: '参考宝宝数值；剩余属性点为演示设置。'
    },
    {
      id: 'hutuantuan', name: '葫团团', level: 78, kind: 'pet',
      subtitle: '葫芦灵狐', element: '土', role: '守护', image: 'hutuantuan.png',
      base: [312, 156, 78, 78], available: 16,
      stats: { hp: 48280, mp: 14320, patk: 5180, matk: 17640, speed: 628, def: 14280 },
      dataSource: '本面板虚构演示数值。'
    },
    {
      id: 'fuxiaohu', name: '符小虎', level: 80, kind: 'pet',
      subtitle: '符箓虎崽', element: '火', role: '物攻', image: 'fuxiaohu.png',
      base: [160, 80, 320, 80], available: 8,
      stats: { hp: 32800, mp: 9840, patk: 36720, matk: 4860, speed: 690, def: 8920 },
      dataSource: '本面板虚构演示数值。'
    },
    {
      id: 'yunjiujiu', name: '云啾啾', level: 75, kind: 'pet',
      subtitle: '云游小仙鹤', element: '木', role: '敏辅', image: 'yunjiujiu.png',
      base: [150, 150, 75, 225], available: 10,
      stats: { hp: 28650, mp: 16800, patk: 4200, matk: 18600, speed: 1280, def: 7640 },
      dataSource: '本面板虚构演示数值。'
    }
  ];
  var byId = Object.create(null);
  var state = Object.create(null);

  entities.forEach(function (entity) {
    Object.freeze(entity.base);
    Object.freeze(entity.stats);
    Object.freeze(entity);
    byId[entity.id] = entity;
    state[entity.id] = { saved: [0, 0, 0, 0], draft: [0, 0, 0, 0], available: entity.available };
  });
  Object.freeze(entities);

  function total(values) {
    return values.reduce(function (sum, value) { return sum + value; }, 0);
  }

  function requireState(id) {
    if (!Object.prototype.hasOwnProperty.call(byId, id)) {
      throw new RangeError('Unknown attribute entity: ' + id);
    }
    return state[id];
  }

  function requireIndex(index) {
    if (!Number.isInteger(index) || index < 0 || index >= attributes.length) {
      throw new RangeError('Attribute index must be an integer from 0 to 3.');
    }
  }

  function integer(value) {
    var parsed = Number(value);
    if (!Number.isFinite(parsed)) throw new TypeError('Allocation must be a finite number.');
    return Math.trunc(parsed);
  }

  function preview(points) {
    var result = {};
    statKeys.forEach(function (key) {
      result[key] = points.reduce(function (sum, value, index) {
        return sum + value * previewCoefficients[index][key];
      }, 0);
    });
    return result;
  }

  function get(id) {
    var current = requireState(id);
    var entity = byId[id];
    var assigned = current.saved.map(function (value, index) { return value + current.draft[index]; });
    var gains = preview(assigned);
    var stats = {};
    statKeys.forEach(function (key) { stats[key] = entity.stats[key] + gains[key]; });
    return {
      entity: entity,
      values: entity.base.map(function (value, index) { return value + assigned[index]; }),
      remaining: current.available - total(current.draft),
      available: current.available,
      saved: current.saved.slice(),
      draft: current.draft.slice(),
      dirty: total(current.draft) > 0,
      stats: stats,
      delta: preview(current.draft),
      previewNotice: previewNotice
    };
  }

  function setDraft(id, index, value) {
    var current = requireState(id);
    requireIndex(index);
    var limit = current.available - total(current.draft) + current.draft[index];
    current.draft[index] = Math.max(0, Math.min(limit, integer(value)));
    return get(id);
  }

  function adjust(id, index, amount) {
    var current = requireState(id);
    requireIndex(index);
    return setDraft(id, index, current.draft[index] + integer(amount));
  }

  function reset(id) {
    var current = requireState(id);
    current.draft = [0, 0, 0, 0];
    return get(id);
  }

  function confirm(id) {
    var current = requireState(id);
    var committed = total(current.draft);
    current.saved = current.saved.map(function (value, index) { return value + current.draft[index]; });
    current.available -= committed;
    current.draft = [0, 0, 0, 0];
    return get(id);
  }

  function auto(id, mode) {
    var current = requireState(id);
    var strategy = mode || 'balanced';
    var targets = { strength: 2, spirit: 1, speed: 3 };
    if (strategy !== 'balanced' && !Object.prototype.hasOwnProperty.call(targets, strategy)) {
      throw new RangeError('Unknown allocation mode: ' + strategy);
    }
    var remaining = current.available - total(current.draft);
    if (strategy === 'balanced') {
      while (remaining > 0) {
        var least = Math.min.apply(null, current.draft);
        current.draft[current.draft.indexOf(least)] += 1;
        remaining -= 1;
      }
    } else {
      current.draft[targets[strategy]] += remaining;
    }
    return get(id);
  }

  function wash(id) {
    var current = requireState(id);
    current.available += total(current.saved);
    current.saved = [0, 0, 0, 0];
    current.draft = [0, 0, 0, 0];
    return get(id);
  }

  return {
    entities: entities,
    state: state,
    attributes: attributes,
    statKeys: statKeys,
    previewNotice: previewNotice,
    previewCoefficients: previewCoefficients,
    get: get,
    adjust: adjust,
    setDraft: setDraft,
    reset: reset,
    confirm: confirm,
    auto: auto,
    wash: wash
  };
});
