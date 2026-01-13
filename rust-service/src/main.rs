use calamine::{open_workbook, Reader, Xlsx, Data};
use serde::Serialize;
use anyhow::{Result, Context};

// Структура должна совпадать с ожиданиями FastAPI
#[derive(Serialize)]
struct Product {
    name: String,
    image_url: Option<String>, // Опционально (может быть null)
    row_index: usize,          // Индекс строки для отслеживания в логах
}

fn main() -> Result<()> {
    println!("--- Rust сервис запущен ---");

    let mut workbook: Xlsx<_> = open_workbook("data/products.xlsx")
        .with_context(|| "Не удалось открыть файл data/products.xlsx. Проверьте, что папка data существует.")?;

    
    let range = workbook
        .worksheet_range("Лист1")
        .context("Лист не найден. Проверьте название вкладки в Excel")?;

    let mut products: Vec<Product> = Vec::new();

    // enumerate() поможет нам получить индекс строки автоматически
    for (i, row) in range.rows().skip(1).enumerate() {
        let name = match row.get(0) {
            Some(Data::String(s)) => s.clone(),
            Some(Data::Float(f)) => f.to_string(),
            _ => continue, // Пропускаем пустые или странные ячейки
        };

        // Если в Excel есть ссылка на фото во втором столбце (индекс 1)
        let image_url = row.get(1).and_then(|data| {
            if let Data::String(url) = data { Some(url.clone()) } else { None }
        });

        println!("Добавлен товар: {} (строка {})", name, i + 2);
        
        products.push(Product {
            name,
            image_url,
            row_index: i + 2, // +2 потому что skip(1) и индекс с 0
        });
    }

    println!("Итого загружено: {} товаров", products.len());

    if products.is_empty() {
        return Ok(());
    }

    let client = reqwest::blocking::Client::new();
    println!("Отправка JSON в AI сервис...");

    let res = client
        .post("http://127.0.0.1:8000/match")
        .json(&products)
        .send()
        .with_context(|| "Ошибка связи с Python. Убедитесь, что uvicorn запущен на порту 8000.")?;

    let status = res.status();
    let body = res.text()?;

    if status.is_success() {
        println!("УСПЕХ! Ответ от сервера:\n{}", body);
    } else {
        println!("СЕРВЕР ВЕРНУЛ ОШИБКУ ({}):\n{}", status, body);
    }

    Ok(())
}