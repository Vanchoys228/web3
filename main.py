from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi.staticfiles import StaticFiles
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image
import os
import requests


if "PORT" in os.environ:
    port = int(os.environ["PORT"])
else:
    port = 8000

app = FastAPI()

templates = Jinja2Templates(directory="templates")
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

def split_image_and_generate_histograms(image_bytes):
    # Загрузить изображение из байтов
    image = Image.open(io.BytesIO(image_bytes))
    # Разделить изображение на 4 части
    width, height = image.size
    left = 0
    top = 0
    right = width // 2
    bottom = height // 2
    img1 = image.crop((left, top, right, bottom))
    img2 = image.crop((right, top, width, bottom))
    img3 = image.crop((left, bottom, right, height))
    img4 = image.crop((right, bottom, width, height))
    # Сохранить новые изображения
    img1.save(f"{static_dir}/part1.jpg")
    img2.save(f"{static_dir}/part2.jpg")
    img3.save(f"{static_dir}/part3.jpg")
    img4.save(f"{static_dir}/part4.jpg")
    # Создать гистограммы для каждого изображения
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
    axes = [ax1, ax2, ax3, ax4]
    for i, img in enumerate([img1, img2, img3, img4]):
        pixels = np.array(img)
        r, g, b = pixels[:, :, 0], pixels[:, :, 1], pixels[:, :, 2]
        axes[i].hist(r.flatten(), bins=256, color='r', alpha=0.5, label='Red')
        axes[i].hist(g.flatten(), bins=256, color='g', alpha=0.5, label='Green')
        axes[i].hist(b.flatten(), bins=256, color='b', alpha=0.5, label='Blue')
        axes[i].set_title(f"Part {i+1}")
        axes[i].legend()
    histogram_bytes = io.BytesIO()
    plt.savefig(histogram_bytes, format='png')
    histogram_bytes.seek(0)
    return [f"{static_dir}/part1.jpg", f"{static_dir}/part2.jpg", f"{static_dir}/part3.jpg", f"{static_dir}/part4.jpg"], histogram_bytes.getvalue()

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "captcha_passed": False, "title": "FastAPI Веб-сайт"})

@app.post("/split_and_plot")
async def split_and_plot(request: Request, file: UploadFile = File(...), resp: str = Form(...)):
    try:
        # Считываем файл изображения
        contents = await file.read()
        # Проверяем Captcha
        secret_key = "6LdMQuYpAAAAAAf52xmo5ehdqOD2VEyCdu5_drkC"
        payload = {
            "secret": secret_key,
            "response": resp
        }
        response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
        result = response.json()
        if result["success"]:
            parts, histogram = split_image_and_generate_histograms(contents)
            parts_base64 = [base64.b64encode(open(part, 'rb').read()).decode('utf-8') for part in parts]
            histogram_base64 = base64.b64encode(histogram).decode('utf-8')
            return templates.TemplateResponse("result.html", {"request": request, "parts": parts_base64, "histogram": histogram_base64, "captcha_passed": True, "title": "FastAPI Веб-сайт - Результат"})
        else:
            return templates.TemplateResponse("index.html", {"request": request, "error": "Captcha не пройдена", "captcha_passed": False, "title": "FastAPI Веб-сайт - Ошибка"})
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "detail": [{"type": "error", "msg": str(e)}], "captcha_passed": False, "title": "FastAPI Веб-сайт - Ошибка"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
