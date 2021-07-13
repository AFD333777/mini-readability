import sys

from mini_readability import MiniReadabilityParser, SiteUnreachableException

if __name__ == "__main__":
    try:
        MiniReadabilityParser(sys.argv[1]).parse()
    except SiteUnreachableException:
        print("Не удалось подключиться к сайту")
