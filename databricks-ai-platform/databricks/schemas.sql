-- Delta schemas for document intelligence platform
CREATE TABLE IF NOT EXISTS raw_documents (
    document_id STRING,
    filename STRING,
    content BINARY,
    content_type STRING,
    source_path STRING,
    created_at TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS parsed_documents (
    document_id STRING,
    text STRING,
    parser STRING,
    created_at TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS text_chunks (
    document_id STRING,
    chunk_id STRING,
    chunk_index INT,
    text STRING,
    created_at TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS embeddings (
    document_id STRING,
    chunk_id STRING,
    embedding ARRAY<DOUBLE>,
    metadata MAP<STRING, STRING>,
    created_at TIMESTAMP
) USING DELTA;
