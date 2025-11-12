-- TGPC Pharmacist Search - Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor after creating your project

-- Create the pharmacists table
CREATE TABLE IF NOT EXISTS pharmacists (
    id BIGSERIAL PRIMARY KEY,
    serial_number INTEGER,
    registration_number TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    father_name TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for fast search performance
CREATE INDEX IF NOT EXISTS idx_registration ON pharmacists(registration_number);
CREATE INDEX IF NOT EXISTS idx_name ON pharmacists(name);
CREATE INDEX IF NOT EXISTS idx_father ON pharmacists(father_name);

-- Enable Row Level Security (RLS)
ALTER TABLE pharmacists ENABLE ROW LEVEL SECURITY;

-- Create policy for read-only public access
-- This allows anyone with the anon key to read data but not modify it
CREATE POLICY "Allow public read access"
ON pharmacists
FOR SELECT
TO anon
USING (true);

-- Optional: Create policy for service role to have full access
-- This allows the sync script to insert/update/delete records
CREATE POLICY "Allow service role full access"
ON pharmacists
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);