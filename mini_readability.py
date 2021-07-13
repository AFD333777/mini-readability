import os
from bs4 import BeautifulSoup, element
import requests


class SiteUnreachableException(Exception):
    pass


class SiteIsNotParsed(Exception):
    print("Не удалось полностью спарсить сайт с данным шаблоном")


class MiniReadabilityParser:
    def __init__(self, website_url):
        self.website_url = website_url

    @staticmethod
    def retrieve_html(website_url: str):
        website_response = requests.get(website_url)
        if website_response.status_code != requests.codes.ok:
            raise SiteUnreachableException()
        return BeautifulSoup(website_response.content, 'html.parser')

    @staticmethod
    def get_params_from_file() -> list:
        if os.path.exists("template.txt"):
            with open("template.txt", "r", encoding="UTF-8") as file:
                data = file.readline()
                if len(data) != 0:
                    return [elem.strip() for elem in data.split(";")]
        return ["", "", "p"]

    def create_formatted_paragraph(self, item):
        paragraph = ""
        for elem in item:
            if elem.find("a") is None:
                if elem.get('href').find("://") == -1:
                    url = self.get_site_name() + elem.get('href')
                    paragraph += elem.text + f" [{url}]"
                else:
                    paragraph += elem.text + f" [{elem.get('href')}]"
            else:
                if type(elem) is element.NavigableString:
                    paragraph += elem
        return paragraph

    def get_text_from_tags(self, items) -> list:
        text = []
        for item in items:
            if item.find("a") is None:
                text.append(item.text)
            else:
                text.append(self.create_formatted_paragraph(item))
        return text

    @staticmethod
    def format_length_text(text: list) -> list:
        result = []
        for paragraph in text:
            tmp = ""
            data = paragraph.split()
            for elem in data:
                if len(tmp + elem) <= 80:
                    tmp += elem + " "
                else:
                    result.append(tmp)
                    tmp = elem + " "
            result.append(tmp)
            result.append("\n")
        return result

    def get_site_name(self) -> str:
        protocol = self.website_url[:self.website_url.find("://") + 3]
        path = self.website_url[len(protocol):]
        site_name = protocol + path[:path.find("/")]
        return site_name

    def parse(self):
        html = self.retrieve_html(self.website_url)
        params = self.get_params_from_file()

        try:
            if params[0] == "" and params[1] == "":
                text = self.get_text_from_tags(html.find_all(params[2]))
            elif params[1] == "":
                text = self.get_text_from_tags(html.find(params[0]).find_all(params[2]))
            else:
                text = self.get_text_from_tags(
                    html.find(params[0], class_=params[1]).find_all(params[2]))
            if html.find("h1") is not None:
                text.insert(0, html.find("h1").text)
            self.create_output_file(self.format_length_text(text))
        except AttributeError:
            raise SiteIsNotParsed

    def create_output_file(self, text):
        file_path, file_name = self.get_name_output_file(self.website_url)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(os.path.join(file_path, file_name), mode="w", encoding="UTF-8") as file:
            for elem in text:
                if elem != "\n":
                    file.write(elem)
                    file.write("\n")
                else:
                    file.write(elem)

    @staticmethod
    def get_name_output_file(url: str):
        cwd = os.getcwd()
        dirs = url[url.find(":") + 2:].strip("/").split("/")
        for item in dirs[:-1]:
            cwd = os.path.join(cwd, item)
        return cwd, dirs[-1] + ".txt"
