COLUMN_ALIASES = {
    "name": ["name", "contact_person","contact person","person_name", "person name"],
    "org_name" : ["org_name","org name", "company_name","company name","organizaion name","organization_name"],
    "designation": ["designation", "title", "job title"],
    "contact_number": ["contact number", "mobile", "phone", "number"],
    "mail_id": ["email", "mail id", "email id"],
    "location": ["address", "location", "area", "place","Address"]
}

def auto_map_columns(df, alias_dict):
    col_map = {}
    for field, aliases in alias_dict.items():
        for alias in aliases:
            for col in df.columns:
                if alias.strip().lower() == col.strip().lower():
                    col_map[col] = field
                    break
    return df.rename(columns=col_map)