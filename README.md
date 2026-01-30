# 🚀 CodeVenture

> A platform for selling digital projects and source code

**CodeVenture** is a powerful platform for developers to monetize their projects and source code. Built with modern asynchronous technologies for high performance and scalability.

---

## 🛠️ Tech Stack

- **FastAPI** — High-performance web framework
- **PostgreSQL** — Relational database
- **Redis** — Caching & sessions
- **Docker** — Containerization
- **Prometheus & Grafana** — Monitoring
- **MinIO** — Object storage
- **Taskiq** — Task queue

---

## ✨ Features

- 🔐 JWT authentication & SSO
- 👥 User management with roles
- 🛍️ Product catalog
- 📦 Secure file storage
- ⚡ Async task processing
- 📊 Monitoring & metrics
- 🛡️ Rate limiting & security

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.13+ (optional)

### Running

```bash
docker compose up --build
```

### Access Services

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

---

## 📁 Project Structure

```
codeventure/
├── app/
│   ├── core/          # Config, DB, utils
│   ├── modules/       # Auth, users, products
│   └── templates/     # HTML
├── migrations/        # DB migrations
├── tests/             # Tests
├── docker-compose.yml
└── pyproject.toml
```

---

## 🔧 Development

```bash
# Install dependencies
uv install
uv install --group dev

# Run tests
pytest

# Format code
ruff format .
ruff check . --fix
```

---

## 📚 API Docs

- **Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📝 License

MIT License - see [LICENSE](LICENSE)

---

Made with ❤️ by [romaperec](https://github.com/romaperec)
