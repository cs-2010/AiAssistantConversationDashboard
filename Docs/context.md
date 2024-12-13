# Unity Context Data Format Documentation

## Overview
This documentation describes various context data formats used in Unity for tracking game objects, scripts, project structure, and scene information.

## Base Structure
```json
{
  "_id": "<ObjectId>",
  "id": "<string>",
  "conversation_id": "<string>",
  "data": "<string>",
  "fragment_id": "<string>",
  "timestamp": <number>
}
```

## Context Types

### 1. MonoScript Context
Details about a C# script file in the project.

#### Structure
```json
{
  "Type": "MonoScript",
  "Path": "<string>",
  "Properties": {
    "m_Name": "<string>",
    "m_ClassName": "<string>",
    "m_Namespace": "<string>",
    "m_AssemblyName": "<string>"
  },
  "File contents": "<string>"
}
```

### 2. GameObject Context
Details about a Unity GameObject and its components.

#### Structure
```json
{
  "Type": "GameObject",
  "Components": [
    {
      "component - <ComponentType>": {
        "m_GameObject": "<string>",
        "m_Enabled": <boolean>,
        "Properties": {
          // Component-specific properties
        }
      }
    }
  ],
  "Properties": {
    "m_Name": "<string>",
    "m_TagString": "<string>",
    "m_IsActive": <boolean>
  }
}
```

### 3. Project Structure Context
Hierarchical representation of project files and folders.

#### Structure
```json
{
  "Type": "Project Structure",
  "Contents": {
    // Directory tree structure
  }
}
```

### 4. Scene Hierarchy Context
List of GameObjects in the current scene.

#### Structure
```json
{
  "Type": "Scene Hierarchy",
  "Objects": [
    "<GameObject names>"
  ]
}
```

## Common Fields

### Identifiers
| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | Database identifier |
| `id` | string | Context identifier |
| `conversation_id` | string | Associated conversation |
| `fragment_id` | string | Fragment reference |

### Metadata
| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | number | Unix timestamp |
| `Type` | string | Context type identifier |
| `Path` | string | Asset path (if applicable) |

## Unity-Specific Fields

### MonoBehaviour Properties
| Field | Type | Description |
|-------|------|-------------|
| `m_Script` | reference | Script reference |
| `m_Enabled` | boolean | Component enabled state |
| `m_EditorHideFlags` | number | Editor visibility flags |

### Transform Properties
| Field | Type | Description |
|-------|------|-------------|
| `m_LocalPosition` | Vector3 | Position in local space |
| `m_LocalRotation` | Quaternion | Rotation in local space |
| `m_LocalScale` | Vector3 | Scale in local space |

