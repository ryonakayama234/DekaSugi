"use strict";
// Explicit, synthetic-only browser runner. Does not import any DekaSugi research code.
const { chromium } = require("playwright");
const assert = require("node:assert/strict"),
  path = require("node:path"),
  fs = require("node:fs");
const { pathToFileURL } = require("node:url");
const url =
  process.env.E1_URL ||
  pathToFileURL(
    path.resolve(__dirname, "../../packages/draft_editor/editor.html"),
  ).href;
const browserPath = process.env.E1_CHROMIUM || "/usr/bin/chromium";
const results = [];
let browser;
const pause = (ms) => new Promise((r) => setTimeout(r, ms));
async function ready(page) {
  await page.waitForFunction(
    () =>
      document.querySelector("#revision").textContent.includes("r1") ||
      document.querySelector("#revision").textContent.includes("r2"),
  );
}
async function saved(page) {
  await page.waitForFunction(() =>
    document
      .querySelector("#save-state")
      .textContent.startsWith("ブラウザ内退避済み"),
  );
  await pause(220);
}
async function exported(page, button = "#export") {
  const wait = page.waitForEvent("download");
  await page.click(button);
  const dl = await wait;
  return fs.readFileSync(await dl.path(), "utf8");
}
async function dbRows(page) {
  return page.evaluate(
    () =>
      new Promise((resolve, reject) => {
        const q = indexedDB.open("dekasugi-e1", 1);
        q.onsuccess = () => {
          const db = q.result,
            tx = db.transaction("drafts");
          const req = tx.objectStore("drafts").getAll();
          req.onsuccess = () => resolve(req.result.filter((x) => !x.probe));
          req.onerror = () => reject(req.error);
          tx.oncomplete = () => db.close();
        };
        q.onerror = () => reject(q.error);
      }),
  );
}
async function ime(
  page,
  {
    value = "資料",
    middle = "しりょう",
    order = "end-first",
    start = true,
    cancel = false,
  } = {},
) {
  await page.evaluate(
    ({ value, middle, order, start, cancel }) => {
      const t = document.querySelector("#body");
      t.focus();
      if (start)
        t.dispatchEvent(
          new CompositionEvent("compositionstart", { bubbles: true }),
        );
      t.value = middle;
      t.setSelectionRange(middle.length, middle.length);
      t.dispatchEvent(
        new InputEvent("input", {
          bubbles: true,
          inputType: "insertCompositionText",
          data: middle,
          isComposing: true,
        }),
      );
      t.value = cancel ? "" : value;
      t.setSelectionRange(t.value.length, t.value.length);
      if (order === "input-first")
        t.dispatchEvent(
          new InputEvent("input", {
            bubbles: true,
            inputType: "insertCompositionText",
            isComposing: true,
          }),
        );
      t.dispatchEvent(
        new CompositionEvent("compositionend", {
          bubbles: true,
          data: cancel ? "" : value,
        }),
      );
      if (order === "end-first") {
        t.dispatchEvent(
          new InputEvent("beforeinput", {
            bubbles: true,
            inputType: "insertFromComposition",
            data: value,
          }),
        );
        t.dispatchEvent(
          new InputEvent("input", {
            bubbles: true,
            inputType: "insertFromComposition",
            data: value,
          }),
        );
      }
    },
    { value, middle, order, start, cancel },
  );
  await pause(30);
}
async function check(name, fn, options = {}) {
  const context = await browser.newContext(options);
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  try {
    await fn(page, context);
    assert.deepEqual(errors, [], "unexpected app error");
    results.push({ name, status: "PASS" });
    console.log("PASS " + name);
  } catch (e) {
    results.push({ name, status: "FAIL", error: e.stack });
    console.error("FAIL " + name + "\n" + e.stack);
  } finally {
    await context.close();
  }
}
(async () => {
  browser = await chromium.launch({
    executablePath: browserPath,
    headless: true,
    args: ["--no-sandbox"],
  });
  console.log("Browser " + browser.version() + " / " + url);
  await check(
    "file startup, Japanese text, LF, emoji, JSON and persisted reopen",
    async (p) => {
      await p.goto(url);
      await ready(p);
      await p.fill("#title", "架空のお願い");
      await p.fill("#purpose", "確認を頼む");
      await p.fill("#body", "今日は資料を確認します。\n確認👍🏽");
      await saved(p);
      const ep = JSON.parse(await exported(p));
      assert.equal(ep.final.text, "今日は資料を確認します。\n確認👍🏽");
      assert.equal(ep.purpose.text, "確認を頼む");
      await p.reload();
      await ready(p);
      assert.equal(await p.inputValue("#body"), ep.final.text);
      await saved(p);
      const resumed = JSON.parse(await exported(p));
      assert.equal(resumed.automatic.replay_integrity, "snapshot_recovered");
      assert.ok(
        resumed.events.some((e) => e.reason === "restart_tail_unobserved"),
      );
    },
  );
  await check(
    "seal immutable revision, continue child, read-only replay and JSONL",
    async (p) => {
      await p.goto(url);
      await ready(p);
      await p.fill("#body", "初稿");
      await p.click("#seal");
      await saved(p);
      assert.equal(await p.getAttribute("#body", "readonly"), "");
      await p.click("#continue");
      await p.fill("#body", "訂正した文");
      await p.click("#seal");
      await saved(p);
      const lines = (await exported(p, "#export-all"))
        .trim()
        .split("\n")
        .map(JSON.parse);
      assert.equal(lines.length, 2);
      assert.equal(lines[0].final.text, "初稿");
      assert.equal(lines[1].revision, 2);
      assert.equal(lines[1].parent_episode_id, lines[0].episode_id);
      await p.click("#history summary");
      await p.selectOption("#history-revision", lines[0].episode_id);
      assert.equal(await p.textContent("#replay-text"), "初稿");
      await p.click("#prev");
      assert.equal(await p.inputValue("#body"), "訂正した文");
    },
  );
  await check(
    "real browser selection replacement and native undo/redo append",
    async (p) => {
      await p.goto(url);
      await ready(p);
      await p.focus("#body");
      await p.keyboard.insertText("今日は晴れ。");
      await p.evaluate(() =>
        document.querySelector("#body").setSelectionRange(0, 2, "forward"),
      );
      await p.keyboard.insertText("明日");
      assert.equal(await p.inputValue("#body"), "明日は晴れ。");
      await p.keyboard.press("Control+z");
      assert.equal(await p.inputValue("#body"), "今日は晴れ。");
      await p.keyboard.press("Control+Shift+z");
      assert.equal(await p.inputValue("#body"), "明日は晴れ。");
      await saved(p);
      const e = JSON.parse(await exported(p));
      assert.ok(e.events.some((x) => x.input_type === "historyUndo"));
      assert.ok(e.events.some((x) => x.input_type === "historyRedo"));
      assert.equal(e.final.text, "明日は晴れ。");
    },
  );
  for (const order of ["end-first", "input-first"])
    await check(
      "synthetic IME " + order + " commits once and excludes preedit",
      async (p) => {
        await p.goto(url);
        await ready(p);
        await ime(p, { order });
        await saved(p);
        const text = await exported(p),
          ep = JSON.parse(text);
        assert.equal(ep.final.text, "資料");
        assert.equal(
          ep.events.filter((e) => e.kind === "edit_commit").length,
          1,
        );
        assert.ok(!text.includes("しりょう"));
      },
    );
  await check(
    "synthetic IME no-change is not fabricated cancellation label",
    async (p) => {
      await p.goto(url);
      await ready(p);
      await ime(p, { cancel: true });
      const ep = JSON.parse(await exported(p));
      assert.equal(ep.final.text, "");
      assert.equal(ep.events.filter((e) => e.kind === "edit_commit").length, 0);
      assert.ok(ep.events.some((e) => e.outcome === "unknown/no_text_change"));
    },
  );
  await check(
    "composition blocks save and never persists unconfirmed text",
    async (p) => {
      await p.goto(url);
      await ready(p);
      await saved(p);
      await p.evaluate(() => {
        const t = document.querySelector("#body");
        t.dispatchEvent(
          new CompositionEvent("compositionstart", { bubbles: true }),
        );
        t.value = "未確定の候補";
        t.dispatchEvent(
          new InputEvent("input", {
            bubbles: true,
            inputType: "insertCompositionText",
            isComposing: true,
          }),
        );
      });
      await pause(1000);
      assert.ok(!JSON.stringify(await dbRows(p)).includes("未確定の候補"));
      await p.click("#seal");
      assert.match(await p.textContent("#notice"), /変換を確定/);
      assert.equal(await p.getAttribute("#body", "readonly"), null);
    },
  );
  await check(
    "missing composition start and unnotified DOM mutation create explicit gaps",
    async (p) => {
      await p.goto(url);
      await ready(p);
      await ime(p, { start: false });
      let ep = JSON.parse(await exported(p));
      assert.ok(
        ep.events.some((e) => e.reason === "composition_start_missing"),
      );
      await p.evaluate(() => {
        document.querySelector("#body").value = "無通知で変わった文";
      });
      await pause(1000);
      ep = JSON.parse(await exported(p));
      assert.ok(
        ep.events.some(
          (e) =>
            e.kind === "capture_gap" &&
            e.snapshot.text === "無通知で変わった文",
        ),
      );
      assert.equal(ep.automatic.replay_integrity, "snapshot_recovered");
    },
  );
  await check(
    "unnotified change immediately followed by input is a gap, not observed typing",
    async (p) => {
      await p.goto(url);
      await ready(p);
      await p.evaluate(() => {
        const t = document.querySelector("#body");
        t.value = "外部変更";
        t.setSelectionRange(t.value.length, t.value.length);
        t.dispatchEvent(
          new InputEvent("beforeinput", {
            bubbles: true,
            inputType: "insertText",
            data: "!",
          }),
        );
        t.value += "!";
        t.setSelectionRange(t.value.length, t.value.length);
        t.dispatchEvent(
          new InputEvent("input", {
            bubbles: true,
            inputType: "insertText",
            data: "!",
          }),
        );
      });
      const ep = JSON.parse(await exported(p));
      assert.ok(
        ep.events.some((e) => e.reason === "beforeinput_value_mismatch"),
      );
      const edits = ep.events.filter((e) => e.kind === "edit_commit");
      assert.equal(edits.length, 1);
      assert.equal(edits[0].patch.insert, "!");
      assert.equal(ep.final.text, "外部変更!");
    },
  );
  await check(
    "JSON import keeps original separate and edits child only",
    async (p) => {
      await p.goto(url);
      await ready(p);
      await p.fill("#body", "持ち出す架空文");
      await p.click("#seal");
      const text = await exported(p),
        ep = JSON.parse(text);
      await p.setInputFiles("#file", {
        name: "invented.json",
        mimeType: "application/json",
        buffer: Buffer.from(text),
      });
      await p.waitForFunction(() =>
        document
          .querySelector("#notice")
          .textContent.includes("読み込みました"),
      );
      assert.equal((await dbRows(p)).length, 2);
      assert.equal(await p.inputValue("#body"), ep.final.text);
      const readback = JSON.parse(await exported(p));
      assert.deepEqual(readback, ep);
      await p.click("#continue");
      const child = JSON.parse(await exported(p));
      assert.equal(child.parent_episode_id, ep.episode_id);
      assert.notEqual(child.episode_id, ep.episode_id);
    },
  );
  await check(
    "malformed JSONL has no partial writes; malicious text stays text",
    async (p) => {
      await p.goto(url);
      await ready(p);
      await p.fill(
        "#body",
        '<img src="https://example.invalid/leak" onerror="window.pwned=1">',
      );
      await p.click("#seal");
      const text = await exported(p);
      const n = (await dbRows(p)).length;
      await p.setInputFiles("#file", {
        name: "bad.jsonl",
        mimeType: "text/plain",
        buffer: Buffer.from(text + '\n{"schema_version":"future"}'),
      });
      await p.waitForFunction(
        () => document.querySelector("#notice").textContent.length > 0,
      );
      assert.equal((await dbRows(p)).length, n);
      assert.equal(await p.evaluate(() => window.pwned), undefined);
      await p.click("#history summary");
      assert.equal(await p.locator("#replay-text img").count(), 0);
      assert.match(await p.textContent("#replay-text"), /<img/);
    },
  );
  await check(
    "unavailable IndexedDB offers JSON fallback without false save success",
    async (p) => {
      await p.addInitScript(() =>
        Object.defineProperty(window, "indexedDB", {
          value: {
            open() {
              throw new Error("invented block");
            },
          },
        }),
      );
      await p.goto(url);
      await ready(p);
      await p.fill("#body", "保存できない時の文");
      assert.match(await p.textContent("#save-state"), /自動退避なし/);
      const wait = p.waitForEvent("download");
      await p.click("#seal");
      const dl = await wait;
      assert.equal(
        JSON.parse(fs.readFileSync(await dl.path(), "utf8")).final.text,
        "保存できない時の文",
      );
      assert.match(
        await p.textContent("#notice"),
        /保存完了は自動判定できません/,
      );
    },
  );
  await check(
    "failed write retains visible text, reports pending, retry works",
    async (p) => {
      await p.goto(url);
      await ready(p);
      await saved(p);
      await p.evaluate(() => {
        window.realTransaction = IDBDatabase.prototype.transaction;
        IDBDatabase.prototype.transaction = function (...args) {
          const tx = window.realTransaction.apply(this, args);
          if (args[1] === "readwrite") queueMicrotask(() => tx.abort());
          return tx;
        };
      });
      await p.fill("#body", "失敗しても残す文");
      await p.waitForFunction(() =>
        document
          .querySelector("#storage-state")
          .textContent.includes("退避に失敗"),
      );
      assert.equal(await p.inputValue("#body"), "失敗しても残す文");
      assert.match(await p.textContent("#save-state"), /未退避/);
      await p.evaluate(() => {
        IDBDatabase.prototype.transaction = window.realTransaction;
      });
      await p.click("#retry");
      await saved(p);
      assert.equal((await dbRows(p))[0].active.final.text, "失敗しても残す文");
    },
  );
  await check(
    "same-origin tab conflict preserves both drafts as separate copies",
    async (p, context) => {
      await p.goto(url);
      await ready(p);
      await p.fill("#body", "元の文");
      await saved(p);
      const p2 = await context.newPage();
      await p2.goto(url);
      await ready(p2);
      await saved(p2);
      await p2.fill("#body", "別タブの文");
      await saved(p2);
      await p.fill("#body", "最初のタブの文");
      await p.waitForFunction(() =>
        document.querySelector("#notice").textContent.includes("別コピー"),
      );
      await pause(600);
      const rows = await dbRows(p);
      assert.equal(rows.length, 2);
      const texts = rows.map((r) => r.active.final.text);
      assert.ok(texts.includes("別タブの文"));
      assert.ok(texts.includes("最初のタブの文"));
      await p2.close();
    },
  );
  await check(
    "delete removes selected browser copy including all its history",
    async (p) => {
      await p.goto(url);
      await ready(p);
      await p.fill("#body", "削除前の秘密の架空文");
      await p.click("#seal");
      await p.click("#continue");
      await p.fill("#body", "短い文");
      await saved(p);
      const old = (await dbRows(p))[0].id;
      p.once("dialog", (d) => d.accept());
      await p.click("#delete");
      await p.waitForFunction(() =>
        document.querySelector("#notice").textContent.includes("削除しました"),
      );
      const rows = await dbRows(p);
      assert.ok(!rows.some((r) => r.id === old));
      assert.ok(!JSON.stringify(rows).includes("削除前の秘密"));
      assert.equal(await p.inputValue("#body"), "");
    },
  );
  await check(
    "no requests from editing, replay, import or export; CSP blocks connect",
    async (p) => {
      const requests = [];
      p.on("request", (r) => requests.push(r.url()));
      await p.goto(url);
      await ready(p);
      await p.fill("#body", "通信しない架空文");
      await p.click("#seal");
      const data = await exported(p);
      await p.setInputFiles("#file", {
        name: "invented.json",
        mimeType: "application/json",
        buffer: Buffer.from(data),
      });
      await p.waitForFunction(() =>
        document
          .querySelector("#notice")
          .textContent.includes("読み込みました"),
      );
      await p.click("#history summary");
      await p.click("#prev");
      const blocked = await p.evaluate(async () => {
        try {
          await fetch("https://example.invalid/test");
          return false;
        } catch {
          return true;
        }
      });
      assert.equal(blocked, true);
      assert.deepEqual(
        requests.filter((x) => x !== url),
        [],
      );
    },
  );
  await check(
    "tablet viewport fits; JSONL reimport and purpose-only changes are retained",
    async (p) => {
      await p.goto(url);
      await ready(p);
      await p.fill("#body", "架空のメモ");
      await p.fill("#purpose", "あとで読む");
      await p.click("#seal");
      await p.click("#continue");
      await p.fill("#body", "架空のメモ\n追記");
      await p.click("#seal");
      const text = await exported(p, "#export-all");
      await p.setInputFiles("#file", {
        name: "invented.jsonl",
        mimeType: "text/plain",
        buffer: Buffer.from(text),
      });
      await p.waitForFunction(() =>
        document.querySelector("#notice").textContent.includes("2件"),
      );
      assert.equal(
        await p.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
        true,
      );
      const ep = JSON.parse(await exported(p));
      assert.equal(ep.purpose.text, "あとで読む");
      if (process.env.E1_SCREENSHOT_DIR) {
        await p.screenshot({
          path: path.join(process.env.E1_SCREENSHOT_DIR, "e1-tablet.png"),
          fullPage: true,
        });
      }
    },
    { viewport: { width: 800, height: 1280 }, isMobile: true, hasTouch: true },
  );
  if (process.env.E1_SCREENSHOT_DIR) {
    const p = await browser.newPage({
      viewport: { width: 1360, height: 1000 },
    });
    await p.goto(url);
    await ready(p);
    await p.fill("#title", "お願いの下書き");
    await p.fill(
      "#body",
      "資料を確認していただけますか。\n\n修正した文も、履歴に残ります。",
    );
    await p.click("#seal");
    await p.click("#history summary");
    await p.screenshot({
      path: path.join(process.env.E1_SCREENSHOT_DIR, "e1-desktop.png"),
      fullPage: true,
    });
    await p.close();
  }
  const report = {
    scope:
      "invented-only engineering; synthetic composition is not real IME verification",
    browser: browser.version(),
    url,
    results,
    passed: results.filter((x) => x.status === "PASS").length,
    total: results.length,
  };
  if (process.env.E1_REPORT)
    fs.writeFileSync(
      process.env.E1_REPORT,
      JSON.stringify(report, null, 2) + "\n",
    );
  console.log(JSON.stringify({ passed: report.passed, total: report.total }));
  await browser.close();
  if (report.passed !== report.total) process.exitCode = 1;
})().catch(async (e) => {
  console.error(e);
  if (browser) await browser.close();
  process.exitCode = 1;
});
