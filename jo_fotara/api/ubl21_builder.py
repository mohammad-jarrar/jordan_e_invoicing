from lxml import etree

def build_ubl2_1_xml(invoice, company, customer, items, invoice_counter, activity_number):
    NSMAP = {
        None: 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
    }

    root = etree.Element("Invoice", nsmap=NSMAP)
    etree.SubElement(root, "{%s}ProfileID" % NSMAP['cbc']).text = "reporting:1.0"
    etree.SubElement(root, "{%s}ID" % NSMAP['cbc']).text = invoice['id']
    etree.SubElement(root, "{%s}UUID" % NSMAP['cbc']).text = invoice['uuid']
    etree.SubElement(root, "{%s}IssueDate" % NSMAP['cbc']).text = invoice['date']
    etree.SubElement(root, "{%s}InvoiceTypeCode" % NSMAP['cbc'], name=invoice['payment_method']).text = invoice['type_code']
    if invoice.get('note'):
        etree.SubElement(root, "{%s}Note" % NSMAP['cbc']).text = invoice['note']
    etree.SubElement(root, "{%s}DocumentCurrencyCode" % NSMAP['cbc']).text = "JOD"
    etree.SubElement(root, "{%s}TaxCurrencyCode" % NSMAP['cbc']).text = "JOD"

    doc_ref = etree.SubElement(root, "{%s}AdditionalDocumentReference" % NSMAP['cac'])
    etree.SubElement(doc_ref, "{%s}ID" % NSMAP['cbc']).text = "ICV"
    etree.SubElement(doc_ref, "{%s}UUID" % NSMAP['cbc']).text = str(invoice_counter)

    supplier = etree.SubElement(root, "{%s}AccountingSupplierParty" % NSMAP['cac'])
    party = etree.SubElement(supplier, "{%s}Party" % NSMAP['cac'])
    address = etree.SubElement(party, "{%s}PostalAddress" % NSMAP['cac'])
    country = etree.SubElement(address, "{%s}Country" % NSMAP['cac'])
    etree.SubElement(country, "{%s}IdentificationCode" % NSMAP['cbc']).text = company['country']
    tax_scheme = etree.SubElement(party, "{%s}PartyTaxScheme" % NSMAP['cac'])
    etree.SubElement(tax_scheme, "{%s}CompanyID" % NSMAP['cbc']).text = company['tax_id']
    tax_scheme_type = etree.SubElement(tax_scheme, "{%s}TaxScheme" % NSMAP['cac'])
    etree.SubElement(tax_scheme_type, "{%s}ID" % NSMAP['cbc']).text = "VAT"
    legal_entity = etree.SubElement(party, "{%s}PartyLegalEntity" % NSMAP['cac'])
    etree.SubElement(legal_entity, "{%s}RegistrationName" % NSMAP['cbc']).text = company['name']

    customer_party = etree.SubElement(root, "{%s}AccountingCustomerParty" % NSMAP['cac'])
    c_party = etree.SubElement(customer_party, "{%s}Party" % NSMAP['cac'])
    party_id = etree.SubElement(c_party, "{%s}PartyIdentification" % NSMAP['cac'])
    etree.SubElement(party_id, "{%s}ID" % NSMAP['cbc'], schemeID=customer['id_type']).text = customer['id_number']
    c_address = etree.SubElement(c_party, "{%s}PostalAddress" % NSMAP['cac'])
    etree.SubElement(c_address, "{%s}PostalZone" % NSMAP['cbc']).text = customer['zip']
    etree.SubElement(c_address, "{%s}CountrySubentityCode" % NSMAP['cbc']).text = customer['city']
    c_country = etree.SubElement(c_address, "{%s}Country" % NSMAP['cac'])
    etree.SubElement(c_country, "{%s}IdentificationCode" % NSMAP['cbc']).text = customer['country']
    c_tax_scheme = etree.SubElement(c_party, "{%s}PartyTaxScheme" % NSMAP['cac'])
    etree.SubElement(c_tax_scheme, "{%s}CompanyID" % NSMAP['cbc']).text = customer['tax_id']
    c_tax_scheme_type = etree.SubElement(c_tax_scheme, "{%s}TaxScheme" % NSMAP['cac'])
    etree.SubElement(c_tax_scheme_type, "{%s}ID" % NSMAP['cbc']).text = "VAT"
    c_legal_entity = etree.SubElement(c_party, "{%s}PartyLegalEntity" % NSMAP['cac'])
    etree.SubElement(c_legal_entity, "{%s}RegistrationName" % NSMAP['cbc']).text = customer['name']
    if customer.get('phone'):
        contact = etree.SubElement(customer_party, "{%s}AccountingContact" % NSMAP['cac'])
        etree.SubElement(contact, "{%s}Telephone" % NSMAP['cbc']).text = customer['phone']

    seller_supplier = etree.SubElement(root, "{%s}SellerSupplierParty" % NSMAP['cac'])
    s_party = etree.SubElement(seller_supplier, "{%s}Party" % NSMAP['cac'])
    s_party_id = etree.SubElement(s_party, "{%s}PartyIdentification" % NSMAP['cac'])
    etree.SubElement(s_party_id, "{%s}ID" % NSMAP['cbc']).text = activity_number

    if invoice.get("total_discount"):
        allowance = etree.SubElement(root, "{%s}AllowanceCharge" % NSMAP['cac'])
        etree.SubElement(allowance, "{%s}ChargeIndicator" % NSMAP['cbc']).text = "false"
        etree.SubElement(allowance, "{%s}AllowanceChargeReason" % NSMAP['cbc']).text = "discount"
        etree.SubElement(allowance, "{%s}Amount" % NSMAP['cbc'], currencyID="JO").text = str(invoice["total_discount"])

    tax_total = etree.SubElement(root, "{%s}TaxTotal" % NSMAP['cac'])
    etree.SubElement(tax_total, "{%s}TaxAmount" % NSMAP['cbc'], currencyID="JO").text = str(invoice["tax_total"])

    legal = etree.SubElement(root, "{%s}LegalMonetaryTotal" % NSMAP['cac'])
    etree.SubElement(legal, "{%s}TaxExclusiveAmount" % NSMAP['cbc'], currencyID="JO").text = str(invoice["amount_before_discount"])
    etree.SubElement(legal, "{%s}TaxInclusiveAmount" % NSMAP['cbc'], currencyID="JO").text = str(invoice["amount_after_tax"])
    etree.SubElement(legal, "{%s}AllowanceTotalAmount" % NSMAP['cbc'], currencyID="JO").text = str(invoice["total_discount"])
    etree.SubElement(legal, "{%s}PayableAmount" % NSMAP['cbc'], currencyID="JO").text = str(invoice["amount_after_tax"])

    for idx, item in enumerate(items, 1):
        inv_line = etree.SubElement(root, "{%s}InvoiceLine" % NSMAP['cac'])
        etree.SubElement(inv_line, "{%s}ID" % NSMAP['cbc']).text = str(idx)
        etree.SubElement(inv_line, "{%s}InvoicedQuantity" % NSMAP['cbc'], unitCode="PCE").text = str(item["qty"])
        etree.SubElement(inv_line, "{%s}LineExtensionAmount" % NSMAP['cbc'], currencyID="JO").text = str(item["amount"])
        line_tax_total = etree.SubElement(inv_line, "{%s}TaxTotal" % NSMAP['cac'])
        etree.SubElement(line_tax_total, "{%s}TaxAmount" % NSMAP['cbc'], currencyID="JO").text = str(item["tax"])
        etree.SubElement(line_tax_total, "{%s}RoundingAmount" % NSMAP['cbc'], currencyID="JO").text = str(item["total_with_tax"])
        tax_sub = etree.SubElement(line_tax_total, "{%s}TaxSubtotal" % NSMAP['cac'])
        etree.SubElement(tax_sub, "{%s}TaxAmount" % NSMAP['cbc'], currencyID="JO").text = str(item["tax"])
        tax_cat = etree.SubElement(tax_sub, "{%s}TaxCategory" % NSMAP['cac'])
        etree.SubElement(tax_cat, "{%s}ID" % NSMAP['cbc'], schemeAgencyID="6", schemeID="UN/ECE 5305").text = item["tax_category"]
        etree.SubElement(tax_cat, "{%s}Percent" % NSMAP['cbc']).text = str(item["tax_percent"])
        tax_scheme = etree.SubElement(tax_cat, "{%s}TaxScheme" % NSMAP['cac'])
        etree.SubElement(tax_scheme, "{%s}ID" % NSMAP['cbc'], schemeAgencyID="6", schemeID="UN/ECE 5153").text = "VAT"
        item_node = etree.SubElement(inv_line, "{%s}Item" % NSMAP['cac'])
        etree.SubElement(item_node, "{%s}Name" % NSMAP['cbc']).text = item["name"]
        price = etree.SubElement(inv_line, "{%s}Price" % NSMAP['cac'])
        etree.SubElement(price, "{%s}PriceAmount" % NSMAP['cbc'], currencyID="JO").text = str(item["unit_price"])
        allowance_charge = etree.SubElement(price, "{%s}AllowanceCharge" % NSMAP['cac'])
        etree.SubElement(allowance_charge, "{%s}ChargeIndicator" % NSMAP['cbc']).text = "false"
        etree.SubElement(allowance_charge, "{%s}AllowanceChargeReason" % NSMAP['cbc']).text = "DISCOUNT"
        etree.SubElement(allowance_charge, "{%s}Amount" % NSMAP['cbc'], currencyID="JO").text = str(item["discount"])

    return etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf-8')