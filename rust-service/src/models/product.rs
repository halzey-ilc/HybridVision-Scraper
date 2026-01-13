use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct Product {
    pub row_index: usize,
    pub name: String,
    pub image_url: Option<String>,
}