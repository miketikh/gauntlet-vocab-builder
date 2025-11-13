# OpenAPI Type Generation Workflow

This document explains how we achieve end-to-end type safety between the FastAPI backend and Next.js frontend.

## Overview

Instead of manually maintaining TypeScript types for API requests/responses, we:
1. Define types once in Python using SQLModel/Pydantic
2. FastAPI auto-generates OpenAPI schema from these types
3. TypeScript types are generated from the OpenAPI schema
4. Frontend uses generated types for type-safe API calls

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Python)                         │
├─────────────────────────────────────────────────────────────┤
│  SQLModel Models (models/database.py)                       │
│    ↓                                                         │
│  FastAPI Endpoints with response_model                      │
│    ↓                                                         │
│  OpenAPI JSON Schema (/openapi.json)                        │
└─────────────────────────────────────────────────────────────┘
                         ↓
                         │ openapi-typescript
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (TypeScript)                     │
├─────────────────────────────────────────────────────────────┤
│  Generated Types (types/api.ts)                             │
│    ↓                                                         │
│  Type-safe API Client (lib/api-client.ts)                   │
│    ↓                                                         │
│  React Components with full IntelliSense                    │
└─────────────────────────────────────────────────────────────┘
```

## Backend Setup (FastAPI)

### 1. Define SQLModel Models

In `api/models/database.py`:

```python
from sqlmodel import SQLModel, Field

# Table model (database)
class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    educator_id: int = Field(foreign_key="educators.id")
    name: str
    grade_level: int = Field(ge=6, le=12)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# API response model
class StudentPublic(SQLModel):
    id: int
    educator_id: int
    name: str
    grade_level: int
    created_at: datetime

# API create model
class StudentCreate(SQLModel):
    name: str
    grade_level: int = Field(ge=6, le=12)
```

### 2. Use Models in FastAPI Endpoints

In `api/main.py`:

```python
from models.database import Student, StudentPublic, StudentCreate

@app.get("/api/students", response_model=list[StudentPublic])
async def get_students(session: Session = Depends(get_session)):
    students = session.exec(select(Student)).all()
    return students

@app.post("/api/students", response_model=StudentPublic)
async def create_student(
    student: StudentCreate,
    session: Session = Depends(get_session)
):
    db_student = Student(**student.dict())
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student
```

### 3. FastAPI Auto-generates OpenAPI Schema

FastAPI automatically creates `/openapi.json` with full type information:

```json
{
  "paths": {
    "/api/students": {
      "get": {
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": { "$ref": "#/components/schemas/StudentPublic" }
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "StudentPublic": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "name": { "type": "string" },
          "grade_level": { "type": "integer", "minimum": 6, "maximum": 12 }
        }
      }
    }
  }
}
```

## Frontend Setup (Next.js)

### 1. Install Dependencies

In `web/package.json`:

```json
{
  "scripts": {
    "generate:api-types": "openapi-typescript http://localhost:8000/openapi.json -o ./types/api.ts"
  },
  "devDependencies": {
    "openapi-typescript": "^7.4.3",
    "openapi-fetch": "^0.12.2"
  }
}
```

### 2. Generate TypeScript Types

```bash
# Start FastAPI server
cd api
uvicorn main:app --reload

# In another terminal, generate types
cd web
npm run generate:api-types
```

This creates `web/types/api.ts` with full TypeScript types:

```typescript
export interface paths {
  "/api/students": {
    get: {
      responses: {
        200: {
          content: {
            "application/json": StudentPublic[];
          };
        };
      };
    };
    post: {
      requestBody: {
        content: {
          "application/json": StudentCreate;
        };
      };
      responses: {
        200: {
          content: {
            "application/json": StudentPublic;
          };
        };
      };
    };
  };
}

export interface components {
  schemas: {
    StudentPublic: {
      id: number;
      educator_id: number;
      name: string;
      grade_level: number;
      created_at: string;
    };
    StudentCreate: {
      name: string;
      grade_level: number;
    };
  };
}
```

### 3. Create Type-safe API Client

In `web/lib/api-client.ts`:

```typescript
import createClient from "openapi-fetch";
import type { paths } from "@/types/api";

export const apiClient = createClient<paths>({
  baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
});

export function setAuthToken(token: string | null) {
  if (token) {
    apiClient.headers.set("Authorization", `Bearer ${token}`);
  } else {
    apiClient.headers.delete("Authorization");
  }
}
```

### 4. Use in React Components

```typescript
import { apiClient } from "@/lib/api-client";

export default function StudentsPage() {
  const [students, setStudents] = useState([]);

  useEffect(() => {
    async function loadStudents() {
      // Fully typed request and response
      const { data, error } = await apiClient.GET("/api/students");

      if (error) {
        console.error("Failed to load students:", error);
        return;
      }

      // `data` is typed as StudentPublic[]
      setStudents(data);
    }

    loadStudents();
  }, []);

  return (
    <div>
      {students.map((student) => (
        <div key={student.id}>
          {/* Full IntelliSense for student.name, student.grade_level, etc. */}
          <h2>{student.name}</h2>
          <p>Grade: {student.grade_level}</p>
        </div>
      ))}
    </div>
  );
}
```

## Development Workflow

### Making Changes to API

1. **Modify SQLModel models** in `api/models/database.py`
2. **Update endpoints** in `api/main.py` (use new models)
3. **Test API** at http://localhost:8000/docs
4. **Regenerate types:**
   ```bash
   cd web
   npm run generate:api-types
   ```
5. **Update frontend** code with new types (TypeScript will show errors for outdated code)
6. **Commit everything** (models, endpoints, generated types)

### When to Regenerate Types

Regenerate types when:
- Adding new endpoints
- Changing request/response models
- Modifying field names or types
- Adding/removing fields
- Changing validation rules

### Continuous Integration

Add to CI pipeline:

```yaml
# .github/workflows/ci.yml
- name: Start FastAPI
  run: |
    cd api
    uvicorn main:app --reload &
    sleep 5  # Wait for server to start

- name: Generate API types
  run: |
    cd web
    npm run generate:api-types

- name: Check for type changes
  run: |
    git diff --exit-code web/types/api.ts || \
    (echo "API types are out of sync! Run 'npm run generate:api-types'" && exit 1)
```

## Benefits

### Type Safety
- Catch API mismatches at compile time
- Full IntelliSense in IDE
- Refactor with confidence

### Single Source of Truth
- Types defined once in Python
- No manual TypeScript type maintenance
- Guaranteed sync between backend and frontend

### Better Developer Experience
- Autocomplete for API endpoints
- Type errors for invalid requests
- Documentation in IDE

### Reduced Bugs
- Impossible to call non-existent endpoints
- Can't send wrong request body
- Response types always match

## Comparison with Manual Types

### ❌ Manual Approach (Old Way)

```typescript
// Frontend: web/types/api.ts (manually maintained)
export interface Student {
  id: number;
  name: string;
  grade: number; // Oops, backend uses "grade_level"
}

// Backend changes grade_level to be optional
// Frontend breaks silently - no way to know!
```

Problems:
- Types drift out of sync
- Requires manual updates
- No guarantee of correctness
- Refactoring is risky

### ✅ Generated Approach (New Way)

```typescript
// Types generated from OpenAPI
// Always in sync with backend
// TypeScript errors if backend changes
```

Benefits:
- Always up to date
- Zero maintenance
- Compile-time errors
- Safe refactoring

## Troubleshooting

### "Cannot find module '@/types/api'"

Run type generation:
```bash
cd web
npm run generate:api-types
```

### "Failed to fetch OpenAPI schema"

Ensure FastAPI is running:
```bash
cd api
uvicorn main:app --reload
```

Verify endpoint is accessible:
```bash
curl http://localhost:8000/openapi.json
```

### Types are outdated

Regenerate types after backend changes:
```bash
cd web
npm run generate:api-types
```

### TypeScript errors after regeneration

This is good! It means the backend changed and your frontend needs updating.
Fix the TypeScript errors to match the new API.

## Best Practices

### DO:
- Regenerate types after every API change
- Commit generated types to version control
- Use `response_model` on all FastAPI endpoints
- Add validation to Pydantic/SQLModel models
- Document complex types with docstrings

### DON'T:
- Don't manually edit `types/api.ts`
- Don't skip type regeneration
- Don't use `any` types to bypass errors
- Don't deploy frontend without regenerating types

## Additional Resources

- [openapi-typescript Documentation](https://github.com/drwpow/openapi-typescript)
- [openapi-fetch Documentation](https://github.com/drwpow/openapi-typescript/tree/main/packages/openapi-fetch)
- [FastAPI OpenAPI Documentation](https://fastapi.tiangolo.com/tutorial/metadata/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
