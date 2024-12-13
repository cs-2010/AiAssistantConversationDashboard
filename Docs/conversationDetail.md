# Message History File Format Documentation

## Overview
The Message History file format is a JSON-based structure designed to store conversation histories with associated metadata, classifications, and performance metrics.

## Base Structure
```json
{
  "_id": "<string>",
  "schema_version": <number>,
  "conversation_id": "<string>",
  "message_history": [...],
  "last_updated_timestamp": <number>
}
```

### Root Fields
| Field | Type | Description |
|-------|------|-------------|
| `_id` | string | Unique identifier for the conversation |
| `schema_version` | number | Version number of the schema |
| `conversation_id` | string | Unique conversation identifier |
| `message_history` | array | Array of message objects |
| `last_updated_timestamp` | number | Unix timestamp of last update |

## Message Objects
Each object in the `message_history` array contains the following structure:

### Core Fields
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique message identifier |
| `request_id` | string | Request tracking identifier |
| `timestamp` | number | Unix timestamp of message |
| `role` | string | Message sender role (e.g., "user", "assistant") |
| `content` | string | Message content |
| `author` | string | Author identifier/name |
| `tags` | array | Associated tags |

### Optional Metadata
| Field | Type | Description |
|-------|------|-------------|
| `preferred` | null/boolean | Preference indicator |
| `context_id` | null/string | Context identifier |
| `selected_context_metadata` | null/object | Selected context metadata |
| `is_internal_unity` | boolean | Internal unity status |
| `opt_status` | string | Opt status indicator |
| `is_beta_request` | boolean | Beta request status |

### Classification Data
Messages may include a `front_desk_classification_results` object containing:

| Field | Type | Description |
|-------|------|-------------|
| `user_language` | string | Detected language |
| `is_safe` | boolean | Safety check result |
| `unity_topics` | array | Relevant topics |
| `sentiment` | string | Message sentiment |
| `plugins` | array/null | Plugin information |
| `external_knowledge` | string | Knowledge requirement level |

### Performance Metrics
| Field | Type | Description |
|-------|------|-------------|
| `message_tokens` | object | Token usage metrics |
| `seconds_until_finished` | number | Processing completion time |
| `seconds_until_streaming` | number | Time until streaming began |

## Implementation Notes

### Timestamps
- All timestamps are stored in Unix timestamp format (milliseconds since epoch)
- `last_updated_timestamp` tracks the most recent update to the conversation

### Nullable Fields
- Fields marked as nullable may contain null or be omitted
- Arrays may be empty but should be present if specified in the schema

### Schema Versioning
- The `schema_version` field should be checked for compatibility
- Different versions may have different required/optional fields

### Example Usage
```json
{
  "_id": "ObjectId('123')",
  "schema_version": 2,
  "conversation_id": "abc-123",
  "message_history": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "Hello",
      ...
    }
  ],
  "last_updated_timestamp": 1732782425694
}
```

