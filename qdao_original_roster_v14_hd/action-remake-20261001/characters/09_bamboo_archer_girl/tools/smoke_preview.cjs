// Isolated headless smoke check of this character's local player; writes no files.
const path = require("node:path");
const {pathToFileURL} = require("node:url");
const assert = require("node:assert/strict");
const runtime = path.join(process.env.USERPROFILE, ".cache", "codex-runtimes", "codex-primary-runtime", "dependencies", "node", "node_modules", "playwright");
const {chromium} = require(runtime);
(async () => {
  const browser = await chromium.launch({channel:"msedge",headless:true});
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror",error => errors.push(error.message));
    await page.goto(pathToFileURL(path.resolve(__dirname,"../preview/index.html")).href);
    await page.waitForSelector("#slots button");
    assert.equal(await page.locator("#sequence option").count(),14);
    assert.equal(await page.locator("#groups tbody tr").count(),14);
    assert.equal(await page.evaluate(() => window.BAMBOO_PREVIEW.sequences.reduce((sum,sequence) => sum + sequence.frames.length,0)),196);
    assert.equal(await page.locator("#slots button").count(),6);
    await page.locator("#sequence").selectOption("12");
    assert.equal(await page.locator("#slots button").count(),16);
    await page.locator("#next").click();
    assert.match(await page.locator("#position").innerText(),/2\/16/);
    await page.locator("#speed").selectOption("0.25");
    assert.match(await page.locator("#position").innerText(),/120ms/);
    await page.locator("#playOne").click();
    await page.waitForTimeout(270);
    await page.locator("#pause").click();
    const afterPlayback = await page.locator("#timeline").inputValue();
    assert.ok(Number(afterPlayback) >= 3,"full-slot timeline should advance at 120ms even with missing PNGs");
    const canvasDimensions = await page.locator("#dark").evaluate(canvas => [canvas.width,canvas.height]);
    assert.deepEqual(canvasDimensions,[1024,1024]);
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({passed:true,sequences:14,slots:196,normalAndSlowControls:true,singleStep:true,missingSlotsPreserveTime:true,fixedCanvas:[1024,1024],imageVisualApproval:false}));
  } finally {await browser.close();}
})().catch(error => {console.error(error);process.exitCode=1;});
