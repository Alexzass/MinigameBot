use axum::{routing::{get, post, patch}, Extension, Router};
use std::sync::Arc;
use crate::handlers::*;
use crate::config::AppState;
use tower_http::{cors::CorsLayer, trace::TraceLayer};


pub fn create_routes(state: Arc<AppState>, cors: CorsLayer) -> Router {
    Router::new()
        .route("/player/{user_id}", get(get_player))
        .route("/player/create", post(create_player))
        .route("/player/update/{user_id}", patch(update_player))
        .route("/leaderboard", get(leaderboard))
        .layer(TraceLayer::new_for_http())
        .layer(Extension(state))
        .layer(cors)
}