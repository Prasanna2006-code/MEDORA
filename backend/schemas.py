from pydantic import BaseModel, Field
from typing import Optional


class PatientInput(BaseModel):
    name: str = "Unknown"

    age: int = Field(..., ge=0, le=120)
    sex: str

    symptoms: str
    disorders: Optional[str] = ""

    heart_rate: int = Field(..., ge=20, le=250)
    systolic_bp: int = Field(..., ge=40, le=300)
    diastolic_bp: int = Field(..., ge=20, le=200)

    respiratory_rate: int = Field(..., ge=5, le=80)

    spo2: float = Field(..., ge=50, le=100)

    temperature: float = Field(..., ge=25, le=45)

    pain_score: int = Field(..., ge=0, le=10)

    gcs_score: int = Field(..., ge=3, le=15)

    arrival_mode: str = "Walk-in"


class ReassessmentInput(BaseModel):
    symptoms: Optional[str] = None
    disorders: Optional[str] = None

    heart_rate: Optional[int] = Field(None, ge=20, le=250)
    systolic_bp: Optional[int] = Field(None, ge=40, le=300)
    diastolic_bp: Optional[int] = Field(None, ge=20, le=200)

    respiratory_rate: Optional[int] = Field(None, ge=5, le=80)

    spo2: Optional[float] = Field(None, ge=50, le=100)

    temperature: Optional[float] = Field(None, ge=25, le=45)

    pain_score: Optional[int] = Field(None, ge=0, le=10)

    gcs_score: Optional[int] = Field(None, ge=3, le=15)