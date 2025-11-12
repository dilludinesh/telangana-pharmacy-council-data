# Requirements Document: TGPC Pharmacist Search Website

## Introduction

A free, forever-hosted, open-source search website for personal use that allows quick search and reference of pharmacist registration data from the TGPC portal. The solution uses a cloud database (Supabase) that automatically syncs with rx.json daily, eliminating the need to download large files and enabling fast searches even on weak network connections.

## Glossary

- **TGPC**: Telangana Government Pharmacy Council
- **rx.json**: JSON file containing 82,000+ pharmacist registration records
- **Supabase**: Open-source cloud database platform (PostgreSQL)
- **GitHub Pages**: Free static site hosting service by GitHub
- **GitHub Actions**: Cloud-based automation for CI/CD
- **API**: Application Programming Interface for database queries

## Requirements

### Requirement 1: Automated Data Collection and Sync

**User Story:** As a project maintainer, I want the system to automatically collect new records from TGPC portal and sync them to the cloud database daily, so that the data is always up-to-date without manual intervention.

#### Acceptance Criteria

1. WHEN the daily GitHub Action runs, THE System SHALL fetch latest data from TGPC portal and update rx.json
2. WHEN rx.json is updated, THE System SHALL automatically sync all records to Supabase database
3. WHEN new records are added, THE System SHALL insert them into the database without duplicates
4. WHEN records are removed from TGPC portal, THE System SHALL remove them from the database
5. THE System SHALL complete the sync process within 5 minutes
6. THE System SHALL log sync results (new records, updated records, errors)
7. THE System SHALL NOT require manual intervention for daily updates

### Requirement 2: Free Cloud Database Hosting

**User Story:** As a project maintainer, I want a free cloud database that stores all pharmacist records, so that users never have to download large files and can query data efficiently.

#### Acceptance Criteria

1. WHEN the database is set up, THE System SHALL use Supabase free tier (500 MB storage)
2. WHEN data is stored, THE System SHALL use PostgreSQL database in Supabase cloud
3. THE System SHALL remain within free tier limits (500 MB database, 2 GB bandwidth/month)
4. THE System SHALL NOT require credit card or payment information
5. THE System SHALL provide API access for querying data
6. WHEN the database grows, THE System SHALL handle 100+ years of data within free tier limits
7. THE System SHALL NOT have any expiration or trial period

### Requirement 3: Simple Search Website

**User Story:** As a user, I want a simple website where I can search pharmacist records instantly, so that I can quickly find information for personal reference.

#### Acceptance Criteria

1. WHEN the website loads, THE System SHALL display a search interface within 2 seconds
2. WHEN a user types in the search box, THE System SHALL query the Supabase database in real-time
3. WHEN search results are returned, THE System SHALL display them within 500 milliseconds
4. THE System SHALL support search by registration number, name, or father name
5. THE System SHALL display registration number, name, father name, and category in results
6. WHEN no results match, THE System SHALL display a clear "No results found" message
7. THE System SHALL work on weak network connections (only small API queries, no large downloads)

### Requirement 4: No Large File Downloads

**User Story:** As a user on weak network, I want the website to work without downloading large files, so that I can search records even with minimal network speed.

#### Acceptance Criteria

1. WHEN the website loads, THE System SHALL NOT download rx.json or any large data files
2. WHEN a search is performed, THE System SHALL send only the search query (few bytes) to the database
3. WHEN results are returned, THE System SHALL receive only matching records (few KB maximum)
4. THE System SHALL NOT require downloading the entire database to the browser
5. WHEN network is weak (few KB/s), THE System SHALL still function normally
6. THE System SHALL complete searches even on 2G network speeds
7. THE System SHALL NOT use browser storage for large data caching

### Requirement 5: Personal Use Optimization

**User Story:** As the sole user of this system, I want it optimized for personal use with minimal complexity, so that it's simple to maintain and use.

#### Acceptance Criteria

1. THE System SHALL be designed for 1-10 users maximum (personal use)
2. THE System SHALL NOT include features for high-traffic scenarios
3. THE System SHALL prioritize simplicity over scalability
4. THE System SHALL have a clean, minimal user interface
5. THE System SHALL NOT include user authentication or accounts
6. THE System SHALL be accessible only via the website URL (no mobile app needed)
7. THE System SHALL focus on search functionality only (no data editing or management)

### Requirement 6: Mobile-Responsive Design

**User Story:** As a mobile user, I want the search interface to work perfectly on my phone, so that I can search records on the go.

#### Acceptance Criteria

1. WHEN accessed on mobile devices, THE System SHALL display a responsive layout that fits the screen
2. WHEN the viewport is less than 768px wide, THE System SHALL stack search results vertically
3. WHEN touch gestures are used, THE System SHALL respond to taps appropriately
4. THE System SHALL use mobile-friendly font sizes (minimum 16px for inputs)
5. THE System SHALL NOT require horizontal scrolling on any device size

### Requirement 7: Zero Maintenance Operation

**User Story:** As a project maintainer, I want the system to run automatically without any maintenance, so that I never have to manually update or monitor it.

#### Acceptance Criteria

1. WHEN the daily GitHub Action runs, THE System SHALL automatically sync data to Supabase
2. WHEN the website is deployed, THE System SHALL remain online indefinitely on GitHub Pages
3. THE System SHALL NOT require manual database updates or maintenance
4. THE System SHALL NOT require server monitoring or management
5. THE System SHALL handle errors gracefully and log them for review
6. WHEN Supabase or GitHub Pages have updates, THE System SHALL continue functioning without changes
7. THE System SHALL NOT require any scheduled maintenance windows

### Requirement 8: Performance and Optimization

**User Story:** As a user, I want the website to be fast and responsive, so that I can search efficiently without delays.

#### Acceptance Criteria

1. WHEN the page loads, THE System SHALL achieve a Lighthouse performance score above 90
2. WHEN searching the database, THE System SHALL use indexed queries for fast lookups
3. WHEN rendering results, THE System SHALL limit initial display to 50 results with pagination
4. THE System SHALL minify all CSS and JavaScript files for faster loading
5. THE System SHALL use browser caching headers for static assets
6. THE System SHALL complete database queries in under 200 milliseconds

### Requirement 9: Data Privacy and Security

**User Story:** As a user, I want to know that my searches are private and the data is secure, so that I can use the service with confidence.

#### Acceptance Criteria

1. THE System SHALL NOT log or store user search queries
2. THE System SHALL NOT collect or track user behavior
3. THE System SHALL NOT use analytics or tracking scripts
4. WHEN served over HTTPS, THE System SHALL ensure all data transfers are encrypted
5. THE System SHALL only display publicly available registration data from TGPC
6. THE System SHALL use Supabase Row Level Security (RLS) for read-only access
7. THE System SHALL NOT expose database credentials in client-side code

### Requirement 10: Open Source and Documentation

**User Story:** As a developer, I want clear documentation and open-source code, so that I can understand and modify the project if needed.

#### Acceptance Criteria

1. THE System SHALL include a README with setup and deployment instructions
2. THE System SHALL use a permissive open-source license (MIT)
3. THE System SHALL include inline code comments for complex logic
4. THE System SHALL document the Supabase setup and configuration process
5. THE System SHALL provide examples of how to customize the search interface
6. THE System SHALL document the GitHub Actions workflow for data sync

## Core Principles (Non-Negotiable)

### 1. Cloud Only
- **Supabase** for cloud database (PostgreSQL)
- **GitHub Pages** for website hosting
- **GitHub Actions** for automation
- **No local servers** or self-hosted components
- **100% cloud-native** solution

### 2. Open Source
- **MIT License**
- **Public GitHub repository** with full source code
- **Supabase** is open source (can self-host if needed in future)
- **No proprietary dependencies**
- **Transparent operation** - all code visible

### 3. Free Forever
- **Supabase Free Tier** - 500 MB database, 2 GB bandwidth/month (forever)
- **GitHub Pages** - Free for public repositories (forever)
- **GitHub Actions** - 2,000 minutes/month free (more than enough)
- **No credit card** required
- **No trial periods** or expiration
- **No hidden costs** or premium features

## Technical Constraints

- Must use Supabase free tier (500 MB database, 2 GB bandwidth/month)
- Must use GitHub Pages for hosting (free)
- Must use GitHub Actions for automation (within free tier limits)
- Must work with the existing rx.json format
- Must handle 82,000+ records efficiently
- Must not require any paid services or API keys
- Must work in all modern browsers (Chrome, Firefox, Safari, Edge)
- Must function on weak network connections (2G/3G)
- Must be optimized for personal use (1-10 users maximum)

## Use Case Scenario

**Typical User Flow:**
1. User opens website on mobile with weak network
2. Website loads in 2 seconds (no large downloads)
3. User types "TS082612" in search box
4. System queries Supabase database (few bytes sent)
5. Results returned in 500ms (only matching record, few KB)
6. User sees: Registration, Name, Father Name, Category
7. User closes browser
8. Next day: Repeat (no data to download, instant search)

**Daily Automation:**
1. GitHub Action runs at scheduled time (IST business hours)
2. Fetches latest data from TGPC portal
3. Updates rx.json in repository
4. Syncs changes to Supabase database
5. Logs results (new records, errors)
6. Website automatically shows updated data
7. No manual intervention required
