def get_stopwords():
    stopwords = []
    with open("resources/stopwords_cn.txt", "r", encoding="utf-8") as file:
        for line in file:
            stopwords.append(line.strip())
    return stopwords
