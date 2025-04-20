use axum::{extract::Path, Json};
use axum::extract::{Extension, Query};
use std::sync::Arc;
use crate::models::Player;
use crate::config::AppState;
use crate::db::PlayerExt;
use crate::dtos::*;

pub async fn get_player(
    Path(user_id): Path<i64>, 
    Extension(state): Extension<Arc<AppState>>,
) -> Json<Option<Player>> {
    let result = state.db_client.get_player(user_id).await;

    match result {
        Ok(Some(player)) => Json(Some(player)),
        Ok(None) => Json(None),
        Err(_) => Json(None),
    }
}

pub async fn create_player(
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<CreatePlayerDto>
) -> Result<Json<String>, axum::http::StatusCode> {
    let result = state.db_client.create_player(
        payload.user_id,
        payload.state,
        payload.server_id,
    ).await;

    match result {
        Ok(_) => Ok(Json("Player created successfully".to_string())),
        Err(_) => Err(axum::http::StatusCode::INTERNAL_SERVER_ERROR),
    }
}

pub async fn update_player(
    Path(user_id): Path<i64>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<UpdatePlayerDto>
) -> Result<Json<String>, axum::http::StatusCode> {
    let result = state.db_client.update_player(
        user_id,
        payload.state,
        payload.highscore,
        payload.highscore_type,
    ).await;

    match result {
        Ok(_) => Ok(Json("Player created successfully".to_string())),
        Err(_) => Err(axum::http::StatusCode::INTERNAL_SERVER_ERROR),
    }
}

pub async fn leaderboard(
    Extension(state): Extension<Arc<AppState>>,
    Query(payload): Query<LeaderboardDto>
) -> Result<Json<Vec<Player>>, axum::http::StatusCode> {
    println!("Leaderboard request: {:?}", payload);
    let result = state.db_client.leaderboard(
        payload.highscore_type,
        payload.limit,
        payload.offset,
    ).await;

    println!("Result: {:?}", result.iter().len());

    match result {
        Ok(players) => Ok(Json(players)),
        Err(_) => Err(axum::http::StatusCode::INTERNAL_SERVER_ERROR),
    }
}