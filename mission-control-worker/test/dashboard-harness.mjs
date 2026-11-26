import assert from 'node:assert/strict';
import vm from 'node:vm';

export function inlineScripts(html) {
  return Array.from(html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g), match => match[1]);
}

export function browser(origin, scripts, storage = new Map(), upstream = async () => new Response(null, { status: 503 }), locks = { request: async (_name, task) => task() }) {
  const listeners = new Map();
  const elements = new Map();
  const requests = [];
  const node = () => ({ innerHTML: '', textContent: '', style: {}, append() {}, querySelector: () => null });
  const getElementById = id => {
    if (!elements.has(id)) elements.set(id, node());
    return elements.get(id);
  };
  const sandbox = vm.createContext({
    document: { body: node(), getElementById, querySelectorAll: () => [], createElement: node,
      addEventListener: (event, handler) => listeners.set(event, handler) },
    localStorage: { getItem: key => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, value),
      removeItem: key => storage.delete(key) },
    window: { scrollTo() {}, addEventListener: (event, handler) => listeners.set(event, handler) },
    navigator: { locks }, URL, AbortController, crypto,
    fetch: async (input, options = {}) => {
      const url = new URL(input, origin);
      requests.push({ url, method: options.method ?? 'GET', options });
      return upstream(url, options);
    },
    setTimeout: () => 1, clearTimeout() {},
  });
  for (const script of scripts) vm.runInContext(script, sandbox);
  function click(attribute, value) {
    return listeners.get('click')({ target: {
      closest: selector => selector === '[data-' + attribute + ']' ? { dataset: { [attribute]: value } } : null,
    } });
  }
  const evaluate = source => vm.runInContext(source, sandbox);
  async function idle() {
    for (let attempt = 0; attempt < 100; attempt++) {
      await new Promise(setImmediate);
      if (evaluate('!state.loading&&!state.gmail.operation')) return;
    }
    assert.fail('Dashboard did not settle');
  }
  return { requests, sandbox, element: getElementById, evaluate, idle,
    navigate: target => click('nav', target), action: target => click('action', target),
    storageEvent: key => listeners.get('storage')({ key }) };
}
