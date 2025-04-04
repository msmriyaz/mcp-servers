# System Patterns: Weather Anywhere MCP

## Architecture Pattern
The Weather Anywhere MCP follows a **tool-based microservice architecture** pattern where specialized tools are registered with the MCP server to handle specific weather-related queries. This follows the Model Context Protocol design principles.

## Core Design Patterns

### Command Pattern
Each weather tool (get-weather, get-forecast, get-alerts) implements a command pattern:
- Each command has a clear responsibility
- Commands are parameterized via Zod schema definitions
- Commands encapsulate API calls and formatting logic
- Commands return standardized response objects

### Adapter Pattern
The system acts as an adapter between Claude and the OpenWeatherMap API:
- Translates Claude's tool invocations into OpenWeatherMap API calls
- Converts OpenWeatherMap responses into Claude-friendly formats
- Handles unit conversions (metric/imperial)

### Facade Pattern
The MCP server presents a simplified interface to Claude, hiding the complexity of:
- API authentication
- HTTP request handling
- Response parsing
- Error management

## Data Flow Pattern

```
┌─────────┐    ┌───────────┐    ┌────────────────┐    ┌──────────────────┐
│ Claude  │───▶│ MCP Server│───▶│ Weather API    │───▶│ OpenWeatherMap   │
│         │    │           │    │ Client         │    │ API              │
└─────────┘    └───────────┘    └────────────────┘    └──────────────────┘
     ▲               │                  ▲                      │
     │               │                  │                      │
     │               ▼                  │                      ▼
     │         ┌──────────┐             │              ┌──────────────┐
     │         │ Parameter │             │              │ Weather Data │
     │         │ Validation│             │              │ (JSON)       │
     │         └──────────┘             │              └──────────────┘
     │                                  │                      │
     │                                  │                      │
     │                                  │                      ▼
     │                                  │              ┌──────────────┐
     │                                  └──────────────│ Data         │
     │                                                 │ Formatting   │
     │                                                 └──────────────┘
     │                                                        │
     │                                                        ▼
     │                                                 ┌──────────────┐
     └─────────────────────────────────────────────────│ Formatted    │
                                                       │ Response     │
                                                       └──────────────┘
```

## Error Handling Pattern
The system implements a **graceful degradation** error handling pattern:
- API errors are caught and logged
- User-friendly error messages are returned
- The system continues running even after encountering errors
- Detailed error information is logged for debugging

## Interface Patterns

### Tool Interface
Each tool follows a consistent interface pattern:
1. **Name**: Short, descriptive identifier
2. **Description**: Human-readable explanation
3. **Parameters**: Zod schema for input validation
4. **Handler Function**: Async function that processes the request

### Response Format
Responses follow a standard structure:
```typescript
{
  content: [
    {
      type: "text",
      text: string // Formatted weather information
    }
  ]
}
```

## Code Organization Pattern
The codebase is organized following these patterns:
1. **Interface Definitions**: Strong typing for API responses
2. **Helper Functions**: Reusable formatting and request utilities
3. **Tool Definitions**: Tool schemas and handlers
4. **Server Configuration**: MCP server setup

## Configuration Pattern
Configuration uses environment variables loaded via dotenv:
- API keys stored outside of code
- Path resolution for finding .env in various execution contexts
- Validation at startup with clear error messages 