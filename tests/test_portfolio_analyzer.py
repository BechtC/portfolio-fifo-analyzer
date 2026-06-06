"""
TDD Tests für Portfolio FIFO Analyzer
Testet public behavior, nicht Implementierungsdetails.
"""
import pytest
import tempfile
import os
import sys

# Projekt-Root zum Pfad hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from portfolio_analyzer import analyze_portfolio_from_csv

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def write_csv(content: str, suffix=".csv") -> str:
    """Schreibt CSV-Inhalt in eine temporäre Datei und gibt den Pfad zurück."""
    f = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False,
                                    encoding='utf-8', newline='')
    f.write(content)
    f.close()
    return f.name


PALANTIR_CSV = os.path.join(os.path.dirname(__file__), '..', 'examples', 'palantir_example.csv')
AMD_CSV      = os.path.join(os.path.dirname(__file__), '..', 'examples', 'amd_example.csv')


# ---------------------------------------------------------------------------
# Test 1 — Tracer Bullet: Single-Asset CSV gibt Dict mit genau 1 Eintrag
# ---------------------------------------------------------------------------

def test_single_asset_returns_dict_with_one_entry():
    """analyze_portfolio_from_csv() mit Single-Asset CSV gibt dict mit 1 Eintrag zurück."""
    result = analyze_portfolio_from_csv(PALANTIR_CSV)

    assert isinstance(result, dict), "Ergebnis muss ein dict sein"
    assert len(result) == 1, f"Erwartet 1 Aktie, erhalten: {list(result.keys())}"


# ---------------------------------------------------------------------------
# Test 2 — Multi-Asset Gruppierung: 2 Aktien in einer CSV → 2 Einträge
# ---------------------------------------------------------------------------

MULTI_ASSET_CSV_CONTENT = (
    "datetime;date;time;price;shares;amount;tax;fee;realizedgains;type;"
    "broker;assettype;identifier;wkn;originalcurrency;currency;fxrate;"
    "holding;holdingname;holdingnickname;exchange;avgholdingperiod\n"
    # AMD Kauf
    "2023-01-10T10:00:00.000Z;10.01.2023;10:00:00;70;10;700;0;0;;Buy;"
    "smartbroker_plus;Security;US0079031078;;;EUR;;;AMD;;;\n"
    # Palantir Kauf
    "2023-01-15T10:00:00.000Z;15.01.2023;10:00:00;8;100;800;0;0;;Buy;"
    "smartbroker_plus;Security;US69608A1088;;;EUR;;;Palantir Technologies;;;\n"
)

def test_multi_asset_returns_one_entry_per_stock():
    """CSV mit 2 Aktien (AMD + Palantir) → dict mit genau 2 Einträgen."""
    path = write_csv(MULTI_ASSET_CSV_CONTENT)
    try:
        result = analyze_portfolio_from_csv(path)
        assert isinstance(result, dict)
        assert len(result) == 2, f"Erwartet 2 Aktien, erhalten: {list(result.keys())}"
        assert "AMD" in result
        assert "Palantir Technologies" in result
    finally:
        os.unlink(path)


def test_multi_asset_transactions_are_isolated():
    """Jede Aktie enthält nur ihre eigenen Transaktionen."""
    path = write_csv(MULTI_ASSET_CSV_CONTENT)
    try:
        result = analyze_portfolio_from_csv(path)
        amd       = result["AMD"]
        palantir  = result["Palantir Technologies"]

        # AMD hat 10 Shares gekauft, Palantir 100 — getrennte Portfolios
        assert amd.analysis_results["current_shares"] == pytest.approx(10, abs=0.01)
        assert palantir.analysis_results["current_shares"] == pytest.approx(100, abs=0.01)
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Test 3 — FIFO-Korrektheit: analysis_results enthält alle erwarteten Keys
# ---------------------------------------------------------------------------

EXPECTED_KEYS = {
    "total_invested",
    "total_withdrawn",
    "total_realized_gains",
    "total_taxes",
    "current_shares",
    "net_realized_gains",
    "total_return_pct",
}

def test_analysis_results_contains_required_keys():
    """analysis_results der Palantir-CSV enthält alle erwarteten Keys."""
    result = analyze_portfolio_from_csv(PALANTIR_CSV)
    analyzer = next(iter(result.values()))

    missing = EXPECTED_KEYS - set(analyzer.analysis_results.keys())
    assert not missing, f"Fehlende Keys in analysis_results: {missing}"


def test_palantir_fifo_realized_gains_positive():
    """Palantir-Beispieldaten haben realisierte Gewinne > 0 (Verkäufe waren profitabel)."""
    result = analyze_portfolio_from_csv(PALANTIR_CSV)
    analyzer = next(iter(result.values()))

    assert analyzer.analysis_results["total_realized_gains"] > 0, \
        "Palantir hatte profitable Verkäufe – realisierte Gewinne müssen > 0 sein"


# ---------------------------------------------------------------------------
# Test 4 — Robustheit: Aktie mit nur Verkäufen → kein Crash
# ---------------------------------------------------------------------------

SELL_ONLY_CSV_CONTENT = (
    "datetime;date;time;price;shares;amount;tax;fee;realizedgains;type;"
    "broker;assettype;identifier;wkn;originalcurrency;currency;fxrate;"
    "holding;holdingname;holdingnickname;exchange;avgholdingperiod\n"
    # AMD Kauf (damit CSV nicht leer ist)
    "2023-01-10T10:00:00.000Z;10.01.2023;10:00:00;70;10;700;0;0;;Buy;"
    "smartbroker_plus;Security;US0079031078;;;EUR;;;AMD;;;\n"
    # GhostStock NUR Verkauf, kein Kauf
    "2023-02-01T10:00:00.000Z;01.02.2023;10:00:00;50;5;250;10;0;50;Sell;"
    "smartbroker_plus;Security;XX0000000000;;;EUR;;;GhostStock;;;\n"
)

def test_sell_only_stock_does_not_crash():
    """Aktie mit nur Verkäufen verursacht keinen Crash; dict wird zurückgegeben."""
    path = write_csv(SELL_ONLY_CSV_CONTENT)
    try:
        result = analyze_portfolio_from_csv(path)
        assert isinstance(result, dict), "Funktion muss dict zurückgeben, auch bei Fehlern"
        # AMD muss drin sein (hat Käufe)
        assert "AMD" in result
    finally:
        os.unlink(path)


def test_sell_only_stock_is_handled_gracefully():
    """Aktie mit nur Verkäufen ist entweder im Dict (mit leerem Portfolio) oder ausgelassen —
    aber die Funktion darf keinen unbehandelten Fehler werfen."""
    path = write_csv(SELL_ONLY_CSV_CONTENT)
    try:
        # Kein pytest.raises — wir erwarten KEINEN Exception-Crash
        result = analyze_portfolio_from_csv(path)
        # GhostStock ist entweder drin (mit 0 Shares) oder ausgelassen (failed-Liste)
        # Beides ist akzeptabel — Hauptsache kein Crash
        if "GhostStock" in result:
            ghost = result["GhostStock"]
            assert isinstance(ghost.analysis_results, dict)
        # else: wurde sauber in failed-Liste eingetragen — auch ok
    finally:
        os.unlink(path)
