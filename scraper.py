import string
import random
import json
import traceback
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    ElementNotInteractableException,
)

import config as cfg
from utils import WriteProductsJson


def get_current_time():
    return datetime.datetime.now()


class GetCategories:
    def __init__(self):
        def get_parent_cat_links():
            print(
                f"{get_current_time()} Collecting parent categories links...",
                flush=True,
            )
            try:
                link_lis = WebDriverWait(browser, 20).until(
                    ec.presence_of_all_elements_located(
                        (By.CLASS_NAME, "menu-category")
                    )
                )

                parents = []

                for li in link_lis:
                    try:
                        parent_cat_link = li.find_element_by_tag_name(
                            "a"
                        ).get_attribute("href")

                        if (
                            "stories" not in parent_cat_link
                            and "new-arrivals" not in parent_cat_link
                            and "gift-ideas" not in parent_cat_link
                            and "recipes" not in parent_cat_link
                            and "business" not in parent_cat_link
                        ):
                            parents.append(parent_cat_link)
                            print(
                                f"{get_current_time()} Collected: {parent_cat_link}",
                                flush=True,
                            )
                        else:
                            print(
                                f"{get_current_time()} Ignoring: {parent_cat_link}",
                                flush=True,
                            )
                    except AttributeError as ae:
                        print(get_current_time(), " ", ae, flush=True)
                    except NoSuchElementException as no_element:
                        print(get_current_time(), " ", no_element, flush=True)

                print(f"{get_current_time()} Done!", flush=True)
                print("--- --- ---", flush=True)
                return parents

            except TimeoutException:
                print(f"{get_current_time()} Timed out.", flush=True)
                browser.quit()
                quit()

        def get_cat_links():
            def if_children(url):
                print(
                    f"{get_current_time()} Checking for child categories: {url}",
                    flush=True,
                )
                try:
                    child_cats = WebDriverWait(browser, 5).until(
                        ec.presence_of_all_elements_located((By.CLASS_NAME, "cat-list"))
                    )
                    print(
                        f"{get_current_time()} Child categories have been found.",
                        flush=True,
                    )
                    ch = []
                    for c in child_cats:
                        ch.append(c.get_attribute("href"))

                    return ch
                except TimeoutException:
                    print(
                        f"{get_current_time()} No child categories found.", flush=True
                    )
                    return None

            def get_links():
                cat_links = WebDriverWait(browser, 10).until(
                    ec.presence_of_all_elements_located(
                        (By.CLASS_NAME, "subcategory-container")
                    )
                )

                categories = []

                for cl in cat_links:
                    try:
                        categories.append(cl.get_attribute("href"))
                    except NoSuchElementException as no_element:
                        print(no_element, flush=True)
                    except AttributeError as ae:
                        print(ae, flush=True)
                return categories

            print(
                f"{get_current_time()} Collecting categories: {parent_link}", flush=True
            )
            print("***", flush=True)
            browser.get(parent_link)

            collected_links = []
            try:
                links_to_check = get_links()

                for link in links_to_check:
                    browser.get(link)
                    print(
                        f"{get_current_time()} Collecting data from {link}", flush=True
                    )
                    children = if_children(url=link)
                    if children is None:
                        collected_links.append(link)
                        print(f"{get_current_time()} Added {link}", flush=True)
                    else:
                        for child in children:
                            collected_links.append(child)
                        print(
                            f"{get_current_time()} Child categories have been added.",
                            flush=True,
                        )
            except TimeoutException:
                print(f"{get_current_time()} No categories inside parent.", flush=True)
                children = if_children(url=parent_link)
                if children is None:
                    collected_links.append(parent_link)
                    print(f"{get_current_time()} Added {parent_link}", flush=True)
                else:
                    for child in children:
                        collected_links.append(child)
                    print(
                        f"{get_current_time()} Child categories have been added.",
                        flush=True,
                    )

            print(f"{get_current_time()} Done!", flush=True)
            print("--- --- ---", flush=True)
            return collected_links

        def write_json(cat_dict):
            json_data = json.dumps(cat_dict, indent=2, ensure_ascii=False)
            with open("categories.json", "w+") as json_file:
                json_file.write(json_data)

        options = Options()
        options.add_argument(f"--user-agent={cfg.request_data['user_agent']}")
        options.headless = True
        browser = webdriver.Chrome(
            executable_path=cfg.webdriver["path"], options=options
        )
        browser.set_window_size("1366", "768")
        browser.get(cfg.urls["category"])

        results = []

        parent_links = get_parent_cat_links()
        for parent_link in parent_links:
            fetched_links = get_cat_links()
            for fl in fetched_links:
                if fl not in results:
                    results.append(fl)

        print(f"{get_current_time()} Categories have been collected.", flush=True)
        results_dicts = []
        for r in results:
            results_dicts.append(dict(cat=r, cat_id=1))

        browser.quit()

        write_json(cat_dict=results_dicts)

        print(f"{get_current_time()} Categories has ben written!", flush=True)
        print("*** *** *** *** *** *** ***", flush=True)


class GetProductLinks:
    """Из-за StaleElementReferenceException, появляющегося по непонятным
    причинам после загрузки каждой следуюший странички, приходится выполнять
    перезапуск браузера."""

    def __init__(self, category):
        def get_links():
            def scroll_to_last_product(product):
                print(f"{get_current_time()} Scrolling...", flush=True)
                action.move_to_element(product).perform()

            product_links = []

            while True:
                len_in_beginning = len(product_links)

                product_uls = WebDriverWait(browser, 10).until(
                    ec.presence_of_all_elements_located((By.CLASS_NAME, "photo-slider"))
                )

                scroll_to_last_product(product_uls[-1])

                for product_ul in product_uls:
                    try:
                        link_tag = product_ul.find_element_by_tag_name("a")
                        cat_url = link_tag.get_attribute("href")
                        if cat_url not in product_links:
                            product_links.append(cat_url)
                    except NoSuchElementException as no_element:
                        print(no_element, flush=True)
                        pass
                current_len = len(product_links)

                if len_in_beginning == current_len:
                    print(
                        f"{get_current_time()} "
                        f"{str(current_len)} products have been collected.",
                        flush=True,
                    )
                    break

            return product_links

        options = Options()
        options.add_argument(f"--user-agent={cfg.request_data['user_agent']}")
        options.headless = True
        browser = webdriver.Chrome(
            executable_path=cfg.webdriver["path"], options=options
        )
        action = ActionChains(browser)
        browser.set_window_size("1366", "768")

        category_url = category["cat"]
        print(
            f"{get_current_time()} Collecting products in category: {category_url}",
            flush=True,
        )
        product_dicts = []
        try:
            browser.get(category_url)

            links = get_links()

            browser.quit()

            product_dicts = []

            for link in links:
                product_dicts.append(
                    dict(product_link=link, cat_url=category_url, cat_id=category["cat_id"])
                )

            WriteProductsJson(product_dicts)
            print(f"{get_current_time()} Written.", flush=True)
            print("--- --- ---", flush=True)
        except WebDriverException as webdriver_exception:
            print(webdriver_exception)
        except Exception as e:
            print(e)

        self.dicts = product_dicts


class GetProductData:
    def __init__(self, product):
        def close_popups():
            to_close = browser.find_elements_by_class_name("close-dialog")
            for i in to_close:
                try:
                    i.click()
                except StaleElementReferenceException:
                    pass
                except ElementClickInterceptedException:
                    pass
                except ElementNotInteractableException:
                    pass

        def colors():
            try:
                WebDriverWait(browser, 5).until(
                    ec.presence_of_element_located(
                        (By.CLASS_NAME, "select-color-container")
                    )
                )
                return True
            except TimeoutException:
                return False

        def get_current_color():
            color_container = browser.find_element_by_class_name(
                "select-color-container"
            )
            try:
                current_clr = (
                    color_container.find_element_by_class_name("on")
                    .find_element_by_tag_name("img")
                    .get_attribute("title")
                )
            except NoSuchElementException:
                current_clr = None
            return current_clr

        def generate_product_ref():
            def generate():
                digits = string.digits
                try:
                    with open("./ref_codes.txt", "r") as txt_file:
                        text_data = txt_file.readlines()

                    existing_codes = []
                    for t in text_data:
                        existing_codes.append(t.replace("\n", ""))
                except FileNotFoundError:
                    existing_codes = []

                char_num = 1
                ref_code = "".join(random.choice(digits) for __ in range(char_num))
                while ref_code in existing_codes:
                    char_num = char_num + 1
                    ref_code = "".join(random.choice(digits) for __ in range(char_num))

                return int(ref_code)

            value = generate()
            with open("./ref_codes.txt", "a+") as text_file:
                text_file.write(f"{value}\n")

            return value

        def get_art():
            return browser.find_element_by_class_name("referencia").text.strip()

        def get_name():
            name_div = browser.find_element_by_class_name("header")

            return name_div.find_element_by_tag_name("span").text

        def get_pictures():
            imgs = []
            image_tags = WebDriverWait(browser, 5).until(
                ec.visibility_of_all_elements_located((By.CLASS_NAME, "show-zoom"))
            )
            for image_tag in image_tags:
                imgs.append(image_tag.get_attribute("href"))
            return imgs

        def get_description():
            description_div = browser.find_element_by_id(
                "product-description-paragraphs"
            )
            return description_div.text.strip()

        def get_sizes():
            def sold_out(element):
                if "inactive sold-out" in element.get_attribute("class"):
                    return True
                else:
                    return False

            def get_size_name(element):
                spans = element.find_elements_by_tag_name("span")
                for span in spans:
                    if span.get_attribute("ng-if") == "::size.description":
                        return span.text

            def get_dimensions(element):
                dims = []
                tds = element.find_elements_by_tag_name("td")
                for td in tds:
                    if (
                        td.get_attribute("ng-if")
                        == "::itxProductAddToCartSelectorCtrl.showDimensions"
                    ):
                        dims.append(td.text.replace("cm", ""))

                if len(dims) > 0:
                    return "x".join(dims)
                else:
                    spans = element.find_elements_by_tag_name("span")
                    for span in spans:
                        if (
                            span.get_attribute("ng-if")
                            == "::(size.displayName && size.description)"
                            or span.get_attribute("ng-if")
                            == "::(size.displayName && !size.description)"
                        ):
                            return span.text

            def get_price(element):
                try:
                    return float(
                        element.find_element_by_class_name("price")
                        .text.replace("€", "")
                        .strip()
                        .replace(",", ".")
                    )
                except NoSuchElementException:
                    return float(
                        browser.find_element_by_class_name("price")
                        .text.replace("€", "")
                        .strip()
                        .replace(",", ".")
                    )

            sizes_dicts = []
            sizes_parent_tags = browser.find_elements_by_tag_name("tr")
            for sizes_parent_tag in sizes_parent_tags[1:]:
                if sold_out(sizes_parent_tag) is False:
                    size_name = get_size_name(sizes_parent_tag)
                    size_dimensions = get_dimensions(sizes_parent_tag)
                    size_price = get_price(sizes_parent_tag)

                    sizes_dicts.append(
                        dict(
                            size_name=size_name,
                            size_dimensions=size_dimensions,
                            size_price=size_price,
                        )
                    )
            return sizes_dicts

        def get_materials():
            info_btn = browser.find_element_by_class_name("button-mas-info")
            try:
                info_btn.click()
            except ElementClickInterceptedException:
                close_popups()
                info_btn.click()

            comps = []

            for i in browser.find_elements_by_class_name("compo"):
                comps.append(i.text)

            close_popups()

            if len(comps) > 0:
                return ", ".join(comps)
            else:
                return None

        options = Options()
        options.add_argument(f"--user-agent={cfg.request_data['user_agent']}")
        options.headless = True
        browser = webdriver.Chrome(
            executable_path=cfg.webdriver["path"], options=options
        )
        browser.set_window_size("1920", "1080")

        url = product["product_link"]
        cat = product["cat_id"]
        print(f"{get_current_time()} Collecting data from {url}", flush=True)
        browser.get(url)

        results = []

        if colors() is True:
            try:
                try:
                    browser.find_element_by_id("onetrust-button-group-parent").click()
                except Exception as e:
                    print(e)

                def get_colors_list():
                    color_container = browser.find_element_by_class_name(
                        "select-color-container"
                    )
                    return color_container.find_elements_by_tag_name("a")

                colors = get_colors_list()
                for color in colors:
                    attempts = 0
                    while attempts < 6:
                        try:
                            color.click()
                            break
                        except ElementClickInterceptedException:
                            close_popups()
                            color.click()
                        attempts = attempts + 1

                    current_color = get_current_color()
                    ref = generate_product_ref()
                    name = get_name()
                    art = get_art()
                    pictures = get_pictures()
                    description = get_description()
                    sizes = get_sizes()
                    materials = get_materials()

                    results_dict = dict(
                        cat_id=cat,
                        ref=ref,
                        color=current_color,
                        name=name,
                        art=art,
                        pictures=pictures,
                        description=description,
                        sizes=sizes,
                        materials=materials,
                    )

                    results.append(results_dict)

            except WebDriverException as webdriver_exception:
                traceback.print_exc()
                print(get_current_time(), webdriver_exception, flush=True)
            except Exception as e:
                print(e)

        else:
            try:
                try:
                    browser.find_element_by_id("onetrust-button-group-parent").click()
                except Exception as e:
                    print(e)
                ref = generate_product_ref()
                name = get_name()
                art = get_art()
                pictures = get_pictures()
                description = get_description()
                sizes = get_sizes()
                materials = get_materials()
                print(materials)

                results_dict = dict(
                    cat_id=cat,
                    ref=ref,
                    color=None,
                    name=name,
                    art=art,
                    pictures=pictures,
                    description=description,
                    sizes=sizes,
                    materials=materials,
                )

                results.append(results_dict)

            except WebDriverException as webdriver_exception:
                print(get_current_time(), webdriver_exception, flush=True)
            except Exception as e:
                print(e)

        browser.quit()
        print(f"{get_current_time()} Product data has been collected!", flush=True)
        print("--- --- ---", flush=True)
        self.results = results
