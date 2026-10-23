---
name: node-doctrine
description: How to build Node/TypeScript services under the doctrine - purpose folders (routes, services, domain, data, config, utils), thin routes, services that hold the logic, one data-access layer, config validated at startup, one error shape, the HTTP framework kept out of domain code. Use when writing or reviewing a Node backend or API.
---

# Node doctrine

Load `doctrine` first. This pack is what its rules look like in a Node service
written in TypeScript - Express, Fastify, Hono or Koa. It specialises rule 3
(the framework stays at the edge), rule 8 (one data door) and the folder model.

## Purpose folders

```
src/
  index.ts        starts the server: load config, build the app, listen. Nothing else.
  app.ts          builds the app: middleware, routes, error handler
  config/         reads and validates configuration once, exports a typed object
  routes/         one unit per resource - parse the request, call a service, shape the response
  services/       the logic, one unit per concern
  domain/         types and pure rules of the business: no framework, no I/O
  data/           the one data-access layer: the database client, repositories, external APIs
  middleware/     auth, logging, rate limiting
  utils/          subject units: dates, money, retry, ids
```

**The request flow is one direction:** `routes → services → domain` and
`services → data`. A route never touches `data/`; `domain/` imports nothing
from the folders above it; `data/` never imports `routes/`.

A unit grows into a folder exactly as `doctrine` describes:

```
routes/orders.ts         →    routes/orders/
                                index.ts        the router: mounts the handlers
                                handlers.ts     one function per endpoint
                                schemas.ts      request and response validation
```

## Thin routes

A handler parses and validates its input, calls one service function, and
shapes the response. Decisions - pricing, permissions beyond "is logged in",
state transitions - are a service's.

```ts
router.post('/orders', async (req, res) => {
  const input = OrderIn.parse(req.body);
  res.status(201).json(toOrderOut(await orders.place(req.user, input)));
});
```

*Why:* a decision inside a handler can only be tested by an HTTP request, and
the next transport (a queue consumer, a CLI, a cron job) has to copy it.

## Domain code is free of the framework

`domain/` holds the business's types and pure rules. It imports no Express,
Fastify or Hono, no database client, and nothing from `routes/`, `services/`
or `data/`. Services pass it plain values.

## One data-access layer

Every database query and every call to an external API goes through `data/`:
one client per source, created once, and repository functions that return
domain types. Services never import the driver or the ORM directly.

*Why:* when queries are scattered, a schema change becomes a search across the
codebase, and two places end up writing the same row two different ways.

## Configuration validated at startup

`config/` reads the environment once, validates it (zod or similar), and
exports a typed, frozen object. A missing secret stops the server at startup
with a clear message, not on the first request that needs it. Nothing reads
`process.env` outside `config/`.

## One error shape

Errors carry a type the error handler understands (`NotFound`, `Forbidden`,
`Invalid`), thrown by services and turned into a response in one place in
`app.ts`. Handlers do not build error responses by hand.

## Platform SDKs

Stripe, Twilio, S3, email providers - each sits behind a unit in `data/` (or
an adapter in `services/`) that the rest of the app calls. Nothing else
imports the SDK, so it can be replaced, and faked in tests.

## Health

`health` runs TypeScript, import cycles, lint, unused code, duplication,
sizes, secrets and dependency scans. Type checking needs the project's own
`npm install`. A reviewer checks the request flow by hand:

```bash
grep -rnE "from ['\"](express|fastify|hono|koa)" src/domain src/services
grep -rnE "from ['\"].*/data/" src/routes
```
