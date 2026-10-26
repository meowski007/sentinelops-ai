# SentinelOps AI - Testing Strategy & Verification Guide

This document details the test coverage, execution commands, and verification criteria for SentinelOps AI.

---

## 1. Test Architecture Overview

| Layer | Framework | Scope / Coverage |
|---|---|---|
| **Backend Unit & Integration** | Pytest 9.1 | Health, incidents, anomaly monitoring, BM25 & semantic RAG, investigation tools, evidence citations, remediation approval state machine, security inputs |
| **Linting & Code Style** | Ruff 0.17 | Python formatting, import sorting, syntax checks |
| **RAG Retrieval Quality** | Custom Benchmark | MRR, Recall@K, Precision@K on 10 IT operations queries |
| **Frontend Unit & Component** | Vitest 5.0 + RTL | Navbar, Sidebar, badge counters, status indicator rendering |
| **Frontend Build & Types** | Vite + TypeScript 6.0 | Production bundle compilation, type verification |

---

## 2. Running All Tests Locally

### Backend Tests (28 tests)
```bash
cd backend
pytest
```
*Expected: 28 passed in ~1s.*

### Ruff Linting
```bash
cd backend
ruff check .
```
*Expected: All checks passed!*

### RAG Retrieval Benchmark
```bash
cd backend
python -m app.scripts.run_eval
```
*Expected: Output table showing MRR 1.0000, Recall@3 1.0000.*

### Frontend Tests
```bash
cd frontend
npm test
```
*Expected: 2 passed in ~3s.*

### Frontend Production Build
```bash
cd frontend
npm run build
```
*Expected: Built bundle in `frontend/dist` without errors.*
