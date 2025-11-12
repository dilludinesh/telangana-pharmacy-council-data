# Implementation Plan: TGPC Pharmacist Search Website

## Task List

- [x] 1. Set up Supabase database
  - Create Supabase account and project
  - Run SQL schema to create pharmacists table
  - Configure Row Level Security (RLS) for read-only access
  - Get API credentials (URL, anon key, service key)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 2. Configure GitHub repository secrets
  - Add SUPABASE_URL to GitHub Secrets
  - Add SUPABASE_SERVICE_KEY to GitHub Secrets
  - Verify secrets are accessible in Actions
  - _Requirements: 2.5, 9.6_

- [x] 3. Create Supabase sync script
  - [x] 3.1 Create scripts/sync_to_supabase.py
    - Import required libraries (supabase-py, json, os)
    - Initialize Supabase client with environment variables
    - Load rx.json data
    - Implement upsert logic for each record
    - Add error handling and logging
    - _Requirements: 1.2, 1.3, 1.4, 1.5_
  
  - [x] 3.2 Update requirements.txt
    - Add supabase-py dependency
    - _Requirements: 1.2_

- [ ] 4. Update GitHub Actions workflow
  - [x] 4.1 Add Supabase sync step to daily-update.yml
    - Add step after database update
    - Configure environment variables from secrets
    - Run sync_to_supabase.py script
    - Add error handling and logging
    - _Requirements: 1.1, 1.2, 1.6, 1.7, 6.1, 6.2_
  
  - [ ] 4.2 Test workflow manually
    - Trigger workflow manually
    - Verify sync completes successfully
    - Check Supabase dashboard for data
    - _Requirements: 1.5, 1.6_

- [ ] 5. Create search website structure
  - [ ] 5.1 Create docs/ folder for GitHub Pages
    - Create docs directory in repository root
    - _Requirements: 3.1_
  
  - [ ] 5.2 Create docs/index.html
    - Add HTML structure with search input
    - Add search button and results container
    - Include Supabase JS library from CDN
    - Link to search.js and styles.css
    - Add mobile viewport meta tag
    - _Requirements: 3.1, 3.2, 3.5, 6.1, 6.2_
  
  - [ ] 5.3 Create docs/search.js
    - Initialize Supabase client with anon key
    - Implement search function with query parameter
    - Add database query with OR condition for multiple fields
    - Implement displayResults function
    - Add event listeners for search button and Enter key
    - Add loading indicator logic
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3_
  
  - [ ] 5.4 Create docs/styles.css
    - Add responsive layout styles
    - Style search box and button
    - Style results table
    - Add mobile-responsive media queries
    - Add loading indicator styles
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 8.1, 8.4_

- [ ] 6. Configure GitHub Pages
  - Enable GitHub Pages in repository settings
  - Set source to docs folder
  - Verify website is accessible at github.io URL
  - _Requirements: 3.1, 7.2_

- [ ] 7. Perform initial data load
  - [ ] 7.1 Run sync script manually
    - Execute sync_to_supabase.py locally or via Actions
    - Monitor progress and check for errors
    - _Requirements: 1.2, 1.3_
  
  - [ ] 7.2 Verify data in Supabase
    - Check record count in Supabase dashboard
    - Verify sample records are correct
    - Check for duplicates
    - _Requirements: 1.3, 1.4_

- [ ] 8. Test search functionality
  - [ ] 8.1 Test exact match search
    - Search by registration number
    - Verify correct record is returned
    - _Requirements: 3.2, 3.3, 3.4_
  
  - [ ] 8.2 Test partial match search
    - Search by partial name
    - Verify multiple results are returned
    - _Requirements: 3.2, 3.4_
  
  - [ ] 8.3 Test empty/no results
    - Search with invalid query
    - Verify "No results found" message
    - _Requirements: 3.6_
  
  - [ ] 8.4 Test mobile responsiveness
    - Open website on mobile device or DevTools mobile view
    - Verify layout adapts correctly
    - Test search functionality on mobile
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ] 8.5 Test on weak network
    - Throttle network in DevTools (2G/3G)
    - Verify search still works
    - Check response times
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [ ] 9. Add documentation
  - [ ] 9.1 Update README.md
    - Add section about search website
    - Include link to live website
    - Document Supabase setup steps
    - Add usage instructions
    - _Requirements: 10.1, 10.4, 10.5_
  
  - [ ] 9.2 Add inline code comments
    - Comment sync_to_supabase.py
    - Comment search.js functions
    - _Requirements: 10.3_

- [ ] 10. Final verification
  - [ ] 10.1 Verify daily automation
    - Wait for next scheduled run
    - Check that new records sync automatically
    - Verify website shows updated data
    - _Requirements: 1.1, 1.2, 1.7, 7.1, 7.2_
  
  - [ ] 10.2 Monitor for errors
    - Check GitHub Actions logs
    - Check Supabase logs
    - Verify no errors in browser console
    - _Requirements: 1.6, 7.5_

## Notes

- All tasks are required for comprehensive implementation
- Tasks build incrementally on previous tasks
- Supabase setup (Task 1) must be completed first before other tasks
- Testing tasks (8, 10) ensure quality and reliability
- Complete tasks in order for best results
