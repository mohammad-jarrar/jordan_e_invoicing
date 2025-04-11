app_name = "jordan_e_invoicing"
app_title = "Jordan E-Invoicing"
app_publisher = "Your Name"
app_description = "Integration with Jordan E-Invoicing (JoFotara)"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "your-email@example.com"
app_license = "MIT"

# Include Doctypes in the module
fixtures = [
    {"dt": "DocType", "filters": [["module", "=", "Jordan E-Invoicing"]]}
]

# Link JavaScript to Sales Invoice
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js"
}