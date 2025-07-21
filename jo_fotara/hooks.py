app_name = "jo_fotara"
app_title = "JoFotara Integration"
app_publisher = "Your Name"
app_description = "Jordan E-Invoicing (JoFotara) integration for ERPNext"
app_icon = "octicon octicon-file-directory"
app_color = "blue"
app_email = "your@email.com"
app_license = "MIT"

doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js",
    "Credit Note": "public/js/credit_note.js"
}

fixtures = [
    {"dt": "Custom Field", "filters": [["name", "in", [
        "Customer-jofotara_tax_id",
        "Customer-jofotara_national_id",
        "Customer-jofotara_passport_no",
        "Customer-jofotara_city",
        "Customer-jofotara_state",
        "Customer-jofotara_zip"
    ]]]}
]