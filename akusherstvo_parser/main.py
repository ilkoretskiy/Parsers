from parser import Parser


def main():
    url = "https://www.akusherstvo.ru"
    folder_name = "dump_2019_04_03"
    parser = Parser(url, folder_name)
    parser.parse()

if __name__ == "__main__":
    main()