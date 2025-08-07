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

## Setup Steps and Field Definitions

### Airtable Base Structure
The system requires a specific Airtable base structure with the following tables:

1. **Applicants**
   - `ApplicantId` (Unique identifier for each applicant)
   - `Personal Details` (Linked record to Personal Details table)
   - `CompressedJSON` (Long text field to store compressed applicant data)
   - `Shortlist Status` (Single select field with options: "Shortlisted", "Not Shortlisted")
   - `LLM Score` (Integer field for AI-generated quality score)
   - `Screening Reason` (Long text field explaining why applicant was shortlisted/not shortlisted)

2. **Personal Details**
   - `ApplicantId` (Unique identifier matching the Applicants table)
   - `Name` (Full name of the applicant)
   - `Email` (Email address)
   - `Location` (Country of residence)
   - `LinkedIn Profile` (URL to LinkedIn profile)

3. **Work Experience**
   - `Personal Details` (Linked record to Personal Details table)
   - `Company` (Company name)
   - `Title` (Job title)
   - `Start` (Start date in YYYY-MM-DD format)
   - `End` (End date in YYYY-MM-DD format)
   - `Technologies` (Comma-separated list of technologies used)

4. **Salary Preferences**
   - `Personal Details` (Linked record to Personal Details table)
   - `Preferred Rate` (Hourly rate in USD)
   - `Minimum Rate` (Minimum acceptable hourly rate in USD)
   - `Currency` (Currency code, e.g., USD)
   - `Availability` (Hours available per week)

5. **Shortlisted Leads**
   - `Applicants` (Linked record to Applicants table)
   - `Summary` (Long text field for AI-generated summary)
   - `Score` (Integer field for AI-generated quality score)
   - `Issues` (Long text field listing data gaps or inconsistencies)
   - `Follow-Ups` (Long text field with AI-generated follow-up questions)

## How Each Automation Works

### Compression Process
The compression process extracts data from multiple Airtable tables and consolidates it into a single JSON structure. Here's how it works:

1. Fetch applicant data from all related tables using the ApplicantId
2. Create a composite Applicant object with all the information
3. Convert the Applicant object to JSON format
4. Perform automated screening based on business rules
5. Send the JSON to Gemini AI for analysis
6. Update the Applicants table with the compressed JSON and screening results

**Script snippet from compression_service.py:**
```python
applicant_data = {
    "personalInfo": personal_info,
    "workExperience": work_experience,
    "salaryPreferences": salary_preferences
}
compressed_json = json.dumps(applicant_data, indent=2)
# Save to Airtable
repository.save_compressed_json(applicant_id, compressed_json)
```

### Decompression Process
The decompression process rebuilds detailed Airtable records from the compressed JSON:

1. Fetch the compressed JSON from the Applicants table
2. Parse the JSON into an Applicant object
3. Save personal information to the Personal Details table
4. Clear existing work experience records and create new ones
5. Clear existing salary preference records and create new ones

**Script snippet from decompression_service.py:**
```python
compressed_data = repository.fetch_compressed_json(applicant_id)
applicant = Applicant.from_dict(compressed_data)
# Save decompressed data
personal_id = repository.save_personal_info(applicant.personal_info, applicant_id)
repository.save_work_experience(applicant.work_experience, personal_id)
repository.save_salary_preferences(applicant.salary_preferences, personal_id)
```

## LLM Integration Configuration and Security

### Configuration
The LLM integration is configured through environment variables:
- `GEMINI_API_KEY`: Your Google Gemini API key

The system uses the `gemini-pro` model for text analysis and maintains a retry mechanism for API calls.

### Security
- API keys are stored in a `.env` file and loaded using `python-dotenv`
- Keys are never hardcoded in the source files
- The `.env` file is included in `.gitignore` to prevent accidental commits
- All API requests are made over HTTPS

**Security implementation in llm_service.py:**
```python
# Load API key from environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')
```

## Extending or Customizing Shortlist Criteria

The shortlist criteria can be easily customized by modifying the `business_rules.py` file:

### Current Criteria
- Minimum total years of experience: 4 years
- Tier-1 companies: Google, Meta, OpenAI
- Maximum hourly rate: $100
- Minimum weekly availability: 20 hours
- Approved countries: USA, Canada, UK, Germany, India

### Customization Examples

1. **Modify experience requirements:**
   ```python
   TOTAL_YEARS_EXPERIENCE = 5  # Change from 4 to 5 years
   ```

2. **Add new tier-1 companies:**
   ```python
   TIER_1_COMPANIES = set(["google", "meta", "openai", "amazon", "microsoft"])
   ```

3. **Adjust rate limits:**
   ```python
   MAX_RATE = 120  # Change from $100 to $120 per hour
   ```

4. **Add new approved countries:**
   ```python
   COUNTRIES = set(["USA", "Canada", "UK", "Germany", "India", "Australia", "Singapore"])
   ```

5. **Modify availability requirements:**
   ```python
   MIN_AVAILABILITY = 25  # Change from 20 to 25 hours per week
   ```

After making changes to `business_rules.py`, simply run the compression command again to apply the new criteria to applicant evaluations.
