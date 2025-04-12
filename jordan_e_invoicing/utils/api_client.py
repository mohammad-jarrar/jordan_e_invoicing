import frappe
import requests

@frappe.whitelist()
def send_invoice(invoice_name):
    """
    Sends a Sales Invoice to the Jordan E-Invoicing (JoFotara) API in JSON format.
    """
    # Fetch the Sales Invoice document
    invoice = frappe.get_doc("Sales Invoice", invoice_name)

    # Validate that the invoice exists
    if not invoice:
        frappe.throw(f"Sales Invoice {invoice_name} not found.")

    # Prepare the payload for the API
    payload = {
        "invoice_number": invoice.name,
        "invoice_date": invoice.posting_date.isoformat(),
        "customer_name": invoice.customer,
        "items": [
            {
                "item_name": item.item_name,
                "qty": item.qty,
                "rate": item.rate,
                "amount": item.amount
            }
            for item in invoice.items
        ],
        "grand_total": invoice.grand_total,
        "currency": invoice.currency
    }

    # Fetch API settings from E-Invoicing Settings
    api_endpoint = frappe.db.get_single_value("E-Invoicing Settings", "api_endpoint")
    client_id = frappe.db.get_single_value("E-Invoicing Settings", "client_id")
    secret_key = frappe.db.get_single_value("E-Invoicing Settings", "secret_key")

    # Validate API settings
    if not all([api_endpoint, client_id, secret_key]):
        frappe.throw("E-Invoicing Settings are incomplete. Please configure them in Settings.")

    # Send the request to the API
    headers = {
        "Content-Type": "application/json",
        "Client-ID": client_id,
        "Secret-Key": secret_key
    }

    try:
        response = requests.post(
            url=api_endpoint,
            headers=headers,
            json=payload  # Send JSON as the request body
        )

        # Log full response for debugging
        frappe.log_error(title="JoFotara API Response", message=response.text)

        # Check if the response is successful
        if response.status_code != 200:
            frappe.throw(f"Failed to send invoice: {response.text}")

        response_json = response.json()
        if response_json.get("status") != "success":
            frappe.throw(f"Failed to send invoice: {response_json.get('message')}")

        # Mark the Sales Invoice as sent
        invoice.db_set("status", "Sent")
        frappe.msgprint(f"Invoice {invoice_name} was sent successfully!")

    except Exception as e:
        frappe.throw(f"Error while sending invoice: {str(e)}")