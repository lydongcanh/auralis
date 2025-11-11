BEGIN;

ALTER TABLE data_rooms
    ADD COLUMN client_id VARCHAR(255) DEFAULT NULL,
    ADD COLUMN client_secret VARCHAR(255) DEFAULT NULL;

COMMENT ON COLUMN data_rooms.client_id IS 'Client identifier for external integrations, only available for Ansarada sources';
COMMENT ON COLUMN data_rooms.client_secret IS 'Encrypted secret for external integrations, only available for Ansarada sources';

COMMIT;