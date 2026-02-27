from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from utils import process_portfolio
from fastapi import Form

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    company: str = Form(...)
):
    try:
        # Detect correct header row 
        raw_df = pd.read_csv(file.file, encoding="latin1", header=None)
        header_row = raw_df[
            raw_df.iloc[:, 0].astype(str).str.contains("Date", case=False)
        ].index[0]

        file.file.seek(0)
        df = pd.read_csv(file.file, encoding="latin1", skiprows=header_row)

        df.columns = df.columns.str.strip()

        # Clean numeric columns
        df["Qty"] = pd.to_numeric(
            df["Qty"].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )
        df["U P"] = pd.to_numeric(
            df["U P"].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )

        df = df.dropna(subset=["Qty", "U P"])

        # FILTER HERE (before calling process_portfolio)
        filtered_df = df[
            df["Scrip"].str.strip().str.lower()
            == company.strip().lower()
        ]

        if filtered_df.empty:
            return {"message": f"No data found for '{company}'"}

        # Now pass only that company data
        result = process_portfolio(filtered_df)
        
        return result

    except Exception as e:
        return {"error": str(e)}