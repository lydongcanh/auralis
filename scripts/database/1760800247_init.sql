-- Enable pgcrypto extension for generating unique identifiers
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Drop existing tables if they exist (for development purposes)
DROP TABLE IF EXISTS project_data_rooms CASCADE;
DROP TABLE IF EXISTS user_projects CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS folders CASCADE;
DROP TABLE IF EXISTS data_rooms CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop existing types if they exist
DROP TYPE IF EXISTS entity_status CASCADE;
DROP TYPE IF EXISTS user_role CASCADE;
DROP TYPE IF EXISTS data_room_source CASCADE;

-- Create ENUM types
CREATE TYPE entity_status AS ENUM (
    'active',
    'disabled',
    'deleted'
);

CREATE TYPE user_role AS ENUM (
    'admin',
    'editor',
    'viewer'
);

CREATE TYPE data_room_source AS ENUM (
    'original',
    'ansarada'
);

-- Create Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_provider_user_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status entity_status DEFAULT 'active'
);

-- Create Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status entity_status DEFAULT 'active'
);

-- Create Data Rooms table
CREATE TABLE data_rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    source data_room_source NOT NULL DEFAULT 'original',
    root_folder_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status entity_status DEFAULT 'active'
);

-- Create Folders table
CREATE TABLE folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    data_room_id UUID NOT NULL,
    parent_folder_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status entity_status DEFAULT 'active',
    
    CONSTRAINT fk_folder_data_room 
        FOREIGN KEY (data_room_id) REFERENCES data_rooms(id) ON DELETE CASCADE,
    CONSTRAINT fk_folder_parent 
        FOREIGN KEY (parent_folder_id) REFERENCES folders(id) ON DELETE CASCADE
);

-- Create Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    content TEXT,
    data_room_id UUID NOT NULL,
    folder_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status entity_status DEFAULT 'active',
    
    CONSTRAINT fk_document_data_room 
        FOREIGN KEY (data_room_id) REFERENCES data_rooms(id) ON DELETE CASCADE,
    CONSTRAINT fk_document_folder 
        FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE CASCADE
);

-- Create User-Project junction table (many-to-many with role)
CREATE TABLE user_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    project_id UUID NOT NULL,
    user_role user_role NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status entity_status DEFAULT 'active',
    
    CONSTRAINT fk_user_project_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_project_project 
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    
    -- Ensure unique user-project combinations
    CONSTRAINT unique_user_project UNIQUE (user_id, project_id)
);

-- Create Project-DataRoom junction table (many-to-many)
CREATE TABLE project_data_rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL,
    data_room_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status entity_status DEFAULT 'active',
    
    CONSTRAINT fk_project_data_room_project 
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_project_data_room_data_room 
        FOREIGN KEY (data_room_id) REFERENCES data_rooms(id) ON DELETE CASCADE,
    
    -- Ensure unique project-data_room combinations
    CONSTRAINT unique_project_data_room UNIQUE (project_id, data_room_id)
);

-- Add foreign key constraint for root_folder_id in data_rooms
ALTER TABLE data_rooms 
ADD CONSTRAINT fk_data_room_root_folder 
    FOREIGN KEY (root_folder_id) REFERENCES folders(id) ON DELETE SET NULL;

-- Create indexes for better performance
CREATE INDEX idx_users_auth_provider_user_id ON users(auth_provider_user_id);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);

CREATE INDEX idx_projects_name ON projects(name);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at);

CREATE INDEX idx_data_rooms_name ON data_rooms(name);
CREATE INDEX idx_data_rooms_source ON data_rooms(source);
CREATE INDEX idx_data_rooms_status ON data_rooms(status);
CREATE INDEX idx_data_rooms_created_at ON data_rooms(created_at);

CREATE INDEX idx_folders_data_room_id ON folders(data_room_id);
CREATE INDEX idx_folders_parent_folder_id ON folders(parent_folder_id);
CREATE INDEX idx_folders_name ON folders(name);
CREATE INDEX idx_folders_status ON folders(status);

CREATE INDEX idx_documents_data_room_id ON documents(data_room_id);
CREATE INDEX idx_documents_folder_id ON documents(folder_id);
CREATE INDEX idx_documents_name ON documents(name);
CREATE INDEX idx_documents_status ON documents(status);

CREATE INDEX idx_user_projects_user_id ON user_projects(user_id);
CREATE INDEX idx_user_projects_project_id ON user_projects(project_id);
CREATE INDEX idx_user_projects_user_role ON user_projects(user_role);
CREATE INDEX idx_user_projects_status ON user_projects(status);

CREATE INDEX idx_project_data_rooms_project_id ON project_data_rooms(project_id);
CREATE INDEX idx_project_data_rooms_data_room_id ON project_data_rooms(data_room_id);
CREATE INDEX idx_project_data_rooms_status ON project_data_rooms(status);

-- Create trigger function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_rooms_updated_at 
    BEFORE UPDATE ON data_rooms 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_folders_updated_at 
    BEFORE UPDATE ON folders 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON documents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_projects_updated_at 
    BEFORE UPDATE ON user_projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_data_rooms_updated_at 
    BEFORE UPDATE ON project_data_rooms 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE users IS 'Stores user information and authentication details';
COMMENT ON TABLE projects IS 'Contains project information and metadata';
COMMENT ON TABLE data_rooms IS 'Stores data room details and configuration';
COMMENT ON TABLE folders IS 'Hierarchical folder structure within data rooms';
COMMENT ON TABLE documents IS 'Documents stored within folders and data rooms';
COMMENT ON TABLE user_projects IS 'Many-to-many relationship between users and projects with roles';
COMMENT ON TABLE project_data_rooms IS 'Many-to-many relationship between projects and data rooms';

COMMENT ON COLUMN users.auth_provider_user_id IS 'External authentication provider user identifier';
COMMENT ON COLUMN data_rooms.source IS 'Source of the data room (original or imported from Ansarada)';
COMMENT ON COLUMN data_rooms.root_folder_id IS 'Reference to the root folder of this data room';
COMMENT ON COLUMN folders.parent_folder_id IS 'Reference to parent folder (NULL for root folders)';
COMMENT ON COLUMN user_projects.user_role IS 'User role within the specific project';


COMMIT;
