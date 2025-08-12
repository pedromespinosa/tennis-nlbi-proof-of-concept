WITH player_ranking AS (
    SELECT 
        tournament_date,
        tournament_name,
        winner_name as player,
        winner_rank as rank,
        winner_rank_points as points
    FROM {{ ref('stg_all_matches_simple') }}
    UNION all
    SELECT 
        tournament_date,
        tournament_name,
        loser_name as player,
        loser_rank as rank,
        loser_rank_points as points
    from {{ ref('stg_all_matches_simple') }}
)
SELECT
    player,
    tournament_name,
    year(tournament_date) as match_year,
    max(tournament_date) as as_of,
    min(rank) as min_rank,
    max(points) as max_points
from player_ranking
group by
    player,
    tournament_name,
    year(tournament_date)
order by
    player, as_of