# SignalDesk AI — Phase 2 UI + Ticket History Update

This update adds:

- visual severity, confidence, and escalation states
- dashboard-level ticket and escalation counts
- interactive recent-incident history
- click-to-reopen analyzed tickets
- stronger workflow cards
- evidence match bars and best-match emphasis
- example incident chips
- responsive product-style layout

## Files changed

- `frontend/src/App.tsx`
- `frontend/src/styles.css`
- `backend/app/main.py`
- `backend/tests/test_api.py`

## Important backend note

The CORS configuration in this development build uses `allow_origins=["*"]` with credentials disabled. This is intentional for local development only. Before deployment, replace it with the exact production frontend origin.

## Run after copying the files

Backend terminal:

```bash
cd backend
source .venv/bin/activate
python3 -m pytest -q
uvicorn app.main:app --reload
```

Frontend terminal:

```bash
cd frontend
npm run dev
```

Then refresh the browser.
