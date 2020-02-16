import os
import unittest
from bs4 import BeautifulSoup

from parser import Parser


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        pass
    def test_item_info_images(self):
        base_url = "https://www.akusherstvo.ru"
        page_url = "/catalog/50666-avtokreslo-rant-star/"

        page_mock_url = base_url + page_url

        dump_folder = "test"
        parser = Parser(base_url, dump_folder)
        page = self.get_page_mock(parser, page_mock_url)

        page_url = "/catalog/36172-carmela/"
        item_info = parser.get_item_info(page, page_url)
        more_photos = item_info["more_photos"]
        color_photos = item_info["color_photos"]
        self.assertEqual(len(more_photos), 4)
        self.assertEqual(len(color_photos), 4)

        self.assertEqual(any([ "_b." in photo_url for photo_url in color_photos]), False, "all paths should be without and postfix")
        self.assertEqual(any([ "_s." in photo_url for photo_url in more_photos]), False, "all paths should be without and postfix")



    def get_page_mock(self, parser, url):
        normalized_url = url.replace("/", "_")
        full_path = "./test_data/mock_{}.html".format(normalized_url)

        if os.path.exists(full_path):
            with open(full_path, "r") as f:
                raw_text = f.read()
                page = BeautifulSoup(raw_text, features="html5lib")
        else:
            page = parser.get_bs(url, codec="cp1251")
            os.makedirs("./test_data", exist_ok=True)
            with open(full_path, "w") as f:
                f.write(str(page))


        return page


if __name__ == '__main__':
    unittest.main()
