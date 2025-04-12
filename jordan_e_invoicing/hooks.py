app_name = "jordan_e_invoicing"
app_title = "Jordan E-Invoicing"
app_publisher = "Globally for information technology and multimedia"
app_description = "Integration with Jordan E-Invoicing (JoFotara)"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@gitmm.com"
app_license = "MIT"

# Include Doctypes in the module
fixtures = [
    {"dt": "DocType", "filters": [["module", "=", "Jordan E-Invoicing"]]} ,
    {"dt": "Module Def", "filters": [["module_name", "=", "Jordan E-Invoicing"]]}
]

# Link JavaScript to Sales Invoice
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js"
}
app_include_js = "/assets/jordan_e_invoicing/js/sales_invoice.js"
after_install = "jordan_e_invoicing.install.create_e_invoicing_settings"
