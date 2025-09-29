from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel

app = FastAPI()

# Valid measures list
VALID_MEASURES = {
    "Violent crime rate",
    "Unemployment",
    "Children in poverty",
    "Diabetic screening",
    "Mammography screening",
    "Preventable hospital stays",
    "Uninsured",
    "Sexually transmitted infections",
    "Physical inactivity",
    "Adult obesity",
    "Premature Death",
    "Daily fine particulate matter",
}

DB_PATH = "data.db"

# Map 2-letter state abbreviations -> FIPS numeric state codes
STATE_FIPS_MAP = {
    "AL": "01","AK": "02","AZ": "04","AR": "05","CA": "06",
    "CO": "08","CT": "09","DE": "10","FL": "12","GA": "13",
    "HI": "15","ID": "16","IL": "17","IN": "18","IA": "19",
    "KS": "20","KY": "21","LA": "22","ME": "23","MD": "24",
    "MA": "25","MI": "26","MN": "27","MS": "28","MO": "29",
    "MT": "30","NE": "31","NV": "32","NH": "33","NJ": "34",
    "NM": "35","NY": "36","NC": "37","ND": "38","OH": "39",
    "OK": "40","OR": "41","PA": "42","RI": "44","SC": "45",
    "SD": "46","TN": "47","TX": "48","UT": "49","VT": "50",
    "VA": "51","WA": "53","WV": "54","WI": "55","WY": "56"
}

class CountyDataRequest(BaseModel):
    zip: str | None = None
    measure_name: str | None = None
    coffee: str | None = None


@app.post("/county_data")
async def county_data(payload: CountyDataRequest):
    # Special case: teapot
    if payload.coffee == "teapot":
        raise HTTPException(status_code=418, detail="I'm a teapot")

    # Required params
    if not payload.zip or not payload.measure_name:
        raise HTTPException(status_code=400, detail="zip and measure_name are required")

    if payload.measure_name not in VALID_MEASURES:
        raise HTTPException(status_code=400, detail="Invalid measure_name")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Step 1: Get state_abbreviation and county_code from zip_county
    cur.execute("SELECT state_abbreviation, county_code FROM zip_county WHERE zip = ?", (payload.zip,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="ZIP not found")

    state_abbr = row["state_abbreviation"]
    county_code = row["county_code"]

    # Step 2: Convert abbreviation → numeric FIPS state code
    state_code = STATE_FIPS_MAP.get(state_abbr)
    if not state_code:
        conn.close()
        raise HTTPException(status_code=400, detail="Unsupported state")

    # Step 3: Query county_health_rankings using codes
    cur.execute(
        """
        SELECT * FROM county_health_rankings
        WHERE fipscode = ? AND measure_name = ?
        """,
        (county_code, payload.measure_name)
    )
    results = cur.fetchall()
    conn.close()

    if not results:
        raise HTTPException(status_code=404, detail="No data found for this zip/measure")

    return [dict(r) for r in results]
