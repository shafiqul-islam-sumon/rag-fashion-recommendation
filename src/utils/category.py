import pandas as pd


def _load_category_tree(csv_path) -> dict:
    df = pd.read_csv(csv_path)
    df = df.drop_duplicates()

    category_tree = (
        df.groupby("master_category")["sub_category"]
        .apply(lambda x: sorted(set(x)))
        .to_dict()
    )
    return category_tree

def get_category_tree():
    category_dict = {
        "👜 Accessories": {
            "Accessories": "👜",
            "Bags": "🧳",
            "Belts": "🩲",
            "Cufflinks": "🧷",
            "Eyewear": "🕶️",
            "Gloves": "🧤",
            "Headwear": "🎩",
            "Jewellery": "💍",
            "Mufflers": "🧣",
            "Perfumes": "🌸",
            "Scarves": "🧣",
            "Shoe Accessories": "👞",
            "Socks": "🧦",
            "Sports Accessories": "🎽",
            "Stoles": "🧣",
            "Ties": "👔",
            "Umbrellas": "🌂",
            "Wallets": "👛",
            "Watches": "⌚",
            "Water Bottle": "🥤"
        },
        "👗 Apparel": {
            "Apparel Set": "👕",
            "Bottomwear": "👖",
            "Dress": "👗",
            "Innerwear": "🩲",
            "Loungewear and Nightwear": "🛌",
            "Saree": "👘",
            "Socks": "🧦",
            "Topwear": "👕"
        },
        "👟 Footwear": {
            "Flip Flops": "🩴",
            "Sandal": "👡",
            "Shoes": "👟"
        },
        "🎁 Free Items": {
            "Free Gifts": "🎁",
            "Vouchers": "🎟️"
        },
        "🏠 Home": {
            "Home Furnishing": "🛋️"
        },
        "💅 Personal Care": {
            "Bath and Body": "🛁",
            "Beauty Accessories": "💅",
            "Eyes": "👁️",
            "Fragrance": "🌸",
            "Hair": "💇",
            "Lips": "💄",
            "Makeup": "💋",
            "Nails": "💅",
            "Perfumes": "🌸",
            "Skin": "🧴",
            "Skin Care": "🧴"
        },
        "🏋️ Sporting Goods": {
            "Sports Equipment": "🏋️",
            "Wristbands": "🧤"
        }
    }

    return category_dict


if __name__ == "__main__":
    style_csv = "data/styles.csv"
    category_tree = _load_category_tree(style_csv)
    print(category_tree)