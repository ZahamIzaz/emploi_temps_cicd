# 🔄 DIAGRAMMES ARCHITECTURE CI/CD

## Pipeline Flow Global

```mermaid
graph TD
    A[Push/PR vers main] --> B{Type événement}
    B -->|Push main/develop| C[Stage 1: Tests & Quality]
    B -->|Tag v*| D[Stage 1: Tests & Quality + Deploy Flag]
    B -->|Pull Request| E[Stage 1: Tests & Quality Only]
    
    C --> F[Stage 2: Build]
    D --> F
    E --> F
    
    F --> G{Deploy Flag?}
    G -->|Tag v*| H[Stage 3: Deploy]
    G -->|Non| I[End - Artifacts Only]
    
    H --> J[GitHub Release + Docker Registry]
```

## Architecture 3-Stages Détaillée

```mermaid
graph LR
    subgraph "STAGE 1 - TESTS & QUALITY"
        A1[Lint: Black + flake8 + isort]
        A2[Unit Tests: 52 tests + coverage]
        A3[Regression: Snapshots JSON]  
        A4[SonarCloud: Quality + Security]
    end
    
    subgraph "STAGE 2 - BUILD"
        B1[PyInstaller: Console Executable]
        B2[Docker: Multi-stage + Smoke Test]
    end
    
    subgraph "STAGE 3 - DEPLOY"
        C1[GitHub Release: Binaries + Notes]
        C2[Docker Registry: ghcr.io Push]
    end
    
    A1 --> B1
    A2 --> B1  
    A3 --> B1
    A4 --> B1
    
    A1 --> B2
    A2 --> B2
    A3 --> B2  
    A4 --> B2
    
    B1 --> C1
    B2 --> C2
```

## Flux de Données

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub
    participant GA as GitHub Actions
    participant SC as SonarCloud
    participant REG as Container Registry
    
    Dev->>GH: Push code + tag v1.0.0
    GH->>GA: Trigger CI/CD Pipeline
    
    Note over GA: STAGE 1 - Tests & Quality
    GA->>GA: Run lint (Black, flake8, isort)
    GA->>GA: Run 52 unit tests + coverage
    GA->>GA: Run regression tests (snapshots)
    GA->>SC: Send code for analysis
    SC-->>GA: Return quality metrics
    
    Note over GA: STAGE 2 - Build  
    GA->>GA: Build PyInstaller executable
    GA->>GA: Build Docker multi-stage image
    GA->>GA: Run smoke test on container
    
    Note over GA: STAGE 3 - Deploy (conditional)
    GA->>GH: Create GitHub Release + upload binaries
    GA->>REG: Push Docker image to ghcr.io
    
    GA->>Dev: Notification: Pipeline Success ✅
```

## Docker Multi-Stage Build

```mermaid
graph TD
    subgraph "BUILDER STAGE"
        A[python:3.10-slim base]
        A --> B[Install build dependencies]
        B --> C[Copy source code]
        C --> D[Run quick tests]  
        D --> E[Build PyInstaller executable]
    end
    
    subgraph "RUNTIME STAGE"  
        F[python:3.10-slim base]
        F --> G[Minimal runtime deps]
        G --> H[Copy executable from builder]
        H --> I[Create non-root user]
        I --> J[Set permissions & health check]
    end
    
    E -.-> H
    J --> K[Final image ~100MB]
```

## Tests Architecture

```mermaid
graph TB
    subgraph "TEST SUITE"
        A[test_boost_coverage.py - 26 tests]
        B[test_functional.py - 9 tests]
        C[test_parser.py - 14 tests]  
        D[test_regression.py - 3 tests]
    end
    
    subgraph "TEST CONFIGS"
        E[pytest-units.ini - Coverage 30%+]
        F[pytest-regression.ini - No coverage]
    end
    
    subgraph "FIXTURES & SNAPSHOTS"
        G[tests/fixtures/sample_timetable.html]
        H[tests/snapshots/*.json]
    end
    
    A --> E
    B --> E
    C --> E
    D --> F
    
    D --> G
    D --> H
```

## Quality Gates

```mermaid
graph TD
    A[Code Push] --> B{Lint Pass?}
    B -->|❌| B1[Fail: Fix formatting]
    B -->|✅| C{Unit Tests Pass?}
    
    C -->|❌| C1[Fail: Fix tests]  
    C -->|✅| D{Coverage ≥ 30%?}
    
    D -->|❌| D1[Fail: Add tests]
    D -->|✅| E{Regression Pass?}
    
    E -->|❌| E1[Fail: Fix breaking changes]
    E -->|✅| F[SonarCloud Analysis]
    
    F --> G{Build Success?}
    G -->|❌| G1[Fail: Fix build issues]
    G -->|✅| H{Smoke Test Pass?}
    
    H -->|❌| H1[Fail: Fix runtime issues]  
    H -->|✅| I{Tag Release?}
    
    I -->|❌| J[End: Artifacts only]
    I -->|✅| K[Deploy: Release + Registry]
```

---

*Diagrammes générés automatiquement pour pipeline CI/CD Wigor Viewer*