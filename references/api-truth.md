# Dreamteam API: verified behaviour

Every statement here was tested live against real tenants on 2026-08-03. Where this
document disagrees with https://docs.dreamteam.co/api/, trust this document and see
"Known documentation defects" at the bottom.

Use the official docs for the full endpoint list, filter syntax and operators. Use this
file for auth, pagination and the traps.

---

## 1. Connecting

```
Base URL:  https://api.dreamteamcrm.ai/api/v1
Auth:      x-api-key: <YOUR_KEY>
Tenant:    Origin: https://<tenant-slug>.dreamteamcrm.ai
```

Both headers are required on every request.

| Mistake | What you get |
|---|---|
| `Authorization: Bearer <key>` | `401 Unauthorized` |
| No `Origin` header | `404` |
| Called from a browser | `403 Invalid CORS request` at preflight |

`https://api.dreamteamcrm.info` is an alias and behaves identically. Prefer the `.ai`
host.

### Why browser calls can never work

The `Origin` header does two jobs at once: it is the CORS allowlist check *and* the
tenant selector. Browsers set `Origin` themselves and forbid JavaScript from changing
it. An app served from `myapp.lovable.app` is therefore rejected by the allowlist, and
even if it were allowed there is no tenant by that name.

Only `*.dreamteamcrm.ai` origins pass preflight. Call from a server.

---

## 2. Pagination: two APIs, opposite conventions

**This is the most dangerous part of the API. Read it twice.**

Neither endpoint errors when you use the other one's convention. You get a valid-looking
response containing the wrong slice of data.

| | `/objects/{type}/records` | `/meetings`, `/recordings` |
|---|---|---|
| First page index | **1** (`page=0` throws `VALIDATION_FAILED`) | **0** (`page=0` is correct) |
| Page size param | **`page_size`** (max 100) | **`size`** |
| Rows array | `results` | `content` |
| Total count | `metadata.total_elements` | `totalElements` |
| More pages? | `metadata.has_next` | `last` is `false` |
| Page number echo | `metadata.page` | `number` |

### Verified evidence

```
/objects/deal/records?page=1&size=100        ->  20 rows   WRONG, size is ignored
/objects/deal/records?page=1&page_size=100   -> 100 rows   correct
/objects/deal/records?page=1&page_size=200   -> 100 rows   capped at 100, no error

/meetings?page=1&page_size=100  ->  20 rows  WRONG, page_size ignored AND page 1 is the second page
/meetings?page=1&size=100       ->  85 rows  this is page TWO of 185, you silently skipped 100
/meetings?page=0&size=100       -> 100 rows  correct first page
```

Read that middle line again. On `/meetings`, starting at `page=1` skips the first page
entirely and returns a smaller number that looks like a complete result set.

### Unknown query parameters are silently ignored

There is no "unknown parameter" error. Passing `size` to an endpoint that wants
`page_size` does not fail. It quietly returns the default 20 rows. This is how a
dashboard ends up built on 20 of 196 deals with no warning anywhere.

### Required fetch procedure

1. Use the correct first-page index and size parameter for that endpoint family.
2. Loop until `metadata.has_next` is false, or `last` is true.
3. Accumulate rows.
4. **Assert** the accumulated count equals `metadata.total_elements` / `totalElements`.
5. If it does not match, throw. Do not render. Do not fall back to partial data.

Show the record count and the source total somewhere in the UI. If a user can see
"212 of 212 meetings", a truncation bug becomes visible instead of invisible.

### Errors do not have a rows key

Error responses are JSON objects with no `results` and no `content`:

```json
{"code":"VALIDATION_FAILED","message":"Page must be at least 1 (pages are 1-based)",
 "path":"/api/v1/objects/deal/records"}
```

Code written as `response.results ?? []` reads an error as "no data" and renders an
empty dashboard. Check for the error shape explicitly before reading rows.

---

## 3. Record shape

`/objects/{type}/records` returns:

```json
{
  "results": [
    {
      "id": "...",
      "type": "deal",
      "properties": { "name": "...", "amount": 50000, "owner_id": 1000004,
                      "stage_id": "...", "pipeline_id": "...",
                      "expected_close_date": "..." },
      "created_at": "...", "updated_at": "...", "created_by": "..."
    }
  ],
  "metadata": { "page": 1, "page_size": 100, "total_elements": 196,
                "total_pages": 2, "has_next": true, "has_previous": false }
}
```

All business fields live under **`properties`**. Older examples showing a `data` key
are stale.

---

## 4. Discovering the schema

```
GET /api/v1/objects/{object}
```

where `{object}` is `contact`, `company`, `deal`, `note`, `meeting` or `task`.

Returns `fields[]`, each with `name`, `type`, `label`, `filterable`, `read_only`,
`required`, and `options` for dropdowns.

**Call this before writing any logic.** Tenants can override standard fields and add
their own. A dashboard that hardcodes field names works for the tenant it was built
against and breaks on the next one.

Field types you will meet: `TEXT`, `TEXTAREA`, `EMAIL`, `PHONE`, `URL`, `DATETIME`,
`DECIMAL`, `NUMBER`, `BOOLEAN`, `DROPDOWN`, `LOOKUP`, `FILE`.

`LOOKUP` fields hold references to other records. `owner_id` is a lookup to a user.

---

## 5. Users, identity and permissions

```
GET /api/v1/users
```

Returns `id`, `primary_email`, `first_name`, `last_name`, `role`, `sales_user`.
Observed roles: `admin`, `sales_member`.

**There is no whoami endpoint.** `/users/me` returns 500.

### The key model

There is exactly one kind of API key: a **per-user profile token**, generated from that
user's profile page. There is no scoped key, no read-only key, and no expiry. The token
stays valid until someone clicks Reset, which invalidates the previous one immediately.

**The token can write.** The same key that reads also creates, updates and deletes.
There is no way to restrict it at issue time.

That is a fact to know, not a reason to cripple the app. Build whatever the reference
pack declares. If it says read-only, the app reads. If it declares writes, build them
properly. The one thing that does not change is that the token stays on the server.

**A key carries the permissions of the user who generated it.** The API filters to
"records the API caller is permissioned to see". So an admin's token returns everything,
including records owned by other people. *Verified:* a single admin token returned deals
under multiple distinct `owner_id` values.

*Inferred, not verified:* a token from a lower-privilege user, for example a
`sales_member`, should return a correspondingly narrower set. This is worth two minutes
to confirm before relying on it: create a limited user, generate its token, and compare
`total_elements` on the same query against an admin token. If the counts match, there is
no per-user filtering and the note above is wrong.

The practical consequence either way: if your app checks "does this signed-in person
exist in Dreamteam" and then queries with one shared token, every signed-in user sees
whatever *that token's* user can see, not what they themselves can see. Per-user scoping
has to be built.

To scope per user, do it in your server route:

- Look up the signed-in person's verified email in `/api/v1/users`.
- If `role` is `admin`, return everything.
- Otherwise filter to records where `properties.owner_id` equals their `id`.

The email must come from your identity provider's verified claim. Never from a form
field, or anyone can type a colleague's address.

---

## 6. Known documentation defects

As of 2026-08-03, https://docs.dreamteam.co/api/ is wrong in two ways that will stop
you cold:

1. It documents `Authorization: Bearer <token>` as always required. That returns 401.
   The working header is `x-api-key`.
2. It does not mention the `Origin` tenant header at all, and states the opposite:
   *"The base URL is the same for all customers. Your Bearer token identifies your
   organization."* Omitting `Origin` returns 404.

It is also silent on the `/meetings` pagination convention differing from
`/objects/*/records`.

The docs are correct and useful for the endpoint list, filter syntax, operators and
sorting. Use them for that.
