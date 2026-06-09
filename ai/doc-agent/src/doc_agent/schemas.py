EXTRACTION_TOOLS = [
    {
        "name": "extract_invoice",
        "description": "Extract structured data from an invoice document",
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor_name": {"type": "string", "description": "Company issuing the invoice"},
                "vendor_address": {"type": "string"},
                "invoice_number": {"type": "string"},
                "invoice_date": {"type": "string", "description": "ISO 8601 date"},
                "due_date": {"type": "string", "description": "ISO 8601 date"},
                "currency": {"type": "string", "description": "ISO 4217 currency code"},
                "line_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "quantity": {"type": "number"},
                            "unit_price": {"type": "number"},
                            "total": {"type": "number"},
                        },
                        "required": ["description", "quantity", "unit_price", "total"],
                    },
                },
                "subtotal": {"type": "number"},
                "tax_amount": {"type": "number"},
                "tax_rate": {"type": "number", "description": "Tax rate as percentage"},
                "total_amount": {"type": "number"},
                "payment_terms": {"type": "string"},
                "bank_details": {"type": "string"},
            },
            "required": ["vendor_name", "invoice_number", "invoice_date", "total_amount", "line_items"],
        },
    },
    {
        "name": "extract_purchase_order",
        "description": "Extract structured data from a purchase order",
        "input_schema": {
            "type": "object",
            "properties": {
                "buyer_name": {"type": "string"},
                "po_number": {"type": "string"},
                "issue_date": {"type": "string", "description": "ISO 8601 date"},
                "delivery_date": {"type": "string", "description": "ISO 8601 date"},
                "vendor_name": {"type": "string"},
                "shipping_address": {"type": "string"},
                "line_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "sku": {"type": "string"},
                            "quantity": {"type": "number"},
                            "unit_price": {"type": "number"},
                        },
                        "required": ["description", "quantity"],
                    },
                },
                "total_amount": {"type": "number"},
                "payment_terms": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["buyer_name", "po_number", "issue_date", "line_items"],
        },
    },
    {
        "name": "extract_contract",
        "description": "Extract structured data from a contract document",
        "input_schema": {
            "type": "object",
            "properties": {
                "parties": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Names of all parties in the contract",
                },
                "contract_date": {"type": "string", "description": "ISO 8601 date"},
                "effective_date": {"type": "string", "description": "ISO 8601 date"},
                "expiry_date": {"type": "string", "description": "ISO 8601 date"},
                "contract_value": {"type": "number"},
                "currency": {"type": "string"},
                "summary": {"type": "string", "description": "Brief summary of the contract scope"},
                "key_terms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key terms and conditions",
                },
            },
            "required": ["parties", "contract_date", "summary"],
        },
    },
    {
        "name": "extract_receipt",
        "description": "Extract structured data from a receipt",
        "input_schema": {
            "type": "object",
            "properties": {
                "merchant_name": {"type": "string"},
                "merchant_address": {"type": "string"},
                "receipt_date": {"type": "string", "description": "ISO 8601 date"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "quantity": {"type": "number"},
                            "amount": {"type": "number"},
                        },
                        "required": ["description", "amount"],
                    },
                },
                "subtotal": {"type": "number"},
                "tax_amount": {"type": "number"},
                "total_amount": {"type": "number"},
                "payment_method": {"type": "string"},
            },
            "required": ["merchant_name", "receipt_date", "total_amount"],
        },
    },
]
