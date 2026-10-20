# Big Data Retail Sales Analytics

An interactive retail analytics dashboard built with **Python, Pandas, Plotly, and Streamlit**, using the public **UCI Online Retail** dataset. An optional **PySpark batch job** demonstrates distributed data processing for the NPTEL Big Data Analytics course.

## Features

- Revenue, order, customer, units-sold, and average-order-value KPIs
- Monthly revenue trend
- Top products by revenue
- Top countries by revenue
- Revenue by weekday
- Date, country, and minimum line-item revenue filters
- Transaction table and filtered CSV download
- Optional PySpark aggregation job for monthly, country, and product reports

## Dataset

The app downloads the dataset ZIP from the [UCI Machine Learning Repository — Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail) when it first runs. You do not need to commit the dataset file to GitHub.

The dataset describes transactions for a UK-based online retailer between 2010 and 2011. See the UCI page for the official description and reuse terms.

## Run the dashboard locally

Python 3.11 or 3.12 is recommended.

### 1. Clone your repository

```bash
git clone https://github.com/YOUR-USERNAME/retail-sales-analytics.git
cd retail-sales-analytics
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start the dashboard

```bash
streamlit run app.py
```

The terminal will show a local URL, normally `http://localhost:8501`. The first run downloads the dataset and may take a little while.

## Deploy to GitHub and Streamlit Community Cloud

1. Create a GitHub account at https://github.com if you do not already have one.
2. Create a **public** repository named `retail-sales-analytics`.
3. Put `app.py`, `requirements.txt`, `README.md`, `pyspark_job.py`, `requirements-spark.txt`, and `.gitignore` in the repository root.
4. Do **not** upload the downloaded dataset or virtual environment. `.gitignore` excludes local `data/` and `output/` folders.
5. Upload files using GitHub's **Add file → Upload files** option, or use Git from your project folder:

```bash
git init
git add app.py requirements.txt requirements-spark.txt pyspark_job.py README.md .gitignore
git commit -m "Build retail sales analytics dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/retail-sales-analytics.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. If GitHub says the remote already exists, inspect it with `git remote -v` rather than adding it again.

6. Open https://share.streamlit.io and sign in with GitHub.
7. Choose **Create app** (or **Deploy an app**).
8. Select your repository, branch `main`, and main file path `app.py`.
9. In advanced settings, choose Python 3.12 if offered.
10. Click **Deploy** and wait for the build logs to finish.
11. Open the generated `*.streamlit.app` URL and test the filters.

Streamlit Community Cloud reads dependencies from `requirements.txt`. If deployment fails, open the app's logs and look for the first dependency or data-download error.

## Optional: run the PySpark analytics job

The PySpark job is a separate, local batch-processing demonstration. It is not required to deploy the Streamlit dashboard.

### Important XLSX note

PySpark does not read Excel natively. Save `Online_Retail.xlsx` as CSV using Excel or LibreOffice, then run:

```bash
pip install -r requirements-spark.txt
spark-submit pyspark_job.py --input data/Online_Retail.csv --output output
```

Make sure the CSV has the original column headers. The job creates Spark output folders:
- `output/monthly_sales/`
- `output/country_sales/`
- `output/top_products/`

Spark writes a folder containing one or more part files rather than one CSV file. Java must be installed and compatible with your PySpark version. If `spark-submit` is not found, confirm Spark/PySpark is installed in the active environment.

## Data cleaning and metric definitions

- Revenue per line item = `Quantity × UnitPrice`
- Cancelled invoices (invoice numbers beginning with `C`) are excluded.
- Rows with missing key fields, non-positive quantities, or non-positive unit prices are excluded from the sales dashboard.
- Orders are distinct invoice numbers; customer count is distinct non-null customer IDs.
- This is a descriptive analytics project, not a production accounting system. The results depend on the cleaning rules and selected filters.

## Suggested project report structure

1. Abstract and problem statement
2. Dataset description and data dictionary
3. System architecture
4. Data cleaning and preprocessing
5. Analytics methods and KPI definitions
6. Dashboard screenshots and findings
7. PySpark distributed aggregation (optional)
8. Limitations and future enhancements
9. Conclusion and references

## References

- [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail)
- [Streamlit Community Cloud deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Streamlit dependency management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)

## License

Choose a license for your code (for example, MIT) if you want others to reuse it. Check the dataset page's terms separately; a code license does not override dataset terms.
