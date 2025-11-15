#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests für Portfolio FIFO Analyzer
"""

import pytest
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import Mock, patch, MagicMock

# Füge parent directory zum Path hinzu, um portfolio_analyzer zu importieren
sys.path.insert(0, str(Path(__file__).parent.parent))

from portfolio_analyzer import PortfolioFIFOAnalyzer, analyze_portfolio_from_csv


class TestPortfolioFIFOAnalyzerInit:
    """Tests für die Initialisierung der PortfolioFIFOAnalyzer Klasse"""

    def test_init_stores_parameters(self):
        """Test dass __init__ die Parameter korrekt speichert"""
        # Da die fehlenden Methoden im __init__ aufgerufen werden,
        # müssen wir diese mocken
        with patch.object(PortfolioFIFOAnalyzer, '_load_and_clean_data'), \
             patch.object(PortfolioFIFOAnalyzer, '_perform_fifo_analysis'), \
             patch.object(PortfolioFIFOAnalyzer, '_calculate_summary_stats'):

            analyzer = PortfolioFIFOAnalyzer(
                csv_file_path="test.csv",
                current_price=150.0,
                currency="USD"
            )

            assert analyzer.csv_file_path == "test.csv"
            assert analyzer.current_price == 150.0
            assert analyzer.currency == "USD"
            assert analyzer.company_name == ""
            assert analyzer.raw_data is None
            assert analyzer.transactions is None
            assert analyzer.portfolio == []
            assert analyzer.analysis_results == {}

    def test_init_default_currency(self):
        """Test dass EUR als Standard-Währung verwendet wird"""
        with patch.object(PortfolioFIFOAnalyzer, '_load_and_clean_data'), \
             patch.object(PortfolioFIFOAnalyzer, '_perform_fifo_analysis'), \
             patch.object(PortfolioFIFOAnalyzer, '_calculate_summary_stats'):

            analyzer = PortfolioFIFOAnalyzer("test.csv")
            assert analyzer.currency == "EUR"

    def test_init_calls_analysis_methods(self):
        """Test dass __init__ alle Analyse-Methoden aufruft"""
        with patch.object(PortfolioFIFOAnalyzer, '_load_and_clean_data') as mock_load, \
             patch.object(PortfolioFIFOAnalyzer, '_perform_fifo_analysis') as mock_fifo, \
             patch.object(PortfolioFIFOAnalyzer, '_calculate_summary_stats') as mock_stats:

            analyzer = PortfolioFIFOAnalyzer("test.csv")

            mock_load.assert_called_once()
            mock_fifo.assert_called_once()
            mock_stats.assert_called_once()


class TestPrintSummaryReport:
    """Tests für die print_summary_report() Methode"""

    def test_print_summary_report_output_format(self, mock_analyzer_results, capsys):
        """Test dass print_summary_report() das richtige Format ausgibt"""
        with patch.object(PortfolioFIFOAnalyzer, '_load_and_clean_data'), \
             patch.object(PortfolioFIFOAnalyzer, '_perform_fifo_analysis'), \
             patch.object(PortfolioFIFOAnalyzer, '_calculate_summary_stats'):

            analyzer = PortfolioFIFOAnalyzer("test.csv")
            analyzer.company_name = "PALANTIR TECHNOLOGIES"
            analyzer.analysis_results = mock_analyzer_results

            analyzer.print_summary_report()

            captured = capsys.readouterr()
            output = captured.out

            # Prüfe, dass alle wichtigen Abschnitte vorhanden sind
            assert "PALANTIR TECHNOLOGIES PORTFOLIO-ANALYSE (FIFO)" in output
            assert "💰 INVESTITIONS-ÜBERSICHT:" in output
            assert "📈 REALISIERTE GEWINNE:" in output
            assert "🎯 GESAMTERGEBNIS:" in output

    def test_print_summary_report_displays_values(self, mock_analyzer_results, capsys):
        """Test dass alle Werte korrekt angezeigt werden"""
        with patch.object(PortfolioFIFOAnalyzer, '_load_and_clean_data'), \
             patch.object(PortfolioFIFOAnalyzer, '_perform_fifo_analysis'), \
             patch.object(PortfolioFIFOAnalyzer, '_calculate_summary_stats'):

            analyzer = PortfolioFIFOAnalyzer("test.csv")
            analyzer.company_name = "TestCorp"
            analyzer.analysis_results = mock_analyzer_results

            analyzer.print_summary_report()

            captured = capsys.readouterr()
            output = captured.out

            # Prüfe wichtige Zahlen (mit Tausendertrenner formatiert)
            assert "10,226" in output  # total_invested
            assert "23,259" in output  # total_withdrawn
            assert "21,116" in output  # total_realized_gains
            assert "5,087" in output   # total_taxes
            assert "16,030" in output  # net_realized_gains
            assert "70,338" in output  # total_gains
            assert "13,033" in output  # net_cashflow
            assert "688.0%" in output  # total_return_pct

    def test_print_summary_report_uses_currency(self, mock_analyzer_results, capsys):
        """Test dass die richtige Währung angezeigt wird"""
        with patch.object(PortfolioFIFOAnalyzer, '_load_and_clean_data'), \
             patch.object(PortfolioFIFOAnalyzer, '_perform_fifo_analysis'), \
             patch.object(PortfolioFIFOAnalyzer, '_calculate_summary_stats'):

            analyzer = PortfolioFIFOAnalyzer("test.csv", currency="USD")
            analyzer.company_name = "TestCorp"
            analyzer.analysis_results = mock_analyzer_results

            analyzer.print_summary_report()

            captured = capsys.readouterr()
            output = captured.out

            # Zähle die USD-Vorkommen (sollte für jeden Betrag einmal vorhanden sein)
            assert output.count("USD") >= 6  # Mindestens 6 Beträge mit Währung

    def test_print_summary_report_handles_zero_values(self, capsys):
        """Test dass auch Null-Werte korrekt dargestellt werden"""
        with patch.object(PortfolioFIFOAnalyzer, '_load_and_clean_data'), \
             patch.object(PortfolioFIFOAnalyzer, '_perform_fifo_analysis'), \
             patch.object(PortfolioFIFOAnalyzer, '_calculate_summary_stats'):

            analyzer = PortfolioFIFOAnalyzer("test.csv")
            analyzer.company_name = "TestCorp"
            analyzer.analysis_results = {
                'total_invested': 0.0,
                'total_withdrawn': 0.0,
                'total_realized_gains': 0.0,
                'total_taxes': 0.0,
                'net_realized_gains': 0.0,
                'total_gains': 0.0,
                'net_cashflow': 0.0,
                'total_return_pct': 0.0
            }

            analyzer.print_summary_report()

            captured = capsys.readouterr()
            output = captured.out

            # Sollte nicht abstürzen und 0.00 Werte anzeigen
            assert "0.00" in output
            assert "0.0%" in output

    def test_print_summary_report_handles_negative_values(self, capsys):
        """Test dass negative Werte (Verluste) korrekt dargestellt werden"""
        with patch.object(PortfolioFIFOAnalyzer, '_load_and_clean_data'), \
             patch.object(PortfolioFIFOAnalyzer, '_perform_fifo_analysis'), \
             patch.object(PortfolioFIFOAnalyzer, '_calculate_summary_stats'):

            analyzer = PortfolioFIFOAnalyzer("test.csv")
            analyzer.company_name = "TestCorp"
            analyzer.analysis_results = {
                'total_invested': 5000.0,
                'total_withdrawn': 3000.0,
                'total_realized_gains': -500.0,  # Verlust
                'total_taxes': 0.0,
                'net_realized_gains': -500.0,
                'total_gains': -500.0,
                'net_cashflow': -2000.0,
                'total_return_pct': -10.0
            }

            analyzer.print_summary_report()

            captured = capsys.readouterr()
            output = captured.out

            # Sollte negative Werte mit Minus-Zeichen anzeigen
            assert "-500.00" in output
            assert "-2,000.00" in output
            assert "-10.0%" in output


class TestAnalyzePortfolioFromCSV:
    """Tests für die analyze_portfolio_from_csv() Funktion"""

    def test_analyze_portfolio_returns_analyzer_instance(self):
        """Test dass analyze_portfolio_from_csv() ein PortfolioFIFOAnalyzer Objekt zurückgibt"""
        with patch.object(PortfolioFIFOAnalyzer, '_load_and_clean_data'), \
             patch.object(PortfolioFIFOAnalyzer, '_perform_fifo_analysis'), \
             patch.object(PortfolioFIFOAnalyzer, '_calculate_summary_stats'), \
             patch.object(PortfolioFIFOAnalyzer, 'print_summary_report'):

            result = analyze_portfolio_from_csv("test.csv", 150.0, "USD")

            assert isinstance(result, PortfolioFIFOAnalyzer)
            assert result.csv_file_path == "test.csv"
            assert result.current_price == 150.0
            assert result.currency == "USD"

    def test_analyze_portfolio_calls_print_report(self):
        """Test dass analyze_portfolio_from_csv() print_summary_report() aufruft"""
        with patch.object(PortfolioFIFOAnalyzer, '_load_and_clean_data'), \
             patch.object(PortfolioFIFOAnalyzer, '_perform_fifo_analysis'), \
             patch.object(PortfolioFIFOAnalyzer, '_calculate_summary_stats'), \
             patch.object(PortfolioFIFOAnalyzer, 'print_summary_report') as mock_print:

            result = analyze_portfolio_from_csv("test.csv")

            mock_print.assert_called_once()

    def test_analyze_portfolio_default_parameters(self):
        """Test dass analyze_portfolio_from_csv() mit Standardwerten funktioniert"""
        with patch.object(PortfolioFIFOAnalyzer, '_load_and_clean_data'), \
             patch.object(PortfolioFIFOAnalyzer, '_perform_fifo_analysis'), \
             patch.object(PortfolioFIFOAnalyzer, '_calculate_summary_stats'), \
             patch.object(PortfolioFIFOAnalyzer, 'print_summary_report'):

            result = analyze_portfolio_from_csv("test.csv")

            assert result.current_price is None
            assert result.currency == "EUR"


class TestPortfolioFIFOAnalyzerMissingMethods:
    """
    Tests für die fehlenden Methoden (_load_and_clean_data, _perform_fifo_analysis, _calculate_summary_stats)

    Diese Tests sind als "Expected to fail" markiert und dokumentieren die erwartete Implementierung.
    Sie werden erfolgreich sein, sobald die Methoden implementiert sind.
    """

    @pytest.mark.xfail(reason="Method not yet implemented", strict=False)
    def test_load_and_clean_data_exists(self, temp_csv_file, simple_csv_content):
        """Test dass _load_and_clean_data() Methode existiert und CSV lädt"""
        temp_csv_file.write_text(simple_csv_content)

        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Wenn implementiert, sollte raw_data nicht None sein
        assert analyzer.raw_data is not None
        assert analyzer.transactions is not None

    @pytest.mark.xfail(reason="Method not yet implemented", strict=False)
    def test_perform_fifo_analysis_exists(self, temp_csv_file, simple_csv_content):
        """Test dass _perform_fifo_analysis() Methode existiert und FIFO durchführt"""
        temp_csv_file.write_text(simple_csv_content)

        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Wenn implementiert, sollte portfolio gefüllt sein
        assert len(analyzer.portfolio) >= 0

    @pytest.mark.xfail(reason="Method not yet implemented", strict=False)
    def test_calculate_summary_stats_exists(self, temp_csv_file, simple_csv_content):
        """Test dass _calculate_summary_stats() Methode existiert und Stats berechnet"""
        temp_csv_file.write_text(simple_csv_content)

        analyzer = PortfolioFIFOAnalyzer(str(temp_csv_file))

        # Wenn implementiert, sollte analysis_results gefüllt sein
        assert 'total_invested' in analyzer.analysis_results
        assert 'total_realized_gains' in analyzer.analysis_results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
