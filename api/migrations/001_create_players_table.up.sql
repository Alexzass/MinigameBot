CREATE TABLE players (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL, 
    state TEXT NOT NULL DEFAULT 'online',
    server_id BIGINT UNIQUE NOT NULL,
    highscore_champs_name BIGINT NOT NULL DEFAULT 0,
    highscore_items_cost BIGINT NOT NULL DEFAULT 0,
    highscore_items_name BIGINT NOT NULL DEFAULT 0
);