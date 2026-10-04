# Sale Order Approval

An Odoo 17 module that adds a discount-approval workflow to the native **Sales** app — built as a customization of the existing `sale.order` model rather than a standalone app, the same kind of work Odoo implementation partners do for their clients.

## Overview

Out of the box, Odoo lets any salesperson confirm a quotation with any discount. This module adds a guardrail: if a quotation's discount exceeds a configurable threshold, it can't go straight to confirmed — it's routed to an **approval** step first, and only a designated **Sales Approver** can let it through.

No new model, no new top-level app. Everything here is a targeted extension of Sales' own `sale.order` model and form view.

## Features

- **Model inheritance** (`_inherit`, not `_name`) on `sale.order` — adds fields and overrides logic on the existing model/table, without duplicating it
- **`discount_percent`** field on the order
- **Computed fields** (`approval_threshold`, `requires_approval`) that flag orders needing approval
- **Extended workflow state** — a new `to_approve` status added to the existing `state` selection via `selection_add`, without touching the native `draft` / `sent` / `sale` / `cancel` options
- **Overridden `action_confirm`** — orders above the threshold are held for approval instead of confirming immediately; everything else still goes through Odoo's native confirmation logic unchanged
- **Approve / Reject actions**, restricted to a dedicated `Sales Approver` security group — enforced both in the UI (hidden buttons) and in the method itself (`has_group()` check), so the restriction holds even if the action is called outside the form
- **View patch via `xpath`** — the discount field and the Approve/Reject buttons are inserted directly into Sales' own order form (`sale.view_order_form`), not a rebuilt copy of it
- **Automated email notification** via a custom `mail.template`, triggered when an order enters the approval state

## Tech stack

Python · Odoo ORM · XML (views, security) · PostgreSQL · Docker

## Project structure

```
sale_approval/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── sale_order.py          # _inherit sale.order: fields, state, workflow logic
├── security/
│   └── sale_approval_security.xml   # Sales Approver group
├── data/
│   └── mail_template.xml      # approval-request email template
└── views/
    └── sale_order_views.xml   # xpath patch on sale.view_order_form
```

## How it works

1. A salesperson creates a quotation and sets **Discount (%)**.
2. On **Confirm**:
   - if the discount is above the threshold → the order moves to **To Approve** instead of confirming, and a notification email goes out
   - otherwise → the order confirms normally, through Odoo's own `action_confirm` logic
3. A user in the **Sales Approver** group sees **Approve** / **Reject** buttons on orders awaiting approval (hidden from everyone else).
4. **Approve** re-runs the standard confirmation logic now that the order has been cleared. **Reject** sends it back to Draft.

## Setup

```bash
docker compose up -d
```

Then in Odoo: **Apps → Update Apps List → search "Sale Order Approval" → Install**.

To approve orders, add a user to the **Sales Approver** group under **Settings → Users & Companies → Users**.

## Security model

Two independent layers, by design:

- **UI layer** — `groups="sale_approval.group_sale_approver"` on the Approve/Reject buttons hides them from anyone outside the group
- **Logic layer** — `self.env.user.has_group(...)` inside `action_approve` / `action_reject` enforces the same restriction at the method level, so it holds even if the action is triggered outside the form (API, shell, another module)

## Known limitations / next steps

- `approval_threshold` is currently hardcoded (15%) — a natural next step is moving it to `res.config.settings` so it's configurable per company
- No automated tests yet (`tests/` folder with `TransactionCase` cases would be the next addition)
- No record rules yet restricting which orders an approver can see — currently access is model-wide, not row-level

## License

LGPL-3
