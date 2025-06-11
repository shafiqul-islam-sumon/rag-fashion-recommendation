
def get_metadata_display_fields():
    fields_to_display = [
        ("product_name", "Name"),
        ("brand", "Brand"),
        ("price", "Price"),
        ("season", "Season"),
        ("base_colour", "Color"),
        ("product_type", "Type"),
        #("materials_care", "Material"),
        ("year", "Year"),
        ("style", "Style"),
        ("gender", "Gender"),
        ("description", "Description"),
        #("style_note", "Style Note"),
        ("master_category", "Main Category"),
        ("sub_category", "Sub Category"),
        ("product_type", "Product Type"),
        ("usage", "Usage"),
        #("image_url", "Image URL")
    ]

    return fields_to_display


if __name__ == "__main__":
    metadata_fields = get_metadata_display_fields()
    print(metadata_fields)