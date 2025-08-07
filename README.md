# Mercor Applicant Processing System

This system processes applicant data from Airtable, performs automated screening based on predefined criteria, and uses Google's Gemini AI model to analyze candidates and generate summaries, scores, and follow-up questions.

## Modular Structure

The codebase has been refactored into a modular architecture with the following components:

### 1. Models (`models/`)
Data classes representing the applicant information:
- `PersonalInfo`: Name, email, location, LinkedIn
- `WorkExperience`: Company, title, dates, technologies
- `SalaryPreferences`: Rate, currency, availability
- `Applicant`: Composite of all the above
- `ScreeningResult`: Results of the screening process

### 2. Configuration (`config/`)
Separation of configuration from business logic:
- `airtable_config.py`: Airtable API keys, base IDs, and table names
- `business_rules.py`: Screening criteria (tier-1 companies, max rate, experience requirements, etc.)

### 3. Data Access Layer (`data_access/`)
Handles all interactions with Airtable:
- `airtable_client.py`: Generic Airtable API client for CRUD operations
- `applicant_repository.py`: Applicant-specific data operations

### 4. Services (`services/`)
Business logic separated into dedicated services:
- `llm_service.py`: Integration with Google's Gemini AI
- `screening_service.py`: Applicant screening based on business rules
- `compression_service.py`: Compressing applicant data into JSON structure
- `decompression_service.py`: Rebuilding detailed records from compressed JSON

### 5. Application (`app/`)
Main entry point that orchestrates the modules:
- `main.py`: Command-line interface for compression/decompression operations

## Usage

### Prerequisites
1. Python 3.7+
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in a `.env` file:
   ```
   AIRTABLE_API_KEY=your_airtable_api_key
   AIRTABLE_BASE_ID=your_airtable_base_id
   GEMINI_API_KEY=your_gemini_api_key
   ```

### Compress Applicant Data
To compress applicant data and perform AI analysis:
```bash
python -m app.main compress <applicant_id>
```

### Decompress Applicant Data
To decompress applicant data and rebuild detailed Airtable records:
```bash
python -m app.main decompress <applicant_id>
```

