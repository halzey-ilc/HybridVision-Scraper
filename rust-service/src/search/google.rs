use anyhow::Result;
use reqwest::Client;
use serde_json::Value;

use crate::models::SearchResult;

const SERP_API_URL: &str = "https://serpapi.com/search";

pub async fn search_google(product_name: &str, api_key: &str) -> Result<Vec<SearchResult>> {
    let client = Client::new();

    let resp = client
        .get(SERP_API_URL)
        .query(&[
            ("q", product_name),
            ("engine", "google"),
            ("api_key", api_key),
        ])
        .send()
        .await?
        .json::<Value>()
        .await?;

    let mut results = Vec::new();

    if let Some(items) = resp["organic_results"].as_array() {
        for item in items {
            let link = item["link"].as_str().unwrap_or("").to_string();

            if link.contains("ozon")
                || link.contains("wildberries")
                || link.contains("amazon")
                || link.contains("aliexpress")
            {
                results.push(SearchResult {
                    title: item["title"].as_str().unwrap_or("").to_string(),
                    link,
                    source: "google".to_string(),
                });
            }
        }
    }

    Ok(results)
}
