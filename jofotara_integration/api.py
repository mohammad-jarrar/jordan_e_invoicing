import requests
import base64
import frappe
from .utils import generate_general_invoice_xml, generate_credit_invoice_xml

def submit_invoice(invoice_name):
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    settings = frappe.get_single("Jofotara Settings")
    
    xml = generate_general_invoice_xml(doc) if not doc.is_return else generate_credit_invoice_xml(doc)
    encoded_xml = base64.b64encode(xml).decode()
    
    payload = {
        "ClientID": settings.client_id,
        "SecretKey": settings.secret_key,
        "InvoiceRequest": encoded_xml
    }
    
    response = requests.post(
        settings.api_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    handle_response(response, doc)

def handle_response(response, doc):
    if response.status_code == 200:
        data = response.json()
        if data.get("Success"):
            doc.db_set("jofotara_qr_code", data.get("QRCode"))
            doc.db_set("jofotara_status", "Submitted")
        else:
            log_error(doc, data.get("ErrorMessage"))
    else:
        log_error(doc, f"HTTP Error {response.status_code}")

def log_error(doc, message):
    frappe.log_error(
        title=f"Jofotara Submission Failed - {doc.name}",
        message=message
    )
    doc.db_set("jofotara_status", "Failed")