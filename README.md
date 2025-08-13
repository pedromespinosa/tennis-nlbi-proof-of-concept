# Tennis Natural Language BI Analytics

*Transform tennis statistics into conversational insights using modern data stack*

## 🎯 Project Overview

This project demonstrates building a **Natural Language Business Intelligence (NLBI)** system that allows users to query ATP/WTA tennis statistics (2000-2024) using conversational language instead of traditional dashboards or SQL queries.

**The Challenge**: Traditional sports analytics require users to know specific metrics, player names, and how to navigate complex dashboards. What if you could just ask *"How did Federer perform against Nadal on clay courts?"* and get instant, accurate insights?

**The Solution**: An AI-powered analytics assistant that interprets natural language, translates intent to SQL, and returns reliable statistical insights with data visualizations.

## 🏗️ Architecture

### Data Pipeline (Event-Driven)
```
Jeff Sackmann CSV Files → Google Cloud Storage → Pub/Sub → Snowflake Auto-Ingest → dbt Models → Analytics Tables
```

### Query Pipeline (Real-time)
```
User Query → Claude AI → Function Calls → Snowflake Analytics Tables → Results → Streamlit UI
```

### Technology Stack
- **📁 Data Source** - Jeff Sackmann's tennis datasets (CSV format)
- **☁️ Google Cloud Storage** - Raw file storage with versioning
- **📡 Google Pub/Sub** - Event-driven file notifications
- **🏔️ Snowflake** - Cloud data warehouse with auto-ingest capabilities
- **🔧 dbt** - Data modeling and transformations
- **🤖 Claude (Anthropic)** - Natural language interpretation and function calling
- **🐍 Python/Streamlit** - Application framework and UI
- **📈 Recharts** - Data visualization
- **🔐 Private Key Auth** - Secure database connections

## 🚀 Key Features

### Conversational Analytics
- **Natural queries**: *"Compare Serena Williams vs Venus Williams on grass courts"*
- **Smart interpretation**: Understands player names, time periods, tournament types
- **Reliable calculations**: AI interprets intent, SQL performs calculations

### Comprehensive Tennis Data
- **25 years of data**: ATP/WTA matches from 2000-2024
- **Tournament-level analytics**: Performance across different tournaments and surfaces
- **Player career summaries**: Games won/lost, rankings, points progression
- **Head-to-head comparisons**: Direct matchup statistics with surface breakdowns

### Professional Implementation
- **Function calling architecture**: Structured AI-to-database communication
- **Error handling**: Graceful fallbacks for ambiguous queries
- **Data validation**: Ensures accurate player name matching
- **Interactive visualizations**: Dynamic charts for statistical insights

## 📊 Sample Queries & Capabilities

```
🎾 "How did Roger Federer perform in 2019?"
   → Tournament count, games won/lost, win percentage, ranking data

🎾 "Show me available ATP players"
   → Top players by tournament participation and game count

🎾 "Compare Djokovic vs Nadal head-to-head"
   → Overall record, Grand Slam performance, surface-specific breakdowns

🎾 "What was Serena Williams' performance from 2010 to 2015?"
   → Filtered career statistics for specified time period
```

## 🛠️ Technical Implementation

### Data Pipeline
1. **Data Source**: Jeff Sackmann's tennis CSV files with 25 years of ATP/WTA data
2. **Cloud Storage**: Files uploaded to Google Cloud Storage bucket with versioning
3. **Event Notification**: GCS Pub/Sub subscription triggers on new file arrivals
4. **Auto-Ingestion**: Snowflake pipes listen to Pub/Sub and automatically load new data
5. **Transformation**: dbt models process raw data into staging and analytics-ready tables

### AI-Powered Query Pipeline
6. **Natural Language Input**: Users ask questions via Streamlit interface
7. **Intent Recognition**: Claude analyzes queries and maps to appropriate database functions
8. **Function Execution**: Python functions execute optimized SQL against transformed tables
9. **Results & Visualization**: Data returned with interactive charts and explanations

### Key Design Decisions

**Why Function Calling over RAG?**
- Ensures mathematical accuracy (AI doesn't perform calculations)
- Provides structured, consistent responses
- Enables complex aggregations and comparisons
- Maintains data integrity through SQL validation

**Why Claude over OpenAI?**
- Superior function calling capabilities
- Better understanding of nuanced sports terminology
- More reliable parameter extraction from natural language

**Architecture Benefits**
- **Scalable**: Easy to add new sports or data sources
- **Maintainable**: Clear separation between AI interpretation and data logic
- **Accurate**: SQL handles all calculations, eliminating AI math errors
- **Fast**: Direct database queries with optimized dbt models

## 📈 Data Model

### Staging Layer
- `stg_atp_matches` - Clean ATP match data
- `stg_wta_matches` - Clean WTA match data  
- `stg_all_matches_simple` - Unified match dataset

### Analytics Layer
- `fct_player_tournament_summary` - Player performance by tournament/year
- `fct_player_ranking` - Player ranking and points progression

## 🎮 Getting Started

### Prerequisites
- Python 3.8+
- Snowflake account with tennis data loaded
- Anthropic API key
- dbt Cloud or dbt Core

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/pedromespinosa/tennis-nlbi-proof-of-concept.git
   cd tennis-nlbi-proof-of-concept
   ```

2. **Install dependencies**
   ```bash
   pip install -r python-app/requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp python-app/config/example.env python-app/config/MyKeys.env
   # Edit MyKeys.env with your credentials
   ```

4. **Set up dbt models**
   ```bash
   cd dbt
   dbt deps
   dbt run
   ```

5. **Launch the application**
   ```bash
   streamlit run python-app/app.py
   ```

### Configuration Files Needed
- `MyKeys.env` - API keys and Snowflake credentials
- `rsa_key.p8` - Snowflake private key for authentication
- `dbt/profiles.yml` - dbt connection configuration

## 💡 What Makes This Special

### Beyond Traditional BI
- **No dashboard navigation** - Just ask questions naturally
- **No SQL knowledge required** - Accessible to any tennis fan or analyst
- **Intelligent interpretation** - Handles variations in player names and query formats

### Technical Excellence
- **Production-ready architecture** - Proper error handling, logging, and validation
- **Modern data stack** - Industry-standard tools and practices
- **Clean code principles** - Modular, documented, and maintainable
- **Portfolio quality** - Demonstrates full-stack data engineering capabilities

### Real-World Applications
This architecture could be extended to:
- **Corporate BI**: "How did our Q3 sales compare to last year?"
- **Financial Analytics**: "Show me portfolio performance by sector"
- **E-commerce**: "Which products are trending this month?"

## 🔧 Technical Deep Dive

### Event-Driven Data Ingestion

**Google Cloud Storage Integration**
```bash
# GCS bucket structure
gs://tennis-analytics-data/
├── atp_matches/
│   ├── atp_matches_2000.csv
│   ├── atp_matches_2001.csv
│   └── ...
└── wta_matches/
    ├── wta_matches_2000.csv
    ├── wta_matches_2001.csv
    └── ...
```

**Snowflake Auto-Ingest Configuration**
```sql
-- Create external stage pointing to GCS bucket
CREATE STAGE gcs_tennis_stage
URL = 'gcs://tennis-analytics-data/'
CREDENTIALS = (GCS_SERVICE_ACCOUNT = 'tennis-analytics@project.iam.gserviceaccount.com');

-- Create pipe for automatic data loading
CREATE PIPE tennis_data_pipe 
AS COPY INTO raw_tennis_matches 
FROM @gcs_tennis_stage
FILE_FORMAT = (TYPE = 'CSV' FIELD_OPTIONALLY_ENCLOSED_BY = '"' SKIP_HEADER = 1)
AUTO_INGEST = TRUE;

-- Enable Pub/Sub notifications
ALTER PIPE tennis_data_pipe SET PIPE_EXECUTION_PAUSED = FALSE;
```

### Function Calling Implementation
```python
def process_query(self, user_message: str):
    # Claude interprets natural language and calls appropriate function
    # Functions execute SQL queries against dbt-transformed tables
    # Results formatted and returned with visualizations
```

### dbt Model Strategy
- **Incremental builds** for large datasets
- **Data quality tests** on key metrics
- **Documentation** for all models and columns
- **Modular design** for easy extension

## 📊 Sample Output

When you ask *"Compare Federer vs Nadal head-to-head"*, you get:

```
Head-to-Head: Roger Federer vs Rafael Nadal
Period: All Time

Overall Record:
Total Matches: 40
Roger Federer: 16 wins  
Rafael Nadal: 24 wins

Grand Slam Record:
Roger Federer: 4 wins
Rafael Nadal: 10 wins

Surface Breakdown:
Hard Court: Federer 11, Nadal 9
Clay Court: Federer 2, Nadal 14  
Grass Court: Federer 3, Nadal 1
```

Plus an interactive bar chart showing wins by surface.

## 🎯 Future Enhancements

- **Real-time data integration** - Live tournament updates
- **Advanced analytics** - Predictive modeling and trend analysis  
- **Multi-sport expansion** - Basketball, soccer, baseball datasets
- **Voice interface** - Speak your questions instead of typing
- **Collaborative features** - Share insights and bookmark queries

## 📚 Data Source & Licensing

### Tennis Match Data
This project analyzes tennis match data generously provided by Jeff Sackmann through the Tennis Abstract project.

**Attribution**: Tennis databases, files, and algorithms by Jeff Sackmann / Tennis Abstract  
**License**: [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/)  
**Source**: https://github.com/JeffSackmann  

### Usage Compliance
- ✅ **Non-commercial**: This project is for educational and portfolio demonstration purposes only
- ✅ **Attribution**: Full attribution provided as required  
- ✅ **Share-alike**: This project is open source under MIT License

### Data Coverage
- **ATP Matches**: 2000-2024 tournament results (200,000+ matches)
- **WTA Matches**: 2000-2024 tournament results (180,000+ matches)
- **Tournaments**: Grand Slams, Masters, ATP 500/250, WTA Premier events
- **Metrics**: Rankings, points, surfaces, match scores, tournament levels

## 🤝 Contributing

This is a portfolio project, but feedback and suggestions are welcome! Feel free to:
- Open issues for bugs or enhancement ideas
- Submit pull requests for improvements
- Use this as inspiration for your own NLBI projects

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note**: While the code is MIT licensed, the underlying tennis data follows CC BY-NC-SA 4.0 (non-commercial use only).

---

## 🏆 About This Project

This tennis NLBI system showcases modern data engineering principles:
- **End-to-end pipeline** from raw data to conversational interface
- **AI integration** that enhances rather than replaces traditional analytics
- **Production-ready code** with proper error handling and documentation
- **Industry best practices** using established tools and patterns

Built as a demonstration of how Natural Language BI can make data analytics accessible to everyone, regardless of technical background.

*Questions? Reach out or check the issues tab for common questions and solutions.*
