import frappe
import json
import base64
import requests
from lxml import etree
from lxml.etree import XMLSyntaxError
from datetime import datetime
from pathlib import Path
from io import BytesIO
from frappe import _

# Load city codes
CITY_CODES = {
    "JO-AJ": "Ajloun",
    "JO-AM": "Amman",
    "JO-AQ": "Aqaba",
    "JO-BA": "Balqa",
    "JO-IR": "Irbid",
    "JO-JA": "Jerash",
    "JO-KA": "Karak",
    "JO-MA": "Mafraq",
    "JO-MD": "Madaba",
    "JO-MN": "Ma'an",
    "JO-TA": "Tafilah",
    "JO-ZQ": "Zarqa"
}

def generate_invoice_xml(doc):
    """
    Generate complete UBL 2.1 XML for both regular and credit invoices
    """
    NSMAP = {
        None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    }

    root = etree.Element("Invoice", nsmap=NSMAP)
    
    # ========== Basic Information Section ==========
    add_element(root, "cbc:ProfileID", "reporting:1.0")
    add_element(root, "cbc:ID", doc.name)
    add_element(root, "cbc:UUID", doc.jofotara_uuid)
    add_element(root, "cbc:IssueDate", format_date(doc.posting_date))
    
    # Invoice Type Code
    inv_type_code = "381" if doc.is_return else "388"
    inv_type = add_element(root, "cbc:InvoiceTypeCode", inv_type_code)
    inv_type.set("name", "022" if doc.is_return else "012")
    
    add_element(root, "cbc:DocumentCurrencyCode", "JOD")
    add_element(root, "cbc:TaxCurrencyCode", "JOD")

    # ========== Original Invoice Reference (Credit Notes) ==========
    if doc.is_return:
        billing_ref = add_element(root, "cac:BillingReference")
        original_ref = add_element(billing_ref, "cac:InvoiceDocumentReference")
        original_inv = frappe.get_doc("Sales Invoice", doc.return_against)
        add_element(original_ref, "cbc:ID", original_inv.name)
        add_element(original_ref, "cbc:UUID", original_inv.jofotara_uuid)
        add_element(original_ref, "cbc:DocumentDescription", 
                  f"Original Invoice Total: {original_inv.grand_total} JOD")

    # ========== Seller Information ==========
    supplier_party = add_element(root, "cac:AccountingSupplierParty")
    party = add_element(supplier_party, "cac:Party")
    
    # Postal Address
    postal_address = add_element(party, "cac:PostalAddress")
    add_element(postal_address, "cac:Country/cbc:IdentificationCode", "JO")
    
    # Tax Scheme
    party_tax = add_element(party, "cac:PartyTaxScheme")
    add_element(party_tax, "cbc:CompanyID", frappe.get_value("Company", doc.company, "tax_id"))
    tax_scheme = add_element(party_tax, "cac:TaxScheme")
    add_element(tax_scheme, "cbc:ID", "VAT")
    
    # Legal Entity
    legal_entity = add_element(party, "cac:PartyLegalEntity")
    add_element(legal_entity, "cbc:RegistrationName", doc.company)

    # ========== Buyer Information ==========
    customer_party = add_element(root, "cac:AccountingCustomerParty")
    party = add_element(customer_party, "cac:Party")
    
    # Identification
    party_id = add_element(party, "cac:PartyIdentification")
    id_type, id_value = get_buyer_identification(doc)
    add_element(party_id, "cbc:ID", id_value, schemeID=id_type)
    
    # Address
    postal_address = add_element(party, "cac:PostalAddress")
    add_element(postal_address, "cbc:PostalZone", doc.postal_code)
    add_element(postal_address, "cbc:CountrySubentityCode", get_city_code(doc.city))
    add_element(postal_address, "cac:Country/cbc:IdentificationCode", "JO")
    
    # Tax Scheme
    party_tax = add_element(party, "cac:PartyTaxScheme")
    add_element(party_tax, "cbc:CompanyID", "1")  # Default as per Jordanian spec
    tax_scheme = add_element(party_tax, "cac:TaxScheme")
    add_element(tax_scheme, "cbc:ID", "VAT")
    
    # Legal Entity
    legal_entity = add_element(party, "cac:PartyLegalEntity")
    add_element(legal_entity, "cbc:RegistrationName", doc.customer_name)
    
    # Contact
    contact = add_element(customer_party, "cac:AccountingContact")
    add_element(contact, "cbc:Telephone", doc.contact_mobile)

    # ========== Invoice Lines ==========
    for item in doc.items:
        add_invoice_line(root, item, is_return=doc.is_return)

    # ========== Totals Section ==========
    # Allowance Charge (Discounts)
    allowance_charge = add_element(root, "cac:AllowanceCharge")
    add_element(allowance_charge, "cbc:ChargeIndicator", "false")
    add_element(allowance_charge, "cbc:AllowanceChargeReason", "Discount")
    add_element(allowance_charge, "cbc:Amount", 
               abs(doc.discount_amount) if doc.is_return else doc.discount_amount, 
               currencyID="JOD")

    # Tax Total
    tax_total = add_element(root, "cac:TaxTotal")
    total_tax = abs(doc.total_taxes_and_charges) if doc.is_return else doc.total_taxes_and_charges
    add_element(tax_total, "cbc:TaxAmount", total_tax, currencyID="JOD")

    # Legal Monetary Total
    legal_total = add_element(root, "cac:LegalMonetaryTotal")
    add_element(legal_total, "cbc:TaxExclusiveAmount", 
               abs(doc.net_total) if doc.is_return else doc.net_total, 
               currencyID="JOD")
    add_element(legal_total, "cbc:TaxInclusiveAmount", 
               abs(doc.grand_total) if doc.is_return else doc.grand_total, 
               currencyID="JOD")
    add_element(legal_total, "cbc:AllowanceTotalAmount", 
               abs(doc.discount_amount) if doc.is_return else doc.discount_amount, 
               currencyID="JOD")
    add_element(legal_total, "cbc:PayableAmount", 
               -abs(doc.grand_total) if doc.is_return else doc.grand_total, 
               currencyID="JOD")

    xml_data = etree.tostring(root, pretty_print=True, encoding="UTF-8", xml_declaration=True)
    return validate_xml(xml_data)

def add_invoice_line(parent, item, is_return=False):
    """
    Create complete InvoiceLine element for both regular and credit invoices
    """
    line = add_element(parent, "cac:InvoiceLine")
    
    # Line ID
    add_element(line, "cbc:ID", str(item.idx))
    
    # Quantity
    quantity = abs(item.qty) if is_return else item.qty
    add_element(line, "cbc:InvoicedQuantity", quantity, unitCode="PCE")
    
    # Line Total
    line_total = abs(item.amount) if is_return else item.amount
    add_element(line, "cbc:LineExtensionAmount", line_total, currencyID="JOD")
    
    # Tax Total
    tax_total = add_element(line, "cac:TaxTotal")
    tax_amount = abs(item.tax_amount) if is_return else item.tax_amount
    add_element(tax_total, "cbc:TaxAmount", tax_amount, currencyID="JOD")
    
    # Tax Subtotal
    tax_subtotal = add_element(tax_total, "cac:TaxSubtotal")
    add_element(tax_subtotal, "cbc:TaxableAmount", line_total, currencyID="JOD")
    add_element(tax_subtotal, "cbc:TaxAmount", tax_amount, currencyID="JOD")
    
    # Tax Category
    tax_category = add_element(tax_subtotal, "cac:TaxCategory")
    tax_code = "S" if item.tax_rate > 0 else "Z"
    add_element(tax_category, "cbc:ID", tax_code, 
               schemeAgencyID="6", 
               schemeID="UN/ECE 5305")
    add_element(tax_category, "cbc:Percent", item.tax_rate)
    
    # Tax Scheme
    tax_scheme = add_element(tax_category, "cac:TaxScheme")
    add_element(tax_scheme, "cbc:ID", "VAT", 
               schemeAgencyID="6", 
               schemeID="UN/ECE 5153")
    
    # Item Information
    item_info = add_element(line, "cac:Item")
    add_element(item_info, "cbc:Name", item.item_name)
    
    # Price Information
    price = add_element(line, "cac:Price")
    add_element(price, "cbc:PriceAmount", 
               abs(item.rate) if is_return else item.rate, 
               currencyID="JOD")
    
    # Discounts
    if item.discount_amount:
        allowance = add_element(price, "cac:AllowanceCharge")
        add_element(allowance, "cbc:ChargeIndicator", "false")
        add_element(allowance, "cbc:AllowanceChargeReason", "DISCOUNT")
        add_element(allowance, "cbc:Amount", 
                   abs(item.discount_amount) if is_return else item.discount_amount, 
                   currencyID="JOD")

def validate_xml(xml_data):
    """
    Validate XML against UBL 2.1 XSD schema
    """
    xsd_path = Path(__file__).parent / "templates" / "UBL-Invoice-2.1.xsd"
    
    try:
        schema = etree.XMLSchema(file=str(xsd_path))
        parser = etree.XMLParser(schema=schema)
        etree.fromstring(xml_data, parser)
        return xml_data
    except XMLSyntaxError as e:
        frappe.log_error(_("XML Validation Failed"), str(e))
        frappe.throw(_("Generated XML failed validation: {0}").format(str(e)))
    except Exception as e:
        frappe.log_error(_("XML Validation Error"), str(e))
        frappe.throw(_("Error validating XML: {0}").format(str(e)))

def add_element(parent, tag, text=None, **attrs):
    """
    Helper to create nested elements with namespaces
    """
    ns_map = {
        'cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        'cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    }
    
    parts = tag.split('/')
    current_element = parent
    
    for part in parts:
        prefix, name = part.split(':') if ':' in part else (None, part)
        ns_uri = ns_map.get(prefix)
        
        if ns_uri:
            element = etree.SubElement(current_element, f"{{{ns_uri}}}{name}")
        else:
            element = etree.SubElement(current_element, name)
        
        current_element = element
    
    if text is not None:
        current_element.text = str(text)
    
    for attr, value in attrs.items():
        current_element.set(attr, str(value))
    
    return current_element

def get_buyer_identification(doc):
    """
    Determine buyer identification type and value
    Returns: (schemeID, identification_value)
    """
    if doc.tax_id:
        return "TN", doc.tax_id
    elif doc.national_id:
        return "NIN", doc.national_id
    else:
        return "PN", doc.passport_number or "1"

def format_date(date_str):
    """
    Convert date to dd-mm-yyyy format
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
    except:
        return datetime.now().strftime("%d-%m-%Y")

def get_city_code(city_name):
    """
    Map city name to Jordanian code
    """
    reverse_map = {v: k for k, v in CITY_CODES.items()}
    return reverse_map.get(city_name, "JO-AM")