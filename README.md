# LinkedIn Sales Navigator Scraper & Email Finder

A comprehensive Python-based automation tool for LinkedIn Sales Navigator that scrapes prospect data, extracts contact information, and manages leads through Baserow CRM integration.

## ⚠️ Important Legal Notice

This tool is for educational and research purposes only. Users are responsible for complying with:
- LinkedIn's Terms of Service
- Data protection regulations (GDPR, CCPA, etc.)
- Local laws regarding web scraping and data collection
- Respect for individuals' privacy and consent

**Use at your own risk and ensure you have proper authorization before scraping any data.**

## 🚀 Features

### Core Functionality
- **LinkedIn Sales Navigator Scraping**: Extract leads from search results across multiple pages
- **Profile Data Extraction**: Gather detailed information from LinkedIn profiles (headlines, summaries, job descriptions)
- **Company Information**: Scrape company pages for overview, industry, and specialties
- **Email Discovery**: Integration with Kaspr extension to find contact email addresses
- **CRM Integration**: Automatic data storage and updates in Baserow database
- **Data Export**: Save results in CSV or Excel formats

### Automation Features
- **Multi-page Scraping**: Process hundreds of search result pages
- **Rate Limiting**: Built-in delays and retry mechanisms to avoid detection
- **Proxy Support**: HTTP proxy configuration for IP rotation
- **Random User Agents**: Dynamic user agent rotation for stealth browsing
- **Human-like Behavior**: Random scrolling, clicking, and waiting patterns
- **DOM-based Email Discovery**: Kaspr extension integration through direct DOM manipulation

## 🔍 Email Discovery Process

The email finding functionality works through automated interaction with the Kaspr browser extension:

1. **Profile Navigation**: Script navigates to LinkedIn profile URLs from Baserow
2. **Kaspr Activation**: Locates and clicks the Kaspr extension button in the DOM
3. **Contact Revelation**: Triggers the "Reveal contact details" button
4. **Data Extraction**: Extracts email address from the Kaspr overlay via XPath selectors
5. **CRM Update**: Immediately updates Baserow database with discovered email
6. **Human Simulation**: Performs random actions between profiles to avoid detection

### DOM Interaction Examples
```python
# Activate Kaspr extension
kasprBtn = driver.find_element(By.XPATH, "//div[@id='KasprPluginBtn']/button")
kasprBtn.click()

# Reveal contact details
kasprCntBtn = driver.find_element(By.XPATH, "//button[normalize-space()='Reveal contact details']")
kasprCntBtn.click()

# Extract email from Kaspr overlay
emailW = driver.find_element(By.XPATH, "//span[@class='star']//span[@class='to-clipboard']")
email = emailW.text
```

## 📋 Prerequisites

- Python 3.7+
- Chrome browser
- LinkedIn account with Sales Navigator access
- Baserow account and API token
- Kaspr account for email discovery

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd linkedin-scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Included Components**
   The repository includes all necessary browser components:
   - **ChromeDriver**: Pre-configured Chrome WebDriver executable
   - **Browser Extensions**:
     - **Kaspr**: Email finder extension for LinkedIn lead enrichment
     - **uBlock Origin**: Ad blocker for cleaner browsing
     - **Cookie Editor**: Cookie management utilities
   
   *No additional downloads required - everything is bundled!*

## ⚙️ Configuration

### 1. LinkedIn Credentials
Create `lk_credentials.json`:
```json
{
  "email": "your-linkedin-email@example.com",
  "password": "your-linkedin-password",
  "TESmail": "test-email@example.com",
  "TESpassword": "test-password",
  "kEmail": "kaspr-email@example.com",
  "kPassword": "kaspr-password",
  "kgEmail": "kaspr-alt-email@example.com",
  "kgPassword": "kaspr-alt-password"
}
```

### 2. Baserow Configuration
Update the Baserow settings in the script files:
```python
baserow_api_token = "your-baserow-api-token"
leads_table_id = "your-table-id"
```

### 3. Extension Configuration
The browser extensions are pre-configured and loaded automatically:
```python
# Kaspr extension is loaded from the included directory
chrome_options.add_argument(r'--load-extension=./Kaspr')
```

*Note: Extension paths are already configured in the scripts to use the included extensions.*

### 4. Proxy Configuration (Optional)
Update proxy settings in the script:
```python
options = {
    'proxy': {
        'http': 'http://username:password@host:port'
    }
}
```

## 📖 Usage

### 1. LinkedIn Sales Navigator Scraping

```bash
python lksn_search_scraper.py \
  --search-url "https://www.linkedin.com/sales/search/people?query=..." \
  --start-page 1 \
  --end-page 10 \
  --wait-time-between-pages 5 \
  --save-format csv
```

**Parameters:**
- `--search-url`: LinkedIn Sales Navigator search URL
- `--start-page`: Starting page number (default: 1)
- `--end-page`: Ending page number (default: 1)
- `--wait-time-between-pages`: Delay between pages in seconds (default: 5)
- `--wait-after-page-loaded`: Wait time after page loads (default: 3)
- `--wait-after-scroll-down`: Wait time after scrolling (default: 3)
- `--save-format`: Output format - 'csv' or 'xlsx' (default: csv)

### 2. Email Finding with Baserow Integration

```bash
python baserow_email_finder.py
```

This script will:
1. Prompt for audience ID
2. Fetch leads from Baserow
3. Filter leads without emails
4. Visit LinkedIn profiles
5. Use Kaspr to find email addresses
6. Update Baserow with found emails

### 3. Profile Information Extraction

```bash
python liProfiles.py
```

### 4. Company Information Extraction

```bash
python liCompanies.py
```

## 📁 Project Structure

```
linkedin-scraper/
├── baserow_email_finder.py      # Main email finding script
├── baserow_email_finder_2.py    # Alternative email finder
├── lksn_search_scraper.py       # Sales Navigator scraper
├── liProfiles.py                # Profile information scraper
├── liCompanies.py               # Company information scraper
├── general_lk_utils.py          # Utility functions
├── requirements.txt             # Python dependencies
├── lk_credentials.json          # LinkedIn credentials (create this)
├── cookies.json                 # Browser cookies storage
├── links.json                   # Scraped LinkedIn URLs
├── lksn_data/                   # Output directory for scraped data
├── chromedriver.exe             # Pre-configured ChromeDriver
├── Kaspr/                       # Kaspr email finder extension
├── uBlock/                      # uBlock Origin ad blocker extension
└── CookieEditor/                # Cookie management extension
```

## 📊 Output Data

### Sales Navigator Export (CSV/Excel)
- Name, LinkedIn profile URL
- Location, role/title
- Company name and LinkedIn URL
- Generated standard LinkedIn URLs

### Profile Data (CSV)
- Headlines and summaries
- Job descriptions
- Professional experience

### Company Data (CSV)
- Company overviews
- Industry classifications
- Specialties and focus areas

## 🔧 Advanced Configuration

### Batch Processing
The email finder processes leads in batches of 50 with 10-minute breaks between batches to avoid rate limiting.

### Pagination Settings
Configure the total pages and starting page in the script:
```python
total_pages = 1024  # Adjust based on your data size
start_page = 800    # Skip processed pages for speed
```

### Random Behavior Timing
Customize wait times to appear more human-like:
```python
def gInt3_6():
    return random.uniform(3, 6)  # Random wait between 3-6 seconds
```

## 🚨 Rate Limiting & Best Practices

- **Respect Rate Limits**: Built-in delays prevent overwhelming LinkedIn's servers
- **Use Proxies**: Rotate IP addresses for large scraping operations
- **Monitor Usage**: Keep track of daily scraping volume
- **Regular Breaks**: Long pauses between batches reduce detection risk
- **Human-like Patterns**: Random scrolling and clicking mimic real user behavior

## 🛡️ Error Handling

The scripts include comprehensive error handling for:
- Network timeouts and connection issues
- Element not found scenarios
- Rate limiting responses (429 errors)
- Authentication challenges
- Proxy failures

## 📝 Logging

All scripts provide detailed console output including:
- Progress indicators with page counts
- Success/failure status for each operation
- Error messages with context
- Timing information for performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is provided as-is for educational purposes. Users assume all responsibility for compliance with applicable laws and terms of service.

## ⚠️ Disclaimer

This tool is not affiliated with LinkedIn, Baserow, or Kaspr. Use responsibly and in accordance with all applicable terms of service and legal requirements.
