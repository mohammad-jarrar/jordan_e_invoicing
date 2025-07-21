# JoFotara Integration for ERPNext

**JoFotara (Jordan E-Invoicing) integration for ERPNext v15.**

## Features

- Send Sales Invoice and Credit Note to JoFotara via button
- UBL 2.1 XML generation
- Multi-company support, per-company credentials
- Sandbox/Test mode
- QR code returned from JoFotara and shown on PDF
- Custom fields for customer e-invoicing data
- JoFotara Settings DocType

## Installation

1. Copy the app folder to your Frappe/ERPNext bench apps directory.
2. Run:
   ```bash
   bench get-app jo_fotara /path/to/jo_fotara
   bench --site yoursite install-app jo_fotara
   ```
3. Run:
   ```bash
   bench migrate
   ```

## Setup

- Go to **JoFotara Settings** list and create a record for each company.
- Enter Client ID, Secret Key, Taxpayer Type, Activity Number, sandbox/test toggle, etc.
- Fill in required customer fields for e-invoicing.
- On Sales Invoice or Credit Note, click **"Send to JoFotara"**.

## Customization

- You may edit the XML builder logic in `jo_fotara/api/send_to_jofotara.py`.
- Add/adjust custom fields for your business requirements.

## Support

Open an issue or PR for improvements!