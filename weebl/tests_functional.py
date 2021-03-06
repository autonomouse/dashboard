#! /usr/bin/env python2

import unittest
import os
from selenium import webdriver
from random import randint


class WebDriverOilTestCase(unittest.TestCase):
    HOST = 'http://localhost'

    def setUp(self):
        # Create a browser instance and go to site:
        self.driver = webdriver.Firefox()

    def go_to_url(self, url):
        self.driver.get(url)

    def clicky(self, locator):
        self.driver.find_element_by_css_selector(locator).click()

    def typey(self, locator, keys):
        self.driver.find_element_by_css_selector(locator).click()
        self.driver.find_element_by_css_selector(locator).clear()
        self.driver.find_element_by_css_selector(locator).send_keys(keys)

    def tearDown(self):
        self.stop_django_runserver()
        self.driver.close()


class SettingsTests(WebDriverOilTestCase):

    def tearDown(self):
        self.typey('#id_check_in_unstable_threshold', randint())
        super(SettingsTests, self).tearDown()

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weebl.settings")
    unittest.main()
