# Sale Order Approval — starter

Odoo 17 module: adds a discount-approval workflow to the native
Sales module via `_inherit` (no new app, no new model — this is a
customization of `sale.order`, the same kind of work Odoo
implementation partners do for clients).

## Run it

```bash
docker compose up
```

Wait ~30s, then open http://localhost:8069 and create a new database
(any master password/email — it's local). Demo data: check the box
so the Sales app already has sample customers/products.

## Install the module

1. Go to **Apps**, remove the "Apps" filter, search "Sale Order Approval".
2. If it doesn't show up: Apps → top-right menu → **Update Apps List** first
   (Odoo needs to rescan `/mnt/extra-addons`).
3. Click **Install**.

## Set yourself as an approver

**Settings → Users & Companies → Users** → your user → **Sales** tab (or
wherever the "Sales Approver" group shows once the category loads) →
check the new "Sales Approver" group. You'll need Developer mode on
(Settings → General Settings → scroll to bottom → Activate developer mode)
to see everything clearly while testing.

## Test the flow

1. Sales → Create a new quotation for any customer/product.
2. Set **Discount (%)** above 15.
3. Click **Confirm** — order should jump to "To Approve" instead of
   "Sales Order", and (if outgoing mail is configured) send a
   notification.
4. As the approver, click **Approve** — order should confirm normally.
5. Try **Reject** on another test order — should return to Draft.

## Known gaps / things to harden next

- `approval_threshold` is hardcoded (15%) — next step: move it to
  `res.config.settings` so it's configurable per company.
- No automated tests yet (`tests/` folder) — worth adding
  `tests/test_sale_approval.py` with a couple of `TransactionCase`
  tests once the manual flow works.
- Outgoing mail needs an actual mail server configured in Odoo to
  actually send — without one, `send_mail` will just log, which is
  fine for local testing.
