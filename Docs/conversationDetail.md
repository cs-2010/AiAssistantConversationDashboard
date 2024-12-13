# Conversation History Data Format Documentation

## Overview
This document describes a JSON format designed to store complete conversation histories in Unity/game development context, including messages, functions, and contextual data.

## Base Structure
```json
{
  "_id": "<ObjectId>",
  "id": "<string>",
  "title": "<string>",
  "history": [<array of messages>],
  "owners": ["<user ids>"],
  "tags": [],
  "context": null,
  "is_favorite": <boolean>,
  "function_catalog": [<array of functions>]
}
```

## Message Objects
Each message in the history array contains:

### Core Fields
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique message identifier |
| `request_id` | string | Request tracking ID |
| `timestamp` | number | Unix timestamp |
| `role` | string | "user" or "assistant" |
| `content` | string | Message content |
| `author` | string | Author identifier |

### Metadata Fields
| Field | Type | Description |
|-------|------|-------------|
| `tags` | array | Associated tags |
| `preferred` | boolean/null | Preference indicator |
| `context_id` | string/null | Context reference |
| `is_internal_unity` | boolean | Unity internal flag |
| `opt_status` | string | Opt status |
| `is_beta_request` | boolean | Beta flag |

## Function Catalog
Each function entry contains:

### Function Definition
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Function name |
| `description` | string | Function purpose |
| `parameters` | array | Function parameters |
| `tags` | array | Function tags |

### Parameter Fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Parameter name |
| `type` | string | Parameter type |
| `description` | string | Parameter description |

## Function Types
The system includes several core function types:

1. **Project Structure Functions**
   - ProjectStructureExtractor
   - ProjectSettingExtractor
   - SceneHierarchyExtractor

2. **Object Management**
   - ObjectDataExtractor
   - TriggerAgentFromPrompt

## Implementation Notes

### Message Processing
- Messages are ordered chronologically by timestamp
- Each message maintains its own context and metadata
- Responses can include code snippets and instructions

### Function Handling
- Functions are registered in the catalog with full definitions
- Parameters are strictly typed and documented
- Each function has specific tags for categorization

### Context Management
- Context can be tracked at conversation and message level
- Unity-specific context is maintained through internal flags