// Simple test script to verify OpenWeatherMap API works
import * as dotenv from 'dotenv';
import * as path from 'path';
import { fileURLToPath } from 'url';

// Get the directory where the current module is located
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from .env file
dotenv.config({ path: path.resolve(__dirname, '.env') });

const WEATHER_API_KEY = process.env.OPENWEATHERMAP_API_KEY;

if (!WEATHER_API_KEY) {
  console.error("Error: OpenWeatherMap API key not found in environment variables.");
  console.error("Please set OPENWEATHERMAP_API_KEY in your .env file.");
  process.exit(1);
}

console.log("API Key found:", WEATHER_API_KEY.substring(0, 5) + "..." + WEATHER_API_KEY.substring(WEATHER_API_KEY.length - 3));

// Test getting weather for Auckland, NZ
async function testWeatherAPI() {
  console.log("Testing OpenWeatherMap API with Auckland, NZ...");
  
  const url = `https://api.openweathermap.org/data/2.5/weather?q=Auckland,NZ&units=metric&appid=${WEATHER_API_KEY}`;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      const errorBody = await response.text();
      console.error(`Error: HTTP status ${response.status}, body: ${errorBody}`);
      return;
    }
    
    const data = await response.json();
    console.log("API Response for Auckland, NZ:");
    console.log("City:", data.name);
    console.log("Country:", data.sys.country);
    console.log("Temperature:", data.main.temp, "°C");
    console.log("Conditions:", data.weather[0].description);
    console.log("\nAPI is working correctly!");
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

testWeatherAPI(); 