#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Fixtures und Konfiguration für Portfolio FIFO Analyzer Tests
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def test_data_dir():
    """Gibt den Pfad zum Test-Daten-Verzeichnis zurück"""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def temp_csv_file():
    """Erstellt eine temporäre CSV-Datei für Tests"""
    temp_dir = tempfile.mkdtemp()
    temp_file = Path(temp_dir) / "test.csv"

    yield temp_file

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_transactions_df():
    """
    Erstellt einen Sample DataFrame mit Transaktionen
    für Tests, die keinen CSV-Import brauchen
    """
    data = {
        'Date': pd.to_datetime(['2024-01-15', '2024-02-20', '2024-03-10', '2024-04-05']),
        'Type': ['Buy', 'Buy', 'Sell', 'Buy'],
        'Shares': [10, 15, 8, 5],
        'Price': [50.0, 55.0, 60.0, 58.0],
        'Amount': [500.0, 825.0, 480.0, 290.0],
        'Tax': [0, 0, 12.0, 0],
        'Company': ['TestCorp', 'TestCorp', 'TestCorp', 'TestCorp']
    }
    return pd.DataFrame(data)


@pytest.fixture
def simple_csv_content():
    """
    Einfacher CSV-Inhalt für Basistests
    Format: Comma-separated mit englischen Spaltennamen
    """
    return """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-20,Buy,15,55.00,825.00,0.00,TestCorp
2024-03-10,Sell,8,60.00,480.00,12.00,TestCorp
2024-04-05,Buy,5,58.00,290.00,0.00,TestCorp"""


@pytest.fixture
def german_csv_content():
    """
    CSV-Inhalt mit deutschem Format
    Format: Semicolon-separated, deutsche Spaltennamen, Komma als Dezimaltrenner
    """
    return """Datum;Typ;Anzahl;Preis;Betrag;Steuer;Unternehmen
15.01.2024;Kauf;10;50,00;500,00;0,00;TestCorp
20.02.2024;Kauf;15;55,00;825,00;0,00;TestCorp
10.03.2024;Verkauf;8;60,00;480,00;12,00;TestCorp
05.04.2024;Kauf;5;58,00;290,00;0,00;TestCorp"""


@pytest.fixture
def broker_format_csv_content():
    """
    CSV-Inhalt im Broker-Format (ähnlich Smartbroker/Trade Republic)
    Mit zusätzlichen Spalten wie datetime, time, fee, holdingname
    """
    return """datetime;date;time;price;shares;amount;tax;fee;realizedgains;type;holdingname
2024-01-15T10:30:00.000Z;15.01.2024;10:30:00;50,00;10;500,00;0,00;0,99;0;Buy;TestCorp Inc.
2024-02-20T14:15:00.000Z;20.02.2024;14:15:00;55,00;15;825,00;0,00;0,99;0;Buy;TestCorp Inc.
2024-03-10T11:45:00.000Z;10.03.2024;11:45:00;60,00;8;480,00;12,00;0,99;68,00;Sell;TestCorp Inc.
2024-04-05T09:20:00.000Z;05.04.2024;09:20:00;58,00;5;290,00;0,00;0,99;0;Buy;TestCorp Inc."""


@pytest.fixture
def complex_portfolio_csv_content():
    """
    Komplexeres Portfolio mit mehr Transaktionen
    zum Testen der FIFO-Logik
    """
    return """Date,Type,Shares,Price,Amount,Tax,RealizedGains,Company
2023-01-10,Buy,100,10.00,1000.00,0.00,0.00,Palantir Technologies
2023-03-15,Buy,50,12.00,600.00,0.00,0.00,Palantir Technologies
2023-06-20,Buy,75,15.00,1125.00,0.00,0.00,Palantir Technologies
2023-09-01,Sell,80,20.00,1600.00,120.00,780.00,Palantir Technologies
2023-11-10,Buy,60,18.00,1080.00,0.00,0.00,Palantir Technologies
2024-02-14,Sell,100,25.00,2500.00,225.00,1275.00,Palantir Technologies
2024-04-01,Buy,40,22.00,880.00,0.00,0.00,Palantir Technologies"""


@pytest.fixture
def expected_analysis_results_simple():
    """
    Erwartete Analyse-Ergebnisse für simple_csv_content

    Käufe:
    - 10 @ 50 = 500
    - 15 @ 55 = 825
    - 5 @ 58 = 290
    Total invested: 1615

    Verkäufe:
    - 8 @ 60 = 480 (davon 8 aus erstem Kauf @ 50 = 400)
    Realized gain: 480 - 400 = 80 (vor Steuern)
    Tax: 12
    Net realized: 80 - 12 = 68

    Aktueller Bestand: 10 + 15 + 5 - 8 = 22 shares
    """
    return {
        'total_invested': 1615.0,
        'total_withdrawn': 480.0,
        'total_realized_gains': 80.0,
        'total_taxes': 12.0,
        'net_realized_gains': 68.0,
        'remaining_shares': 22,
        'remaining_shares_cost_basis': 1215.0  # 1615 - 400
    }


@pytest.fixture
def mock_analyzer_results():
    """
    Mock analysis_results Dictionary für print_summary_report() Tests
    """
    return {
        'total_invested': 10226.0,
        'total_withdrawn': 23259.0,
        'total_realized_gains': 21116.0,
        'total_taxes': 5087.0,
        'net_realized_gains': 16030.0,
        'total_gains': 70338.0,
        'net_cashflow': 13033.0,
        'total_return_pct': 688.0
    }
