import frappe
import requests
import base64
from .xml_generator import create_invoice_xml

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

    # Prepare invoice data for XML generation
    invoice_data = {
        "invoice_no": invoice.name,
        "uuid": str(invoice.uuid),
        "issue_date": invoice.posting_date.isoformat(),
        "payment_method": "Cash" if invoice.is_cash else "Receivable",
        "note": invoice.remarks or "",
        "currency": invoice.currency,
        "tax_currency": "JOD",
        "seller_tin": frappe.db.get_single_value("E-Invoicing Settings", "seller_tin"),
        "seller_name": frappe.db.get_single_value("E-Invoicing Settings", "seller_name"),
        "buyer_tin": invoice.customer_tin or "",
        "buyer_name": invoice.customer_name or ""
    }

    # Generate XML and encode in Base64
    xml_data = create_invoice_xml(invoice_data)
    encoded_xml = base64.b64encode(xml_data.encode("utf-8")).decode("utf-8")

    # Prepare the payload for the API
    payload = {
        "client_id": frappe.db.get_single_value("E-Invoicing Settings", "client_id"),
        "secret_key": frappe.db.get_single_value("E-Invoicing Settings", "secret_key"),
        "invoice_data": encoded_xml
    }

    # Fetch API settings from E-Invoicing Settings
    api_endpoint = frappe.db.get_single_value("E-Invoicing Settings", "api_endpoint")

    # Validate API settings
    if not api_endpoint or not payload["client_id"] or not payload["secret_key"]:
        frappe.throw("E-Invoicing Settings are incomplete. Please configure them in Settings.")

    # Send the request to the API
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url=api_endpoint, headers=headers, json=payload)

        # Log the API response
        frappe.log_error(title="JoFotara API Response", message=response.text)

        # Ensure the response is successful
        if response.status_code != 200:
            frappe.throw(f"Failed to send invoice: {response.text}")

        response_json = response.json()
        if response_json.get("status") != "success":
            frappe.throw(f"Failed to send invoice: {response_json.get('message')}")

        # Save QR code and mark invoice as sent
        qr_code = response_json.get("qr_code")
        invoice.db_set("qr_code", qr_code)
        invoice.db_set("status", "Sent")
        frappe.msgprint(f"Invoice {invoice_name} was sent successfully!")

    except Exception as e:
        frappe.throw(f"Error while sending invoice: {str(e)}")
