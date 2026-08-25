PRODUCT_POLICY_MAPPING = {
    "iPhone 15": "Telefon",
    "bilgisayar": "Bilgisayar",
    "kalem": "Kırtasiye"
}


def get_policy_category(
    product_name: str
):
    return PRODUCT_POLICY_MAPPING.get(
        product_name
    )