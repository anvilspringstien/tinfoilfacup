import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../beta/post-office-launcher.js', import.meta.url), 'utf8');
function harness() {
 const assets = [], opened = []; let onClick;
 const window = {}, document = { currentScript: { src: 'https://tinfoilfacup.com/beta/post-office-launcher.js' },
  addEventListener(type, fn) { assert.equal(type, 'click'); onClick = fn; },
  createElement(tag) { return { tag }; },
  head: { appendChild(el) { assets.push(el); queueMicrotask(() => { if (el.tag === 'script') window.tffcOpenPostOffice = (...args) => opened.push(args); el.onload(); }); } },
 };
 vm.runInNewContext(source, { window, document, URL, Promise });
 async function click(href, extra = {}) { let prevented = false;
  onClick({ button: 0, target: { closest: () => ({ href }) }, preventDefault() { prevented = true; }, ...extra });
  await new Promise(resolve => setImmediate(resolve)); return prevented;
 }
 return { assets, opened, click };
}
test('launcher adds no form or security resources before a contact click', () => { const h = harness(); assert.equal(h.assets.length, 0); assert.equal(h.opened.length, 0); });
test('every existing Campaign and Challenges email link opens the correct Post Office subject', async () => {
 for (const file of ['clubfinder-beta.html', 'challenges-beta.html']) {
  const html = fs.readFileSync(new URL('../beta/' + file, import.meta.url), 'utf8');
  const urls = [...html.matchAll(/href="(https:\/\/mail\.google\.com\/[^\"]+)"/g)].map(m => m[1].replaceAll('&amp;', '&'));
  assert.ok(urls.length >= 2, file + ' contact links found');
  for (const url of urls) {
   const h = harness(); assert.equal(await h.click(url), true);
   assert.equal(h.opened.length, 1); assert.equal(h.opened[0][0], new URL(url).searchParams.get('su').includes('Issue Report') ? 'issue' : 'feedback');
   assert.equal(h.opened[0][1].endpoint, 'https://tffc-barry-post-office.anvilspringstien.workers.dev/messages');
   assert.equal(h.assets.length, 2); assert.ok(h.assets.every(el => (el.src || el.href).startsWith('https://tinfoilfacup.com/beta/post-office.')));
  }
 }
});
test('repeated contact clicks reuse loaded resources', async () => {
 const h = harness(), url = 'https://mail.google.com/mail/?view=cm&to=tinfoilfacup%40gmail.com&su=Tin%20Foil%20FA%20Cup%20Feedback';
 await h.click(url); await h.click(url); assert.equal(h.assets.length, 2); assert.equal(h.opened.length, 2);
});
test('modified clicks and unrelated links preserve their original behaviour', async () => {
 const h = harness(), url = 'https://mail.google.com/mail/?to=tinfoilfacup%40gmail.com&su=Feedback';
 assert.equal(await h.click(url, { ctrlKey: true }), false);
 assert.equal(await h.click(url, { metaKey: true }), false);
 assert.equal(await h.click('https://tinfoilfacup.com/'), false);
 assert.equal(await h.click('https://mail.google.com/mail/?to=someone%40example.org&su=Feedback'), false);
 assert.equal(h.assets.length, 0); assert.equal(h.opened.length, 0);
});
