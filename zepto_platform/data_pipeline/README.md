# Data Pipeline

A lightweight ETL pipeline that creates a product catalog in SQLite.

## Flow

`source records -> validation -> transformation -> SQLite load -> quality report`

Run:

```bash
python data_pipeline/pipeline.py
```

The pipeline is idempotent: it recreates the target table before loading the current source batch.
