'use strict';
// Reproduce with the bundled Node.js runtime. Uses existing Playwright and Edge.
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const { chromium } = require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = __dirname;
const outputDir = path.resolve(root, '../../.work/guild-ui-browser');
const reportPath = path.join(root, 'guild-browser-validation.json');
const report = { testedAt: new Date().toISOString(), browser: 'Microsoft Edge (headless)', checks: [], screenshots: [] };
const entries = { quests: '01-quests.png', inventory: '02-inventory.png', activities: '03-activities.png', guild: '04-guild.png' };
const assert = (name, pass, details) => {
  report.checks.push({ name, passed: Boolean(pass), details });
  if (!pass) throw new Error(name + ': ' + JSON.stringify(details));
};
const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
async function streamSha256(stream) {
  const hash = crypto.createHash('sha256');
  for await (const chunk of stream) hash.update(chunk);
  return hash.digest('hex');
}
const server = http.createServer((req, res) => {
  const name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname).replace(/^\/+/, '') || 'index.html';
  if (![ 'index.html', ...Object.values(entries) ].includes(name)) { res.writeHead(404); res.end(); return; }
  const file = path.join(root, name);
  res.writeHead(200, { 'Content-Type': name.endsWith('.png') ? 'image/png' : 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
  fs.createReadStream(file).pipe(res);
});
(async () => {
  let browser;
  try {
    fs.mkdirSync(outputDir, { recursive: true });
    await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    const url = 'http://127.0.0.1:' + server.address().port + '/';
    browser = await chromium.launch({ executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless: true });
    report.browserVersion = browser.version();
    const context = await browser.newContext({ viewport: { width: 1600, height: 1000 }, acceptDownloads: true });
    const page = await context.newPage();
    const pageErrors = [];
    page.on('pageerror', error => pageErrors.push(error.message));
    async function selected(view) {
      await page.waitForFunction(file => {
        const img = document.getElementById('artwork');
        return img.getAttribute('src') === file && img.complete && img.naturalWidth > 0;
      }, entries[view]);
      return page.evaluate(view => ({
        active: [...document.querySelectorAll('[aria-pressed="true"]')].map(b => b.dataset.view),
        src: document.getElementById('artwork').getAttribute('src'),
        query: new URL(location.href).searchParams.get('view'),
        alt: document.getElementById('artwork').alt,
        download: document.getElementById('download').getAttribute('download'),
        errorVisible: !document.getElementById('imageError').hidden,
        title: document.title
      }), view);
    }
    await page.goto(url + '?view=guild');
    let state = await selected('guild');
    assert('Direct guild URL', state.active.join() === 'guild' && state.query === 'guild' && !state.errorVisible, state);
    await page.reload();
    state = await selected('guild');
    assert('Guild persists after refresh', state.active.join() === 'guild' && state.src === entries.guild, state);
    for (const view of Object.keys(entries)) {
      await page.locator('[data-view="' + view + '"]').click();
      state = await selected(view);
      assert('Switch to ' + view, state.active.join() === view && state.query === view && state.download === entries[view], state);
    }
    await page.goto(url + '?view=invalid');
    state = await selected('quests');
    assert('Invalid query defaults to quests', state.query === 'quests' && state.active.join() === 'quests', state);
    await page.locator('[data-view="quests"]').focus();
    for (const [view, key] of [['inventory', 'Space'], ['activities', 'Enter'], ['guild', 'Space']]) {
      await page.keyboard.press('Tab');
      const focused = await page.evaluate(() => document.activeElement.dataset.view);
      await page.keyboard.press(key);
      state = await selected(view);
      assert('Keyboard Tab + ' + key + ' switches to ' + view, focused === view && state.active.join() === view, { focused, ...state });
    }
    await page.keyboard.press('Tab');
    const focusIsDownload = await page.locator('#download').evaluate(el => el === document.activeElement);
    const downloadPromise = page.waitForEvent('download');
    await page.keyboard.press('Enter');
    const download = await downloadPromise;
    const stream = await download.createReadStream();
    const downloadHash = await streamSha256(stream);
    const source = fs.readFileSync(path.join(root, entries.guild));
    const originalHash = sha256(source);
    assert('Keyboard download returns original guild bytes', focusIsDownload && download.suggestedFilename() === entries.guild && downloadHash === originalHash, { focusIsDownload, suggestedFilename: download.suggestedFilename(), bytes: source.length, sha256: downloadHash, originalSha256: originalHash });
    for (const viewport of [{ width: 320, height: 740 }, { width: 390, height: 844 }, { width: 844, height: 390 }, { width: 1600, height: 1000 }]) {
      await page.setViewportSize(viewport);
      await selected('guild');
      const layout = await page.evaluate(() => ({
        viewportWidth: innerWidth,
        scrollWidth: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth),
        nav: [...document.querySelectorAll('nav button')].map(b => {
          const r = b.getBoundingClientRect();
          return { view: b.dataset.view, x: r.x, y: r.y, width: r.width, height: r.height, visible: r.width > 0 && r.height > 0 && r.left >= 0 && r.right <= innerWidth && r.top >= 0 && r.bottom <= innerHeight };
        }),
        image: (() => { const r = document.getElementById('artwork').getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; })()
      }));
      assert('Responsive ' + viewport.width + 'x' + viewport.height, layout.scrollWidth <= viewport.width && layout.nav.length === 4 && layout.nav.every(b => b.visible && b.width >= 44 && b.height >= 44), layout);
      if (viewport.width === 390 || viewport.width === 1600) {
        const screenshotPath = path.join(outputDir, viewport.width === 390 ? 'guild-mobile-390.png' : 'guild-desktop-1600.png');
        await page.screenshot({ path: screenshotPath, fullPage: true });
        report.screenshots.push(screenshotPath);
      }
    }
    assert('No page JavaScript errors', pageErrors.length === 0, pageErrors);
    report.passed = true;
  } catch (error) {
    report.passed = false;
    report.error = error.stack;
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ passed: report.passed, checks: report.checks.length, report: reportPath, screenshots: report.screenshots, error: report.error }, null, 2));
  }
})();
