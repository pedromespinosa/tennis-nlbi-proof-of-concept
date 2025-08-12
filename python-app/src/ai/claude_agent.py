# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 22:25:29 2025

@author: pedro
Claude AI agent for Tennis Analytics.
Handles conversation flow, intent recognition, and AI orchestration.

"""
import anthropic
from typing import Dict, Any, List
from config.settings import settings
from ..services.tennis_service import TennisAnalysisService

class TennisAnalysisAgent:
    """AI agent for tennis analysis conversations."""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.tennis_service = TennisAnalysisService()
        
        # System prompt defining the assistant behavior
        self.system_prompt = """
You are a professional tennis statistics analyst. You help users analyze ATP and WTA tennis data from 2000-2024.

AVAILABLE METRICS:
- Player tournament performance (games won/lost, rankings, points)
- Tournament-level statistics
- Player career summaries by year ranges
- Player comparison

RULES:
1. NEVER perform calculations yourself - always call the appropriate function
2. Always validate that you have required parameters (player names, years, governing body)
3. If missing parameters, ask the user to provide them
4. Always specify the exact filters you're using in your response
5. Only answer tennis-related queries using the available functions
6. IMPORTANT: When a function returns complete results, use ONLY those results. Do NOT call additional functions unless specifically requested by the user.
7. Answer the user's question completely using the function result provided. Do not gather additional data unless the user explicitly asks for it.

FUNCTION CALLING:
- If asked about player performance: call get_player_stats
- If asked about available players: call get_available_players
- If asked about player games comparison: call compare_players_games
- If asked about tournament results: call get_tournament_stats (not implemented yet)

Remember: You interpret the user's intent and call functions. The functions do all calculations.
"""

        # Define available tools for Claude
        self.tools = [
            {
                "name": "get_player_stats",
                "description": "Get tournament performance statistics for a specific player",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "player_name": {"type": "string", "description": "Player name"},
                        "year_start": {"type": "integer", "description": "Start year (optional)"},
                        "year_end": {"type": "integer", "description": "End year (optional)"}
                    },
                    "required": ["player_name"]
                }
            },
            {
                "name": "get_available_players",
                "description": "Get list of available players in the database",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "governing_body": {"type": "string", "description": "ATP or WTA or All"},
                        "year_start": {"type": "integer", "description": "Start year (optional)"},
                        "year_end": {"type": "integer", "description": "End year (optional)"},
                        "limit": {"type": "integer", "description": "Number of players to return"}
                    }
                }
            },
            {
                "name": "compare_players_games",
                "description": "Get performance statistics for when a set of players play each other",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "player_one_name": {"type": "string", "description": "1st Player name"},
                        "player_two_name": {"type": "string", "description": "2nd Player name"},
                        "year_start": {"type": "integer", "description": "Start year (optional)"},
                        "year_end": {"type": "integer", "description": "End year (optional)"},
                        "tournament_name": {"type": "string", "description": "Tournament name (optional)"},
                        "tournament_level": {"type": "string", "description": "Tournament level (optional)"},
                        "surface": {"type": "string", "description": "Surface of the match (optional)"}
                    },
                    "required": ["player_one_name", "player_two_name"]
                }
            },
        ]
    
    def process_query(self, user_message: str) -> Dict[str, Any]:
        """Process user query using Claude with function calling."""
        try:
            # Create message with tools
            message = self.client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                temperature=settings.ANTHROPIC_TEMPERATURE,
                system=self.system_prompt,
                tools=self.tools,
                messages=[{"role": "user", "content": user_message}]
            )
            
            print(f"CA - Claude's initial response:")
            print(f"CA - Stop reason: {message.stop_reason}")
            
            # Log message content for debugging
            if message.content:
                for i, content in enumerate(message.content):
                    print(f"CA - Content block {i}: type={getattr(content, 'type', 'unknown')}")
                    if hasattr(content, 'type') and content.type == "tool_use":
                        print(f"CA -   Tool name: {content.name}")
                        print(f"CA -   Tool input: {content.input}")
            
            # Check if Claude wants to use a tool
            if message.stop_reason == "tool_use":
                return self._handle_tool_use(message, user_message)
            else:
                # Direct response without tool use
                text_content = self._extract_text_content(message.content)
                return {"text": text_content, "chart_data": None}
                
        except Exception as e:
            return {"text": f"Error processing query: {str(e)}", "chart_data": None}
    
    def _handle_tool_use(self, message, user_message: str) -> Dict[str, Any]:
        """Handle tool use requests from Claude."""
        if not message.content or len(message.content) == 0:
            return {"text": "Error: Tool use indicated but message.content is empty", "chart_data": None}
        
        # Find the tool use block
        tool_use = None
        for content_block in message.content:
            if hasattr(content_block, 'type') and content_block.type == "tool_use":
                tool_use = content_block
                break
        
        if not tool_use:
            return {"text": "Error: Tool use indicated but no tool_use block found", "chart_data": None}
        
        # Execute the function
        function_result = self._execute_function(tool_use.name, tool_use.input)
        print(f"CA - Function {tool_use.name} completed with results")
        
        # Check if the function returned text and chart data
        if isinstance(function_result, dict) and 'text' in function_result:
            text_to_interpret = function_result["text"]
            chart_df = function_result.get("chart_data")
        else:
            text_to_interpret = str(function_result)
            chart_df = None
        
        # Send result back to Claude for final response
        try:
            follow_up = self.client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                temperature=0.2,
                system=self.system_prompt,
                tools=self.tools,
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": message.content},
                    {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_use.id, "content": text_to_interpret}]}
                ]
            )
            
            final_response = self._extract_text_content(follow_up.content)
            
            return {
                "text": final_response,
                "chart_data": chart_df
            }
            
        except Exception as e:
            return {"text": f"Error in follow-up: {str(e)}", "chart_data": chart_df}
    
    def _execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the requested function using the tennis service."""
        try:
            print(f"CA - Executing function: {function_name}")
            print(f"CA - Parameters: {parameters}")
            
            if function_name == "get_player_stats":
                result = self.tennis_service.analyze_player_performance(
                    player_name=parameters.get('player_name'),
                    year_start=parameters.get('year_start'),
                    year_end=parameters.get('year_end')
                )
                return {"text": self._format_player_stats_response(result)}
            
            elif function_name == "get_available_players":
                result = self.tennis_service.get_available_players_list(
                    governing_body=parameters.get('governing_body', 'All'),
                    year_start=parameters.get('year_start'),
                    year_end=parameters.get('year_end'),
                    limit=parameters.get('limit')
                )
                return {"text": self._format_players_list_response(result)}
            
            elif function_name == "compare_players_games":
                result = self.tennis_service.analyze_head_to_head(
                    player_one=parameters.get('player_one_name'),
                    player_two=parameters.get('player_two_name'),
                    year_start=parameters.get('year_start'),
                    year_end=parameters.get('year_end'),
                    tournament_name=parameters.get('tournament_name'),
                    tournament_level=parameters.get('tournament_level'),
                    surface=parameters.get('surface')
                )
                
                if result['success']:
                    return {
                        "text": self._format_head_to_head_response(result),
                        "chart_data": result['chart_data']
                    }
                else:
                    return {"text": result['message']}
            
            else:
                return {"text": f"Error: Unknown function {function_name}"}
                
        except Exception as e:
            print(f"CA - ERROR in execute_function: {str(e)}")
            return {"text": f"Function execution error: {str(e)}"}
    
    def _format_player_stats_response(self, result: Dict[str, Any]) -> str:
        """Format player statistics response."""
        if not result['success']:
            response = result['message']
            if result.get('similar_players'):
                response += f"\n\nSimilar players found: {', '.join(result['similar_players'])}"
            return response
        
        stats = result['statistics']
        return f"""Player: {result['player_name']} ({result['governing_body']})
Filters: {result['period']}
Total Tournaments: {stats['total_tournaments']}
Games Won: {stats['games_won']}
Games Lost: {stats['games_lost']}
Games Win %: {stats['win_percentage']}%
Average Ranking: {stats['average_ranking'] if stats['average_ranking'] else 'N/A'}
Total Points: {stats['total_points']}"""
    
    def _format_players_list_response(self, result: Dict[str, Any]) -> str:
        """Format available players list response."""
        if not result['success']:
            return result['message']
        
        header = f"Top {result['limit']} {result['governing_body']} players:"
        return header + "\n" + "\n".join(result['players'])
    
    def _format_head_to_head_response(self, result: Dict[str, Any]) -> str:
        """Format head-to-head analysis response."""
        player_one = result['player_one']
        player_two = result['player_two']
        overall = result['overall_record']
        grand_slam = result['grand_slam_record']
        surface = result['surface_breakdown']
        
        response = f"""Head-to-Head: {player_one} vs {player_two}
{result['period']}

Overall Record:
Total Matches: {result['total_matches']}
{player_one}: {overall[player_one]} wins
{player_two}: {overall[player_two]} wins

Grand Slam Record:
{player_one}: {grand_slam[player_one]} wins
{player_two}: {grand_slam[player_two]} wins

Surface Breakdown:"""
        
        for surf, wins in surface.items():
            response += f"""
{surf} Court:
  {player_one}: {wins[player_one]} wins
  {player_two}: {wins[player_two]} wins"""
        
        return response
    
    def _extract_text_content(self, content_blocks) -> str:
        """Extract text content from Claude's response blocks."""
        if not content_blocks:
            return "Claude returned empty response"
        
        text_blocks = []
        for block in content_blocks:
            if getattr(block, "type", None) == "text":
                text_blocks.append(block.text)
        
        return "\n\n".join(text_blocks) if text_blocks else "No text content found"