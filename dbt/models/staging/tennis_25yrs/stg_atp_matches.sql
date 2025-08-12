select
    tourney_id as tournament_id,
    tourney_name as tournament_name,
    surface,
    draw_size,
    tourney_level as tournament_level,
    to_date(tourney_date, 'YYYYMMDD') as tournament_date,
    match_num,
    winner_id,
    winner_seed,
    winner_entry,
    winner_name,
    winner_hand,
    winner_ht as winner_height,
    winner_ioc,
    winner_age,
    loser_id,
    loser_seed,
    loser_entry,
    loser_name,
    loser_hand,
    loser_ht as loser_height,
    loser_ioc,
    loser_age,
    score,
    best_of,
    round_of_match,
    case round_of_match
        WHEN 'F' THEN 2
        WHEN 'SF' THEN 4
        WHEN 'QF' THEN 8
        WHEN 'R16' THEN 16
        WHEN 'R32' THEN 32
        WHEN 'R64' THEN 64
        WHEN 'R128' THEN 128
        ELSE 130
    END AS round_of_match_number,
    minutes,
    w_ace as winner_ace,
    w_df as winner_double_faults,
    w_svpt as winner_service_points,
    w_1stIn as winner_1st_serves,
    w_1stWon as winner_1st_serves_won,
    w_2ndWon as winner_2nd_serves_won,
    w_svGms as winner_serve_games,
    w_bpSaved as winner_break_points_saved,
    w_bpFaced as winner_break_points_faced,
    l_ace as loser_ace,
    l_df as loser_double_faults,
    l_svpt as loser_service_points,
    l_1stIn as loser_1st_serves,
    l_1stWon as loser_1st_serves_won,
    l_2ndWon as loser_2nd_serves_won,
    l_svGms as loser_serve_games,
    l_bpSaved as loser_break_points_saved,
    l_bpFaced as loser_break_points_faced,
    winner_rank,
    winner_rank_points,
    loser_rank,
    loser_rank_points,
    'atp' as governing_body
from {{ source('tennis_25yrs', 'atp_matches') }}
