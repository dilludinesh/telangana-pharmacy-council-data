# Requirements Document: TGPC Pharmacist Search Website

## Introduction

A free, forever-hosted, open-source search website that allows users to quickly search and reference pharmacist registration data from the TGPC rx.json dataset. The solution must be completely free, require zero maintenance, and stay online indefinitely using static hosting platforms.

## Glossary

- **TGPC**: Telangana Government Pharmacy Council
- **rx.json**: JSON file containing 82,000+ pharmacist registration records
- **Static Site**: Website with no server-side processing, only HTML/CSS/JavaScript
- **GitHub Pages**: Free static site hosting service by GitHub
- **Client-Side Search**: Search functionality that runs in the user's browser
- **CDN**: Content Delivery Network for fast global access

## Requirements

### Requirement 1: Free Forever Hosting

**User Story:** As a project maintainer, I want the website to be hosted completely free forever, so that I never have to pay hosting fees or worry about service interruptions.

#### Acceptance Criteria

1. WHEN the website is deployed, THE System SHALL use GitHub Pages for hosting at zero cost
2. WHEN the repository is public, THE System SHALL remain accessible indefinitely without payment
3. WHEN GitHub Pages is used, THE System SHALL provide a custom domain option (optional)
4. WHERE the data updates daily, THE System SHALL automatically redeploy with new data via GitHub Actions
5. THE System SHALL NOT require any paid services, APIs, or third-party dependencies

### Requirement 2: Fast Client-Side Search

**User Story:** As a user, I want to search pharmacist records instantly without page reloads, so that I can quickly find the information I need.

#### Acceptance Criteria

1. WHEN a user types in the search box, THE System SHALL filter results in real-time without server requests
2. WHEN the search query matches registration number, THE System SHALL display exact matches first
3. WHEN the search query matches name or father name, THE System SHALL display partial matches
4. WHEN search results exceed 50 records, THE System SHALL paginate results for performance
5. THE System SHALL complete searches within 100 milliseconds for optimal user experience
6. THE System SHALL support case-insensitive search across all text fields

### Requirement 3: Efficient Data Loading with Search Index

**User Story:** As a user, I want the website to load quickly without downloading the entire 13+ MB dataset, so that I can start searching immediately.

#### Acceptance Criteria

1. WHEN the page loads, THE System SHALL load only a lightweight search index (registration numbers and names) instead of full records
2. WHEN a search is performed, THE System SHALL use the index to find matching records
3. WHEN a specific record is selected, THE System SHALL fetch only that record's details on-demand
4. WHEN the search index is generated, THE System SHALL be compressed and under 2 MB in size
5. THE System SHALL use browser localStorage to cache the search index between visits
6. WHEN the rx.json updates, THE System SHALL generate a new search index automatically via GitHub Actions
7. THE System SHALL load the initial page and search index within 2 seconds on a 3G connection
8. THE System SHALL NOT require downloading the full 13+ MB rx.json file for basic searches

### Requirement 4: Mobile-Responsive Design

**User Story:** As a mobile user, I want the search interface to work perfectly on my phone, so that I can search records on the go.

#### Acceptance Criteria

1. WHEN accessed on mobile devices, THE System SHALL display a responsive layout that fits the screen
2. WHEN the viewport is less than 768px wide, THE System SHALL stack search results vertically
3. WHEN touch gestures are used, THE System SHALL respond to taps and swipes appropriately
4. THE System SHALL use mobile-friendly font sizes (minimum 16px for inputs)
5. THE System SHALL NOT require horizontal scrolling on any device size

### Requirement 5: Search Result Display

**User Story:** As a user, I want to see clear, organized search results with all relevant information, so that I can quickly identify the pharmacist I'm looking for.

#### Acceptance Criteria

1. WHEN search results are displayed, THE System SHALL show registration number, name, father name, and category
2. WHEN multiple results match, THE System SHALL display them in a table or card layout
3. WHEN no results match, THE System SHALL display a helpful "No results found" message
4. WHEN results are displayed, THE System SHALL highlight the matching search terms
5. THE System SHALL show the total count of matching records
6. THE System SHALL allow sorting results by registration number or name

### Requirement 6: Zero Maintenance Operation with Auto-Index Generation

**User Story:** As a project maintainer, I want the website to update automatically with new data, so that I never have to manually update or maintain it.

#### Acceptance Criteria

1. WHEN the daily GitHub Action updates rx.json, THE System SHALL automatically generate a new search index
2. WHEN the search index is generated, THE System SHALL create a lightweight JSON file with only searchable fields
3. WHEN the index generation completes, THE System SHALL automatically redeploy the website via GitHub Pages
4. WHEN the deployment completes, THE System SHALL serve the latest data within 5 minutes
5. THE System SHALL NOT require manual intervention for updates or maintenance
6. THE System SHALL NOT have any server-side components that need monitoring or updates
7. THE System SHALL use only static files (HTML, CSS, JavaScript, JSON)
8. THE System SHALL generate the search index as part of the existing daily update workflow

### Requirement 7: Search Index Structure

**User Story:** As a developer, I want a well-structured search index that enables fast lookups without loading the full dataset, so that the website performs efficiently.

#### Acceptance Criteria

1. WHEN the search index is created, THE System SHALL include only registration_number, name, father_name, and category fields
2. WHEN the index is generated, THE System SHALL compress it using gzip to minimize file size
3. WHEN the index is structured, THE System SHALL use an array format for minimal overhead
4. THE System SHALL generate the index file to be under 2 MB (compressed)
5. WHEN a user needs full details, THE System SHALL provide a link to view the complete record in rx.json
6. THE System SHALL include a version timestamp in the index to detect updates
7. THE System SHALL NOT duplicate data between the index and the full rx.json file

### Requirement 8: Performance and Optimization

**User Story:** As a user, I want the website to be fast and responsive, so that I can search efficiently without delays.

#### Acceptance Criteria

1. WHEN the page loads, THE System SHALL achieve a Lighthouse performance score above 90
2. WHEN searching the index, THE System SHALL use efficient string matching for fast lookups
3. WHEN rendering results, THE System SHALL limit initial display to 50 results with "Load More" option
4. THE System SHALL minify all CSS and JavaScript files for faster loading
5. THE System SHALL use browser caching headers for static assets
6. THE System SHALL load and parse the search index in under 500 milliseconds

### Requirement 9: Accessibility

**User Story:** As a user with accessibility needs, I want the website to be usable with screen readers and keyboard navigation, so that I can access the information independently.

#### Acceptance Criteria

1. WHEN using keyboard navigation, THE System SHALL allow full functionality without a mouse
2. WHEN using a screen reader, THE System SHALL provide appropriate ARIA labels and roles
3. THE System SHALL maintain sufficient color contrast (WCAG AA standard)
4. WHEN forms are used, THE System SHALL provide clear labels and error messages
5. THE System SHALL support browser zoom up to 200% without breaking layout

### Requirement 10: Open Source and Documentation

**User Story:** As a developer or contributor, I want clear documentation and open-source code, so that I can understand, modify, or contribute to the project.

#### Acceptance Criteria

1. THE System SHALL include a README with setup and deployment instructions
2. THE System SHALL use a permissive open-source license (MIT or similar)
3. THE System SHALL include inline code comments for complex logic
4. THE System SHALL document the search algorithm and data structure
5. THE System SHALL provide examples of how to customize or extend the search functionality

### Requirement 11: Data Privacy and Security

**User Story:** As a user, I want to know that my searches are private and the data is secure, so that I can use the service with confidence.

#### Acceptance Criteria

1. THE System SHALL NOT send search queries to any external servers
2. THE System SHALL NOT collect or store user search history
3. THE System SHALL NOT use analytics or tracking scripts
4. WHEN served over HTTPS, THE System SHALL ensure all data transfers are encrypted
5. THE System SHALL only display publicly available registration data from TGPC

## Core Principles (Non-Negotiable)

### 1. Cloud Only
- **GitHub Pages** for hosting (Microsoft's cloud infrastructure)
- **GitHub Actions** for automation (cloud-based CI/CD)
- **CDN delivery** via GitHub's global network
- **No local servers** or self-hosted components
- **100% cloud-native** solution

### 2. Open Source
- **MIT License** (or similar permissive license)
- **Public GitHub repository** with full source code
- **No proprietary dependencies** or closed-source tools
- **Community contributions** welcome
- **Transparent operation** - all code visible and auditable

### 3. Free Forever
- **GitHub Pages** - Free for public repositories (forever)
- **GitHub Actions** - 2,000 minutes/month free (more than enough for daily updates)
- **No credit card** required
- **No trial periods** or expiration
- **No hidden costs** or premium features
- **No paid APIs** or third-party services

## Technical Constraints

- Must use only free services (GitHub Pages, GitHub Actions)
- Must be 100% static (no backend servers, no databases)
- Must work with the existing rx.json format
- Must handle 82,000+ records efficiently
- Must be deployable with a single GitHub Actions workflow
- Must not require any API keys, credentials, or paid services
- Must work in all modern browsers (Chrome, Firefox, Safari, Edge)
- Must remain functional even if the repository is forked or cloned
