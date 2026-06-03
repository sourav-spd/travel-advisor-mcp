# Travel Advisor MCP Server

A production-ready Model Context Protocol (MCP) server that provides comprehensive travel information, destination guides, attraction finder, hotel search, and personalized itinerary planning.

## Features

- **7 Travel Planning Tools**:
  - `travel_connect` - Connect with API key for authentication
  - `search_destinations` - Search for travel destinations by name
  - `get_destination_details` - Get detailed destination information
  - `find_attractions` - Find tourist attractions and points of interest
  - `search_hotels` - Search for hotels and accommodations
  - `get_travel_tips` - Get practical travel tips and recommendations
  - `get_travel_itinerary` - Generate personalized travel itineraries

- **Multiple Transport Modes**:
  - `stdio` - Standard input/output for Claude Desktop, Cursor
  - `sse` - Server-Sent Events for web clients
  - `streamable-http` - MCP v1 preferred HTTP mode

- **Comprehensive Travel Data**: Destinations, attractions, hotels, tips, itineraries
- **Customizable Planning**: Filter by interests, budget, trip duration
- **Production-Ready**: Error handling, logging, session-based authentication

## Installation

```bash
cd travel-advisor-mcp
pip install -e .
```

## API Key Setup

**Demo Mode (Default):** The server works immediately with simulated data - no API key required! Perfect for testing and development.

**Production Mode (Optional):** For real travel APIs (like RapidAPI Travel Advisor), set up authentication:

**Option 1: Use environment variable**
```bash
# Windows PowerShell
$env:RAPIDAPI_KEY = "your_api_key_here"

# Linux/macOS
export RAPIDAPI_KEY="your_api_key_here"
```

**Option 2: Use the travel_connect tool**
Call the `travel_connect` tool with your API key after starting the server.

## Usage

### stdio Mode (Default - for Claude Desktop/Cursor)
```bash
travel-advisor-mcp
```

### SSE Mode (for Web Clients)
```bash
travel-advisor-mcp --mode sse --port 8000
```

### Streamable HTTP Mode (MCP v1)
```bash
travel-advisor-mcp --mode streamable-http --port 8000
```

### Environment Variables

- `MCP_MODE`: Transport mode (`sse`, `streamable-http`, `stdio`) - default: `sse`
- `MCP_HOST`: Host to bind to - default: `0.0.0.0`
- `MCP_PORT`: Port to bind to - default: `8000`
- `RAPIDAPI_KEY`: Optional API key for production use


## Tools

### travel_connect
Connect to the travel API with authentication.

**Parameters:**
- `api_key` (string): RapidAPI key for authentication

### search_destinations
Search for travel destinations by name or query.

**Parameters:**
- `query` (string): Search query (city, country, or region)
- `limit` (integer, optional): Max results (1-30, default: 10)

**Returns:** List of matching destinations with ratings and popular attractions

**Example:** `query: "Paris", limit: 5`

### get_destination_details
Get detailed information about a specific destination.

**Parameters:**
- `destination` (string): Destination name
- `country` (string, optional): Country for disambiguation

**Returns:**
- Overview and description
- Best time to visit (peak/shoulder/off season)
- Climate information
- Top attractions
- Travel tips
- Budget estimates
- Safety ratings

**Example:** `destination: "Rome", country: "Italy"`

### find_attractions
Find tourist attractions and points of interest.

**Parameters:**
- `destination` (string): Destination name
- `category` (string, optional): "all", "landmarks", "museums", "nature", "entertainment", "shopping", "food"
- `limit` (integer, optional): Max results (1-20, default: 10)

**Returns:** Attractions with ratings, descriptions, prices, visit duration

**Example:** `destination: "London", category: "museums", limit: 5`

### search_hotels
Search for hotels and accommodations.

**Parameters:**
- `destination` (string): Destination name
- `check_in` (string, optional): Check-in date (YYYY-MM-DD)
- `check_out` (string, optional): Check-out date (YYYY-MM-DD)
- `guests` (integer, optional): Number of guests (1-10, default: 2)
- `price_range` (string, optional): "budget", "moderate", "upscale", "luxury", "all"
- `limit` (integer, optional): Max results (1-20, default: 10)

**Returns:** Hotels with ratings, prices, amenities, locations

**Example:** `destination: "Tokyo", price_range: "moderate", guests: 2`

### get_travel_tips
Get practical travel tips and recommendations.

**Parameters:**
- `destination` (string): Destination name
- `category` (string, optional): "all", "transportation", "safety", "culture", "food", "budget", "packing"

**Returns:**
- Transportation tips
- Safety advice and emergency numbers
- Cultural customs and etiquette
- Food and dining recommendations
- Budget-saving tips
- Packing essentials
- Money and connectivity info

**Example:** `destination: "Bangkok", category: "safety"`

### get_travel_itinerary
Generate a personalized travel itinerary.

**Parameters:**
- `destination` (string): Destination name
- `duration_days` (integer, optional): Trip duration (1-14, default: 3)
- `interests` (array, optional): ["culture", "history", "nature", "food", "adventure", "relaxation", "nightlife", "shopping"]
- `pace` (string, optional): "relaxed", "moderate", "packed"

**Returns:**
- Day-by-day schedule with activities
- Morning/afternoon/evening plans
- Cost estimates per activity
- Daily tips and recommendations
- Total budget estimate

**Example:** `destination: "Barcelona", duration_days: 5, interests: ["culture", "food"], pace: "moderate"`

## Configuration

### For Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "travel-advisor": {
      "command": "travel-advisor-mcp"
    }
  }
}
```

### For SSE Mode

```json
{
  "mcpServers": {
    "travel-advisor": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## Health Checks

- `GET /` - Root endpoint (returns transport mode)
- `GET /health` - Health check endpoint

## Architecture

```
travel-advisor-mcp/
├── travel_server.py            # Main server with transport modes
├── tools/
│   ├── __init__.py
│   ├── toolhandler.py          # Abstract base class
│   └── travel_tools.py         # 7 travel tool implementations
├── pyproject.toml              # Package configuration
├── LICENSE
└── README.md
```

## Requirements

- Python 3.10+
- mcp[cli] >= 1.12.0
- starlette >= 0.27.0
- uvicorn >= 0.20.0
- httpx >= 0.27.0

## Data Mode

**Current Mode:** Demo Mode with API Integration Support

### Demo Mode (Default)
- Works immediately with comprehensive simulated data
- No external API calls or subscription required
- Perfect for testing, development, and learning MCP
- Includes realistic data for major destinations (Paris, Tokyo, New York, London, Rome, Dubai, Barcelona, Kolkata)

### API Integration (Optional)
- Can connect to RapidAPI Travel Advisor for real-time data
- Supports automatic retry logic and error handling
- Falls back to demo data if API is unavailable
- Session-based connection (not persisted)

## Use Cases

- **Trip Planning**: Generate complete itineraries with attractions and hotels
- **Destination Research**: Get detailed information about any destination
- **Travel Advice**: Access practical tips for transportation, safety, and culture
- **Hotel Booking Research**: Compare accommodations and prices
- **Attraction Discovery**: Find points of interest by category
- **Budget Planning**: Get cost estimates for trips

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please visit the repository.
