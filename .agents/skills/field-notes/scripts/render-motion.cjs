// Render an SVG (or HTML) animation to MP4, frame by frame.
// The file must expose a global `frame(t)` that draws time t in seconds, as a pure function
// (see examples/11-motion.svg). One Chrome is driven over DevTools, so every frame is exact.
//
//   node render-motion.cjs <in.svg> <out.mp4> [seconds=7] [fps=30] [width=1080] [height=1080]
//
// Needs Google Chrome, ffmpeg, and puppeteer-core (`npm i puppeteer-core`).
const puppeteer = require('puppeteer-core');
const { execFileSync } = require('child_process');
const fs = require('fs'), os = require('os'), path = require('path');

const [, , input, output, seconds = '7', fps = '30', width = '1080', height = '1080'] = process.argv;
if (!input || !output) { console.error('usage: node render-motion.cjs <in.svg> <out.mp4> [seconds] [fps] [w] [h]'); process.exit(1); }
const CHROME = process.env.CHROME || [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
].find(p => fs.existsSync(p));

(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'motion-'));
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage();
  await page.setViewport({ width: +width, height: +height, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(input) + '?t=0', { waitUntil: 'load' });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  const n = Math.round(+seconds * +fps);
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => frame(t), i / +fps);
    await page.screenshot({ path: path.join(tmp, String(i).padStart(5, '0') + '.png') });
  }
  await browser.close();
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', fps, '-i', path.join(tmp, '%05d.png'),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', output]);
  fs.copyFileSync(path.join(tmp, String(Math.max(0, n - Math.round(+fps * 0.8))).padStart(5, '0') + '.png'),
    output.replace(/\.mp4$/, '') + '-still.png');
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log(`${output} (${n} frames) + still`);
})();
