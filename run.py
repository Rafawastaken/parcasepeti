from bs4 import BeautifulSoup as sp, XMLParsedAsHTMLWarning
import requests
import json
import warnings

def get_data(link: str) -> dict:
    r = requests.get(link)
    print(f"{r.status_code} - {link}")
    soup = sp(r.text, "lxml")

    container = soup.find("div", class_="summary")
    product_id = container.find(class_ = 'wd-product-info').get("data-product-id")
    product_title = container.find(class_ = 'product_title').text.replace("\n", "")

    product_info_raw = str(container.find(class_='woocommerce-product-details__short-description').find("p")).split(" : ")
    product_code = product_info_raw[1].strip().replace("</p>", "").split("  ")[0]
    product_partnumber = product_info_raw[-1].strip().replace("</p>", "")
    product_price = container.find(class_ = 'woocommerce-Price-amount amount').text
    product_stock = container.find("p", class_ = "stock").text.strip().lower()
    if product_stock == "stokta":
        product_stock = True
    else :
        product_stock = False

    product_images = []
    product_images_container = soup.find(class_ = "woocommerce-product-gallery__wrapper").find_all("figure")
    for product_image in product_images_container:
        image_src = product_image.get("data-thumb")
        product_images.append(image_src)

    product_description_html = str(soup.find("div", {"data-accordion-index": "description"})).replace("  ", "")

    product_attributes = []
    product_attributes_container = soup.find("table", {"class": "woocommerce-product-attributes"}).find_all("tr")
    for attribute in product_attributes_container:
        attribute_title = attribute.find("th").text.replace("\n", "").strip()
        attribute_value = attribute.find("td").text.replace("\n", "").strip()
        product_attributes.append({
            "attribute_title": attribute_title,
            "attribute_value": attribute_value,
        })

    product_info = {
        "product_id": product_id,
        "product_title": product_title,
        "product_code": product_code,
        "product_partnumber": product_partnumber,
        "product_price": product_price,
        "product_stock": product_stock,
        "product_description_html": product_description_html,
        "product_attributes": product_attributes,
        "product_images": product_images,
    }

    return product_info

def main():
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

    sitemaps = [
        "https://www.parcasepeti.com.tr/product-sitemap1.xml",
        "https://www.parcasepeti.com.tr/product-sitemap2.xml",
        "https://www.parcasepeti.com.tr/product-sitemap3.xml",
        "https://www.parcasepeti.com.tr/product-sitemap4.xml",
        "https://www.parcasepeti.com.tr/product-sitemap5.xml",
    ]

    final_links = []
    for sitemap in sitemaps:
        response = requests.get(sitemap)
        soup = sp(response.text, "lxml")  # using XML parser

        loc_tags = soup.find_all("loc")
        for tag in loc_tags:
            final_links.append(tag.text.strip())

    all_products = []
    for enum, link in enumerate(final_links):
        print(f"[{enum}/{len(final_links)}] {link}]")
        try:
            product_info = get_data(link)
            with open("completed.txt", "a") as file:
                file.write(link + "\n")
            all_products.append(product_info)
            print(f"\t{product_info.get("product_title")} - encontrado")
        except Exception as e:
            with open("error.txt", "a") as file:
                file.write(link + "\n")
            print(f"\tErro: {link}")
            continue

        with open("final.json", "w", encoding="utf-8") as file:
            json.dump(all_products, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()