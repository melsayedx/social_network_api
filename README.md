# Social Network API

**Production-Grade Social Graph Platform**

> **Engineering Analysis:** This project serves as a reference implementation for a production-grade social network backend. It prioritizes data integrity, reliability, and sub-millisecond read latency through the use of aggressive caching strategies, cryptographic-grade authentication, and idempotent write operations.

---

## Engineering Deep Dive: Core Systems

### 1. Idempotency and Distributed Integrity
**The Challenge:** In distributed systems, network partitions or client retries can lead to duplicate resource creation (e.g., posting the same comment twice).
**Implementation:**
*   **Idempotency Keys:** Implemented strict `X-Idempotency-Key` header handling.
*   **Atomic Locking:** Uses Redis atomic operations to lock keys during processing.
*   **Result:** Guarantees exactly-once semantics for all critical POST operations.

### 2. Query Optimization (N+1 Elimination)
**The Challenge:** Fetching social feeds (posts + author + comments + likes) often leads to the N+1 query problem, causing exponential database load.
**Implementation:**
*   **Eager Loading:** Extensive use of `select_related` and `prefetch_related` in Django ORM.
*   **Connection Pooling:** Implemented database connection pooling for both PostgreSQL and Redis to handle concurrent load.
*   **Analysis:** Reduced feed retrieval complexity from O(N) to O(1) database round-trips.

### 3. Security Architecture
**The Challenge:** Storing sensitive user data requires defense-in-depth strategies.
**Implementation:**
*   **Argon2 Hashing:** Password storage uses Argon2, a memory-hard function resistant to GPU/ASIC attacks.
*   **JWT Strategy:** Stateless authentication with short-lived access tokens (15m) and sliding refresh tokens (7d).
*   **SSL/TLS:** Full HTTPS support for local development to mirror production security constraints.

---

## Infrastructure Stack

### Backend
| Technology | Version | Engineering Purpose |
|------------|---------|---------------------|
| Python | 3.13+ | Core Runtime |
| Django | 6.0 | MVT Framework |
| DRF | 3.15+ | REST Interface |
| PostgreSQL | 18 | Primary Relational Store (JSONB support) |
| Redis | 7 | Cache Layer & Message Broker |
| Uvicorn | Latest | ASGI Concurrency Wrappers |

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | Component Library |
| TypeScript | Static Type Assurance |
| Vite | O(1) Bundling |
| React Query | Server State Management |
| Zustand | Client State Management |

---

## Interface Specification

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register user entity |
| POST | `/api/v1/auth/token/` | Issue JWT credentials |
| POST | `/api/v1/auth/token/refresh/` | Rotate access tokens |

### Users Domain
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/` | Paginatable user list |
| GET | `/api/v1/users/me/` | Authenticated context |
| PATCH | `/api/v1/users/me/` | Partial profile update |
| GET | `/api/v1/users/{username}/` | Public profile view |
| POST | `/api/v1/users/{username}/follow/` | Graph connection toggle |

### Core Content (Posts)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/posts/` | Global feed |
| POST | `/api/v1/posts/` | Create node (Idempotent) |
| GET | `/api/v1/posts/{id}/` | Node detail |
| PATCH | `/api/v1/posts/{id}/` | Node update |
| DELETE | `/api/v1/posts/{id}/` | Node removal |
| POST | `/api/v1/posts/{id}/like/` | Interaction toggle |
| GET | `/api/v1/posts/following/` | Personalized edge feed |

### Interactions (Comments)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/posts/{id}/comments/` | Fetch child nodes |
| POST | `/api/v1/posts/{id}/comments/` | Attach child node (Idempotent) |
| DELETE | `/api/v1/comments/{id}/` | Remove child node |

---

## Deployment & Usage

```bash
# 1. Initialization
cd social-network-api

# 2. Security Configuration (Optional)
# Generates local SSL certificates for HTTPS emulation
cd certs && bash generate-certs.sh && cd ..

# 3. Infrastructure Orchestration
docker-compose up -d

# 4. Schema Migration
docker-compose exec backend python manage.py migrate

# 5. Administrative Access
docker-compose exec backend python manage.py createsuperuser

# 6. Verification Suite
docker-compose exec backend pytest -v
```

**Service Endpoints:**
- **Frontend SPA:** http://localhost:3000 (or https://localhost:3000)
- **API Gateway:** http://localhost:8000/api/v1/
- **Swagger Documentation:** http://localhost:8000/api/docs/
- **Admin Portal:** http://localhost:8000/admin/

---

## Codebase Organization

```
social-network-api/
├── backend/
│   ├── apps/
│   │   ├── core/          # Shared utilities, abstract models
│   │   ├── users/         # Identity management & profiles
│   │   ├── posts/         # Content nodes & JSONB metadata
│   │   ├── comments/      # Interaction sub-nodes
│   │   ├── likes/         # Edge interactions
│   │   └── follows/       # Graph edges
│   ├── config/            # Environment & middleware config
│   └── requirements/      # Dependency lockfiles
├── frontend/
│   └── src/
│       ├── components/    # Atomic UI units
│       ├── pages/         # Route definitions
│       ├── hooks/         # Data fetching logic
│       ├── stores/        # Global state atoms
│       └── lib/           # Network clients
├── certs/                 # TLS artifacts
└── docker-compose.yml     # Orchestration manifest
```

---

## Quality Assurance

The project maintains a rigorous testing suite covering unit, integration, and property-based scenarios.

```bash
# Full Regression Suite
docker-compose exec backend pytest -v

# Coverage Analysis
docker-compose exec backend pytest --cov=apps --cov-report=html

# Specific Domain Testing
docker-compose exec backend pytest apps/posts/tests/ -v
```

---

## Environment Configuration

Reference `.env.example` for runtime parameters.

```env
# Persistence Layer
POSTGRES_DB=social_network
DB_POOL_MIN_SIZE=2
DB_POOL_MAX_SIZE=10

# Caching & Message Broker
REDIS_URL=redis://redis:6379/0
REDIS_MAX_CONNECTIONS=50

# Security Policies
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```
