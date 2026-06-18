
const puppeteer = require('puppeteer');
const path = require('path');
(async () => {
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  const input = process.argv[2];
  const output = process.argv[3];
  await page.goto('file://' + path.resolve(input), { waitUntil: 'networkidle0' });
  await page.pdf({
    path: output,
    format: 'A4',
    margin: { top: '12mm', right: '12mm', bottom: '12mm', left: '12mm' },
    printBackground: true,
  });
  await browser.close();
  console.log('PDF:', output);
})();
