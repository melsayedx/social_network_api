# Social Network API

A modern, full-stack social network platform with Django REST API backend and React frontend.

## ✨ Features

- **User Authentication** - JWT with Argon2 password hashing
- **Posts** - Create, edit, delete with hashtag support
- **Social** - Like posts, follow users, feed from followed users
- **Comments** - Nested comments on posts
- **Performance** - Redis caching, query optimization, connection pooling
- **Idempotency** - Safe POST retries with idempotency keys
- **HTTPS** - SSL support for local development

## 🛠 Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.13+ | Runtime |
| Django | 6.0 | Web framework |
| DRF | 3.15+ | REST API |
| PostgreSQL | 18 | Database with JSONB |
| Redis | 7 | Caching |
| Uvicorn | Latest | ASGI server |

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI library |
| TypeScript | Type safety |
| Vite | Build tool |
| React Query | Data fetching |
| Zustand | State management |

## 🚀 Quick Start

```bash
# Clone and navigate
cd social-network-api

# Generate SSL certificates (optional, for HTTPS)
cd certs && bash generate-certs.sh && cd ..

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create admin user
docker-compose exec backend python manage.py createsuperuser

# Run tests
docker-compose exec backend pytest -v
```

**Access:**
- Frontend: http://localhost:3000 (or https://localhost:3000)
- API: http://localhost:8000/api/v1/
- API Docs: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

## 📁 Project Structure

```
social-network-api/
├── backend/
│   ├── apps/
│   │   ├── core/          # Base models, utils, caching
│   │   ├── users/         # User model, auth, profiles
│   │   ├── posts/         # Posts with JSONB metadata
│   │   ├── comments/      # Comments on posts
│   │   ├── likes/         # Post likes
│   │   └── follows/       # User follows
│   ├── config/            # Django settings
│   └── requirements/      # Python dependencies
├── frontend/
│   └── src/
│       ├── components/    # React components
│       ├── pages/         # Route pages
│       ├── hooks/         # React Query hooks
│       ├── stores/        # Zustand stores
│       └── lib/           # API client
├── certs/                 # SSL certificates
└── docker-compose.yml
```

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register user |
| POST | `/api/v1/auth/token/` | Get JWT token |
| POST | `/api/v1/auth/token/refresh/` | Refresh token |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/` | List users |
| GET | `/api/v1/users/me/` | Current user |
| PATCH | `/api/v1/users/me/` | Update profile |
| GET | `/api/v1/users/{username}/` | User profile |
| POST | `/api/v1/users/{username}/follow/` | Toggle follow |

### Posts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/posts/` | List posts |
| POST | `/api/v1/posts/` | Create post (idempotent) |
| GET | `/api/v1/posts/{id}/` | Post detail |
| PATCH | `/api/v1/posts/{id}/` | Update post |
| DELETE | `/api/v1/posts/{id}/` | Delete post |
| POST | `/api/v1/posts/{id}/like/` | Toggle like |
| GET | `/api/v1/posts/following/` | Following feed |

### Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/posts/{id}/comments/` | List comments |
| POST | `/api/v1/posts/{id}/comments/` | Add comment (idempotent) |
| DELETE | `/api/v1/comments/{id}/` | Delete comment |

## 🔐 Idempotency

POST requests support idempotency to prevent duplicates:

```bash
curl -X POST https://localhost:8000/api/v1/posts/ \
  -H "Authorization: Bearer <token>" \
  -H "X-Idempotency-Key: unique-key-123" \
  -d '{"content": "Hello World"}'
```

Retrying with the same key returns the cached response.

## 🧪 Testing

```bash
# Run all tests
docker-compose exec backend pytest -v

# With coverage
docker-compose exec backend pytest --cov=apps --cov-report=html

# Specific app
docker-compose exec backend pytest apps/posts/tests/ -v
```

## 📊 Performance Features

- **Query Optimization** - N+1 elimination with `select_related`/`prefetch_related`
- **Connection Pooling** - PostgreSQL and Redis connection pools
- **Caching** - Redis caching for feeds and user data
- **Query Monitoring** - Dev middleware logs slow queries

## 🔧 Environment Variables

See `.env.example` for all available options:

```env
# Database
POSTGRES_DB=social_network
DB_POOL_MIN_SIZE=2
DB_POOL_MAX_SIZE=10

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_MAX_CONNECTIONS=50

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

## 📄 License

MIT
