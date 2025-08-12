# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 22:24:32 2025

@author: pedro
 
Business logic services for Tennis Analytics.
Contains all tennis-specific calculations and analysis.
"""
import pandas as pd
from typing import Dict, Any, List, Optional
from ..data.repositories import PlayerRepository, MatchRepository
from config.settings import settings

class TennisAnalysisService:
    """Service for tennis data analysis and calculations."""
    
    def __init__(self):
        self.player_repo = PlayerRepository()
        self.match_repo = MatchRepository()
    
    def analyze_player_performance(self, player_name: str, year_start: Optional[int] = None, 
                                 year_end: Optional[int] = None) -> Dict[str, Any]:
        """Analyze player performance statistics."""
        print(f"TS - Analyzing player: '{player_name}'")
        print(f"TS - Filters: year_start={year_start}, year_end={year_end}")
        
        # Get raw data from repository
        result = self.player_repo.get_player_tournament_stats(player_name, year_start, year_end)
        
        if not result or result[0] == 0:
            # Try to find similar players
            similar_players = self.player_repo.find_similar_player_names(player_name)
            return {
                'success': False,
                'message': f"No tournament data found for player: {player_name}",
                'similar_players': similar_players
            }
        
        # Extract data and perform calculations
        tournaments, games_won, games_lost, avg_rank, total_points, governing_body = result
        
        # Business logic calculations
        total_games = games_won + games_lost
        win_percentage = round((games_won / total_games) * 100, 1) if total_games > 0 else 0
        avg_ranking = round(avg_rank, 1) if avg_rank else None
        
        # Format period description
        period = self._format_period(year_start, year_end)
        
        return {
            'success': True,
            'player_name': player_name,
            'governing_body': governing_body,
            'period': period,
            'statistics': {
                'total_tournaments': tournaments,
                'games_won': games_won,
                'games_lost': games_lost,
                'total_games': total_games,
                'win_percentage': win_percentage,
                'average_ranking': avg_ranking,
                'total_points': total_points or 0
            }
        }
    
    def get_available_players_list(self, governing_body: str = 'All',
                                   year_start: Optional[int] = None, year_end: Optional[int] = None,
                                 limit: Optional[int] = None) -> Dict[str, Any]:
        """Get formatted list of available players."""
        print(f"TS - Getting '{governing_body}' players")
        if limit is None:
            limit = settings.DEFAULT_PLAYER_LIMIT
        
        players_data = self.player_repo.get_all_players(governing_body, limit)
        
        if not players_data:
            return {
                'success': False,
                'message': f"No {governing_body} players found"
            }
        
        # Format player information
        player_list = []
        for player, tournament_count, total_games in players_data:
            player_list.append(f"{player} ({tournament_count} tournaments, {total_games} games)")
        
        return {
            'success': True,
            'governing_body': governing_body,
            'count': len(player_list),
            'limit': limit,
            'players': player_list
        }
    
    def analyze_head_to_head(self, player_one: str, player_two: str, 
                           year_start: Optional[int] = None, year_end: Optional[int] = None,
                           tournament_name: Optional[str] = None, 
                           tournament_level: Optional[str] = None,
                           surface: Optional[str] = None) -> Dict[str, Any]:
        """Analyze head-to-head performance between two players."""
        print(f"TS - Analyzing head-to-head: '{player_one}' vs '{player_two}'")
        print(f"TS - Filters: year_start={year_start}, year_end={year_end}")
        
        # Get match data from repository
        matches_df = self.match_repo.get_head_to_head_matches(
            player_one, player_two, year_start, year_end, 
            tournament_name, tournament_level, surface
        )
        
        if matches_df.empty:
            return {
                'success': False,
                'message': f"No matches found between {player_one} and {player_two}"
            }
        
        # Perform head-to-head analysis
        analysis = self._calculate_head_to_head_stats(matches_df, player_one, player_two)
        analysis['period'] = self._format_period(year_start, year_end)
        analysis['success'] = True
        
        return analysis
    
    def _calculate_head_to_head_stats(self, matches_df: pd.DataFrame, 
                                    player_one: str, player_two: str) -> Dict[str, Any]:
        """Calculate detailed head-to-head statistics."""
        total_matches = len(matches_df)
        
        # Overall record
        player_one_wins = len(matches_df[matches_df['WINNER_NAME'] == player_one])
        player_two_wins = len(matches_df[matches_df['WINNER_NAME'] == player_two])
        
        # Grand Slam analysis
        grand_slam_matches = matches_df[matches_df['TOURNAMENT_LEVEL'] == 'G']
        player_one_gs_wins = len(grand_slam_matches[grand_slam_matches['WINNER_NAME'] == player_one])
        player_two_gs_wins = len(grand_slam_matches[grand_slam_matches['WINNER_NAME'] == player_two])
        
        # Surface analysis
        surface_stats = self._analyze_surface_performance(matches_df, player_one, player_two)
        
        return {
            'player_one': player_one,
            'player_two': player_two,
            'total_matches': total_matches,
            'overall_record': {
                player_one: player_one_wins,
                player_two: player_two_wins
            },
            'grand_slam_record': {
                player_one: player_one_gs_wins,
                player_two: player_two_gs_wins
            },
            'surface_breakdown': surface_stats['breakdown'],
            'chart_data': surface_stats['chart_data']
        }
    
    def _analyze_surface_performance(self, matches_df: pd.DataFrame, 
                                   player_one: str, player_two: str) -> Dict[str, Any]:
        """Analyze performance by surface type."""
        surfaces = ['Hard', 'Clay', 'Grass']
        
        breakdown = {}
        chart_data = []
        
        for surface in surfaces:
            surface_matches = matches_df[matches_df['SURFACE'] == surface]
            p1_wins = len(surface_matches[surface_matches['WINNER_NAME'] == player_one])
            p2_wins = len(surface_matches[surface_matches['WINNER_NAME'] == player_two])
            
            breakdown[surface] = {player_one: p1_wins, player_two: p2_wins}
            
            # Prepare chart data
            chart_data.extend([
                {"player": player_one, "surface": surface, "wins": p1_wins},
                {"player": player_two, "surface": surface, "wins": p2_wins}
            ])
        
        return {
            'breakdown': breakdown,
            'chart_data': pd.DataFrame(chart_data)
        }
    
    def _format_period(self, year_start: Optional[int], year_end: Optional[int]) -> str:
        """Format the time period description."""
        if year_start and year_end:
            return f"Years: {year_start}-{year_end}"
        elif year_start:
            return f"From: {year_start}"
        elif year_end:
            return f"Until: {year_end}"
        else:
            return "All years"
