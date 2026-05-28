"""Travel advisor tool implementations for MCP server."""

import json
import os
from collections.abc import Sequence
from typing import Any

import httpx
from mcp.types import TextContent, Tool

from .toolhandler import ToolHandler


# Session state for API key
_session_state = {"api_key": None}


def _get_api_key() -> str:
    """Get the travel API key from session or environment."""
    if _session_state["api_key"]:
        return _session_state["api_key"]
    
    api_key = os.environ.get("RAPIDAPI_KEY", "")
    if not api_key:
        raise ValueError(
            "Travel API key not configured. Either use the travel_connect tool "
            "or set the RAPIDAPI_KEY environment variable."
        )
    return api_key


class TravelConnectToolHandler(ToolHandler):
    """Connect to travel API with API key."""

    def __init__(self) -> None:
        super().__init__("travel_connect")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Connect to the travel advisor API by providing a RapidAPI key. This establishes authentication for subsequent travel queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_key": {
                        "type": "string",
                        "description": "RapidAPI key for authentication (for Travel Advisor API)",
                    }
                },
                "required": ["api_key"],
            },
        )

    async def run_tool(self, args: dict) -> Sequence[TextContent]:
        self.validate_required_args(args, ["api_key"])
        api_key = args["api_key"]
        
        # Store the API key in session state
        _session_state["api_key"] = api_key
        
        result = {
            "status": "connected",
            "message": "Successfully connected to Travel Advisor API",
            "api_key_prefix": api_key[:8] + "...",
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


class SearchDestinationsToolHandler(ToolHandler):
    """Search for travel destinations."""

    def __init__(self) -> None:
        super().__init__("search_destinations")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Search for travel destinations by name or query. Returns a list of matching destinations with basic information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (city, country, or region name)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-30)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 30,
                    },
                },
                "required": ["query"],
            },
        )

    async def run_tool(self, args: dict) -> Sequence[TextContent]:
        self.validate_required_args(args, ["query"])
        query = args["query"]
        limit = args.get("limit", 10)
        api_key = _get_api_key()
        
        # Simulated travel destination search
        # In a real implementation, this would call a travel API
        destinations = []
        
        # Sample destinations based on query
        sample_data = {
            "paris": {
                "name": "Paris", 
                "country": "France",
                "type": "City",
                "description": "City of Light, capital of France",
                "rating": 4.7,
                "popular_attractions": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral"]
            },
            "tokyo": {
                "name": "Tokyo",
                "country": "Japan",
                "type": "City",
                "description": "Japan's bustling capital mixing ultra-modern with traditional",
                "rating": 4.6,
                "popular_attractions": ["Senso-ji Temple", "Tokyo Tower", "Meiji Shrine"]
            },
            "new york": {
                "name": "New York City",
                "country": "United States",
                "type": "City",
                "description": "The city that never sleeps",
                "rating": 4.5,
                "popular_attractions": ["Statue of Liberty", "Central Park", "Times Square"]
            },
            "london": {
                "name": "London",
                "country": "United Kingdom",
                "type": "City",
                "description": "Historic capital with royal palaces and modern culture",
                "rating": 4.6,
                "popular_attractions": ["Big Ben", "British Museum", "Tower of London"]
            },
            "rome": {
                "name": "Rome",
                "country": "Italy",
                "type": "City",
                "description": "Eternal City with ancient ruins and Renaissance art",
                "rating": 4.8,
                "popular_attractions": ["Colosseum", "Vatican City", "Trevi Fountain"]
            },
        }
        
        query_lower = query.lower()
        for key, data in sample_data.items():
            if query_lower in key or query_lower in data["name"].lower() or query_lower in data["country"].lower():
                destinations.append(data)
                if len(destinations) >= limit:
                    break
        
        # If no matches, provide generic result
        if not destinations:
            destinations.append({
                "name": query.title(),
                "country": "Unknown",
                "type": "Destination",
                "description": f"Travel destination: {query}",
                "rating": 4.0,
                "popular_attractions": ["Various attractions"]
            })
        
        result = {
            "query": query,
            "result_count": len(destinations),
            "destinations": destinations[:limit],
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


class GetDestinationDetailsToolHandler(ToolHandler):
    """Get detailed information about a destination."""

    def __init__(self) -> None:
        super().__init__("get_destination_details")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Get detailed information about a specific travel destination including attractions, best time to visit, climate, and travel tips.",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Destination name (city or region)",
                    },
                    "country": {
                        "type": "string",
                        "description": "Country name (optional, helps with disambiguation)",
                        "default": "",
                    },
                },
                "required": ["destination"],
            },
        )

    async def run_tool(self, args: dict) -> Sequence[TextContent]:
        self.validate_required_args(args, ["destination"])
        destination = args["destination"]
        country = args.get("country", "")
        api_key = _get_api_key()
        
        # Simulated destination details
        result = {
            "destination": destination,
            "country": country if country else "Various",
            "overview": {
                "description": f"{destination} is a popular travel destination known for its culture, attractions, and hospitality.",
                "rating": 4.5,
                "visitor_count_annual": "Millions of visitors",
            },
            "best_time_to_visit": {
                "peak_season": "June to August",
                "shoulder_season": "April to May, September to October",
                "off_season": "November to March",
                "recommendation": "Visit during shoulder season for better weather and fewer crowds",
            },
            "climate": {
                "average_temp_summer": "25-30°C (77-86°F)",
                "average_temp_winter": "5-10°C (41-50°F)",
                "rainy_season": "October to March",
            },
            "top_attractions": [
                "Historic landmarks and monuments",
                "Museums and cultural centers",
                "Local markets and shopping districts",
                "Parks and natural areas",
                "Restaurants and local cuisine"
            ],
            "travel_tips": [
                "Book accommodations in advance during peak season",
                "Learn basic phrases in the local language",
                "Try local cuisine and street food",
                "Use public transportation to save money",
                "Respect local customs and traditions"
            ],
            "estimated_daily_budget": {
                "budget": "$50-100",
                "mid_range": "$100-200",
                "luxury": "$200+"
            },
            "safety_rating": "Generally safe for tourists",
            "language": "Local language (English widely spoken in tourist areas)",
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


class FindAttractionsToolHandler(ToolHandler):
    """Find tourist attractions in a destination."""

    def __init__(self) -> None:
        super().__init__("find_attractions")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Find tourist attractions and points of interest in a specific destination. Returns attractions with ratings, descriptions, and visitor information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Destination name (city or region)",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["all", "landmarks", "museums", "nature", "entertainment", "shopping", "food"],
                        "description": "Category of attractions to search for",
                        "default": "all",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of attractions to return (1-20)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 20,
                    },
                },
                "required": ["destination"],
            },
        )

    async def run_tool(self, args: dict) -> Sequence[TextContent]:
        self.validate_required_args(args, ["destination"])
        destination = args["destination"]
        category = args.get("category", "all")
        limit = args.get("limit", 10)
        api_key = _get_api_key()
        
        # Simulated attractions data
        attractions = []
        
        sample_attractions = [
            {
                "name": f"{destination} Historic Center",
                "category": "landmarks",
                "rating": 4.7,
                "description": "Historic district with centuries-old architecture",
                "price_level": "Free",
                "estimated_visit_duration": "2-3 hours",
                "best_time": "Morning",
            },
            {
                "name": f"{destination} National Museum",
                "category": "museums",
                "rating": 4.6,
                "description": "Premier museum showcasing art and history",
                "price_level": "$15-25",
                "estimated_visit_duration": "2-4 hours",
                "best_time": "Afternoon",
            },
            {
                "name": f"{destination} Central Park",
                "category": "nature",
                "rating": 4.5,
                "description": "Beautiful urban park with gardens and trails",
                "price_level": "Free",
                "estimated_visit_duration": "1-3 hours",
                "best_time": "Early morning or evening",
            },
            {
                "name": f"{destination} Local Market",
                "category": "shopping",
                "rating": 4.4,
                "description": "Vibrant market with local crafts and food",
                "price_level": "Varies",
                "estimated_visit_duration": "1-2 hours",
                "best_time": "Morning",
            },
            {
                "name": f"{destination} Observation Tower",
                "category": "landmarks",
                "rating": 4.8,
                "description": "Iconic tower with panoramic city views",
                "price_level": "$20-35",
                "estimated_visit_duration": "1-2 hours",
                "best_time": "Sunset",
            },
        ]
        
        # Filter by category if specified
        for attraction in sample_attractions:
            if category == "all" or attraction["category"] == category:
                attractions.append(attraction)
                if len(attractions) >= limit:
                    break
        
        result = {
            "destination": destination,
            "category": category,
            "result_count": len(attractions),
            "attractions": attractions[:limit],
            "tips": [
                "Book popular attractions in advance to avoid lines",
                "Consider getting a city pass for multiple attractions",
                "Check opening hours before visiting",
            ]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


class SearchHotelsToolHandler(ToolHandler):
    """Search for hotels and accommodations."""

    def __init__(self) -> None:
        super().__init__("search_hotels")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Search for hotels and accommodations in a destination. Returns hotels with ratings, prices, and amenities.",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Destination name (city or region)",
                    },
                    "check_in": {
                        "type": "string",
                        "description": "Check-in date (YYYY-MM-DD format)",
                        "default": "",
                    },
                    "check_out": {
                        "type": "string",
                        "description": "Check-out date (YYYY-MM-DD format)",
                        "default": "",
                    },
                    "guests": {
                        "type": "integer",
                        "description": "Number of guests",
                        "default": 2,
                        "minimum": 1,
                        "maximum": 10,
                    },
                    "price_range": {
                        "type": "string",
                        "enum": ["budget", "moderate", "upscale", "luxury", "all"],
                        "description": "Price range category",
                        "default": "all",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of hotels to return (1-20)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 20,
                    },
                },
                "required": ["destination"],
            },
        )

    async def run_tool(self, args: dict) -> Sequence[TextContent]:
        self.validate_required_args(args, ["destination"])
        destination = args["destination"]
        check_in = args.get("check_in", "")
        check_out = args.get("check_out", "")
        guests = args.get("guests", 2)
        price_range = args.get("price_range", "all")
        limit = args.get("limit", 10)
        api_key = _get_api_key()
        
        # Simulated hotel data
        hotels = []
        
        sample_hotels = [
            {
                "name": f"Grand {destination} Hotel",
                "rating": 4.5,
                "stars": 5,
                "price_per_night": "$250-400",
                "price_category": "luxury",
                "location": "City Center",
                "amenities": ["WiFi", "Pool", "Spa", "Gym", "Restaurant", "Room Service"],
                "distance_to_center": "0.5 km",
                "guest_reviews": 1250,
            },
            {
                "name": f"{destination} Boutique Inn",
                "rating": 4.3,
                "stars": 4,
                "price_per_night": "$150-250",
                "price_category": "upscale",
                "location": "Historic District",
                "amenities": ["WiFi", "Breakfast", "Concierge", "Bar"],
                "distance_to_center": "1.2 km",
                "guest_reviews": 890,
            },
            {
                "name": f"Comfort Stay {destination}",
                "rating": 4.0,
                "stars": 3,
                "price_per_night": "$80-150",
                "price_category": "moderate",
                "location": "Near Metro",
                "amenities": ["WiFi", "Breakfast", "Parking"],
                "distance_to_center": "2.5 km",
                "guest_reviews": 645,
            },
            {
                "name": f"Budget Lodge {destination}",
                "rating": 3.8,
                "stars": 2,
                "price_per_night": "$40-80",
                "price_category": "budget",
                "location": "Outskirts",
                "amenities": ["WiFi", "Basic Breakfast"],
                "distance_to_center": "5 km",
                "guest_reviews": 420,
            },
        ]
        
        # Filter by price range if specified
        for hotel in sample_hotels:
            if price_range == "all" or hotel["price_category"] == price_range:
                hotels.append(hotel)
                if len(hotels) >= limit:
                    break
        
        result = {
            "destination": destination,
            "search_params": {
                "check_in": check_in if check_in else "Not specified",
                "check_out": check_out if check_out else "Not specified",
                "guests": guests,
                "price_range": price_range,
            },
            "result_count": len(hotels),
            "hotels": hotels[:limit],
            "booking_tips": [
                "Prices may vary based on dates and availability",
                "Book early for better rates and selection",
                "Check cancellation policies before booking",
                "Consider location relative to attractions you want to visit",
            ]
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


class GetTravelTipsToolHandler(ToolHandler):
    """Get travel tips and recommendations for a destination."""

    def __init__(self) -> None:
        super().__init__("get_travel_tips")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Get practical travel tips, recommendations, and insider advice for a specific destination including transportation, safety, customs, and money-saving tips.",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Destination name (city, region, or country)",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["all", "transportation", "safety", "culture", "food", "budget", "packing"],
                        "description": "Specific category of tips",
                        "default": "all",
                    },
                },
                "required": ["destination"],
            },
        )

    async def run_tool(self, args: dict) -> Sequence[TextContent]:
        self.validate_required_args(args, ["destination"])
        destination = args["destination"]
        category = args.get("category", "all")
        api_key = _get_api_key()
        
        # Comprehensive travel tips
        tips = {
            "destination": destination,
            "general_tips": [
                "Research local customs and etiquette before arrival",
                "Keep copies of important documents",
                "Notify your bank of travel plans",
                "Download offline maps of the area",
            ],
            "transportation": {
                "getting_around": [
                    "Public transportation is efficient and cost-effective",
                    "Consider getting a transit pass for multiple days",
                    "Taxis/rideshares are widely available",
                    "Walking is great for exploring central areas",
                ],
                "from_airport": [
                    "Airport shuttle buses available",
                    "Metro/train connection to city center",
                    "Taxi/rideshare costs approximately $30-50",
                ],
            },
            "safety": {
                "general": [
                    "Keep valuables secure and out of sight",
                    "Be aware of your surroundings, especially at night",
                    "Use hotel safe for passports and extra cash",
                    "Keep emergency numbers saved in your phone",
                ],
                "common_scams": [
                    "Be cautious of overly friendly strangers offering help",
                    "Verify taxi meters are running",
                    "Check restaurant bills for accuracy",
                ],
                "emergency_numbers": {
                    "police": "Local emergency number",
                    "ambulance": "Local emergency number",
                    "embassy": "Contact nearest embassy/consulate",
                },
            },
            "culture_and_customs": {
                "dress_code": "Dress modestly when visiting religious sites",
                "tipping": "Tipping customs vary; research local practices",
                "greetings": "Learn basic greetings in local language",
                "etiquette": [
                    "Respect local customs and traditions",
                    "Ask permission before taking photos of people",
                    "Remove shoes when entering homes or temples",
                ],
            },
            "food_and_dining": {
                "what_to_try": [
                    "Local street food (from busy vendors)",
                    "Regional specialties and traditional dishes",
                    "Fresh local produce at markets",
                ],
                "tips": [
                    "Eat where locals eat for authentic experience",
                    "Try breakfast at local cafes",
                    "Ask for recommendations from hotel staff",
                    "Be adventurous but cautious with street food hygiene",
                ],
                "water": "Drink bottled water if tap water safety is uncertain",
            },
            "budget_tips": [
                "Visit free attractions and museums on discount days",
                "Eat at local restaurants away from tourist areas",
                "Shop at local markets for souvenirs",
                "Use public transportation instead of taxis",
                "Book activities and tours in advance for discounts",
                "Consider staying in neighborhoods outside city center",
            ],
            "packing_essentials": [
                "Comfortable walking shoes",
                "Weather-appropriate clothing",
                "Power adapter for local outlets",
                "Basic first aid kit and medications",
                "Reusable water bottle",
                "Daypack for excursions",
                "Travel insurance documentation",
            ],
            "money_matters": {
                "currency": "Local currency recommended",
                "exchange": "Use ATMs for best rates; avoid airport exchanges",
                "cards": "Credit cards widely accepted in cities",
                "cash": "Carry some cash for small purchases and tips",
            },
            "connectivity": {
                "wifi": "WiFi available in most hotels, cafes, and public spaces",
                "phone": "Consider local SIM card or international roaming plan",
                "apps": "Download useful apps: maps, translation, transportation",
            },
        }
        
        # Filter by category if requested
        if category != "all":
            filtered_tips = {
                "destination": destination,
                "category": category,
                "tips": tips.get(category, tips["general_tips"]),
            }
            return [TextContent(type="text", text=json.dumps(filtered_tips, indent=2))]
        
        return [TextContent(type="text", text=json.dumps(tips, indent=2))]


class GetTravelItineraryToolHandler(ToolHandler):
    """Generate a travel itinerary for a destination."""

    def __init__(self) -> None:
        super().__init__("get_travel_itinerary")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Generate a suggested travel itinerary for a destination based on duration and interests. Returns day-by-day schedule with activities and recommendations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Destination name (city or region)",
                    },
                    "duration_days": {
                        "type": "integer",
                        "description": "Number of days for the trip (1-14)",
                        "default": 3,
                        "minimum": 1,
                        "maximum": 14,
                    },
                    "interests": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["culture", "history", "nature", "food", "adventure", "relaxation", "nightlife", "shopping"]
                        },
                        "description": "Travel interests to customize itinerary",
                        "default": ["culture", "food"],
                    },
                    "pace": {
                        "type": "string",
                        "enum": ["relaxed", "moderate", "packed"],
                        "description": "Trip pace preference",
                        "default": "moderate",
                    },
                },
                "required": ["destination"],
            },
        )

    async def run_tool(self, args: dict) -> Sequence[TextContent]:
        self.validate_required_args(args, ["destination"])
        destination = args["destination"]
        duration_days = args.get("duration_days", 3)
        interests = args.get("interests", ["culture", "food"])
        pace = args.get("pace", "moderate")
        api_key = _get_api_key()
        
        # Generate sample itinerary
        itinerary = {
            "destination": destination,
            "duration": f"{duration_days} days",
            "interests": interests,
            "pace": pace,
            "days": []
        }
        
        # Generate day-by-day schedule
        for day_num in range(1, min(duration_days + 1, 4)):  # Show up to 3 days as example
            day_plan = {
                "day": day_num,
                "theme": "culture" if "culture" in interests else "exploration",
                "schedule": {
                    "morning": {
                        "time": "9:00 AM - 12:00 PM",
                        "activity": f"Visit {destination} Historic Center",
                        "description": "Explore historic landmarks and architecture",
                        "estimated_cost": "$0-20",
                    },
                    "lunch": {
                        "time": "12:00 PM - 1:30 PM",
                        "activity": "Local Restaurant",
                        "description": "Try traditional cuisine",
                        "estimated_cost": "$15-30",
                    },
                    "afternoon": {
                        "time": "2:00 PM - 5:00 PM",
                        "activity": f"{destination} Museum or Attraction",
                        "description": "Cultural experience or sightseeing",
                        "estimated_cost": "$10-25",
                    },
                    "evening": {
                        "time": "6:00 PM - 9:00 PM",
                        "activity": "Dinner and Evening Stroll",
                        "description": "Enjoy local dining and nightlife",
                        "estimated_cost": "$25-50",
                    },
                },
                "tips": [
                    "Book popular attractions in advance",
                    "Wear comfortable walking shoes",
                    "Bring water and sunscreen",
                ],
            }
            itinerary["days"].append(day_plan)
        
        if duration_days > 3:
            itinerary["days"].append({
                "note": f"Days 4-{duration_days} would include additional attractions, day trips, and activities based on your interests"
            })
        
        itinerary["general_recommendations"] = [
            "Start days early to avoid crowds",
            "Balance busy sightseeing days with relaxation time",
            "Leave flexibility for spontaneous discoveries",
            "Consider a day trip to nearby attractions",
            "Reserve last day for shopping and final experiences",
        ]
        
        itinerary["estimated_total_cost"] = {
            "budget": f"${duration_days * 100}-${duration_days * 200}",
            "moderate": f"${duration_days * 200}-${duration_days * 400}",
            "luxury": f"${duration_days * 400}+",
            "note": "Costs exclude flights and accommodation",
        }
        
        return [TextContent(type="text", text=json.dumps(itinerary, indent=2))]
