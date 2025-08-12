# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 22:28:24 2025

@author: pedro
Streamlit UI for Tennis Analytics Assistant.
Handles user interface, conversation flow, and chart display.
"""
import streamlit as st
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.ai.claude_agent import TennisAnalysisAgent
from config.settings import settings

class TennisAnalyticsUI:
    """Streamlit user interface for tennis analytics."""
    
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Tennis Analytics Assistant",
            page_icon="🎾",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def initialize_session_state(self):
        """Initialize session state variables."""
        if 'agent' not in st.session_state:
            try:
                # Validate settings before creating agent
                settings.validate()
                st.session_state.agent = TennisAnalysisAgent()
            except ValueError as e:
                st.error(f"Configuration Error: {str(e)}")
                st.stop()
            except Exception as e:
                st.error(f"Failed to initialize agent: {str(e)}")
                st.stop()
        
        if 'messages' not in st.session_state:
            st.session_state.messages = []
    
    def render_header(self):
        """Render the application header."""
        st.title("🎾 Tennis Analytics Assistant")
        st.markdown("Ask questions about tennis statistics (ATP/WTA 2000-2024)")
        
        # Add some example queries in the sidebar
        with st.sidebar:
            st.header("Example Queries")
            st.markdown("""
            **Player Statistics:**
            - "Show me Rafael Nadal's stats from 2005 to 2010"
            - "What are Serena Williams' career numbers?"
            
            **Head-to-Head Analysis:**
            - "Compare Federer vs Nadal"
            - "Djokovic vs Murray on clay courts"
            
            **Player Lists:**
            - "Show me top ATP players"
            - "List WTA players with most tournaments"
            """)
    
    def render_conversation_history(self):
        """Render the conversation history."""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display charts if available
                if message["role"] == "assistant" and "chart_data" in message:
                    chart_data = message["chart_data"]
                    if chart_data is not None and not chart_data.empty:
                        self.display_chart(chart_data)
    
    def display_chart(self, chart_data):
        """Display chart for head-to-head analysis."""
        try:
            # Create pivot table for bar chart
            pivot = chart_data.pivot(index="player", columns="surface", values="wins").fillna(0)
            
            if not pivot.empty:
                st.markdown("**Wins by Surface**")
                st.bar_chart(pivot)
        except Exception as e:
            st.error(f"Error displaying chart: {str(e)}")
    
    def handle_user_input(self):
        """Handle user input and generate responses."""
        if prompt := st.chat_input("Ask about tennis statistics..."):
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    response = st.session_state.agent.process_query(prompt)
                    
                    # Display the text response
                    st.markdown(response["text"])
                    
                    # Display chart if available
                    chart_data = response.get("chart_data")
                    if chart_data is not None and not chart_data.empty:
                        self.display_chart(chart_data)
            
            # Add assistant response to history
            assistant_message = {
                "role": "assistant", 
                "content": response["text"]
            }
            
            # Include chart data in message for history
            if chart_data is not None:
                assistant_message["chart_data"] = chart_data
            
            st.session_state.messages.append(assistant_message)
    
    def render_sidebar_info(self):
        """Render additional information in the sidebar."""
        with st.sidebar:
            st.markdown("---")
            st.header("About")
            st.markdown("""
            This application provides AI-powered analysis of tennis statistics 
            from 2000-2024, covering both ATP and WTA tournaments.
            
            **Features:**
            - Player performance analysis
            - Head-to-head comparisons
            - Tournament statistics
            - Interactive visualizations
            """)
            
            st.markdown("---")
            st.header("Data Coverage")
            st.markdown("""
            - **Years:** 2000-2024
            - **Tours:** ATP & WTA
            - **Tournaments:** All levels
            - **Surfaces:** Hard, Clay, Grass
            """)
    
    def run(self):
        """Run the Streamlit application."""
        self.render_header()
        self.render_sidebar_info()
        self.render_conversation_history()
        self.handle_user_input()

def main():
    """Main function to run the application."""
    try:
        app = TennisAnalyticsUI()
        app.run()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.markdown("Please check your configuration and try again.")

if __name__ == "__main__":
    main()
