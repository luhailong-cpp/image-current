'use strict';
// Reproducible UI checks against the local preview; each run uses isolated browser contexts.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium } = require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const url = process.env.GUILD_PREVIEW_URL || 'http://127.0.0.1:4345/guild-ui-v2/';
const qa = __dirname;
const reportPath = path.join(qa, 'browser-validation.json');
const report = { testedAt: new Date().toISOString(), url, browser: 'Microsoft Edge headless', isolatedContexts: true, checks: [], screenshots: [], pageErrors: [], failedRequests: [] };
const tabs = ['overview', 'members', 'donation', 'tasks', 'events', 'shop'];
const key = 'wuxing-guild-demo-v2';
let browser;
let testPage;
function check(name, condition, details) {
  report.checks.push({ name, passed: Boolean(condition), ...(details === undefined ? {} : { details }) });
  assert.ok(condition, name + (details === undefined ? '' : ': ' + JSON.stringify(details)));
}
async function scenario(name, fn) {
  console.log('START ' + name);
  try { await fn(); }
  catch (error) {
    report.checks.push({ name: name + ' completed', passed: false, error: error.stack });
    console.log('FAIL ' + name + ': ' + error.message);
    if (testPage && !testPage.isClosed()) {
      if (await testPage.locator('#actionDialog').evaluate(dialog => dialog.open).catch(() => false)) await testPage.locator('#dialogClose').click().catch(() => {});
      if (await testPage.locator('#reopenButton').isVisible().catch(() => false)) await testPage.locator('#reopenButton').click().catch(() => {});
    }
  }
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
  console.log('DONE ' + name);
}
async function newPage(options = {}) {
  const context = await browser.newContext({ viewport: { width: 1600, height: 675 }, deviceScaleFactor: 1.6, ...options });
  const page = await context.newPage();
  page.setDefaultTimeout(8000);
  page.on('pageerror', error => report.pageErrors.push(error.message));
  page.on('requestfailed', request => report.failedRequests.push({ url: request.url(), error: request.failure()?.errorText }));
  return { context, page };
}
async function load(page, hash = 'overview') {
  await page.goto(url + '#' + hash, { waitUntil: 'networkidle' });
  await page.locator('#tab-' + hash + '[aria-selected="true"]').waitFor();
}
async function select(page, name) {
  await page.locator('#tab-' + name).click();
  await page.locator('#tab-' + name + '[aria-selected="true"]').waitFor();
}
async function saved(page) { return page.evaluate(key => JSON.parse(localStorage.getItem(key)), key); }
async function opened(page) { await page.locator('#actionDialog[open]').waitFor(); }
async function closed(page) { await page.locator('#actionDialog[open]').waitFor({ state: 'hidden' }); }
async function clickConfirm(page) { await page.locator('#dialogConfirm').click(); await closed(page); }
async function focusId(page) { return page.evaluate(() => document.activeElement.id); }
async function reset(page) { await page.locator('#resetButton').click(); await opened(page); await clickConfirm(page); }
async function visualHealth(page) {
  await page.waitForFunction(() => [...document.images].every(image => image.complete));
  return page.evaluate(() => ({
    viewportWidth: innerWidth, viewportHeight: innerHeight,
    scrollWidth: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth),
    brokenImages: [...document.images].filter(image => image.naturalWidth === 0).map(image => image.getAttribute('src')),
    selectedTabs: [...document.querySelectorAll('[role="tab"][aria-selected="true"]')].map(button => button.dataset.page),
    pageScrollWidth: document.getElementById('pageContent').scrollWidth,
    pageClientWidth: document.getElementById('pageContent').clientWidth,
    selectedTabVisible: (() => { const tab = document.querySelector('[aria-selected="true"]'); const rect = tab.getBoundingClientRect(); return rect.left >= -1 && rect.right <= innerWidth + 1; })()
  }));
}

(async function main() {
  fs.mkdirSync(qa, { recursive: true });
  try {
    browser = await chromium.launch({ executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless: true });
    report.browserVersion = browser.version();
    const { context, page } = await newPage();
    testPage = page;
    await load(page);

    await scenario('Navigation and keyboard', async () => {
      for (const tab of tabs) {
        await select(page, tab);
        check('Click opens ' + tab + ' and updates its URL', new URL(page.url()).hash === '#' + tab && await page.locator('[role="tab"][aria-selected="true"]').count() === 1);
      }
      await page.goBack();
      await page.locator('#tab-events[aria-selected="true"]').waitFor();
      check('Browser Back restores events', new URL(page.url()).hash === '#events');
      await page.goForward();
      await page.locator('#tab-shop[aria-selected="true"]').waitFor();
      check('Browser Forward restores shop', new URL(page.url()).hash === '#shop');
      await page.reload({ waitUntil: 'networkidle' });
      check('Reload restores selected page', await page.locator('#tab-shop').getAttribute('aria-selected') === 'true');
      await page.locator('#tab-shop').focus();
      await page.keyboard.press('Home');
      check('Home activates and focuses first tab', await focusId(page) === 'tab-overview' && new URL(page.url()).hash === '#overview');
      await page.keyboard.press('ArrowRight');
      check('Right arrow activates next tab', await focusId(page) === 'tab-members' && new URL(page.url()).hash === '#members');
      await page.keyboard.press('ArrowLeft');
      check('Left arrow activates previous tab', await focusId(page) === 'tab-overview');
      await page.keyboard.press('End');
      check('End activates and focuses final tab', await focusId(page) === 'tab-shop');
      await page.keyboard.press('ArrowRight');
      check('Right arrow wraps to first tab', await focusId(page) === 'tab-overview');
      await page.keyboard.press('Tab');
      check('Tab exits roving tab list', !(await focusId(page)).startsWith('tab-'));
      await page.keyboard.press('Escape');
      check('Escape closes guild and focuses reopen', await page.locator('#guildWindow').isHidden() && await focusId(page) === 'reopenButton');
      await page.keyboard.press('Enter');
      check('Enter reopens guild and restores selected tab focus', await page.locator('#guildWindow').isVisible() && await focusId(page) === 'tab-overview');
      await page.locator('#rulesButton').click();
      await opened(page);
      check('Informational modal initially focuses its dismissal button', await focusId(page) === 'dialogCancel');
      const focusTrace = [];
      for (let count = 0; count < 6; count++) {
        await page.keyboard.press('Tab');
        focusTrace.push(await page.evaluate(() => ({ id: document.activeElement.id, tag: document.activeElement.tagName, inDialog: document.getElementById('actionDialog').contains(document.activeElement), open: document.getElementById('actionDialog').open })));
      }
      // Native Edge dialog can hand focus to browser chrome (activeElement becomes BODY).
      // Background page controls must remain unreachable; browser chrome is not page content.
      check('Native modal keeps background controls out of keyboard focus', focusTrace.every(item => item.open && (item.inDialog || item.tag === 'BODY')) && focusTrace.some(item => item.inDialog), focusTrace);
      await page.keyboard.press('Escape');
      await closed(page);
      check('Escape closes only the modal and returns focus', await page.locator('#guildWindow').isVisible() && await focusId(page) === 'rulesButton');
      await page.locator('#hallButton').click();
      await opened(page);
      await page.locator('#dialogBody [data-go="tasks"]').click();
      await closed(page);
      check('Guild hall navigation opens requested feature', new URL(page.url()).hash === '#tasks');
    });

    await scenario('Member directory', async () => {
      await select(page, 'members');
      check('Member directory paginates twelve members into five rows', await page.locator('.member-row').count() === 5 && (await page.locator('.pagination').innerText()).includes('第 1 / 3 页'));
      await page.locator('#memberNext').click();
      check('Next page displays next group', (await page.locator('.pagination').innerText()).includes('第 2 / 3 页'));
      await page.locator('#memberNext').click();
      check('Final page has two members and disables next', await page.locator('.member-row').count() === 2 && await page.locator('#memberNext').isDisabled());
      await page.locator('#memberPrev').click();
      check('Previous page works', (await page.locator('.pagination').innerText()).includes('第 2 / 3 页'));
      await page.locator('#memberSearch').fill('青云');
      check('Search filters by member name and resets pagination', await page.locator('.member-row').count() === 1 && (await page.locator('.member-row').innerText()).includes('青云小道'));
      await page.locator('#profile-self').click();
      await opened(page);
      check('Member profile contains selected member', (await page.locator('#dialogBody').innerText()).includes('青云小道'));
      await page.keyboard.press('Escape');
      check('Closing member profile returns focus', await focusId(page) === 'profile-self');
      await page.locator('#memberSearch').fill('不存在的成员');
      check('No results provides clear filter action', await page.locator('.member-row').count() === 0 && await page.locator('#clearMemberFilter').isVisible());
      await page.locator('#clearMemberFilter').click();
      check('Clear filter restores directory and search focus', await page.locator('.member-row').count() === 5 && await page.locator('#memberSearch').inputValue() === '' && await focusId(page) === 'memberSearch');
      await page.locator('#onlineOnly').check();
      check('Online filter removes offline members', await page.locator('.member-row .offline').count() === 0 && (await page.locator('.pagination').innerText()).includes('共 7 人'));
      await page.locator('#onlineOnly').uncheck();
      for (const sort of ['level', 'role', 'contribution']) {
        await page.locator('#memberSort').selectOption(sort);
        const expected = (await saved(page)).members.slice().sort((a, b) => sort === 'level' ? b.level - a.level : sort === 'role' ? ['帮主','长老','精英','帮众'].indexOf(a.role) - ['帮主','长老','精英','帮众'].indexOf(b.role) || b.weeklyContribution - a.weeklyContribution : b.weeklyContribution - a.weeklyContribution).slice(0, 5).map(member => member.id);
        const actual = await page.locator('.member-row [data-profile]').evaluateAll(buttons => buttons.map(button => button.dataset.profile));
        check('Sorting by ' + sort + ' orders visible members correctly', JSON.stringify(actual) === JSON.stringify(expected), { actual, expected });
      }
    });

    await scenario('Sign in, donation, and task rewards', async () => {
      await reset(page);
      await page.locator('#signInButton').click();
      const signed = await saved(page);
      check('Sign in credits contribution and disables repeating', signed.currentUser.contribution === 3380 && await page.locator('#signInButton').isDisabled());
      await page.reload({ waitUntil: 'networkidle' });
      check('Repeated sign in stays disabled after reload', await page.locator('#signInButton').isDisabled() && (await saved(page)).currentUser.contribution === 3380);
      await select(page, 'donation');
      let before = await saved(page);
      await page.locator('#donate-small').click();
      await opened(page);
      check('Donation confirmation defaults to cancel', await focusId(page) === 'dialogCancel');
      await page.locator('#dialogCancel').click();
      await closed(page);
      check('Cancel donation leaves all resources unchanged and restores focus', JSON.stringify(await saved(page)) === JSON.stringify(before) && await focusId(page) === 'donate-small');
      await page.locator('#donate-small').click();
      await clickConfirm(page);
      let after = await saved(page);
      check('Confirm donation updates wallet and guild together', after.currentUser.coins === 70000 && after.currentUser.contribution === 3580 && after.guild.funds === 138600 && after.guild.construction === 8800 && after.donationCounts.small === 1);
      await page.locator('#donate-large').click(); await clickConfirm(page);
      await page.locator('#donate-large').click(); await clickConfirm(page);
      check('Insufficient coins disable unaffordable donation', (await saved(page)).currentUser.coins === 10000 && await page.locator('#donate-large').isDisabled() && (await page.locator('#donate-large').innerText()).includes('铜钱不足'));
      await select(page, 'tasks');
      before = await saved(page);
      check('Incomplete task is visibly disabled', await page.locator('#claim-practice').isDisabled());
      await page.locator('#claim-herbs').click();
      after = await saved(page);
      check('Claimed task credits all rewards and disables repeat', after.currentUser.coins === before.currentUser.coins + 5000 && after.currentUser.contribution === before.currentUser.contribution + 180 && after.inventory.pill === 2 && await page.locator('#claim-herbs').isDisabled());
      await page.reload({ waitUntil: 'networkidle' });
      check('Task reward cannot be repeated after reload', await page.locator('#claim-herbs').isDisabled() && (await saved(page)).inventory.pill === 2);
      await page.locator('#bagButton').click(); await opened(page);
      check('Task items appear in earned inventory', (await page.locator('#dialogBody').innerText()).includes('清灵丹') && (await page.locator('#dialogBody').innerText()).includes('× 2'));
      await page.keyboard.press('Escape');
    });

    await scenario('Event signup and cancellation', async () => {
      await select(page, 'events');
      check('Upcoming and ended event actions are disabled', await page.locator('#event-trial').isDisabled() && await page.locator('#event-moon').isDisabled());
      await page.locator('#event-lantern').click();
      check('Signup updates participants and action state', (await saved(page)).events[0].joined === true && (await saved(page)).events[0].participants === 19 && (await page.locator('#event-lantern').innerText()).includes('取消报名'));
      await page.locator('#event-lantern').click(); await opened(page);
      await page.locator('#dialogCancel').click(); await closed(page);
      check('Canceling cancellation keeps signup', (await saved(page)).events[0].joined === true);
      await page.locator('#event-lantern').click(); await clickConfirm(page);
      check('Confirm cancellation restores participant count', (await saved(page)).events[0].joined === false && (await saved(page)).events[0].participants === 18);
    });

    await scenario('Exchange, validation, inventory, and persistence', async () => {
      await reset(page); await select(page, 'shop');
      await page.locator('#buy-pill').click(); await opened(page);
      check('Exchange focuses quantity input', await focusId(page) === 'exchangeQuantity');
      const before = await saved(page);
      for (const value of ['0', '-1', '1.5', '11']) {
        await page.locator('#exchangeQuantity').fill(value);
        await page.locator('#dialogConfirm').click();
        check('Invalid exchange quantity ' + value + ' shows an error without spending', await page.locator('#actionDialog').evaluate(dialog => dialog.open) && await page.locator('#dialogError').isVisible() && JSON.stringify(await saved(page)) === JSON.stringify(before));
      }
      await page.locator('#exchangeQuantity').fill('3');
      check('Quantity updates total contribution', (await page.locator('#exchangeTotal').innerText()).includes('540'));
      await page.locator('#dialogCancel').click(); await closed(page);
      check('Cancel exchange leaves wallet and stock unchanged', JSON.stringify(await saved(page)) === JSON.stringify(before));
      await page.locator('#buy-pill').click();
      await page.locator('#exchangeQuantity').fill('10'); await clickConfirm(page);
      let after = await saved(page);
      check('Exchange updates contribution, stock, limit, and inventory', after.currentUser.contribution === 1480 && after.shop[0].stock === 0 && after.shop[0].purchased === 10 && after.inventory.pill === 10 && await page.locator('#buy-pill').isDisabled());
      check('Unaffordable product clearly disables exchange', await page.locator('#buy-chest').isDisabled() && (await page.locator('#buy-chest').innerText()).includes('贡献不足'));
      await page.locator('#buy-scroll').click();
      await page.locator('#exchangeQuantity').fill('4'); await page.locator('#dialogConfirm').click();
      check('Quantity within stock but above available contribution is rejected', await page.locator('#dialogError').isVisible() && (await page.locator('#dialogError').innerText()).includes('贡献不足') && (await saved(page)).currentUser.contribution === 1480);
      await page.keyboard.press('Escape');
      await page.locator('#bagButton').click(); await opened(page);
      check('Exchanged items are visible in earned inventory', (await page.locator('#dialogBody').innerText()).includes('清灵丹') && (await page.locator('#dialogBody').innerText()).includes('× 10'));
      await page.keyboard.press('Escape');
      await page.reload({ waitUntil: 'networkidle' });
      check('Refresh preserves all transaction state and sold-out display', JSON.stringify(await saved(page)) === JSON.stringify(after) && await page.locator('#buy-pill').isDisabled());
    });

    await scenario('Announcement permissions and text safety', async () => {
      await select(page, 'overview');
      await page.locator('#editAnnouncement').click(); await opened(page);
      check('Member sees announcement without an editor', await page.locator('#announcementInput').count() === 0 && (await page.locator('#dialogBody').innerText()).includes('仅帮主、长老'));
      await page.keyboard.press('Escape');
      await page.locator('#demoRoleButton').click(); await opened(page);
      await page.locator('#demoRole').selectOption({ label: '长老' }); await clickConfirm(page);
      check('Role switch updates visible permissions', (await saved(page)).currentUser.role === '长老' && (await page.locator('#editAnnouncement').innerText()).includes('编辑'));
      await page.locator('#editAnnouncement').click(); await opened(page);
      check('Announcement editor receives initial focus', await focusId(page) === 'announcementInput');
      await page.locator('#announcementInput').fill('短');
      await page.locator('#dialogConfirm').click();
      check('Short announcement is rejected visibly', await page.locator('#dialogError').isVisible() && (await page.locator('#dialogError').innerText()).includes('8–180'));
      const text = '<img src=x onerror="window.__guildXss=1">同门相聚，赏灯论道。';
      await page.locator('#announcementInput').fill(text); await clickConfirm(page);
      check('Announcement renders malicious-looking input as literal text', await page.locator('.announcement blockquote').innerText() === text && await page.locator('.announcement blockquote img').count() === 0 && await page.evaluate(() => window.__guildXss === undefined));
      await page.reload({ waitUntil: 'networkidle' });
      check('Saved announcement and permission survive refresh safely', await page.locator('.announcement blockquote').innerText() === text && (await saved(page)).currentUser.role === '长老' && await page.evaluate(() => window.__guildXss === undefined));
    });

    await scenario('Reset confirmation and cancellation', async () => {
      const before = await saved(page);
      await page.locator('#resetButton').click(); await opened(page);
      await page.locator('#dialogCancel').click(); await closed(page);
      check('Cancel reset preserves prior progress', JSON.stringify(await saved(page)) === JSON.stringify(before));
      await reset(page);
      const after = await saved(page);
      check('Confirm reset restores balances, tasks, events, inventory and role', after.currentUser.contribution === 3280 && after.currentUser.coins === 80000 && after.currentUser.role === '精英' && after.tasks.every(task => !task.claimed) && after.events.every(event => !event.joined) && Object.values(after.inventory).every(value => value === 0) && after.shop.every(product => product.purchased === 0) && after.signedInDate === null);
    });

    await scenario('Desktop exports and responsive layout', async () => {
      await load(page);
      for (const [index, tab] of tabs.entries()) {
        await select(page, tab);
        const health = await visualHealth(page);
        check('Desktop ' + tab + ' has no horizontal overflow or missing image', health.scrollWidth <= 1600 && health.pageScrollWidth <= health.pageClientWidth + 1 && health.brokenImages.length === 0, health);
        const file = String(index + 1).padStart(2, '0') + '-' + tab + '_2560x1080.png';
        const target = path.join(qa, file);
        await page.screenshot({ path: target });
        const png = fs.readFileSync(target);
        check('Export ' + tab + ' is exactly 2560 by 1080', png.readUInt32BE(16) === 2560 && png.readUInt32BE(20) === 1080);
        report.screenshots.push({ page: tab, viewport: '1600x675', deviceScaleFactor: 1.6, file, width: 2560, height: 1080 });
      }
      const responsive = await newPage({ deviceScaleFactor: 1 });
      await load(responsive.page);
      for (const viewport of [{ width: 390, height: 844 }, { width: 844, height: 390 }, { width: 320, height: 700 }]) {
        await responsive.page.setViewportSize(viewport);
        for (const tab of tabs) {
          await select(responsive.page, tab);
          const health = await visualHealth(responsive.page);
          check(viewport.width + 'x' + viewport.height + ' ' + tab + ' fits width and loads every image', health.scrollWidth <= viewport.width && health.pageScrollWidth <= health.pageClientWidth + 1 && health.brokenImages.length === 0 && health.selectedTabVisible, health);
        }
        await select(responsive.page, 'overview');
        const file = 'responsive-' + viewport.width + 'x' + viewport.height + '.png';
        await responsive.page.screenshot({ path: path.join(qa, file), fullPage: true });
        report.screenshots.push({ page: 'overview', viewport: viewport.width + 'x' + viewport.height, file });
      }
      await responsive.context.close();
    });

    await scenario('Storage unavailable fallback', async () => {
      const temporary = await newPage();
      await temporary.context.addInitScript(() => Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('Storage is disabled for this test', 'SecurityError'); } }));
      await load(temporary.page);
      check('Blocked localStorage shows a clear temporary-session status', (await temporary.page.locator('#saveStatus').innerText()).includes('仅本次有效'));
      await temporary.page.locator('#signInButton').click();
      check('Interactions still work with blocked localStorage', await temporary.page.locator('#signInButton').isDisabled() && (await temporary.page.locator('#contribution').innerText()).includes('3,380'));
      await temporary.page.reload({ waitUntil: 'networkidle' });
      check('Blocked-storage reload safely starts a new temporary session', !(await temporary.page.locator('#signInButton').isDisabled()) && (await temporary.page.locator('#contribution').innerText()).includes('3,280'));
      await temporary.context.close();
    });

    check('No uncaught page JavaScript errors', report.pageErrors.length === 0, report.pageErrors);
    check('No failed resource requests', report.failedRequests.length === 0, report.failedRequests);
    await context.close();
  } catch (error) {
    report.error = error.stack;
  } finally {
    if (browser) await browser.close();
    report.passed = !report.error && report.checks.length > 0 && report.checks.every(check => check.passed);
    report.summary = { passed: report.checks.filter(check => check.passed).length, failed: report.checks.filter(check => !check.passed).length, screenshots: report.screenshots.length };
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ success: report.passed, ...report.summary, report: reportPath, failures: report.checks.filter(check => !check.passed), error: report.error }, null, 2));
    if (!report.passed) process.exitCode = 1;
  }
}());
