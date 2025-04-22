from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Literal
import json

from .palmetto_data import (
    df_from_address,
    calculate_costs,
    generate_heater_params,
    generate_cooling_params,
    compare_monthly_costs
)

class ConsumptionRecord(BaseModel):
    from_datetime: datetime
    to_datetime: datetime
    variable: Literal['consumption.electricity', 'consumption.fossil_fuel']
    value: float
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class ForecastRequest(BaseModel):
    address: str
    from_datetime: datetime
    to_datetime: datetime
    granularity: Optional[str] = 'hour'
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class HVACRecord(BaseModel):
    variable: Literal['heating', 'cooling']
    start_time: int
    duration: int
    setpoint: int

class ConsumptionRequest(BaseModel):
    forecast: ForecastRequest
    consumption_records: Optional[List[ConsumptionRecord]] = None
    HVAC_info: Optional[List[HVACRecord]] = None

class ForecastResponseRecord(BaseModel):
    month_year: str
    baseline_cost: float
    action_cost: float
    action_savings: float

class ConsumptionResponse(BaseModel):
    monthly_forecasts: List[ForecastResponseRecord]

app = FastAPI(
    title="EnergyMuffin Data API",
    description="API for energy consumption forecasting and cost analysis",
    version="0.1.0"
)

@app.post("/consumption", response_model=ConsumptionResponse)
async def get_consumption(request: ConsumptionRequest):
    """
    Calculate the monthly forecast based on the provided consumption records.
    """
    if not request.forecast:
        raise HTTPException(status_code=400, detail="No forecast information provided")
    
    if not request.consumption_records:
        known_usage_dict = None
    else:
        known_usage_dict = request.consumption_records
    
    baseline_df = df_from_address(
        address=request.forecast.address,
        start_time=request.forecast.from_datetime,
        end_time=request.forecast.to_datetime,
        granularity=request.forecast.granularity,
        known_usage_dict=known_usage_dict,
        baseline_params=None
    )

    if request.HVAC_info:
        baseline_params = []
        for hvac in request.HVAC_info:
            if hvac.variable == 'heating':
                baseline_params.append(generate_heater_params(hvac.start_time, hvac.duration, hvac.setpoint))
            elif hvac.variable == 'cooling':
                baseline_params.append(generate_cooling_params(hvac.start_time, hvac.duration, hvac.setpoint))
        
        action_df = df_from_address(
            address=request.forecast.address,
            start_time=request.forecast.from_datetime,
            end_time=request.forecast.to_datetime,
            granularity=request.forecast.granularity,
            known_usage_dict=known_usage_dict,
            baseline_params=baseline_params
        )
    else:
        action_df = df_from_address(
            address=request.forecast.address,
            start_time=request.forecast.from_datetime,
            end_time=request.forecast.to_datetime,
            granularity=request.forecast.granularity,
            known_usage_dict=known_usage_dict,
            baseline_params=None
        )
    
    monthly_forecast_before = calculate_costs(baseline_df).reset_index()
    monthly_forecast_after = calculate_costs(action_df).reset_index()

    compared_costs = compare_monthly_costs(
        monthly_forecast_before.set_index("from_datetime")["cost"],
        monthly_forecast_after.set_index("from_datetime")["cost"]
    )
    
    json_response = compared_costs.to_json(orient="records", date_format="iso")
    monthly_forecasts = [ForecastResponseRecord(**record) for record in json.loads(json_response)]

    return ConsumptionResponse(monthly_forecasts=monthly_forecasts)    

@app.get("/")
async def root():
    return {"message": "Welcome to the EnergyMuffin Data API!"} 