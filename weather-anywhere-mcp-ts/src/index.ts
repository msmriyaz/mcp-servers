import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import * as dotenv from 'dotenv';
import * as path from 'path';
import { fileURLToPath } from 'url';

// Get the directory where the current module is located
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from .env file
// Look for .env file in the project root, not where the script is run from
dotenv.config({ path: path.resolve(__dirname, '../.env') });

// API Configuration
const WEATHER_API_BASE = "https://api.openweathermap.org/data/2.5";
const WEATHER_API_KEY = process.env.OPENWEATHERMAP_API_KEY;
const USER_AGENT = "weather-app/1.0";

// Check if API key is available
if (!WEATHER_API_KEY) {
  console.error("Error: OpenWeatherMap API key not found in environment variables.");
  console.error("Please set OPENWEATHERMAP_API_KEY in your .env file.");
  process.exit(1);
}

// Helper function for making OpenWeatherMap API requests
async function makeWeatherAPIRequest<T>(endpoint: string, params: Record<string, any> = {}): Promise<T | null> {
  // Add the API key to the parameters
  params.appid = WEATHER_API_KEY;
  
  // Construct query string
  const queryString = new URLSearchParams(params).toString();
  const url = `${WEATHER_API_BASE}/${endpoint}?${queryString}`;

  const headers = {
    "User-Agent": USER_AGENT,
  };

  try {
    const response = await fetch(url, { headers });
    if (!response.ok) {
      const errorBody = await response.text();
      console.error(`HTTP error! status: ${response.status}, body: ${errorBody}`);
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return (await response.json()) as T;
  } catch (error) {
    console.error("Error making Weather API request:", error);
    return null;
  }
}

// Weather API Interfaces
interface WeatherAlert {
  event: string;
  description: string;
  tags: string[];
  start: number;
  end: number;
  sender_name: string;
}

interface CurrentWeather {
  main: {
    temp: number;
    feels_like: number;
    temp_min: number;
    temp_max: number;
    pressure: number;
    humidity: number;
  };
  weather: Array<{
    id: number;
    main: string;
    description: string;
    icon: string;
  }>;
  wind: {
    speed: number;
    deg: number;
    gust?: number;
  };
  clouds: {
    all: number;
  };
  sys: {
    country: string;
  };
  name: string;
}

interface ForecastData {
  list: Array<{
    dt: number;
    main: {
      temp: number;
      feels_like: number;
      temp_min: number;
      temp_max: number;
      pressure: number;
      humidity: number;
    };
    weather: Array<{
      id: number;
      main: string;
      description: string;
      icon: string;
    }>;
    clouds: {
      all: number;
    };
    wind: {
      speed: number;
      deg: number;
      gust?: number;
    };
    dt_txt: string;
  }>;
  city: {
    id: number;
    name: string;
    country: string;
  };
}

interface OneCallData {
  lat: number;
  lon: number;
  timezone: string;
  current: {
    dt: number;
    temp: number;
    feels_like: number;
    weather: Array<{
      id: number;
      main: string;
      description: string;
      icon: string;
    }>;
    wind_speed: number;
    wind_deg: number;
  };
  daily: Array<{
    dt: number;
    temp: {
      day: number;
      min: number;
      max: number;
      night: number;
      eve: number;
      morn: number;
    };
    feels_like: {
      day: number;
      night: number;
      eve: number;
      morn: number;
    };
    weather: Array<{
      id: number;
      main: string;
      description: string;
      icon: string;
    }>;
    wind_speed: number;
    wind_deg: number;
  }>;
  alerts?: WeatherAlert[];
}

// Format temperature with unit
function formatTemperature(temp: number, units: string): string {
  return `${Math.round(temp)}°${units === 'metric' ? 'C' : 'F'}`;
}

// Format wind speed with unit
function formatWindSpeed(speed: number, units: string): string {
  if (units === 'metric') {
    return `${speed.toFixed(1)} m/s`;
  } else {
    return `${speed.toFixed(1)} mph`;
  }
}

// Format alert data
function formatAlert(alert: WeatherAlert): string {
  const startDate = new Date(alert.start * 1000).toLocaleString();
  const endDate = new Date(alert.end * 1000).toLocaleString();
  
  return [
    `Event: ${alert.event || "Unknown"}`,
    `Sender: ${alert.sender_name || "Unknown"}`,
    `Start: ${startDate}`,
    `End: ${endDate}`,
    `Description: ${alert.description || "No description"}`,
    "---",
  ].join("\n");
}

// Create server instance
const server = new McpServer({
  name: "weather",
  version: "1.0.0",
});

// Register weather tools
server.tool(
  "get-forecast",
  "Get weather forecast for a location anywhere in the world",
  {
    latitude: z.number().min(-90).max(90).describe("Latitude of the location"),
    longitude: z.number().min(-180).max(180).describe("Longitude of the location"),
    units: z.enum(["metric", "imperial"]).default("metric").describe("Units to use for temperature and wind speed"),
    days: z.number().min(1).max(7).default(3).describe("Number of days to forecast"),
  },
  async ({ latitude, longitude, units, days }) => {
    // Get One Call API data (current weather and daily forecast)
    const oneCallData = await makeWeatherAPIRequest<OneCallData>("onecall", {
      lat: latitude,
      lon: longitude,
      units: units,
      exclude: "minutely,hourly", // We only need daily forecast and current weather
    });

    if (!oneCallData) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to retrieve weather data for coordinates: ${latitude}, ${longitude}.`,
          },
        ],
      };
    }

    // Format current weather
    const current = oneCallData.current;
    const currentWeatherText = [
      `Current Weather for ${oneCallData.timezone}:`,
      `Temperature: ${formatTemperature(current.temp, units)}`,
      `Feels Like: ${formatTemperature(current.feels_like, units)}`,
      `Conditions: ${current.weather[0]?.description || "Unknown"}`,
      `Wind: ${formatWindSpeed(current.wind_speed, units)} at ${current.wind_deg}°`,
      "---",
    ].join("\n");

    // Format daily forecast
    const dailyForecast = oneCallData.daily.slice(0, days).map(day => {
      const date = new Date(day.dt * 1000).toLocaleDateString();
      return [
        `${date}:`,
        `High: ${formatTemperature(day.temp.max, units)}`,
        `Low: ${formatTemperature(day.temp.min, units)}`,
        `Conditions: ${day.weather[0]?.description || "Unknown"}`,
        `Wind: ${formatWindSpeed(day.wind_speed, units)} at ${day.wind_deg}°`,
        "---",
      ].join("\n");
    });

    const forecastText = `${currentWeatherText}\n\nForecast for next ${days} days:\n\n${dailyForecast.join("\n")}`;

    return {
      content: [
        {
          type: "text",
          text: forecastText,
        },
      ],
    };
  },
);

server.tool(
  "get-weather",
  "Get current weather for a location anywhere in the world",
  {
    location: z.string().describe("City name, e.g. 'London' or 'London,UK'"),
    units: z.enum(["metric", "imperial"]).default("metric").describe("Units to use for temperature and wind speed"),
  },
  async ({ location, units }) => {
    const weatherData = await makeWeatherAPIRequest<CurrentWeather>("weather", {
      q: location,
      units: units,
    });

    if (!weatherData) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to retrieve weather data for location: ${location}.`,
          },
        ],
      };
    }

    const weatherText = [
      `Current Weather for ${weatherData.name}, ${weatherData.sys.country}:`,
      `Temperature: ${formatTemperature(weatherData.main.temp, units)}`,
      `Feels Like: ${formatTemperature(weatherData.main.feels_like, units)}`,
      `Min: ${formatTemperature(weatherData.main.temp_min, units)}`,
      `Max: ${formatTemperature(weatherData.main.temp_max, units)}`,
      `Humidity: ${weatherData.main.humidity}%`,
      `Conditions: ${weatherData.weather[0]?.description || "Unknown"}`,
      `Wind: ${formatWindSpeed(weatherData.wind.speed, units)} at ${weatherData.wind.deg}°`,
      `Cloudiness: ${weatherData.clouds.all}%`,
    ].join("\n");

    return {
      content: [
        {
          type: "text",
          text: weatherText,
        },
      ],
    };
  },
);

server.tool(
  "get-alerts",
  "Get weather alerts for a location anywhere in the world",
  {
    latitude: z.number().min(-90).max(90).describe("Latitude of the location"),
    longitude: z.number().min(-180).max(180).describe("Longitude of the location"),
  },
  async ({ latitude, longitude }) => {
    // Get One Call API data with alerts
    const oneCallData = await makeWeatherAPIRequest<OneCallData>("onecall", {
      lat: latitude,
      lon: longitude,
      exclude: "minutely,hourly,daily,current", // We only need alerts
    });

    if (!oneCallData) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to retrieve alert data for coordinates: ${latitude}, ${longitude}.`,
          },
        ],
      };
    }

    const alerts = oneCallData.alerts || [];
    if (alerts.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: `No active weather alerts for location (${latitude}, ${longitude}).`,
          },
        ],
      };
    }

    const formattedAlerts = alerts.map(formatAlert);
    const alertsText = `Active alerts for ${oneCallData.timezone || `${latitude}, ${longitude}`}:\n\n${formattedAlerts.join("\n")}`;

    return {
      content: [
        {
          type: "text",
          text: alertsText,
        },
      ],
    };
  },
);

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Weather MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
