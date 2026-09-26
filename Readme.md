# INF601 - Advanced Programming in Python

## Scheduled Check-In Bot

**Author:** Gabriel Itegbe

## Project Overview

This project is a scheduled Python bot that automates interactions with the Practice Hub REST API. It runs on a daily GitHub Actions cron schedule to perform two main tasks:

- **Data Collection:** Fetches all instructor posts, handles API pagination, saves the post content to `artifact/collected.json`, and downloads all attachments to `artifact/files/`.
- **Automated Check-Ins:** Identifies open "check-in" posts by the instructor and automatically posts a reply comment within the allowed time window.

## What Was Implemented

- Built a Python script (`main.py`) utilizing the `requests` library to interface with the API.
- Implemented API pagination using `limit` and `offset` parameters to iterate through all available posts.
- Added conditional logic to filter posts specifically by the instructor's ID (`7`).
- Configured absolute file paths using `os.path` to ensure the `artifact/` directory always generates correctly within the project structure.
- Handled graceful error catching for HTTP `423` status codes to avoid crashing when a check-in window is closed.
- Managed sensitive credentials locally using a `.env` file, `python-dotenv`, and a `.gitignore` file to prevent token leakage.
- Created a GitHub Actions workflow (`main.yml`) that triggers on both a cron schedule and a manual `workflow_dispatch`.
- Configured GitHub Actions repository secrets and variables (`PRACTICE_API_TOKEN`, `PRACTICE_API_URL`, `INSTRUCTOR_ID`) to securely pass credentials to the runner.
- Granted the GitHub Actions runner read and write workflow permissions to automatically commit the generated `artifact/` directory back to the main repository.

## Project Structure

```
.
├── main.py                     # The bot
├── requirements.txt            # Python dependencies
├── .github/workflows/main.yml  # GitHub Actions workflow
├── .gitignore                  # Ignores .venv/, .env, __pycache__/
└── artifact/
    ├── collected.json          # Instructor posts (written by the bot)
    └── files/                  # Downloaded attachments
```

## Running Locally

```bash
git clone https://github.com/Techman261/checkinbotGabriel_Itegbe.git
cd checkinbotGabriel_Itegbe

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```env
PRACTICE_API_TOKEN=your-token-here
PRACTICE_API_URL=https://practice.fhsucyber.com
INSTRUCTOR_ID=7
```

Then run:

```bash
python main.py
```

AI-Generated Components:

Initial Code Structure: AI was used to draft the initial boilerplate for main.py and the GitHub Actions workflow YAML configuration (.github/workflows/checkin.yml).

API Schema Alignment: AI assisted in analyzing the OpenAPI 3.1.0 Swagger specification for the Practice Hub API to ensure correct endpoint paths, request query parameters (offset, limit, author), header tokens (Bearer), and payload structures.

Human Modifications & Customizations:

Endpoint & Parameter Adjustments: Modified the pagination logic in main.py to use offset and limit query parameters instead of page numbers to strictly match the server's OpenAPI schema.

Authentication & Identity Matching: Integrated GET /api/v1/me dynamic checks to identify the account's user ID so duplicate replies are strictly avoided across manual and automated runs.

Attachment Endpoint Handling: Configured fallback download logic to retrieve files either via direct download_url properties or the /api/v1/attachments/{attachment_id} endpoint.

Error Handling: Added exception handling and HTTP 423 (Locked/Closed Window) status code checks to ensure the workflow runs smoothly without failing when check-in windows expire.

Workflow Configuration: Custom-tailored the GitHub Actions commit step to automatically push updated artifact/ contents back to the main repository branch after each run.