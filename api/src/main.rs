use dotenv::dotenv;
use tower_http::cors::CorsLayer;
use api::db::DBClient;
use api::config::AppState;
use api::routes::create_routes;
use std::sync::Arc;
use api::config::Config;
use tracing_subscriber::filter::LevelFilter;
use sqlx::postgres::PgPoolOptions;

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_max_level(LevelFilter::DEBUG)
        .init();

    dotenv().ok();
    
    let config: Config = Config::new();
    
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&config.db_url)
        .await
        .expect("Failed to create pool");

    let db_client = DBClient::new(pool);

    let app_state: Arc<AppState> = Arc::new(AppState {
        config,
        db_client
    });

    let cors: CorsLayer = CorsLayer::new()
        .allow_origin(tower_http::cors::Any)
        .allow_methods(tower_http::cors::Any)
        .allow_headers(tower_http::cors::Any);

    let app = create_routes(app_state.clone(), cors.clone());

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();

    axum::serve(listener, app).await.unwrap();
}