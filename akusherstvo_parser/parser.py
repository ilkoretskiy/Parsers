from bs4 import BeautifulSoup
import urllib.request as req
import urllib.request
import http.cookiejar
import json
import os
import pandas as pd
import logging

from selenium import webdriver


class Parser(object):
    def __init__(self, url, dump_folder):
        self._opener = None

        self._base_url = url
        self._dump_folder = dump_folder

        os.makedirs(dump_folder, exist_ok=True)
        self._init_logger(dump_folder)
        self._logger.info("Start")
        self.set_cookies_for_website(url)



    def set_cookies_for_website(self, url):
        normalized_base_url = url.replace("/", "_")
        cookies_path = "cookies_{}.json".format(normalized_base_url)

        cookies = []
        if os.path.exists(cookies_path):
            with open(cookies_path) as f:
                cookies = json.load(f)
        else:
            driver = self._launch_browser(url)
            cookies = driver.get_cookies()
            with open(cookies_path, "w") as f:
                json.dump(cookies, f)

        self._copy_cookies(cookies)

    def _launch_browser(self, url):
        driver = webdriver.Chrome()
        driver.get(url)
        return driver

    def _init_logger(self, log_filename):
        self._logger = logging.getLogger("parser")
        self._logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('{}.log'.format(log_filename))
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self._logger.addHandler(fh)
        self._logger.addHandler(ch)

    def _copy_cookies(self, cookies):
        cj = http.cookiejar.CookieJar()
        for s_cookie in cookies:
            cj.set_cookie(
                http.cookiejar.Cookie(
                    version=0
                    , name=s_cookie['name']
                    , value=s_cookie['value']
                    , port='80'
                    , port_specified=False
                    , domain=s_cookie['domain']
                    , domain_specified=True
                    , domain_initial_dot=False
                    , path=s_cookie['path']
                    , path_specified=True
                    , secure=s_cookie['secure']
                    , expires=None
                    , discard=False
                    , comment=None
                    , comment_url=None
                    , rest=None
                    , rfc2109=False
                )
            )

        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        self._opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)')]
        req.install_opener(self._opener)

    def get_bs(self, url, codec='utf8', wait=0):
        # with req.urlopen(url=url) as f:
        response = self._opener.open(url)
        #        time.sleep(wait)
        #    readed_bytes = f.read()
        readed_bytes = response.read()
        text = readed_bytes.decode(codec)
        bs = BeautifulSoup(text)
        return bs

    def parse_comment(self, html_comment):
        comment = html_comment
        processed_comment = {}
        user_name = comment.find("a", attrs={"class": "comments-item__user"}).text.strip()
        time = comment.find("time", attrs={"class": "comments-item__time"}).text.strip()

        comment_titles = comment("strong", "comments-item__title")
        if len(comment_titles) == 0 or ("Оценка товара" in comment_titles[0].text and len(comment_titles) == 1):
            text = comment("p", "comments-item__text")[0].text
            processed_comment["Коммментарий:"] = text
        else:
            for item in comment_titles:
                if not "Оценка товара" in item.text:
                    # print(item.text, )
                    processed_comment[item.text] = item.findNext("p").text

        result = {
            "username": user_name,
            "time": time,
            "review": processed_comment
        }

        return result

    def get_color_photos(self, item_page):
        color_photos = []
        for img in item_page("div", "itemImg")[0]("img"):
            #due to the fact that i receive different image links from what i have in a browser
            #i want to update links manually to get always big images
            src = img["src"]
            src = src.replace("_b.", ".").replace("_medium", "").replace("//", "")
            #using get because some imgs don't contain title prop
            title = img.get("title")
            color_photos.append((src, title))
        return color_photos


    def get_more_photos(self, item_page):
        more_photos_el = item_page("ul", attrs={"id": "multimedia-carousel"})

        more_photos = []
        if len(more_photos_el) > 0:
            more_photos = [img["src"] for img in more_photos_el[0]("img")]
            more_photos = [photo_url.replace("//", "").replace("_s.", ".") for photo_url in more_photos]
        return more_photos

    def get_item_info(self, item_page, item_url):
        price = item_page.find(name="span", attrs={"class": "valuePrice"}).text
        price = price.replace(" ", "")
        title = item_page.find(name="h1", attrs={"class": "title-page"}).text
        in_stock = item_page.find(name="span", attrs={"class": "in_stock"}).text.strip()

        votes_count = item_page.find(name="span", attrs={"class": "ui-rater-rateCount"}).text
        rate = item_page.find(name="span", attrs={"class": "ui-rater-rating"}).text

        comments = [self.parse_comment(article) for article in
                    item_page.find(name="div", attrs={"class": "comment-list-block"}).findAll("div", attrs={
                        "class": "comments-item__info"})]
        # comments = item_page("div", "comment-list-block")[0]("div", "comments-item__info")
        options = {}
        try:
            options_entries = [option.text for option in
                               item_page.find(name="select", attrs={"class": "itemColor"}).findAll("option")]
            for option in options_entries:
                [option_text, option_price] = option.split(" - ")
                option_text = option_text.strip()
                option_price = option_price.strip()
                option_price = option_price.replace("Р", "")
                option_price = option_price.replace(" ", "")
                options[option_text] = float(option_price)
        except Exception as e:
            self._logger.exception("can't load options for {}".format(item_url))

        age = "undefined"
        try:
            age = item_page.find(name="div", attrs={"class": "brand"}).text.strip().split(",")[1].strip().split(":")[
                1].strip()
        except Exception as e:
            self._logger.exception("can't load age for {}".format(item_url))

        more_photos = []
        try:
            more_photos = self.get_more_photos(item_page)
        except Exception as e:
            self._logger.exception("can't load more photos for {}".format(item_url))

        color_photos = self.get_color_photos(item_page)

        text_description = ""
        try:
            text_description_block = item_page("div", "text-block-first")[0]
            text_description = " ".join(str(item) for item in text_description_block.contents).strip()
        except Exception as e:
            self._logger.exception("can't load text description {}".format(item_url))

        features = {}
        try:
            features_block = item_page("ul", "specification-list")[0]
            for row in features_block("li"):
                key = row("span")[0].text
                value = row("div", "specification-value")[0].text.strip()
                features[key] = value
        except Exception as e:
            self._logger.exception("can't load features for {}".format(item_url))

        result = {
            "price": float(price),
            "title": title,
            "in_stock": in_stock,
            "options": options,
            "age": age,
            "votes_count": votes_count,
            "rate": rate,
            "comments": comments,
            "more_photos": more_photos,
            "color_photos": color_photos,
            "description": text_description,
            "features": features
        }

        return result


    def get_item_info_by_url(self, item_url):
        item_page = self.get_bs(self._base_url + item_url, codec="cp1251")
        return self.get_item_info(item_page, item_url)

    def get_all_for_brand_in_group(self, group, brand):
        full_brand_url = self._base_url + brand["brand_url"]
        brand_items = self.get_bs(full_brand_url, codec="cp1251")
        catalog = brand_items.find(name="div", attrs={"id": "catalog"})
        catalog_items = catalog.findAll(name="div", attrs={"class": "itemRow"})

        results = []
        for catalog_item in catalog_items:
            item_url = catalog_item.find("p", attrs={"class": "itemName"}).find("a").attrs["href"]
            self._logger.info("\t\t{}".format(item_url))
            result = self.get_item_info_by_url(item_url)
            result["item_url"] = item_url
            result["brand_name"] = brand["brand_name"]
            result["brand_url"] = brand["brand_url"]
            result["group_title"] = group["title"]
            result["group_url"] = group["url"]
            results.append(result)
        return results

    def get_brands_for_group(self, group):
        url = self._base_url + group['url']
        self._logger.info(url)
        group_bs = self.get_bs(url, codec='cp1251', wait=10)
        a = group_bs.find(name="a", attrs={"title": group["title"]})
        brands = [({"brand_url": item.attrs["href"], "brand_name": item.text}) for item in
                  a.parent.nextSibling.findAll("a") if item.attrs["href"] != "#"]
        return brands

    def get_groups(self ):
        url = "https://www.akusherstvo.ru/magaz.php?action=cat_show&ordby=type&type_active=11"
        res = self.get_bs(url, codec='cp1251')
        groups = []
        table = res.find(name="table", attrs={"class": "all_types_table"})
        for idx, item in enumerate(table.find("tbody").findAll("td")):
            # print (idx,item)
            link = item.find("a")
            url = link.attrs['href']
            title = link.attrs['title']
            img_src = link.find("img").attrs["src"]
            groups.append({"url": url, "title": title, "img_src": img_src})
            # print (link)
        return groups


    def parse(self):
        groups = self.get_groups()
        all_items = []
        for group_id, group in enumerate(groups):

            brands = self.get_brands_for_group(group)
            for brand_id, brand in enumerate(brands):
                dump_name = os.path.join(self._dump_folder, group["title"] + "_" + brand["brand_name"] + ".txt")
                if os.path.exists(dump_name):
                    logging.info("Skip {}".format(dump_name))
                    continue

                logging.info("\tProcess brand : {} {}".format(brand_id, brand["brand_name"]))
                all_items_for_brand = self.get_all_for_brand_in_group(group, brand)
                logging.info("Items count {}".format(len(all_items_for_brand)))

                with open(dump_name, "w") as f:
                    json.dump(all_items_for_brand, f)
                all_items.extend(all_items_for_brand)

        dump_name = "final.txt"
        with open(dump_name, "w") as f:
            json.dump(all_items, f)

        normalized_date = self._normalize_data(all_items)
        os.makedirs("dump", exist_ok=True)
        normalized_date.to_json("dump/{}.json".format(self._dump_folder))
        normalized_date.to_csv("dump/{}.csv".format(self._dump_folder), encoding='utf8')
        normalized_date.to_pickle("dump/{}.pickle".format(self._dump_folder))

    def _normalize_data(self, data):
        frame = pd.DataFrame(data)
        frame["clean_title"] = frame.apply(lambda row: row["title"].replace("Автокресло ", ""), axis=1)
        frame['brand_url'] = frame['brand_url'].apply(lambda val: self._base_url + val)
        frame['group_url'] = frame['group_url'].apply(lambda val: self._base_url + val)
        frame['item_url'] = frame['item_url'].apply(lambda val: self._base_url + val)
        frame["is_carseat"] = frame.apply(lambda row: "Автокресло" in row["title"], axis=1)
        frame["main_photo"] = frame["color_photos"].apply(lambda val: val[0][0])
        frame["img_name"] = frame.main_photo.apply(lambda url: os.path.basename(url))
        return frame

