// Headless screenshot + console capture for local pages: node tools/shot.mjs <url> <out.png> [waitMs] [w] [h] [js]
import { createRequire } from 'module';
const require = createRequire('/Users/ethan/code/projects/interpreter/package.json');
const { chromium } = require('playwright-core');
const [url, out, wait = '4000', w = '1200', h = '800', js = ''] = process.argv.slice(2);
const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: +w, height: +h }, colorScheme: process.env.SCHEME || 'light', isMobile: +w < 600, hasTouch: +w < 600, deviceScaleFactor: +w < 600 ? 2 : 1 });
page.on('console', m => console.log('[console]', m.type(), m.text()));
page.on('pageerror', e => console.log('[pageerror]', e.message));
page.on('requestfailed', r => console.log('[reqfail]', r.url(), r.failure()?.errorText));
await page.goto(url);
await page.waitForTimeout(+wait);
if (js) { console.log('[eval]', JSON.stringify(await page.evaluate(js))); await page.waitForTimeout(+(process.env.POSTWAIT || 5000)); }
if (process.env.AFTER) console.log('[after]', JSON.stringify(await page.evaluate(process.env.AFTER)));
await page.screenshot({ path: out });
await browser.close();
