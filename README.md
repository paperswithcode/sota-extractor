# Automatic SOTA (state-of-the-art) extraction

Requires Python 3.6+.

```bash
pip install -r requirements.txt
```

## Getting the data

The data is kept in the [data](data/) directory. 

The scrapers and the JSON format spec are in [scrapers](scrapers/README.md) directory. 

## Running

To evaluate the predictions for all tasks:

```bash
python -m extractor.eval_all
```

The most current report can be seen here: [eval_all_report.csv](eval_all_report.csv).

