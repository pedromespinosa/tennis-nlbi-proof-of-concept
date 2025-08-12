with player_games as (
    select
       tournament_date,
       tournament_name,
       tournament_level,
       winner_name as player,
       winner_rank as rank,
       winner_rank_points as points,
       1 as games_won,
       0 as games_lost,
       governing_body,
       round_of_match,
       round_of_match_number
    from {{ ref('stg_all_matches_simple') }}
    union all
    select
       tournament_date,
       tournament_name,
       tournament_level,
       loser_name as player,
       loser_rank as rank,
       loser_rank_points as points,
       0 as games_won,
       1 as games_lost,
       governing_body,
       round_of_match,
       round_of_match_number
    from {{ ref('stg_all_matches_simple') }}
),
last_round as (
    select
        player,
        tournament_name,
        tournament_level,
        governing_body,
        tournament_date,
        year(tournament_date) as match_year,
        round_of_match,
        round_of_match_number,
        row_number() over (
            partition by player, tournament_name, tournament_level, governing_body, year(tournament_date)
            order by round_of_match_number
        ) as rn
    from player_games
    qualify rn = 1
)
SELECT
    pg.player,
    pg.tournament_name,
    pg.tournament_level,
    year(pg.tournament_date) as match_year,
    max(pg.tournament_date) as as_of,
    min(pg.rank) as min_rank,
    max(pg.points) as max_points,
    sum(pg.games_won) as games_won,
    sum(pg.games_lost) as games_lost,
    min(pg.round_of_match_number) as round_of_match_number,
    lr.round_of_match as last_round_of_match,
    pg.governing_body
from player_games pg
left join last_round lr
    on pg.player = lr.player
    and pg.tournament_name = lr.tournament_name
    and pg.tournament_level = lr.tournament_level
    and pg.tournament_date = lr.tournament_date
    and pg.governing_body = lr.governing_body
group by
    pg.player,
    pg.tournament_name,
    pg.tournament_level,
    year(pg.tournament_date),
    pg.governing_body,
    lr.round_of_match
order by
    player asc, as_of desc