# Weather MCP Server (TypeScript)

A global weather server for Claude desktop integration using OpenWeatherMap API.

## Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Get an API key from [OpenWeatherMap](https://openweathermap.org/api) (Free tier available)

3. Create a `.env` file in the root directory with your API key:
   ```
   OPENWEATHERMAP_API_KEY=your_api_key_here
   ```

4. Build the server:
   ```
   npm run build
   ```

## Integration with Claude Desktop

1. Make sure Claude desktop is closed completely (check task manager to ensure it's not running)

2. Find your Claude MCP configuration file:
   - Windows: `%APPDATA%\Claude\mcp.json` (typically `C:\Users\<username>\AppData\Roaming\Claude\mcp.json`)
   - macOS: `~/Library/Application Support/Claude/mcp.json`
   - Linux: `~/.config/Claude/mcp.json`

3. If the file doesn't exist, create it. Add or replace the `mcpServers` section with the following (make sure to use your actual path):

```json
{
    "mcpServers": {
        "weather": {
            "command": "node",
            "args": [
                "D:/Dev/mcp/nodejs/weather-server-typescript/build/index.js"
            ],
            "cwd": "D:/Dev/mcp/nodejs/weather-server-typescript"
        }
    }
}
```

> **IMPORTANT**: 
> - Use forward slashes `/` in the path, not backslashes
> - Add the `cwd` property pointing to your project directory
> - Use absolute paths, not relative paths
> - Double-check that the file exists at the specified location

4. Save the file and restart Claude desktop

5. To verify it's working, ask Claude something like:
   - "What's the weather in Auckland, New Zealand?"
   - "What's the forecast for Tokyo?"

## Troubleshooting

If Claude is still using the old NWS API:

1. Check that the `.env` file contains your OpenWeatherMap API key
2. Make sure the path in the `args` and `cwd` are correct
3. Try restarting your computer
4. Look for a Claude desktop log file that might contain error messages

## Available Tools

- **get-weather**: Get current weather for any location by city name
  Example: `get-weather({ location: "Auckland, NZ" })`

- **get-forecast**: Get detailed weather forecast for any location by coordinates
  Example: `get-forecast({ latitude: -36.8485, longitude: 174.7633 })`

- **get-alerts**: Get weather alerts for any location by coordinates
  Example: `get-alerts({ latitude: -36.8485, longitude: 174.7633 })`

## Example Usage in Claude

```
Can you check the current weather in Tokyo?
```

```
What's the forecast for the next 3 days at latitude 51.5074 and longitude -0.1278 (London)?
```

```
Are there any weather alerts for latitude 25.7617 and longitude -80.1918 (Miami)?
```
