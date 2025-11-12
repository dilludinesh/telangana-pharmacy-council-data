# Supabase Setup Guide

Follow these steps one at a time. Don't worry, I'll guide you through each one!

---

## STEP 1: Create Your Supabase Account

**What to do:**
1. Open your web browser
2. Go to: **https://supabase.com**
3. Click the green **"Start your project"** button
4. Choose **"Continue with GitHub"** (easiest option)
   - OR use your email if you prefer
5. Complete the sign-up process

**When done:** You'll see a dashboard. Come back here for Step 2.

---

## STEP 2: Create a New Project

**What to do:**
1. On the Supabase dashboard, click **"New Project"** (green button)
2. Fill in these details:
   - **Name**: Type `tgpc-search`
   - **Database Password**: Click "Generate a password" button
     - ⚠️ **IMPORTANT**: Copy this password and save it somewhere safe (like a notes app)
   - **Region**: Select **"Mumbai (South Asia)"** (closest to Pakistan)
   - **Pricing Plan**: Leave as **"Free"** (already selected)
3. Click **"Create new project"**
4. Wait 2-3 minutes while it sets up (you'll see a loading screen)

**When done:** You'll see your project dashboard. Come back here for Step 3.

---

## STEP 3: Open the SQL Editor

**What to do:**
1. Look at the left sidebar in your Supabase dashboard
2. Find and click the **"SQL Editor"** icon (looks like `</>`)
3. Click the **"New query"** button

**When done:** You'll see an empty text box. Come back here for Step 4.

---

## STEP 4: Copy the Database Setup Code

**What to do:**
1. In VS Code (or your code editor), open the file: `scripts/supabase_setup.sql`
2. Select ALL the text in that file (Ctrl+A on Windows, Cmd+A on Mac)
3. Copy it (Ctrl+C on Windows, Cmd+C on Mac)

**When done:** The code is copied. Come back here for Step 5.

---

## STEP 5: Run the Database Setup

**What to do:**
1. Go back to your Supabase browser tab (SQL Editor should be open)
2. Click in the empty text box
3. Paste the code you copied (Ctrl+V on Windows, Cmd+V on Mac)
4. Click the green **"Run"** button (or press Ctrl+Enter / Cmd+Enter)
5. Wait a few seconds

**What you should see:** A green message saying "Success. No rows returned"

**If you see an error:** That's okay! Tell me what the error says and I'll help.

**When done:** Your database table is created! Come back here for Step 6.

---

## STEP 6: Verify Your Table Was Created

**What to do:**
1. Look at the left sidebar in Supabase
2. Click the **"Table Editor"** icon (looks like a table/grid)
3. You should see a table named **"pharmacists"** in the list
4. Click on it

**What you should see:** An empty table with columns like `id`, `registration_number`, `name`, etc.

**When done:** Perfect! Come back here for Step 7.

---

## STEP 7: Get Your Project URL

**What to do:**
1. In Supabase, click the **Settings** icon (gear ⚙️) at the bottom of the left sidebar
2. Click **"API"** in the settings menu
3. Look for **"Project URL"** at the top
4. Copy the URL (it looks like: `https://xxxxxxxxxxxxx.supabase.co`)
5. Save it in a notes app with the label "SUPABASE_URL"

**When done:** You have your URL saved. Come back here for Step 8.

---

## STEP 8: Get Your Public Key (Safe Key)

**What to do:**
1. On the same API page, scroll down to **"Project API keys"**
2. Find the key labeled **"anon public"**
3. Click the **copy icon** next to it
4. Save it in your notes app with the label "SUPABASE_ANON_KEY"

**Note:** This key is safe to share publicly - it only allows reading data.

**When done:** You have your public key saved. Come back here for Step 9.

---

## STEP 9: Get Your Secret Key (Private Key)

**What to do:**
1. On the same API page, find the key labeled **"service_role"**
2. Click **"Reveal"** to show the key
3. Click the **copy icon** next to it
4. Save it in your notes app with the label "SUPABASE_SERVICE_KEY"
5. ⚠️ **IMPORTANT**: Keep this key private! Don't share it with anyone.

**Note:** This key has full access to your database - keep it secret!

**When done:** You have all three credentials saved. Come back here for Step 10.

---

## STEP 10: Open GitHub Secrets Settings

**What to do:**
1. Open your web browser
2. Go to your GitHub repository (the one for this project)
3. Click the **"Settings"** tab at the top
4. On the left sidebar, click **"Secrets and variables"**
5. Click **"Actions"**

**When done:** You'll see a page for managing secrets. Come back here for Step 11.

---

## STEP 11: Add Your Project URL to GitHub

**What to do:**
1. Click the green **"New repository secret"** button
2. In the **"Name"** field, type exactly: `SUPABASE_URL`
3. In the **"Secret"** field, paste your Project URL (from your notes)
4. Click **"Add secret"**

**When done:** You'll see SUPABASE_URL in your secrets list. Come back here for Step 12.

---

## STEP 12: Add Your Public Key to GitHub

**What to do:**
1. Click **"New repository secret"** again
2. In the **"Name"** field, type exactly: `SUPABASE_ANON_KEY`
3. In the **"Secret"** field, paste your anon public key (from your notes)
4. Click **"Add secret"**

**When done:** You'll see SUPABASE_ANON_KEY in your secrets list. Come back here for Step 13.

---

## STEP 13: Add Your Secret Key to GitHub

**What to do:**
1. Click **"New repository secret"** one more time
2. In the **"Name"** field, type exactly: `SUPABASE_SERVICE_KEY`
3. In the **"Secret"** field, paste your service_role key (from your notes)
4. Click **"Add secret"**

**When done:** You'll see all 3 secrets in your list. Come back here for Step 14.

---

## STEP 14: Verify Everything is Set Up

**What to check:**
- ✅ You have a Supabase account
- ✅ You created a project named "tgpc-search"
- ✅ You ran the SQL code and created the "pharmacists" table
- ✅ You saved 3 credentials in your notes
- ✅ You added 3 secrets to GitHub:
  - SUPABASE_URL
  - SUPABASE_ANON_KEY
  - SUPABASE_SERVICE_KEY

**All done?** Congratulations! 🎉 Your database is ready. You can now move to the next task.

---

## Common Problems and Solutions

**Problem:** "relation already exists" error when running SQL
- **Solution:** The table was already created. You can skip this step.

**Problem:** Can't find the API keys
- **Solution:** Go to Settings (gear icon) → API in your Supabase dashboard

**Problem:** GitHub won't let me add secrets
- **Solution:** Make sure you're in the repository Settings, not your personal settings

---

## What You Get for Free

Your free Supabase account includes:
- 500 MB database storage (enough for many years of pharmacist data)
- 2 GB bandwidth per month
- 50,000 monthly active users
- Unlimited API requests

This is more than enough for your personal TGPC search website!

---

## Need Help?

If you get stuck on any step, just tell me:
1. Which step number you're on
2. What you see on your screen
3. Any error messages

I'll help you figure it out!
