BEGIN;

-- Drop the existing non-deferrable constraint
ALTER TABLE data_rooms 
DROP CONSTRAINT IF EXISTS fk_data_room_root_folder;

-- Add the constraint back as deferrable
ALTER TABLE data_rooms 
ADD CONSTRAINT fk_data_room_root_folder 
    FOREIGN KEY (root_folder_id) REFERENCES folders(id) 
    ON DELETE SET NULL 
    DEFERRABLE INITIALLY IMMEDIATE;

-- Add comment explaining the change
COMMENT ON CONSTRAINT fk_data_room_root_folder ON data_rooms IS 
    'Foreign key constraint made deferrable to support atomic data room and root folder creation';

COMMIT;