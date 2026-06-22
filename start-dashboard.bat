@echo off
title FIFO Portfolio Analyzer
cd /d "%~dp0"

echo === FIFO Portfolio Analyzer ===
echo Analysiere neueste CSV aus csvs/ ...

python -c "from portfolio_analyzer import analyze_portfolio_from_csv, generate_multi_asset_report, find_latest_csv; csv_file = find_latest_csv(); print(f'Neueste CSV-Datei: {csv_file}'); analyzers = analyze_portfolio_from_csv(csv_file, currency='EUR'); generate_multi_asset_report(analyzers)"

echo.
echo Analyse abgeschlossen! Reports in output/ Ordner.
timeout /t 5
