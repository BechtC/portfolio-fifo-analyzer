#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-End Tests für Portfolio FIFO Analyzer

Diese Tests testen den kompletten Workflow von CSV-Import bis zum fertigen Report.
Sie sind als xfail markiert, bis die vollständige Implementierung erfolgt ist.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from portfolio_analyzer import PortfolioFIFOAnalyzer, analyze_portfolio_from_csv


class TestEndToEndSimpleScenario:
    """End-to-End Tests für einfache Szenarien"""

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_simple_english_csv_complete_workflow(self, test_data_dir):
        """
        Test kompletten Workflow mit englischer CSV

        Erwartet:
        - CSV wird geladen und geparst
        - FIFO-Analyse wird durchgeführt
        - Statistiken werden berechnet
        - Report kann ausgegeben werden
        """
        csv_file = test_data_dir / "simple_english.csv"
        analyzer = PortfolioFIFOAnalyzer(str(csv_file), current_price=70.0)

        # Überprüfe dass alle Schritte erfolgreich waren
        assert analyzer.transactions is not None
        assert len(analyzer.transactions) == 4
        assert analyzer.analysis_results is not None
        assert 'total_invested' in analyzer.analysis_results

        # Sollte ohne Fehler den Report ausgeben können
        analyzer.print_summary_report()

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_simple_german_csv_complete_workflow(self, test_data_dir):
        """Test kompletten Workflow mit deutscher CSV"""
        csv_file = test_data_dir / "simple_german.csv"
        analyzer = PortfolioFIFOAnalyzer(str(csv_file), current_price=70.0, currency="EUR")

        assert analyzer.transactions is not None
        assert analyzer.currency == "EUR"
        assert analyzer.company_name == "TestCorp"

        analyzer.print_summary_report()

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_broker_format_csv_complete_workflow(self, test_data_dir):
        """Test kompletten Workflow mit Broker-Format CSV"""
        csv_file = test_data_dir / "broker_format.csv"
        analyzer = PortfolioFIFOAnalyzer(str(csv_file), current_price=70.0)

        assert analyzer.transactions is not None
        # Broker Format hat auch 4 Transaktionen
        assert len(analyzer.transactions) == 4

        analyzer.print_summary_report()


class TestEndToEndComplexScenarios:
    """End-to-End Tests für komplexere Szenarien"""

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_palantir_example_complete_workflow(self, test_data_dir):
        """
        Test kompletten Workflow mit Palantir-Beispiel

        Dies ist ein realistisches Szenario mit mehreren Käufen und Verkäufen
        """
        csv_file = test_data_dir / "palantir_example.csv"
        analyzer = PortfolioFIFOAnalyzer(str(csv_file), current_price=157.0, currency="EUR")

        # 7 Transaktionen im Palantir-Beispiel
        assert len(analyzer.transactions) == 7
        assert analyzer.company_name == "Palantir Technologies"

        # Überprüfe dass alle Statistiken vorhanden sind
        assert 'total_invested' in analyzer.analysis_results
        assert 'total_realized_gains' in analyzer.analysis_results
        assert 'unrealized_gains' in analyzer.analysis_results

        analyzer.print_summary_report()

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_complete_liquidation_workflow(self, test_data_dir):
        """Test Workflow bei vollständiger Liquidation"""
        csv_file = test_data_dir / "complete_liquidation.csv"
        analyzer = PortfolioFIFOAnalyzer(str(csv_file))

        # Bei vollständiger Liquidation sollten keine Aktien mehr vorhanden sein
        assert analyzer.analysis_results['remaining_shares'] == 0

        # Unrealized gains sollten 0 sein
        if 'unrealized_gains' in analyzer.analysis_results:
            assert analyzer.analysis_results['unrealized_gains'] == 0.00

        analyzer.print_summary_report()

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_portfolio_with_losses_workflow(self, test_data_dir):
        """Test Workflow mit Portfolio das Verluste hat"""
        csv_file = test_data_dir / "with_losses.csv"
        analyzer = PortfolioFIFOAnalyzer(str(csv_file), current_price=90.0)

        # Erste Verkauf macht Verlust, zweiter Gewinn
        # Sollte beides korrekt berechnen
        assert 'total_realized_gains' in analyzer.analysis_results

        analyzer.print_summary_report()


class TestAnalyzePortfolioFromCSVFunction:
    """End-to-End Tests für die analyze_portfolio_from_csv() Funktion"""

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_analyze_function_returns_complete_analyzer(self, test_data_dir, capsys):
        """
        Test dass analyze_portfolio_from_csv() einen vollständigen Analyzer zurückgibt
        und den Report ausgibt
        """
        csv_file = test_data_dir / "simple_english.csv"
        analyzer = analyze_portfolio_from_csv(str(csv_file), current_price=70.0, currency="USD")

        # Sollte ein vollständiges Analyzer-Objekt zurückgeben
        assert isinstance(analyzer, PortfolioFIFOAnalyzer)
        assert analyzer.transactions is not None
        assert analyzer.analysis_results is not None

        # Sollte den Report ausgegeben haben
        captured = capsys.readouterr()
        assert "PORTFOLIO-ANALYSE" in captured.out

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_analyze_function_with_all_parameters(self, test_data_dir):
        """Test analyze_portfolio_from_csv() mit allen Parametern"""
        csv_file = test_data_dir / "palantir_example.csv"

        analyzer = analyze_portfolio_from_csv(
            csv_file_path=str(csv_file),
            current_price=157.0,
            currency="EUR"
        )

        assert analyzer.csv_file_path == str(csv_file)
        assert analyzer.current_price == 157.0
        assert analyzer.currency == "EUR"

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_analyze_function_minimal_parameters(self, test_data_dir):
        """Test analyze_portfolio_from_csv() mit minimalen Parametern"""
        csv_file = test_data_dir / "simple_english.csv"

        analyzer = analyze_portfolio_from_csv(csv_file_path=str(csv_file))

        # Sollte Standardwerte verwenden
        assert analyzer.current_price is None
        assert analyzer.currency == "EUR"


class TestErrorHandlingEndToEnd:
    """End-to-End Tests für Fehlerbehandlung"""

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_file_not_found_error(self):
        """Test dass FileNotFoundError bei nicht existierender Datei geworfen wird"""
        with pytest.raises(FileNotFoundError):
            analyzer = PortfolioFIFOAnalyzer("/non/existent/file.csv")

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_invalid_csv_format_error(self, temp_csv_file):
        """Test dass ein Fehler bei ungültigem CSV-Format geworfen wird"""
        temp_csv_file.write_text("This is not a valid CSV\nJust some text")

        with pytest.raises(Exception):
            analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_sell_before_buy_error(self, temp_csv_file):
        """Test dass ein Fehler bei Verkauf vor Kauf geworfen wird"""
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Sell,10,60.00,600.00,0.00,TestCorp
2024-02-15,Buy,20,50.00,1000.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)

        with pytest.raises(Exception):
            analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_overselling_error(self, temp_csv_file):
        """Test dass ein Fehler bei Überverkauf geworfen wird"""
        csv_content = """Date,Type,Shares,Price,Amount,Tax,Company
2024-01-15,Buy,10,50.00,500.00,0.00,TestCorp
2024-02-15,Sell,15,60.00,900.00,0.00,TestCorp"""

        temp_csv_file.write_text(csv_content)

        with pytest.raises(Exception):
            analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))


class TestDataIntegrity:
    """Tests für Datenintegrität über den gesamten Workflow"""

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_share_count_conservation(self, test_data_dir):
        """
        Test dass die Aktienanzahl korrekt verwaltet wird

        Summe aller Käufe - Summe aller Verkäufe = Verbleibende Aktien
        """
        csv_file = test_data_dir / "simple_english.csv"
        analyzer = PortfolioFIFOAnalyzer(str(csv_file))

        # Berechne aus Transaktionen
        buy_transactions = analyzer.transactions[analyzer.transactions['Type'] == 'Buy']
        sell_transactions = analyzer.transactions[analyzer.transactions['Type'] == 'Sell']

        total_bought = buy_transactions['Shares'].sum()
        total_sold = sell_transactions['Shares'].sum()
        expected_remaining = total_bought - total_sold

        # Vergleiche mit berechnetem Ergebnis
        actual_remaining = analyzer.analysis_results['remaining_shares']
        assert actual_remaining == expected_remaining

    @pytest.mark.xfail(reason="Full implementation not yet complete", strict=False)
    def test_money_flow_consistency(self, test_data_dir):
        """
        Test dass der Geldfluss konsistent ist

        (Withdrawn - Invested) + Current_Value = Total_Gains
        """
        csv_file = test_data_dir / "simple_english.csv"
        analyzer = PortfolioFIFOAnalyzer(str(csv_file), current_price=70.0)

        invested = analyzer.analysis_results['total_invested']
        withdrawn = analyzer.analysis_results['total_withdrawn']
        remaining_shares = analyzer.analysis_results['remaining_shares']
        current_value = remaining_shares * 70.0

        # Net Flow + Current Value sollte Total Gains + Invested sein
        net_flow = withdrawn - invested
        calculated_total_gains = net_flow + current_value

        actual_total_gains = analyzer.analysis_results['total_gains']

        assert calculated_total_gains == pytest.approx(actual_total_gains, rel=1e-2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
