# backend/services/prompt_templates.py

def get_diagram_prompt(diagram_type: str, repo_context: str) -> str:
    """Get prompt template for specific diagram types"""
    
    base_prompt = f"""
You are an expert software architect analyzing this GitHub repository:

{repo_context}

Generate a detailed {diagram_type} diagram in Mermaid syntax.

IMPORTANT RULES:
1. Base the diagram on ACTUAL files, components, and code from the repository above
2. Use proper Mermaid syntax
3. Return ONLY the Mermaid code, no explanations
4. Make it detailed and comprehensive
5. Reference real file names and components from the repository
"""
    
    specific_instructions = {
        "sequence": """
Create a sequence diagram showing the main user interaction flow.
Include actual API endpoints, services, and database calls you see in the code.
Example format:
```
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Service
    participant Database
    
    User->>Frontend: action
    Frontend->>API: POST /endpoint
    API->>Service: method()
    Service->>Database: query
    Database-->>Service: data
    Service-->>API: response
    API-->>Frontend: JSON
    Frontend-->>User: display
```
""",
        "component": """
Create a component diagram showing the system architecture.
Include actual modules, services, and their dependencies from the codebase.
Example format:
```
graph TB
    subgraph Frontend
        A[Component1]
        B[Component2]
    end
    
    subgraph Backend
        C[Service1]
        D[Service2]
    end
    
    subgraph Database
        E[DB]
    end
    
    A-->C
    B-->D
    C-->E
    D-->E
```
""",
        "database": """
Create an ER diagram showing the database schema.
Base it on actual models, schemas, or database files you see.
Example format:
```
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"
    
    USER {
        int id PK
        string email
        string name
    }
    
    ORDER {
        int id PK
        int user_id FK
        date created_at
    }
```
""",
        "flowchart": """
Create a flowchart showing the main business logic flow.
Base it on actual functions and control flow from the code.
Example format:
```
flowchart TD
    Start([Start]) --> Input[/User Input/]
    Input --> Validate{Valid?}
    Validate -->|Yes| Process[Process Data]
    Validate -->|No| Error[Show Error]
    Process --> Save[(Save to DB)]
    Save --> Success([Success])
    Error --> End([End])
    Success --> End
```
""",
        "class": """
Create a class diagram showing the object-oriented structure.
Include actual classes, their methods, and relationships from the code.
Example format:
```
classDiagram
    class User {
        +int id
        +string email
        +login()
        +logout()
    }
    
    class Order {
        +int id
        +Date created
        +calculate_total()
    }
    
    User "1" --> "*" Order : has
```
"""
    }
    
    return base_prompt + "\n\n" + specific_instructions.get(diagram_type, "")

def get_custom_diagram_prompt(user_request: str, repo_context: str) -> str:
    """Get prompt for custom user-requested diagrams"""
    
    return f"""
You are an expert software architect analyzing this GitHub repository:

{repo_context}

User's Request: {user_request}

Generate a Mermaid diagram that fulfills the user's request.

IMPORTANT RULES:
1. Base the diagram on ACTUAL files, components, and code from the repository
2. Choose the most appropriate Mermaid diagram type (sequence, flowchart, class, component, etc.)
3. Use proper Mermaid syntax
4. Return ONLY the Mermaid code, no explanations
5. Make it detailed and reference real elements from the codebase
6. If the user's request is unclear, create the most relevant architecture diagram

Common Mermaid diagram types:
- sequenceDiagram: for interaction flows
- flowchart TD: for process flows
- classDiagram: for OOP structure
- graph TB: for component architecture
- erDiagram: for database schema
- stateDiagram-v2: for state machines
"""