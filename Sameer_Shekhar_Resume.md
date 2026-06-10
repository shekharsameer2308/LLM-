# Sameer Shekhar
**Location:** India | **Email:** shekharsameer2308@gmail.com | **GitHub:** [github.com/shekharsameer2308](https://github.com/shekharsameer2308)  
**LinkedIn:** [linkedin.com/in/yourprofile](#) | **Portfolio:** [yourportfolio.dev](#) | **Phone:** +91-XXXXX-XXXXX

---

## Professional Summary
High-performance **Software Engineer / Data & MLOps Engineer** with extensive experience architecting production-grade distributed systems, real-time data streaming pipelines, AI-driven applications, and machine learning models. Expert in designing decoupled full-stack architectures combining reactive frontends (**React**, **Vite**, **Streamlit**) with asynchronous, type-safe API gateways (**FastAPI**). Deep technical proficiency in data orchestration (**Apache Kafka**, **ETL pipelines**), relational warehousing (**PostgreSQL star schema**, **SQLAlchemy**, **Alembic**), vector search (**Qdrant**), and statistical/predictive modeling (**XGBoost**, **Scikit-Learn**, **ARIMA**, **BERT** models). Proven capability in implementing containerized cloud deployments (**Docker**, **Render**, **Vercel**) and robust system telemetry (**Prometheus**, **Grafana**).

---

## Technical Skills

*   **Languages:** Python (3.10–3.12), SQL (PostgreSQL, SQLite), JavaScript, TypeScript, HTML5, CSS3 (Tailwind CSS v4)
*   **Data Engineering & Streaming:** Apache Kafka (Confluent 7.4), Stream Processing, ETL Pipeline Design, Star Schema Warehousing, Materialized Views, Dynamic Upsert & Late-Arriving Dimension Handling
*   **Machine Learning & NLP:** PyTorch, XGBoost, Scikit-Learn (Isolation Forest, K-Means, Random Forest), Statsmodels (ARIMA), Sentence Transformers, FinBERT, KeyBERT, BERTopic, HDBSCAN, UMAP-Learn, Google Generative AI (Gemini API), LangChain
*   **Databases & Vector Search:** PostgreSQL, Qdrant (Vector DB), SQLite, SQLAlchemy 2.0 ORM, Alembic migrations
*   **Backend & APIs:** FastAPI, Uvicorn, Asynchronous REST APIs, WebSockets (Real-Time Broadcasting), Pydantic v2
*   **Frontend Client:** React 19, Vite, Streamlit, TanStack React Query, Plotly.js, Recharts, Lucide React
*   **DevOps & Telemetry:** Docker, Docker Compose, Nginx, Prometheus, Grafana (Panel Provisioning), Git/GitHub CI/CD, Render, Vercel

---

## Technical Projects

### **NEXUS: Real-Time E-Commerce Analytics Platform**  
*Enterprise-scale, near real-time data engineering and predictive MLOps platform simulating high-volume online marketplace operations.*  
*   **Streaming & Ingestion:** Built an asynchronous data pipeline using **Apache Kafka** distributing events across 5 topics (customer, order, payment, inventory, shipment) at **10–50 events per second**.
*   **ETL & Warehousing:** Engineered a Python ETL consumer utilizing **Pandas** to sanitize, transform, and write data into a **PostgreSQL star schema** warehouse using a 2-second buffer to balance write throughput.
*   **Database Optimizations:** Designed concurrently-refreshed materialized views for analytical metrics (`mv_daily_revenue`, `mv_product_performance`) and composite indexes. Implemented *late-arriving dimension handling* to auto-resolve Kafka order-registration race conditions.
*   **Machine Learning Daemon:** Deployed an asynchronous ML engine performing **ARIMA** revenue forecasting, **K-Means & Random Forest** for RFM customer segmentation and churn prediction, and **Isolation Forest** for transaction fraud detection.
*   **API & Visualization:** Built a **FastAPI backend** using WebSockets to stream live transactions with sub-second latency to a **React (Vite/TypeScript)** glassmorphic dashboard powered by **Recharts**.
*   **Monitoring & Telemetry:** Provisioned **Prometheus & Grafana** configs to track Kafka throughput, API endpoint response times, and database query latencies across containerized environments.
*   **Tech Stack:** Apache Kafka, PostgreSQL 15, FastAPI, React, TypeScript, Scikit-Learn, Statsmodels, Docker, Grafana.

### **Scout: AI-Powered Market Intelligence & Competitor Research Platform**  
*Full-stack, NLP-driven competitive research platform automating industry trends tracking and generative RAG analyses.*  
*   **Ingestion Pipeline:** Created a modular data collector parsing articles from **NewsAPI** and RSS feeds; cleaned HTML boilerplate, ran URL deduplication, and automated industry categorization (Pharma, Logistics, Defense, Agriculture).
*   **NLP Analytics Engine:** Integrated **FinBERT** for contextual sentiment analysis, **KeyBERT** for dynamic keyword extraction, and **BERTopic** (with UMAP & HDBSCAN) for semantic clustering of unstructured industry feeds.
*   **Retrieval-Augmented Generation (RAG):** Embedded normalized text using **Sentence Transformers** and indexed embeddings into a **Qdrant Vector Database** for semantic search.
*   **AI Research Analyst:** Integrated **Google Gemini LLM** via a custom RAG orchestrator to generate structured, context-aware competitive research reports citing original publications.
*   **Frontend Dashboard:** Built an interactive **Streamlit frontend** dashboard connected to a **FastAPI backend** (SQLAlchemy, Alembic migrations), providing market trend explorer, SWOT matrixes, and keyword tag clouds.
*   **Tech Stack:** FastAPI, Streamlit, Qdrant, Google Gemini, Sentence Transformers, FinBERT, BERTopic, KeyBERT, Docker.

### **CoalLab AI: Enterprise Coal Quality Analytics & Blending Optimization**  
*Industrial-grade machine learning and quality validation platform to predict Gross Calorific Value (GCV) and optimize raw material blending.*  
*   **Predictive Regression:** Trained an **XGBoost Regressor** (`XGBRegressor`) in-memory using proximate analysis features (Moisture, Ash, Volatile Matter, Fixed Carbon) to predict coal GCV (kcal/kg) instantly, replacing slow laboratory testing.
*   **Outlier Telemetry:** Developed an anomaly detection pipeline leveraging **Scikit-Learn Isolation Forest** to isolate telemetry drift and sensor failures across six dimensions.
*   **Prescriptive Optimizer:** Designed a linear programming model to solve cost-minimizing mixing ratios of coal sources while satisfying strict contract limits on sulfur and calorific targets.
*   **Decoupled Full-Stack:** Deployed a **React 19/Vite** Single Page Application styled with **Tailwind CSS v4**, visualizing dense distributions via **Plotly.js** and managing server-client state with **TanStack React Query**.
*   **API Gateway:** Created a high-performance, asynchronous **FastAPI server** with **Pydantic v2** validation schemas and **SQLAlchemy 2.0 ORM**.
*   **Tech Stack:** React 19, Vite, Tailwind CSS v4, Plotly.js, FastAPI, XGBoost, Scikit-Learn, SQLite, Render, Vercel.

---

## Experience
**Full-Stack Software / Data Engineer** | *Personal Portfolio & Open Source*  
*Jan 2024 – Present*
*   Architected, coded, and deployed three complex distributed projects showcasing modern data engineering, machine learning pipelines, and responsive frontend systems.
*   Focused on type safety, asynchronous API concurrency, database tuning, and automated microservice containerization.

---

## Education
**Bachelor of Technology (B.Tech) / Science in Computer Science / Engineering**  
*University Name (Placeholder) | Graduation Year (Placeholder)*

---

## Certifications & Extracurriculars
*   **Certifications:** (e.g., AWS Certified Developer, Kafka Developer, Google Cloud Data Engineer - Placeholders)
*   **Open Source:** Maintained multiple repositories with clean architectures, detailed mermaid diagrams, and comprehensive unit tests (`pytest`).
