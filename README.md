# Mercor Applicant Processing System

This system is designed to streamline the applicant evaluation process by integrating with Airtable and leveraging Google's Gemini AI model. It automates the screening of candidates based on predefined business criteria and provides AI-powered analysis to generate comprehensive candidate summaries, scores, and follow-up questions.

The system operates in two primary modes:
1. **Compression**: Extracts detailed applicant information from multiple Airtable tables, consolidates it into a compact JSON format, performs automated screening, and uses Gemini AI to analyze the candidate profile.
2. **Decompression**: Takes the compressed JSON data and rebuilds detailed records in the appropriate Airtable tables.

## Key Features

- **Automated Screening**: Evaluates candidates based on configurable business rules including work experience, tier-1 company employment, compensation requirements, and location preferences.
- **AI-Powered Analysis**: Uses Google's Gemini AI to provide qualitative assessments, scoring, and generate relevant follow-up questions for shortlisted candidates.
- **Airtable Integration**: Seamlessly reads from and writes to multiple Airtable tables (Personal Details, Work Experience, Salary Preferences, Applicants, Shortlisted Leads).
- **Duplicate Prevention**: Implements robust logic to prevent duplicate records during both compression and decompression operations.
- **Structured Logging**: Replaces all print statements with proper logging for better traceability and debugging.
- **Highly Configurable**: Business rules, API keys, and table mappings can be easily modified through dedicated configuration files without changing core logic.

## Modular Architecture

The codebase follows a clean, modular architecture with well-defined separation of concerns:

### 1. Models (`models/`)
Data classes that represent the core entities in the system:
- `PersonalInfo`: Contains personal details such as full name, email address, location, and LinkedIn profile URL
- `WorkExperience`: Represents professional experience with company name, title, start/end dates, and technologies used
- `SalaryPreferences`: Stores compensation details including preferred and minimum hourly rates, currency, and weekly availability
- `Applicant`: A composite model that aggregates PersonalInfo, WorkExperience, and SalaryPreferences
- `ScreeningResult`: Encapsulates the results of the screening process including status, score, and reasoning

### 2. Configuration (`config/`)
Centralized configuration management separate from business logic:
- `airtable_config.py`: Manages Airtable API authentication, base identification, and table name mappings
- `business_rules.py`: Defines configurable screening criteria such as tier-1 company lists, maximum rate thresholds, minimum experience requirements, and approved countries

The system is highly configurable through these Python configuration files. Business rules can be easily adjusted without modifying the core logic:
- Modify screening criteria by updating values in `business_rules.py`
- Change Airtable table names or field mappings in `airtable_config.py`
- Update API keys and base IDs in the `.env` file

This configuration approach allows for rapid adaptation to different business requirements or Airtable schemas without touching the application logic.

### 3. Data Access Layer (`data_access/`)
Handles all interactions with the Airtable API:
- `airtable_client.py`: A generic client that implements CRUD operations (Create, Read, Update, Delete) for Airtable records with proper error handling
- `applicant_repository.py`: Repository pattern implementation that provides applicant-specific data operations, including fetching and saving data across multiple related tables

### 4. Services (`services/`)
Business logic separated into dedicated services:
- `llm_service.py`: Integration with Google's Gemini AI API for natural language processing and analysis
- `screening_service.py`: Implements applicant screening logic based on business rules defined in configuration
- `compression_service.py`: Consolidates applicant data from multiple Airtable tables into a single compressed JSON structure
- `decompression_service.py`: Rebuilds detailed Airtable records from compressed JSON data

### 5. Application (`app/`)
Main entry point that orchestrates all modules:
- `main.py`: Command-line interface that handles both compression and decompression operations through simple commands

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

