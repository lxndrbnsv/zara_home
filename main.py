import sys

from utils import ReadCategories, ReadProducts, WriteResults
from scraper import GetCategories, GetProductLinks, GetProductData


# sys.stdout = open("logs.log", "w")
# sys.stderr = open("logs.log", "w")

if __name__ == "__main__":
    categories = ReadCategories().cat_dicts
    for category in categories:
        GetProductLinks(category)
        """products = ReadProducts().dicts
        for product in products:
            WriteResults(GetProductData(product).results)"""
