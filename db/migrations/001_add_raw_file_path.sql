DO $$
BEGIN
    ALTER TABLE documents ADD COLUMN raw_file_path TEXT;
END
$$;
