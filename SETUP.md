# Getting your API key

You need two things before you paste the prompt, and one page gives you both.

---

## Step 1: Create a user for your dashboards

**Do not use your own personal token.** Take two minutes and create a separate
Dreamteam user first, for example `dashboards@yourcompany.com`, named something like
"Dashboards".

Three reasons this is worth the two minutes:

- **The token inherits that user's permissions.** A user with a limited role sees less,
  so the app sees less. This is the only scoping mechanism available today.
- **Resetting it breaks nothing else.** Your personal token is also used by anything
  else you have connected. Rotating a dedicated one is safe.
- **Audit trails make sense.** Activity shows as "Dashboards", not as you.

Give that user the **narrowest role that still shows the data your dashboard needs**.
If the dashboard is org-wide reporting, it will need an admin-level role. If it only
needs one team's records, give it a limited role and it will only ever see those.

---

## Step 2: Copy the token

Signed in as that user:

1. Click the **profile icon**, top right
2. Click **View Profile**
3. Scroll to **API Token** at the bottom
4. Click **Reveal**, then **Copy**

The token does not expire. It stays valid until someone clicks **Reset**, which
invalidates the old one immediately.

---

## Step 3: Copy your Dreamteam web address

While you are on that page, copy the address from your browser's address bar. It looks
like:

```
https://acme.dreamteamcrm.ai/...
```

Paste the whole thing when the prompt asks. The part before `.dreamteamcrm.ai` is what
identifies your workspace, and the tool will pull it out for you.

---

## That's everything

Paste those two into the prompt when asked. Everything else is a multiple-choice
question.

---

## What the token can do

**The token is not read-only, and it cannot be made read-only.** Dreamteam has one kind
of API key today, and the same token that reads your CRM can also create, update and
delete records.

Most solutions only read. Each pack declares its access at the top of its file, so you
are not asked to decide. The dashboards in this catalogue are read-only.

Two things keep this sensible:

**The token stays on the server.** It goes in an environment variable and is never sent
to the browser. See [references/api-truth.md](references/api-truth.md) for why a
browser-side call would not work anyway.

**The dedicated user from step 1 sets the ceiling.** The token can only ever do what
that user can do. This is the part only you can do, and it is the one that actually
limits the blast radius.

### Rotating

Anyone can invalidate a token instantly: sign in as that user, go to the same API Token
panel, click **Reset**. Do that if the token is ever pasted somewhere it should not have
been, and paste the new one into your app's environment variable.
