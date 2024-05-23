from PIL import Image
import numpy as np

# Открываем изображение
img = Image.open("panda.jpg")
# Преобразуем изображение в массив NumPy
img_array = np.array(img)
# Поворачиваем массив NumPy на 90 градусов с помощью transpose
rotated_img_array = np.transpose(img_array, axes=(1,0,2))
# Преобразуем массив обратно в изображение
rotated_img = Image.fromarray(rotated_img_array)
# Показываем повернутое изображение
rotated_img.save("panda_swap.jpg")
rotated_img.show()
