use crate::db::DBClient;

#[derive(Debug, Clone)]
pub struct Config {
    pub db_url: String,
    pub port: u16 
}

pub struct AppState{
    pub config: Config,
    pub db_client: DBClient
}

impl Config {
    pub fn new() -> Self {
        let db_url = std::env::var("DATABASE_URL").expect("DATABASE_URL must be set");
        
        Config { db_url, port: 8000 }
    }
}