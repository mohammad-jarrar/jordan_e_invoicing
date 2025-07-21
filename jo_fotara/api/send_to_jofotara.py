import frappe
import base64
import requests
from lxml import etree

@frappe.whitelist()
def send_to_jofotara(doc_type, doc_name):
    doc = frappe.get_doc(doc_type, doc_name)
    company = frappe.get_doc("Company", doc.company)
    settings = frappe.get_doc("JoFotara Settings", {"company": doc.company})

    customer = frappe.get_doc("Customer", doc.customer)

    # Prepare data
    invoice = {
        "id": doc.name,
        "uuid": getattr(doc, "jofotara_uuid", frappe.generate_hash(length=32)),
        "date": doc.posting_date.strftime("%d-%m-%Y"),
        "payment_method": "012" if getattr(doc, "is_pos", False) else "022",
        "type_code": "388" if doc.doctype == "Sales Invoice" else "381",
        "note": getattr(doc, "remarks", ""),
        "total_discount": getattr(doc, "discount_amount", 0) or 0,
        "tax_total": getattr(doc, "total_taxes_and_charges", 0) or 0,
        "amount_before_discount": getattr(doc, "net_total", 0) or 0,
        "amount_after_tax": getattr(doc, "grand_total", 0) or 0
    }

    # Company data
    company_data = {
        "country": "JO",
        "tax_id": getattr(company, "tax_id", ""),
        "name": company.company_name
    }

    # Customer data
    id_type = "TN"  # Default to TIN
    id_number = getattr(customer, "jofotara_tax_id", None)
    if getattr(customer, "jofotara_national_id", None):
        id_type = "NIN"
        id_number = customer.jofotara_national_id
    elif getattr(customer, "jofotara_passport_no", None):
        id_type = "PN"
        id_number = customer.jofotara_passport_no

    customer_data = {
        "id_type": id_type,
        "id_number": id_number or "1",
        "zip": getattr(customer, "jofotara_zip", "") or "",
        "city": getattr(customer, "jofotara_city", "") or "",
        "country": getattr(customer, "country", "") or "JO",
        "tax_id": getattr(customer, "jofotara_tax_id", "") or "1",
        "name": customer.customer_name,
        "phone": getattr(customer, "mobile_no", "") or getattr(customer, "phone", "")
    }

    # Items
    items_list = []
    for item in doc.items:
        items_list.append({
            "qty": item.qty,
            "amount": (item.rate * item.qty) - (getattr(item, "discount_amount", 0) or 0),
            "tax": getattr(item, "tax_amount", 0) or 0,
            "total_with_tax": ((item.rate * item.qty) - (getattr(item, "discount_amount", 0) or 0)) + (getattr(item, "tax_amount", 0) or 0),
            "tax_category": "S" if getattr(item, "tax_rate", 0) else "Z",
            "tax_percent": getattr(item, "tax_rate", 0),
            "name": item.item_name,
            "unit_price": item.rate,
            "discount": getattr(item, "discount_amount", 0) or 0,
        })

    from jo_fotara.api.ubl21_builder import build_ubl2_1_xml

    xml_str = build_ubl2_1_xml(
        invoice=invoice,
        company=company_data,
        customer=customer_data,
        items=items_list,
        invoice_counter=getattr(doc, "jofotara_counter", doc.name),
        activity_number=settings.activity_number
    )

    xml_base64 = base64.b64encode(xml_str.encode('utf-8')).decode('utf-8')

    payload = {
        "client_id": settings.client_id,
        "secret_key": settings.secret_key,
        "invoice_xml_base64": xml_base64
    }

    url = "https://backend.jofotara.gov.jo/core/invoices/"
    if settings.sandbox_mode:
        url = "https://sandbox.jofotara.gov.jo/core/invoices/"

    resp = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        res_json = resp.json()
    except Exception:
        res_json = {"error": resp.text}

    qr_code = res_json.get('qr_code')
    if qr_code:
        doc.db_set('jofotara_qr_code', qr_code)
        return {"success": True, "qr_code": qr_code}
    else:
        frappe.log_error(str(res_json), "JoFotara Failure")
        return {"success": False, "message": res_json}