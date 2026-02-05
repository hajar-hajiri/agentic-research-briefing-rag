.PHONY: install lint test eval api app run

install:
	python -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -e ".[dev]"

lint:
	. .venv/bin/activate && ruff check .

test:
	. .venv/bin/activate && pytest -q

eval:
	. .venv/bin/activate && python -m core.eval

api:
	. .venv/bin/activate && uvicorn api.main:app --reload --port 8000

app:
	. .venv/bin/activate && streamlit run app/streamlit_app.py

run:
	. .venv/bin/activate && python -c "from core.engine import Engine; print(Engine().run('agentic AI trends', mode='offline').answer)"
