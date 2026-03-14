.PHONY: dev test seed build clean dev-frontend dev-backend

dev: dev-backend

dev-backend:
	source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 3007

dev-frontend:
	cd frontend && npm start

test:
	source .venv/bin/activate && python -m pytest tests/ -v --tb=short

seed:
	source .venv/bin/activate && python -c "\
from app.database import engine, SessionLocal; \
from app.models.base import Base; \
from app.models.patient import Patient; \
Base.metadata.create_all(bind=engine); \
db = SessionLocal(); \
p1 = Patient(name='Jane Doe', email='jane@example.com', consent_verified=True, phase='PENDING'); \
p2 = Patient(name='John Smith', email='john@example.com', consent_verified=True, phase='ACTIVE', goal='Improve shoulder mobility'); \
p3 = Patient(name='Alice Johnson', email='alice@example.com', consent_verified=False, phase='PENDING'); \
db.add_all([p1, p2, p3]); \
db.commit(); \
print('Seeded 3 patients successfully'); \
db.close()"

build:
	pip install -r requirements.txt
	cd frontend && npm install && npm run build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	rm -f medbridge.db; \
	rm -rf frontend/build
