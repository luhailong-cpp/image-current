// Targeted verification of the last focus/skin fixes and standard screenshot export.
const { chromium } = require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
(async () => {
  const report = { checkedAt: new Date().toISOString(), checks: [], errors: [], screenshots: [] };
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  const context = await browser.newContext({ viewport: { width: 1600, height: 675 }, deviceScaleFactor: 1.6 });
  const page = await context.newPage();
  page.on('pageerror', e => report.errors.push(e.message));
  page.on('response', r => { if (r.status() >= 400) report.errors.push(r.status() + ' ' + r.url()); });
  const base = process.env.PREVIEW_URL || 'http://127.0.0.1:4345/guild-ui-v2/';
  try {
    await page.goto(base, { waitUntil: 'networkidle' });
    await page.locator('#rulesButton').click();
    for (let i = 0; i < 12; i++) {
      await page.keyboard.press(i % 3 === 0 ? 'Shift+Tab' : 'Tab');
      assert(await page.evaluate(() => document.getElementById('actionDialog').contains(document.activeElement)), 'Dialog must retain keyboard focus');
    }
    await page.keyboard.press('Escape');
    assert(await page.locator('#guildWindow').isVisible());
    assert.equal(await page.evaluate(() => document.activeElement.id), 'rulesButton');
    report.checks.push('Modal focus retained for 12 Tab/Shift+Tab steps; Escape returns to invoker.');
    const modes = ['overview', 'members', 'donation', 'tasks', 'events', 'shop'];
    for (let i = 0; i < modes.length; i++) {
      const mode = modes[i];
      await page.locator('#tab-' + mode).click();
      await page.evaluate(() => Promise.all(Array.from(document.images).map(im => im.decode())));
      assert(await page.locator('#tab-' + mode).evaluate(el => getComputedStyle(el).borderImageSlice.includes('fill')));
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      const file = String(i + 1).padStart(2, '0') + '-' + mode + '_2560x1080.png';
      await page.screenshot({ path: path.join(__dirname, file) });
      report.screenshots.push(file);
    }
    report.checks.push('All six final pages load; selected tab skins have a filled nine-slice centre.');
    await page.setViewportSize({ width: 320, height: 700 });
    await page.locator('#tab-overview').click();
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.screenshot({ path: path.join(__dirname, 'final-320-overview.png'), fullPage: true });
    await page.goto('http://127.0.0.1:4345/gameplay-ui/?view=guild', { waitUntil: 'networkidle' });
    assert(await page.locator('#guildInteractive').isVisible());
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.locator('#guildInteractive').click();
    assert(page.url().includes('/guild-ui-v2/'));
    assert(await page.locator('#guildWindow').isVisible());
    report.checks.push('320px gallery link opens the complete guild UI without horizontal overflow.');
    assert.deepEqual(report.errors, []);
    report.passed = true;
  } catch (error) {
    report.passed = false;
    report.failure = error.stack;
    process.exitCode = 1;
  } finally {
    report.fileHashes = Object.fromEntries(['index.html', 'app.js', 'styles.css', 'model.js'].map(file => [file, crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname, '..', file))).digest('hex')]));
    fs.writeFileSync(path.join(__dirname, 'final-ui-validation.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify(report, null, 2));
    await browser.close();
  }
})();
