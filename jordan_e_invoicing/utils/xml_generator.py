import xml.etree.ElementTree as ET

def get_invoice_type_code(invoice_type, payment_method):
    if invoice_type == "Sales":
        return "388" if payment_method in ["Cash", "Receivable"] else None
    elif invoice_type == "Credit":
        return "381" if payment_method in ["Cash", "Receivable"] else None
    else:
        raise ValueError("Invalid invoice type or payment method")

def create_invoice_xml(invoice_data):
    # Validate mandatory fields
    mandatory_fields = ["invoice_no", "uuid", "issue_date", "payment_method", 
                        "currency", "tax_currency", "seller_tin", "seller_name", 
                        "buyer_tin", "buyer_name", "items", "tax_amount"]
    for field in mandatory_fields:
        if field not in invoice_data or not invoice_data[field]:
            raise ValueError(f"Mandatory field '{field}' is missing or empty.")

    # Get the invoice type code
    invoice_type_code = get_invoice_type_code(
        invoice_data["invoice_type"], 
        invoice_data["payment_method"]
    )

    # Root element with namespaces
    root = ET.Element("Invoice", {
        "xmlns": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
        "xmlns:cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "xmlns:cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "xmlns:ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    })

    # Add basic invoice details
    ET.SubElement(root, "cbc:ID").text = invoice_data["invoice_no"]
    ET.SubElement(root, "cbc:UUID").text = invoice_data["uuid"]
    ET.SubElement(root, "cbc:IssueDate").text = invoice_data["issue_date"]
    ET.SubElement(root, "cbc:InvoiceTypeCode", {"name": invoice_data["payment_method"]}).text = invoice_type_code
    ET.SubElement(root, "cbc:Note").text = invoice_data["note"]
    ET.SubElement(root, "cbc:DocumentCurrencyCode").text = invoice_data["currency"]
    ET.SubElement(root, "cbc:TaxCurrencyCode").text = invoice_data["tax_currency"]

    # Add seller details
    supplier_party = ET.SubElement(root, "cac:AccountingSupplierParty")
    party = ET.SubElement(supplier_party, "cac:Party")
    tax_scheme = ET.SubElement(party, "cac:PartyTaxScheme")
    ET.SubElement(tax_scheme, "cbc:CompanyID").text = invoice_data["seller_tin"]
    ET.SubElement(tax_scheme, "cbc:RegistrationName").text = invoice_data["seller_name"]
    ET.SubElement(tax_scheme, "cbc:ID").text = "VAT"

    # Add buyer details
    customer_party = ET.SubElement(root, "cac:AccountingCustomerParty")
    customer = ET.SubElement(customer_party, "cac:Party")
    ET.SubElement(customer, "cbc:ID", {"schemeID": "TIN"}).text = invoice_data["buyer_tin"]
    ET.SubElement(customer, "cbc:RegistrationName").text = invoice_data["buyer_name"]

    # Add items to the invoice
    invoice_lines = ET.SubElement(root, "cac:InvoiceLine")
    for item in invoice_data["items"]:
        line_item = ET.SubElement(invoice_lines, "cac:Item")
        ET.SubElement(line_item, "cbc:Name").text = item["item_name"]
        ET.SubElement(line_item, "cbc:Quantity").text = str(item["qty"])
        ET.SubElement(line_item, "cbc:Price").text = str(item["rate"])
        ET.SubElement(line_item, "cbc:Amount").text = str(item["amount"])

    # Add additional document reference
    if "additional_doc_id" in invoice_data and "additional_doc_type" in invoice_data:
        additional_doc_ref = ET.SubElement(root, "cac:AdditionalDocumentReference")
        ET.SubElement(additional_doc_ref, "cbc:ID").text = invoice_data["additional_doc_id"]
        ET.SubElement(additional_doc_ref, "cbc:DocumentType").text = invoice_data["additional_doc_type"]

    # Add tax details
    tax_total = ET.SubElement(root, "cac:TaxTotal")
    ET.SubElement(tax_total, "cbc:TaxAmount").text = str(invoice_data["tax_amount"])

    # Convert XML to string
    xml_str = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
    return xml_str
