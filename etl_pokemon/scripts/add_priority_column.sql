-- Migration: Add priority column to move table
-- This script adds the priority column for move priority in battle
-- Run this before re-running the ETL if the table already exists

-- Add column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'move' AND column_name = 'priority'
    ) THEN
        ALTER TABLE move ADD COLUMN priority INTEGER NOT NULL DEFAULT 0;
    END IF;
END $$;

-- Verify the column was added
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'move' AND column_name = 'priority';
