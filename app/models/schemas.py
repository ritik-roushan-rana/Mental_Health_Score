from pydantic import BaseModel, Field
from typing import Literal

class MentalHealthInput(BaseModel):
    Age: int = Field(..., ge=18, le=24, description="Age in years")
    Gender: Literal["Male", "Female"]
    Academic_Level: Literal["High School", "Undergraduate", "Graduate"]
    Most_Used_Platform: Literal[
        "Facebook", "LinkedIn", "Instagram", "Snapchat", "Twitter",
        "YouTube", "TikTok", "LINE", "KakaoTalk", "VKontakte", "WhatsApp", "WeChat"
    ]
    Purpose_Of_Use: Literal["Networking", "Education", "Entertainment", "News"]
    Avg_Daily_Usage_Hours: float = Field(..., ge=0, le=12)
    Study_Hours: float = Field(..., ge=0, le=12)
    Physical_Activity_Hours: float = Field(..., ge=0, le=6)
    Sleep_Hours_Per_Night: float = Field(..., ge=0, le=12)
    Stress_Level: Literal["Low", "Medium", "High", "Very High"]
    Country_grouped_Canada: bool = False
    Country_grouped_France: bool = False
    Country_grouped_Germany: bool = False
    Country_grouped_India: bool = False
    Country_grouped_Mexico: bool = False
    Country_grouped_Other: bool = False
    Country_grouped_Turkey: bool = False
    Country_grouped_UK: bool = False
    Country_grouped_USA: bool = False

class PredictionOutput(BaseModel):
    predicted_mental_health_score: float