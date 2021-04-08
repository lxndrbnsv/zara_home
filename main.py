from utils import ReadCategories, ReadProducts, WriteResults
from scraper import GetCategories, GetProductLinks, GetProductData


if __name__ == "__main__":
    categories = ReadCategories().cat_dicts
    for category in categories:
        products = ReadProducts().dicts
        for product in products:
            WriteResults(GetProductData(product).results)
