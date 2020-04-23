import pandas


def main():
    words_data = pandas.read_csv('data/words.csv')
    print(words_data)


if __name__ == '__main__':
    main()
