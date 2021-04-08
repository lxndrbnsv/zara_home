import json


class ReadCategories:
    def __init__(self):
        with open("./categories.json", "r") as json_file:
            categories = json.load(json_file)

        cat_list = []

        for c in categories:
            cat_list.append(c["cat"])

        self.categories = cat_list
        self.cat_dicts = categories


class WriteProductsJson:
    def __init__(self, dicts):
        try:
            with open("./products.json", "r") as json_file:
                existing_products = json.load(json_file)

            products = []

            for e in existing_products:
                products.append(e)
        except FileNotFoundError:
            products = []

        for product_dict in dicts:
            products.append(product_dict)
        products_to_write = json.dumps(products, indent=2, ensure_ascii=False)

        with open("./products.json", "w+") as json_file:
            json_file.write(products_to_write)


class ReadProducts:
    def __init__(self):
        with open("products.json", "r") as json_file:
            json_data = json.load(json_file)
        self.dicts = json_data


class IfDuplicates:
    def __init__(self):
        with open("products.json", "r") as json_file:
            products_dict = json.load(json_file)

        dicts_len = len(products_dict)

        links = []
        for product_dict in products_dict:
            if product_dict["product_link"] not in links:
                links.append(product_dict["product_link"])

        unique_len = len(links)

        if dicts_len - unique_len == 0:
            print("No duplicates found!", flush=True)
        else:
            print(dicts_len-unique_len, " duplicates found!")


class RemoveDuplicates:
    def __init__(self):
        with open("products.json", "r") as json_file:
            products_dict = json.load(json_file)

        links = []
        new_data = []

        for product_dict in products_dict:
            if product_dict["product_link"] not in links:
                links.append(product_dict["product_link"])
                new_data.append(product_dict)

        data_to_write = json.dumps(new_data, indent=2, ensure_ascii=False)
        with open("products.json", "w") as json_file:
            json_file.write(data_to_write)


class WriteResults:
    def __init__(self, dicts):
        try:
            with open("./results.json", "r") as json_file:
                existing_products = json.load(json_file)

            products = []

            for e in existing_products:
                products.append(e)
        except FileNotFoundError:
            products = []

        for product_dict in dicts:
            products.append(product_dict)
        products_to_write = json.dumps(products, indent=2, ensure_ascii=False)

        with open("./results.json", "w+") as json_file:
            json_file.write(products_to_write)


class DownloadPictures:
    # TODO: загрузка картинок будет производиться уже после размещения парсера
    # на сервере.
    pass
