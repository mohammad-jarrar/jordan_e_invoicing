def get_custom_fields():
    return {
        "Sales Invoice": [
            {
                "fieldname": "jofotara_section",
                "label": "Jofotara Integration",
                "fieldtype": "Section Break",
                "insert_after": "terms"
            },
            {
                "fieldname": "jofotara_uuid",
                "label": "UUID",
                "fieldtype": "Data",
                "read_only": 1,
                "insert_after": "jofotara_section"
            },
            {
                "fieldname": "jofotara_qr_code",
                "label": "QR Code",
                "fieldtype": "Attach Image",
                "insert_after": "jofotara_uuid"
            },
            {
                "fieldname": "reason_for_return",
                "label": "Return Reason",
                "fieldtype": "Small Text",
                "insert_after": "customer",
                "depends_on": "eval:doc.is_return"
            }
        ],
        "Address": [
            {
                "fieldname": "jofotara_city_code",
                "label": "City Code",
                "fieldtype": "Select",
                "options": "\n".join(CITY_CODES.keys()),
                "insert_after": "city"
            }
        ]
    }