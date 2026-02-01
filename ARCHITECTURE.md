# Annapurna-AI Architecture

This document visualizes the high-level architecture of the Annapurna-AI application, illustrating the flow of data between the Client, Frontend, Backend, and External Services.

## Architecture Diagram

```mermaid
graph TB
    %% =====================
    %% Client Layer
    %% =====================
    subgraph Client ["Client Layer"]
        User(("User (Browser)"))
    end

    %% =====================
    %% Frontend Layer
    %% =====================
    subgraph Frontend ["Frontend (Next.js App Router)"]
        UI["UI Components (Radix + Tailwind)"]
        Pages["App Router (Pages)"]
        AuthMiddleware["Auth Middleware (Clerk)"]
    end

    %% =====================
    %% Backend Layer
    %% =====================
    subgraph Backend ["Backend (FastAPI)"]
        APIGateway["API Gateway (/api/v1)"]

        subgraph Middleware ["Middleware Layer"]
            RateLimit["Rate Limiter (SlowAPI)"]
            AuditLog["Audit Logger (structlog)"]
            AuthGuard["Auth Dependency (JWT)"]
        end

        subgraph ServiceLayer ["Service Layer"]
            Orchestrator["Evidence Orchestrator"]
            PlanService["Plan Service"]
            EvidenceService["Evidence Service"]
            LLMService["LLM Service"]
        end

        subgraph DataLayer ["Data Access Layer"]
            DB[(SQLModel DB)]
            USDAClient["USDA Client"]
            PubMedClient["PubMed Client"]
        end
    end

    %% =====================
    %% External Services
    %% =====================
    subgraph External ["External Services"]
        OpenAI["OpenAI / LiteLLM"]
        USDA["USDA FoodData Central"]
        PubMed["PubMed API"]
        Clerk["Clerk Auth"]
    end

    %% =====================
    %% Client → Frontend
    %% =====================
    User -->|HTTPS| UI
    UI --> Pages
    Pages --> AuthMiddleware

    %% =====================
    %% Auth Flow
    %% =====================
    User -->|Login| Clerk
    AuthMiddleware -->|Session/JWT| Clerk
    Pages -->|JWT| APIGateway

    %% =====================
    %% Backend Request Flow
    %% =====================
    APIGateway --> RateLimit
    RateLimit --> AuditLog
    AuditLog --> AuthGuard
    AuthGuard --> Orchestrator

    %% =====================
    %% Service Coordination
    %% =====================
    Orchestrator -->|Request Evidence| EvidenceService
    Orchestrator -->|Create Plan| PlanService

    EvidenceService -->|Primary Search| DB
    EvidenceService -->|Fallback Search| PubMedClient

    PlanService -->|Nutrition Data| USDAClient
    PlanService -->|Generate Text| LLMService
    PlanService -->|Persist| DB

    %% =====================
    %% External Calls
    %% =====================
    LLMService -->|Inference| OpenAI
    USDAClient -->|Food Query| USDA
    PubMedClient -->|Literature Search| PubMed

    %% =====================
    %% Styling
    %% =====================
    classDef client fill:#f9f,stroke:#333,stroke-width:2px;
    classDef frontend fill:#d4e1f5,stroke:#333,stroke-width:2px;
    classDef backend fill:#e1f5d4,stroke:#333,stroke-width:2px;
    classDef data fill:#fff3cd,stroke:#333,stroke-width:2px;
    classDef external fill:#f0f0f0,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5;

    class User client;
    class UI,Pages,AuthMiddleware frontend;
    class APIGateway,RateLimit,AuditLog,AuthGuard,Orchestrator,PlanService,EvidenceService,LLMService backend;
    class DB,USDAClient,PubMedClient data;
    class OpenAI,USDA,PubMed,Clerk external;
```

## Component Details

### Frontend
- **Next.js 16**: Uses App Router for routing and server-side rendering.
- **Clerk**: Handles user authentication and session management.
- **Tailwind CSS & Radix UI**: Provides the styling and accessible interactive components.

### Backend
- **FastAPI**: Main application framework.
- **Orchestrator**: Central logic for handling complex flows like "Evidence Retrieval" which combines safety checks, local guideline lookups, and external research searches.
- **Services**:
    - `PlanService`: Manages meal plan creation using LLMs and user preferences.
    - `EvidenceService`: Interfaces with local curated data (IFCT/Guidelines).
- **Middleware**: Includes Rate Limiting (SlowAPI) and detailed structural logging for auditability.

### Data & External
- **SQLModel**: ORM for database interactions.
- **External APIs**: 
    - **USDA**: For accurate food nutrition data.
    - **PubMed**: For fetching scientific abstracts.
    - **OpenAI**: For intelligence and plan synthesis.
