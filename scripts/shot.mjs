/**
 * 用 CDP 做真实视口截图（Chrome headless 的 --window-size 最小被钳制在 500px，
 * 手机视口必须走 Emulation.setDeviceMetricsOverride）。
 *
 * 用法：
 *   chrome --headless=new --remote-debugging-port=9333 --remote-allow-origins=*
 *   node scripts/shot.mjs <url> <out.png> [width] [height]
 */
import { writeFileSync } from 'node:fs';

const [url, out, widthArg, heightArg] = process.argv.slice(2);
if (!url || !out) {
  console.error('usage: node shot.mjs <url> <out.png> [width=390] [height=844]');
  process.exit(2);
}
const width = Number(widthArg || 390);
const height = Number(heightArg || 844);
const base = process.env.CDP_BASE || 'http://127.0.0.1:9333';

const target = await (await fetch(`${base}/json/new?about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(target.webSocketDebuggerUrl);
const pending = new Map();
let seq = 0;

const send = (method, params = {}) =>
  new Promise((resolve, reject) => {
    const id = ++seq;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });

await new Promise((resolve) => ws.addEventListener('open', resolve));
ws.addEventListener('message', (event) => {
  const msg = JSON.parse(event.data);
  const slot = pending.get(msg.id);
  if (!slot) return;
  pending.delete(msg.id);
  if (msg.error) slot.reject(new Error(`${msg.error.message} (${msg.error.code})`));
  else slot.resolve(msg.result);
});

await send('Page.enable');
await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', {
  width,
  height,
  deviceScaleFactor: 2,
  mobile: width < 600,
});
await send('Page.navigate', { url });
await new Promise((resolve) => setTimeout(resolve, 2500));

// .reveal 元素只有在滚动进入视口时才会淡入，先滚动整页触发，再回到顶部。
await send('Runtime.evaluate', {
  awaitPromise: true,
  expression: `
    (async () => {
      // 页面根节点带 scroll-smooth，平滑动画会吞掉逐屏滚动，先临时关掉。
      const html = document.documentElement;
      const prev = html.style.scrollBehavior;
      html.style.scrollBehavior = 'auto';
      const step = Math.max(200, Math.floor(window.innerHeight * 0.8));
      const total = document.documentElement.scrollHeight;
      for (let y = 0; y < total; y += step) {
        window.scrollTo(0, y);
        await new Promise((r) => setTimeout(r, 120));
      }
      window.scrollTo(0, 0);
      await new Promise((r) => setTimeout(r, 500));
      html.style.scrollBehavior = prev;
    })()
  `,
});

const metrics = await send('Runtime.evaluate', {
  expression: `JSON.stringify({
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth: window.innerWidth,
    pageHeight: document.documentElement.scrollHeight,
    overflowing: [...document.querySelectorAll('body *')]
      .filter((el) => {
        const r = el.getBoundingClientRect();
        return r.right > window.innerWidth + 1 || r.left < -1;
      })
      .slice(0, 8)
      .map((el) => el.tagName + '.' + String(el.className).slice(0, 40))
  })`,
  returnByValue: true,
});

const { data } = await send('Page.captureScreenshot', {
  format: 'png',
  captureBeyondViewport: true,
});
writeFileSync(out, Buffer.from(data, 'base64'));

console.log(`${out} :: ${metrics.result.value}`);
ws.close();
await fetch(`${base}/json/close/${target.id}`).catch(() => {});
