use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, sqlx::FromRow, sqlx::Type, Clone)]
pub struct Player {
    pub id: i64,
    pub user_id: i64,
    pub state: String,
    pub server_id: i64,
    pub highscore_champs_name: i64,
    pub highscore_items_cost: i64,
    pub highscore_items_name: i64,
}