# emilygao12-hw4

# County Data API


- **Live Deployment:** https://emilygao12-hw4.vercel.app
- **Backend:** A FastAPI service deployed on Vercel at `/api/county_data`.  
- **Frontend:** A static HTML page served at `/`, which allows users to enter a ZIP code and select a health measure to query.  
---

## 🚀 Features
- **/api/county_data** (POST):  
  Accepts JSON input with a ZIP code and a measure name. Returns matching records from the `county_health_rankings` SQLite database.  

  Example request:
  ```json
  {
    "zip": "02138",
    "measure_name": "Adult obesity"
  }
