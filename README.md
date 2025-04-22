# EnergyMuffin Data API

A FastAPI-based service for energy consumption forecasting and cost analysis.

## Features

- Energy consumption forecasting based on address
- HVAC system optimization analysis
- Cost comparison between baseline and optimized scenarios
- Monthly cost savings calculations

## Local Development

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
EIAPI_DEV_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Deployment

### Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Add the following environment variables:
   - `EIAPI_DEV_API_KEY`: Your Palmetto API key
4. Deploy!

The application will be automatically deployed and available at the Railway-provided URL.

## API Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Endpoints

### POST /consumption
Calculate energy consumption forecasts and cost savings.

Request body:
```json
{
  "forecast": {
    "address": "string",
    "from_datetime": "2024-01-01T00:00:00",
    "to_datetime": "2024-12-31T23:59:59",
    "granularity": "hour"
  },
  "consumption_records": [
    {
      "from_datetime": "2024-01-01T00:00:00",
      "to_datetime": "2024-01-01T01:00:00",
      "variable": "consumption.electricity",
      "value": 1.5
    }
  ],
  "HVAC_info": [
    {
      "variable": "heating",
      "start_time": 12,
      "duration": 3,
      "setpoint": 20
    }
  ]
}
```

## Development

This project uses:
- FastAPI for the web framework
- Pandas for data processing
- Python-dotenv for environment variable management
- Gunicorn for production deployment
