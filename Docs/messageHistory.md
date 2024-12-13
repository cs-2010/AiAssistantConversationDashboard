# Message Object Documentation

## Overview
This document describes the structure of a single message object within a conversation system, including user input classification and safety validation.

## Base Structure
```json
{
  "id": "<string>",
  "request_id": "<string>",
  "timestamp": <number>,
  "role": "<string>",
  "content": "<string>",
  "author": "<string>"
}
```

### Core Fields
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique message identifier |
| `request_id` | string | Request tracking identifier |
| `timestamp` | number | Unix timestamp of message |
| `role` | string | Message sender role (e.g., "user") |
| `content` | string | Message content |
| `author` | string | Author identifier |

### Metadata Fields
| Field | Type | Description |
|-------|------|-------------|
| `tags` | array | Associated tags |
| `preferred` | null/boolean | Preference indicator |
| `context_id` | null/string | Context identifier |
| `is_internal_unity` | boolean | Internal Unity User |
| `opt_status` | string | Opt status indicator |
| `is_beta_request` | boolean | Beta request status |

## Classification Results
The `front_desk_classification_results` object contains:

### Core Classification Fields
| Field | Type | Description |
|-------|------|-------------|
| `user_language` | string | Detected language of message |
| `is_safe` | boolean | Safety check result |
| `unity_topics` | array | Array of relevant Unity topics |
| `sentiment` | string | Message sentiment analysis |
| `plugins` | array | Relevant plugins information |
| `external_knowledge` | string | Required knowledge level |
| `is_valid_query` | boolean | Query validation status |

### Classification Specifications
Each classification type includes detailed specifications:

```json
{
  "allowed_predictions": ["<array of allowed values>"],
  "max_predictions": <number>,
  "will_deny_query": ["<array of denial conditions>"],
  "description": "<string>"
}
```

## Implementation Notes

### Language Support
- Supports multiple languages including Arabic, Chinese, Dutch, English, French, German, Italian, Japanese, Korean, Portuguese, Russian, Spanish, Turkish
- Default fallback to "unknown"

### Safety Validation
- Binary validation (true/false)
- Includes comprehensive safety policy description
- Evaluates against defined content guidelines

### Topic Classification
- Supports multiple Unity-related topics
- Limited to maximum of 3 topics per message
- Includes both technical and gameplay-related categories

### Knowledge Levels
Three levels of external knowledge requirements:
- `none`: No external documentation needed
- `intermediate`: Some documentation beneficial
- `advanced`: Requires extensive documentation