import { DurableObject } from "cloudflare:workers";

const COUNTER_NAME = "clubfinder-global";

function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      ...headers,
    },
  });
}

function allowedOrigins(env) {
  return String(env.ALLOWED_ORIGINS || "")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
}

function corsHeaders(request, env) {
  const origin = request.headers.get("Origin") || "";
  const allowed = allowedOrigins(env);

  if (!origin) return {};
  if (allowed.length && !allowed.includes(origin)) return null;

  return {
    "access-control-allow-origin": allowed.length ? origin : "*",
    "access-control-allow-methods": "POST, OPTIONS",
    "access-control-allow-headers": "content-type",
    "access-control-max-age": "86400",
    vary: "Origin",
  };
}

function isAdmin(request, env) {
  if (!env.ADMIN_TOKEN) return false;
  const auth = request.headers.get("Authorization") || "";
  return auth === `Bearer ${env.ADMIN_TOKEN}`;
}

export class ClubfinderCounter extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec(`
      CREATE TABLE IF NOT EXISTS usage_counter (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        total INTEGER NOT NULL DEFAULT 0
      )
    `);
    this.sql.exec("INSERT OR IGNORE INTO usage_counter (id, total) VALUES (1, 0)");
  }

  increment() {
    this.sql.exec("UPDATE usage_counter SET total = total + 1 WHERE id = 1");
  }

  value() {
    const row = this.sql.exec("SELECT total FROM usage_counter WHERE id = 1").one();
    return Number(row.total || 0);
  }

  async fetch(request) {
    const path = new URL(request.url).pathname;

    if (request.method === "POST" && path === "/increment") {
      this.increment();
      return new Response(null, { status: 204 });
    }

    if (request.method === "GET" && path === "/value") {
      return json({ total: this.value() });
    }

    return new Response("Not found", { status: 404 });
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/health") {
      return json({ ok: true, service: "tffac-clubfinder-counter" });
    }

    if (request.method === "OPTIONS" && url.pathname === "/increment") {
      const cors = corsHeaders(request, env);
      if (cors === null) return new Response(null, { status: 403 });
      return new Response(null, { status: 204, headers: cors });
    }

    if (request.method === "POST" && url.pathname === "/increment") {
      const cors = corsHeaders(request, env);
      if (cors === null) return new Response(null, { status: 403 });

      const id = env.CLUBFINDER_COUNTER.idFromName(COUNTER_NAME);
      const stub = env.CLUBFINDER_COUNTER.get(id);
      await stub.fetch("https://counter.internal/increment", { method: "POST" });

      // Deliberately do not expose the private total to Clubfinder users.
      return new Response(null, { status: 204, headers: cors });
    }

    if (request.method === "GET" && url.pathname === "/admin/count") {
      if (!isAdmin(request, env)) {
        return json({ error: "unauthorized" }, 401, {
          "www-authenticate": "Bearer",
        });
      }

      const id = env.CLUBFINDER_COUNTER.idFromName(COUNTER_NAME);
      const stub = env.CLUBFINDER_COUNTER.get(id);
      const response = await stub.fetch("https://counter.internal/value");
      const { total } = await response.json();
      return json({ total });
    }

    return new Response("Not found", { status: 404 });
  },
};
