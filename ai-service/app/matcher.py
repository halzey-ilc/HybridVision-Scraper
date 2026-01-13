import asyncio
import httpx
from pathlib import Path
from playwright.async_api import async_playwright
# Импортируем твои функции из clip_model
from .clip_model import encode_image, similarity_score 

async def search_wb(product_name: str) -> list[dict]:
    """Быстрый асинхронный поиск по API Wildberries"""
    url = "https://search.wb.ru/exactmatch/ru/common/v4/search"
    params = {"query": product_name, "appType": 1, "curr": "rub", "dest": -1257744}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                return [{
                    "shop": "Wildberries",
                    "url": f"https://www.wildberries.ru/catalog/{p['id']}/detail.aspx",
                    "price": p.get("salePriceU", 0) / 100
                } for p in data.get("data", {}).get("products", [])[:3]]
        except Exception as e:
            print(f"WB error: {e}")
    return []

async def search_ozon(product_name: str) -> list[dict]:
    """Асинхронный поиск Ozon через Playwright (имитация браузера)"""
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        try:
            url = f"https://www.ozon.ru/search/?text={product_name.replace(' ', '+')}"
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_selector("[data-component='SearchResultGrid']", timeout=5000)
            
            links = await page.query_selector_all("a[href*='/product/']")
            for link in links[:3]:
                href = await link.get_attribute("href")
                if href:
                    results.append({
                        "shop": "Ozon",
                        "url": "https://www.ozon.ru" + href.split("?")[0]
                    })
        except Exception as e:
            print(f"Ozon error: {e}")
        finally:
            await browser.close()
    return results

async def search_marketplace(product_name: str) -> list[dict]:
    """ГЛАВНАЯ ФУНКЦИЯ: Запускает все поиски ПАРАЛЛЕЛЬНО"""
    # Запускаем WB и Ozon одновременно, чтобы сэкономить время
    tasks = [search_wb(product_name), search_ozon(product_name)]
    combined_results = await asyncio.gather(*tasks)
    
    # Склеиваем списки результатов в один
    return [item for sublist in combined_results for item in sublist]

def match_by_image(image_path: str, catalog_folder: str, threshold=0.25) -> list[dict]:
    """Синхронное сравнение CLIP (обычно работает быстро локально)"""
    results = []
    try:
        target_emb = encode_image(image_path)
        catalog = list(Path(catalog_folder).glob("*.jpg")) + list(Path(catalog_folder).glob("*.png"))
        
        for file in catalog:
            emb = encode_image(str(file))
            score = similarity_score(target_emb, emb)
            if score >= threshold:
                results.append({
                    "shop": "Internal Catalog", 
                    "url": f"file://{file.absolute()}", 
                    "score": float(score)
                })
    except Exception as e:
        print(f"Image Matching Error: {e}")
    return sorted(results, key=lambda x: x['score'], reverse=True)