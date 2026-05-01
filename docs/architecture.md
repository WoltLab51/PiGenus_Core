# PiGenus Architecture

PiGenus is a FastAPI-based orchestration core for Raspberry Pi clusters.

## Components
- **API Layer**: FastAPI REST endpoints
- **Database**: SQLite with WAL mode via SQLModel
- **Auth**: JWT tokens for users and workers
- **Job Queue**: Leasing-based job distribution
- **Memory Store**: Key-value persistent memory
- **Scheduler**: APScheduler for maintenance tasks
