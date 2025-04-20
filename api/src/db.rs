use async_trait::async_trait;
use crate::{dtos::HighscoreType, models::Player};
use sqlx::PgPool;

pub struct DBClient {
    pub pool: PgPool
}

impl DBClient {
    pub fn new(pool : PgPool) -> Self {
        DBClient { pool }
    }
}

#[async_trait]
pub trait PlayerExt {
    async fn get_player(&self, user_id: i64) -> Result<Option<Player>, sqlx::Error>;
    async fn create_player(&self, user_id: i64, state: String, server_id: i64) -> Result<(), sqlx::Error>;
    async fn update_player(&self, user_id: i64, state: String, highscore: Option<i64>, htype: Option<HighscoreType>) -> Result<(), sqlx::Error>;
    async fn leaderboard(&self, htype: HighscoreType, limit: i64, offset: i64) -> Result<Vec<Player>, sqlx::Error>;
}

#[async_trait]
impl PlayerExt for DBClient {
    async fn get_player(&self, user_id: i64) -> Result<Option<Player>, sqlx::Error> {
        let result = sqlx::query_as!(
            Player,
            "SELECT * FROM players WHERE user_id = $1",
            user_id
        )
        .fetch_optional(&self.pool)
        .await?;
        Ok(result)
    }
    async fn create_player(&self, user_id: i64, state: String, server_id: i64) -> Result<(), sqlx::Error> {
        println!("Creating player with user_id: {}, state: {}, server_id: {}", user_id, state, server_id);
        sqlx::query!(
            r#"
            INSERT INTO players (user_id, "state", server_id)
            VALUES ($1, $2, $3)
            "#,
            user_id,
            state,
            server_id,
        )
        .execute(&self.pool)
        .await?;
        Ok(())
    }
    async fn update_player(&self, user_id: i64, state: String, highscore: Option<i64>, htype: Option<HighscoreType>) -> Result<(), sqlx::Error> {
        match (highscore, htype) {
            (Some(highscore), Some(HighscoreType::ChampsName)) => sqlx::query!(
                r#"
                UPDATE players SET "state" = $1, highscore_champs_name = $2 WHERE user_id = $3
                "#,
                state,
                highscore,
                user_id,
            ),
            (Some(highscore), Some(HighscoreType::ItemsCost)) => sqlx::query!(
                r#"
                UPDATE players SET "state" = $1, highscore_items_cost = $2 WHERE user_id = $3
                "#,
                state,
                highscore,
                user_id,
            ),
            (Some(highscore), Some(HighscoreType::ItemsName)) => sqlx::query!(
                r#"
                UPDATE players SET "state" = $1, highscore_items_name = $2 WHERE user_id = $3
                "#,
                state,
                highscore,
                user_id,
            ),
            (_, _) => sqlx::query!(
                r#"
                UPDATE players SET "state" = $1 WHERE user_id = $2
                "#,
                state,
                user_id,
            ),
        }
        .execute(&self.pool)
        .await?;
        Ok(())
    }

    async fn leaderboard(&self, htype: HighscoreType, limit: i64, offset: i64) -> Result<Vec<Player>, sqlx::Error> {
        let result = match htype {
            HighscoreType::ChampsName => sqlx::query_as!(
                Player,
                r#"
                SELECT * FROM players 
                ORDER BY highscore_champs_name DESC
                LIMIT $1 OFFSET $2
                "#,
                limit,
                offset,
            )
            .fetch_all(&self.pool)
            .await?,
        
            HighscoreType::ItemsCost => sqlx::query_as!(
                Player,
                r#"
                SELECT * FROM players 
                ORDER BY highscore_items_cost DESC
                LIMIT $1 OFFSET $2
                "#,
                limit,
                offset,
            )
            .fetch_all(&self.pool)
            .await?,
        
            HighscoreType::ItemsName => sqlx::query_as!(
                Player,
                r#"
                SELECT * FROM players 
                ORDER BY highscore_items_name DESC
                LIMIT $1 OFFSET $2
                "#,
                limit,
                offset,
            )
            .fetch_all(&self.pool)
            .await?,
        };
        Ok(result)
    }
}