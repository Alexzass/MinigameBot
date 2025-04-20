use validator::Validate;
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Clone)]
#[serde(rename_all = "snake_case")]
pub enum HighscoreType {
    ChampsName,
    ItemsCost,
    ItemsName,
}

#[derive(Serialize, Deserialize, Clone, Debug, Validate, Default)]
pub struct CreatePlayerDto {
    pub user_id: i64,
    pub state: String,
    pub server_id: i64
}

#[derive(Deserialize, Clone, Debug, Validate)]
pub struct UpdatePlayerDto{
    pub state: String,
    pub highscore_type: Option<HighscoreType>,
    pub highscore: Option<i64>
}

#[derive(Deserialize, Clone, Debug, Validate)]
pub struct LeaderboardDto {
    pub highscore_type: HighscoreType,
    pub limit: i64,
    pub offset: i64
}