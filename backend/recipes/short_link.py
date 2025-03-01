import pyshorteners # библиотека


# функция для сокращении ссылок
def shorten_url(url):
    type_tiny = pyshorteners.Shortener()
    short_url = type_tiny.tinyurl.short(url)
    return short_url

url = input("http://127.0.0.1:8000/api/recipes/94/")
print("Сокращенный URL - ", format(shorten_url(url)))




