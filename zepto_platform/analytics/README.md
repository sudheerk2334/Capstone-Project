# Analytics

Titanic analytics example with a reusable scikit-learn classification pipeline.

## Run

```bash
python analytics/run_analytics.py
```

The script:

- loads `titanic.csv`
- cleans missing values
- creates simple features
- trains logistic regression
- evaluates accuracy
- saves `full_pipeline.joblib`
- prints business-style summary statistics
