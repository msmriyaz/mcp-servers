# Technical Context: Weather Anywhere MCP

## Technologies & Dependencies

### Core Technologies
- **TypeScript**: Main implementation language (v5.8.2)
- **Node.js**: Runtime environment
- **MCP SDK**: Model Context Protocol SDK (@modelcontextprotocol/sdk v1.4.0)
- **dotenv**: Environment variable management (v16.4.7)
- **Zod**: Schema validation for tool parameters

### External APIs
- **OpenWeatherMap API**: Primary data source for weather information
  - Endpoints used:
    - `/weather`: Current weather conditions
    - `/onecall`: Forecast and alerts data

## Architecture Overview

### Component Structure
1. **Server Initialization**: Setup using MCP SDK
2. **Tool Definitions**: Three main tools registered with the server
   - `get-weather`: Current weather by city name
   - `get-forecast`: Multi-day forecasts by coordinates
   - `get-alerts`: Weather alerts by coordinates
3. **API Integration Layer**: Helper functions for making OpenWeatherMap requests
4. **Data Formatting**: Functions to format temperatures, wind speeds, and alerts

### Data Flow
1. Claude sends tool invocation requests to the MCP server
2. Server validates parameters using Zod schemas
3. Server makes appropriate OpenWeatherMap API calls
4. Responses are formatted and returned to Claude
5. Claude presents the information to the user

## Technical Requirements

### Environment Variables
- `OPENWEATHERMAP_API_KEY`: API key for OpenWeatherMap (required)

### Claude Desktop Integration
- Requires configuration in Claude's `claude_desktop_config.json` file to point to this server

## Development Setup

### Local Development
1. Install Node.js and npm
2. Clone repository
3. Run `npm install` to install dependencies
4. Create `.env` file with OpenWeatherMap API key
5. Build with `npm run build`
6. Test with direct Node.js execution

### Deployment
1. Build the TypeScript project
2. Configure Claude desktop to point to the built server
3. Ensure environment variables are properly set

## Technical Constraints

### API Limitations
- OpenWeatherMap API has rate limits (60 calls/minute on free tier)
- Some detailed data requires paid API tiers

### Performance Considerations
- API calls introduce latency in response times
- No caching mechanism currently implemented

## Integration Points

### Claude Desktop
- Integration via MCP JSON configuration
- Communication through standard input/output

### OpenWeatherMap
- REST API integration
- JSON response parsing
- Error handling for API failures 