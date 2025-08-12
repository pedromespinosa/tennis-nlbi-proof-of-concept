# Tennis Analytics Assistant 🎾

An AI-powered tennis statistics analysis application that provides insights into ATP and WTA tournament data from 2000-2024.

## Features

- **Player Performance Analysis**: Get detailed statistics for any player including games won/lost, rankings, and tournament performance
- **Head-to-Head Comparisons**: Compare two players' performance against each other with surface-specific breakdowns
- **Interactive Visualizations**: Dynamic charts showing performance by surface type
- **Natural Language Interface**: Ask questions in plain English using Claude AI
- **Comprehensive Data**: Covers ATP and WTA tournaments from 2000-2024

## Architecture

This project follows a clean, layered architecture:

```
src/
├── data/           # Data access layer (repositories, connections)
├── services/       # Business logic layer (tennis analysis)
├── ai/            # AI orchestration layer (Claude integration)
└── ui/            # Presentation layer (Streamlit interface)
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/tennis-analytics.git
   cd tennis-analytics
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `MyKeys.env` file in the project root:
   ```env
   # Anthropic API
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   
   # Snowflake Connection
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_ROLE=your_role
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_SCHEMA=your_schema
   ```

4. **Add your Snowflake private key**
   
   Place your `rsa_key.p8` file in the project root.

## Usage

### Running the Application

```bash
streamlit run src/ui/streamlit_app.py
```

### Example Queries

- **Player Statistics**: "Show me Rafael Nadal's stats from 2005 to 2010"
- **Head-to-Head**: "Compare Federer vs Nadal on clay courts"
- **Player Discovery**: "List top 10 ATP players by tournament count"

## Project Structure

```
tennis-analytics/
├── README.md
├── requirements.txt
├── MyKeys.env              # Environment variables (create this)
├── rsa_key.p8              # Snowflake private key (add this)
├── config/
│   └── settings.py         # Configuration management
├── src/
│   ├── data/
│   │   ├── connections.py  # Database connection handling
│   │   └── repositories.py # Data access objects
│   ├── services/
│   │   └── tennis_service.py # Business logic and calculations
│   ├── ai/
│   │   └── claude_agent.py # AI conversation orchestration
│   └── ui/
│       └── streamlit_app.py # User interface
└── tests/                  # Unit tests (future)
```

## Database Schema

The application expects the following Snowflake tables:

- `FCT_PLAYER_TOURNAMENT_SUMMARY`: Player tournament-level statistics
- `STG_ALL_MATCHES_SIMPLE`: Individual match results for head-to-head analysis

## Technologies Used

- **Frontend**: Streamlit
- **AI**: Anthropic Claude
- **Database**: Snowflake
- **Data Processing**: Pandas
- **Language**: Python 3.8+

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
flake8 src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions or issues, please open an issue on GitHub or contact [your-email@example.com].