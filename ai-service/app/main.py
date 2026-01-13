import asyncio
import sys

# Исправление для Windows + Playwright
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import httpx
import os
from pathlib import Path
from fastapi import FastAPI
from .schemas import Product, MatchResult, Source
from .matcher import search_marketplace, match_by_image

app = FastAPI(title='Product AI Service')

CATALOG_FOLDER = "app/catalog_images"

@app.post("/match", response_model=list[MatchResult])
async def match_products(products: list[Product]):
    results = []
    
    # Создаем асинхронный клиент для скачивания картинок
    async with httpx.AsyncClient() as client:
        for p in products:
            # 1. Текстовый поиск (асинхронно вызывает WB и Ozon)
            sources_data = await search_marketplace(p.name)
            
            # 2. Поиск по картинке (если передан URL)
            if p.image_url:
                temp_file = Path(f"temp_{p.row_index}_{os.getpid()}.jpg")
                try:
                    # Скачиваем изображение асинхронно
                    response = await client.get(p.image_url, timeout=5.0)
                    if response.status_code == 200:
                        with open(temp_file, "wb") as f:
                            f.write(response.content)
                        
                        # CLIP-сравнение (обычно синхронное, так как грузит CPU/GPU)
                        img_matches = match_by_image(str(temp_file), CATALOG_FOLDER)
                        sources_data.extend(img_matches)
                except Exception as e:
                    print(f"Ошибка при обработке изображения для {p.name}: {e}")
                finally:
                    if temp_file.exists():
                        os.remove(temp_file)

            # 3. Формируем итоговый объект
            # Приводим все результаты к формату Source
            formatted_sources = []
            for s in sources_data:
                if isinstance(s, dict):
                    formatted_sources.append(Source(**s))
                else:
                    formatted_sources.append(s)

            results.append(MatchResult(
                name=p.name,
                found=len(formatted_sources) > 0,
                sources=formatted_sources
            ))
    
    return results