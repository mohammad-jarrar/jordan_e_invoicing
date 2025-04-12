import frappe
import xml.etree.ElementTree as ET

@frappe.whitelist()
def get_invoice_as_xml(invoice_name):
    """
    Fetches a Sales Invoice and returns it in XML format.
    """
    # Fetch the Sales Invoice document
    invoice = frappe.get_doc("Sales Invoice", invoice_name)

    # Validate that the invoice exists
    if not invoice:
        frappe.throw(f"Sales Invoice {invoice_name} not found.")

    # Create the root element for the XML
    root = ET.Element("Invoice")

    # Add basic invoice details
    ET.SubElement(root, "InvoiceNumber").text = invoice.name
    ET.SubElement(root, "InvoiceDate").text = invoice.posting_date.isoformat()
    ET.SubElement(root, "CustomerName").text = invoice.customer
    ET.SubElement(root, "GrandTotal").text = str(invoice.grand_total)
    ET.SubElement(root, "Currency").text = invoice.currency

    # Add items to the invoice
    items_element = ET.SubElement(root, "Items")
    for item in invoice.items:
        item_element = ET.SubElement(items_element, "Item")
        ET.SubElement(item_element, "ItemName").text = item.item_name
        ET.SubElement(item_element, "Quantity").text = str(item.qty)
        ET.SubElement(item_element, "Rate").text = str(item.rate)
        ET.SubElement(item_element, "Amount").text = str(item.amount)

    # Convert the XML tree to a string
    xml_data = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
    return xml_data