from fastapi import FastAPI, File, UploadFile
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from captcha.image import ImageCaptcha

app = FastAPI()

# Функция для генерации Captcha
def generate_captcha(text):
    image = ImageCaptcha()
    data = image.generate(text)
    return data


# Функция для классификации изображения с использованием нейронной сети
def classify_image(img):
    # Здесь должен быть код для загрузки и использования обученной модели нейронной сети
    # Например, использование TensorFlow для классификации изображения
    # Вернем для примера случайную категорию
    categories = ['cat', 'dog', 'bird', 'flower']
    return np.random.choice(categories)


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), captcha: str = None):
    if captcha is None or not check_captcha(captcha):  # Проверка Captcha
        return {"error": "Invalid Captcha"}

    # Сохраняем загруженное изображение
    with open(file.filename, "wb") as image_file:
        content = await file.read()
        image_file.write(content)

    # Открываем изображение с помощью Pillow
    img = Image.open(file.filename)

    # Разбиваем изображение на четыре части
    split_images = split_image(img)

    color_distributions = []
    for i, split_img in enumerate(split_images):
        # Строим гистограмму распределения цветов
        histogram = split_img.histogram()

        r = histogram[0:256]
        g = histogram[256:512]
        b = histogram[512:768]

        plt.bar(np.arange(256), r, color='red', alpha=0.5)
        plt.bar(np.arange(256), g, color='green', alpha=0.5)
        plt.bar(np.arange(256), b, color='blue', alpha=0.5)

        plt.savefig(f"color_distribution_{i + 1}.png")
        color_distributions.append(f"color_distribution_{i + 1}.png")
        plt.clf()

    # Классификация изображения
    classification_result = classify_image(img)

    return {"split_images": split_images, "color_distributions": color_distributions,
            "classification_result": classification_result}


# Функция для проверки Captcha (заглушка, необходимо реализовать)
def check_captcha(captcha):
    # Здесь должна быть реализация проверки Captcha
    # Например, сравнение введенного пользователем значения с ожидаемым
    expected_captcha = "1234"  # Пример ожидаемого значения Captcha
    return captcha == expected_captcha

def split_image(img):
    width, height = img.size
    images = []
    for x in range(2):
        for y in range(2):
            left = x * width // 2
            upper = y * height // 2
            right = (x + 1) * width // 2
            lower = (y + 1) * height // 2
            images.append(img.crop((left, upper, right, lower)))
    return images