-- Chat/Dynamic Records Database Schema

-- Chat Rooms
CREATE TABLE chat_rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- public, private, group
    created_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    max_participants INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Room Participants
CREATE TABLE room_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID REFERENCES chat_rooms(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- owner, moderator, participant
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_read_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(room_id, user_id)
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID REFERENCES chat_rooms(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id) ON DELETE SET NULL,
    message_type VARCHAR(50) NOT NULL, -- text, image, video, audio
    content TEXT,
    media_url TEXT,
    is_edited BOOLEAN DEFAULT false,
    parent_message_id UUID REFERENCES messages(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Live Streams
CREATE TABLE live_streams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID REFERENCES chat_rooms(id) ON DELETE CASCADE,
    streamer_id UUID REFERENCES users(id),
    title VARCHAR(255),
    status VARCHAR(50) NOT NULL, -- live, ended, scheduled
    stream_key VARCHAR(255),
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    max_viewers INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Stream Viewers
CREATE TABLE stream_viewers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_id UUID REFERENCES live_streams(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMP WITH TIME ZONE,
    device_info JSONB
);

-- Media Files
CREATE TABLE media_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    uploader_id UUID REFERENCES users(id),
    file_type VARCHAR(50) NOT NULL, -- image, video, audio
    file_url TEXT NOT NULL,
    thumbnail_url TEXT,
    mime_type VARCHAR(100),
    file_size INTEGER,
    duration INTEGER, -- for audio/video
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Interactions
CREATE TABLE user_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    target_type VARCHAR(50) NOT NULL, -- message, stream, media
    target_id UUID NOT NULL,
    interaction_type VARCHAR(50) NOT NULL, -- like, share, report
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_room_participants_room ON room_participants(room_id);
CREATE INDEX idx_room_participants_user ON room_participants(user_id);
CREATE INDEX idx_messages_room ON messages(room_id);
CREATE INDEX idx_messages_sender ON messages(sender_id);
CREATE INDEX idx_messages_parent ON messages(parent_message_id);
CREATE INDEX idx_live_streams_room ON live_streams(room_id);
CREATE INDEX idx_live_streams_streamer ON live_streams(streamer_id);
CREATE INDEX idx_stream_viewers_stream ON stream_viewers(stream_id);
CREATE INDEX idx_stream_viewers_user ON stream_viewers(user_id);
CREATE INDEX idx_media_files_uploader ON media_files(uploader_id);
CREATE INDEX idx_user_interactions_user ON user_interactions(user_id);
CREATE INDEX idx_user_interactions_target ON user_interactions(target_id);
