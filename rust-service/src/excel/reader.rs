// use calamine::{open_workbook, Reader, Xlsx, DataType};
// use anyhow::{Result, Context};
// use crate::models::product::Product;

// pub fn read_excel(file_path: &str, sheet_name: &str) -> Result<Vec<Product>> {
//     let mut workbook: Xlsx<_> = open_workbook(file_path)
//         .with_context(|| format!("Cannot open Excel file '{}'", file_path))?;

//     // Result<Option<Range<Data>>, _> -> Range<Data>
//     let range = workbook
//         .worksheet_range(sheet_name)?
//         .ok_or_else(|| anyhow::anyhow!("Sheet '{}' not found", sheet_name))?;

//     let mut products = Vec::new();
//     for (i, row) in range.rows().enumerate() {
//         let name = match row.get(0) {
//             Some(DataType::String(s)) => s.clone(),
//             Some(DataType::Float(f)) => f.to_string(),
//             Some(DataType::Int(i)) => i.to_string(),
//             Some(DataType::Bool(b)) => b.to_string(),
//             _ => "".to_string(),
//         };

//         let image_url = match row.get(1) {
//             Some(DataType::String(s)) => Some(s.clone()),
//             _ => None,
//         };

//         products.push(Product {
//             row_index: i + 1,
//             name,
//             image_url,
//         });
//     }

//     Ok(products)
// }
use calamine::{open_workbook, Reader, Xlsx, Data};
use anyhow::{Result, Context};
use crate::models::product::Product;

pub fn read_excel(file_path: &str, sheet_name: &str) -> Result<Vec<Product>> {
    let mut workbook: Xlsx<_> = open_workbook(file_path)
        .with_context(|| format!("Не удалось открыть файл '{}'", file_path))?;

    // Пытаемся открыть лист по имени, если нет — берем самый первый доступный
    let actual_sheet = if workbook.sheet_names().contains(&sheet_name.to_string()) {
        sheet_name.to_string()
    } else {
        workbook.sheet_names().get(0)
            .ok_or_else(|| anyhow::anyhow!("В файле нет листов"))?
            .clone()
    };

    let range = workbook
        .worksheet_range(&actual_sheet)
        .with_context(|| format!("Ошибка чтения листа '{}'", actual_sheet))?;

    let mut products = Vec::new();

    // skip(1) пропускает строку заголовков
    for (i, row) in range.rows().enumerate().skip(1) {
        let name = row.get(0)
            .map(|d| d.to_string())
            .unwrap_or_default();

        if name.is_empty() { continue; } // Пропускаем пустые строки

        let image_url = match row.get(1) {
            Some(Data::String(s)) if !s.is_empty() => Some(s.clone()),
            _ => None,
        };

        products.push(Product {
            row_index: i + 1,
            name,
            image_url,
        });
    }

    Ok(products)
}