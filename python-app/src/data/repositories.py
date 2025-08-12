# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 21:51:52 2025

@author: pedro
 
Data repositories for Tennis Analytics.
Contains all database queries and data access logic.
"""
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from .connections import snowflake_db
from config.settings import settings

class PlayerRepository:
    """Repository for player-related data operations."""
    
    def __init__(self):
        self.db = snowflake_db
    
    def get_player_tournament_stats(self, player_name: str, year_start: Optional[int] = None, 
                                  year_end: Optional[int] = None) -> Optional[Tuple]:
        """Get tournament statistics for a specific player."""
        sql = """
        SELECT 
            COUNT(*) as total_tournaments,
            SUM(GAMES_WON) as total_games_won,
            SUM(GAMES_LOST) as total_games_lost,
            AVG(MIN_RANK) as avg_ranking,
            MAX(MAX_POINTS) as max_points,
            MAX(GOVERNING_BODY) as governing_body
        FROM FCT_PLAYER_TOURNAMENT_SUMMARY 
        WHERE PLAYER = %s
        """
        
        params = [player_name]
        
        if year_start:
            sql += " AND MATCH_YEAR >= %s"
            params.append(year_start)
        if year_end:
            sql += " AND MATCH_YEAR <= %s"
            params.append(year_end)
        
        print(f"DLR - Executing SQL: {sql}")
        print(f"DLR - With parameters: {params}")
        
        try:
            results = self.db.execute_query(sql, params)
            return results[0] if results else None
        except Exception as e:
            print(f"DLR - Error getting player stats: {str(e)}")
            return None
    
    def find_similar_player_names(self, partial_name: str, limit: int = 5) -> List[str]:
        """Find players with names similar to the given partial name."""
        sql = """
        SELECT DISTINCT PLAYER 
        FROM FCT_PLAYER_TOURNAMENT_SUMMARY 
        WHERE UPPER(PLAYER) LIKE UPPER(%s)
        LIMIT %s
        """
        
        search_term = f"%{partial_name.split()[0]}%"  # Search by first name
        params = [search_term, limit]
        
        try:
            results = self.db.execute_query(sql, params)
            return [row[0] for row in results] if results else []
        except Exception as e:
            print(f"Error finding similar players: {str(e)}")
            return []
    
    def get_all_players(self, governing_body: str = 'All', year_start: Optional[int] = None, year_end: Optional[int] = None, limit: int = None) -> List[Tuple]:
        """Get list of all players with their tournament counts."""
        sql = """
        SELECT 
            PLAYER, 
            COUNT(*) as tournament_count,
            SUM(GAMES_WON + GAMES_LOST) as total_games
        FROM FCT_PLAYER_TOURNAMENT_SUMMARY
        """
        
        params = []
        if governing_body != 'All':
            sql += " WHERE UPPER(GOVERNING_BODY) = UPPER(%s)"
            params.append(governing_body)
            if year_start:
                sql += " AND MATCH_YEAR >= %s"
                params.append(year_start)
            if year_end:
                sql += " AND MATCH_YEAR <= %s"
                params.append(year_end)
        
        sql += """
        GROUP BY PLAYER
        ORDER BY tournament_count DESC
        """
        
        if limit:
            sql += " LIMIT %s"
            params.append(limit)
        
        try:
            return self.db.execute_query(sql, params)
        except Exception as e:
            print(f"DLR - Error getting players list: {str(e)}")
            return []

class MatchRepository:
    """Repository for match-related data operations."""
    
    def __init__(self):
        self.db = snowflake_db
    
    def get_head_to_head_matches(self, player_one: str, player_two: str, 
                               year_start: Optional[int] = None, year_end: Optional[int] = None,
                               tournament_name: Optional[str] = None, 
                               tournament_level: Optional[str] = None,
                               surface: Optional[str] = None) -> pd.DataFrame:
        """Get all matches between two specific players."""
        sql = """
        SELECT 
            TOURNAMENT_NAME,
            TOURNAMENT_DATE,
            TOURNAMENT_LEVEL,
            WINNER_NAME,
            WINNER_RANK,
            WINNER_RANK_POINTS,
            LOSER_NAME,
            LOSER_RANK,
            LOSER_RANK_POINTS,
            ROUND_OF_MATCH,
            ROUND_OF_MATCH_NUMBER,
            SURFACE,
            BEST_OF,
            SCORE
        FROM STG_ALL_MATCHES_SIMPLE
        WHERE
            WINNER_NAME IN (%s, %s) AND
            LOSER_NAME IN (%s, %s)
        """
        
        params = [player_one, player_two, player_one, player_two]
        
        # Add optional filters
        if year_start:
            sql += " AND YEAR(TOURNAMENT_DATE) >= %s"
            params.append(year_start)
        if year_end:
            sql += " AND YEAR(TOURNAMENT_DATE) <= %s"
            params.append(year_end)
        if tournament_name:
            sql += " AND UPPER(TOURNAMENT_NAME) LIKE UPPER(%s)"
            params.append(f"%{tournament_name}%")
        if tournament_level:
            sql += " AND TOURNAMENT_LEVEL = %s"
            params.append(tournament_level)
        if surface:
            sql += " AND SURFACE = %s"
            params.append(surface)
        
        print(f"DLR - Executing SQL: {sql}")
        print(f"DLR - With parameters: {params}")
        
        try:
            return self.db.execute_query_pandas(sql, params)
        except Exception as e:
            print(f"DLR - Error getting head-to-head matches: {str(e)}")
            return pd.DataFrame()

class TournamentRepository:
    """Repository for tournament-related data operations."""
    
    def __init__(self):
        self.db = snowflake_db
    
    def get_tournament_stats(self, tournament_name: str, year: Optional[int] = None) -> List[Tuple]:
        """Get statistics for a specific tournament."""
        # This method can be implemented when tournament analysis is needed
        pass
    
    def get_available_tournaments(self, year: Optional[int] = None) -> List[str]:
        """Get list of available tournaments."""
        # This method can be implemented when tournament listing is needed
        pass