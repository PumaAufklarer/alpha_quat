"""
Backtest result visualization plotting.
"""

from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from .engine import BacktestResult


class BacktestPlotter:
    """
    Plotter for backtest results.

    Generates various charts from backtest results, including:
    - Equity curve
    - Drawdown curve
    - Price with buy/sell markers (single asset)
    - Trade overview (multi-asset)
    - Composite report
    """

    def __init__(self, result: BacktestResult, price_data: pd.DataFrame | None = None):
        """
        Initialize BacktestPlotter.

        Args:
            result: BacktestResult from backtest run
            price_data: Optional DataFrame containing price data for trade plotting
        """
        self.result = result
        self.price_data = price_data

        # Set default style
        plt.style.use("seaborn-v0_8-darkgrid")
        plt.rcParams["figure.figsize"] = (12, 8)
        plt.rcParams["font.size"] = 10

    def _plot_equity_to_ax(self, ax: plt.Axes) -> None:
        """Plot equity curve to given axes."""
        df = pd.DataFrame(self.result.portfolio.equity_history)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime")

        initial_equity = self.result.portfolio.initial_cash
        final_equity = df["equity"].iloc[-1]
        total_return = (final_equity / initial_equity) - 1

        ax.plot(df["datetime"], df["equity"], linewidth=2, color="#2e86ab", label="Equity")
        ax.axhline(y=initial_equity, color="#e74c3c", linestyle="--", alpha=0.7, label="Initial")
        ax.scatter(df["datetime"].iloc[-1], final_equity, color="#2e86ab", s=80, zorder=5)
        ax.text(
            df["datetime"].iloc[-1],
            final_equity,
            f"  ¥{final_equity:,.0f}\n  {total_return:+.1%}",
            va="center",
            fontweight="bold",
        )

        ax.set_title("Equity Curve", fontsize=12, fontweight="bold", pad=10)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper left")

    def _plot_drawdown_to_ax(self, ax: plt.Axes) -> None:
        """Plot drawdown to given axes."""
        df = pd.DataFrame(self.result.portfolio.equity_history)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime")

        df["return"] = df["equity"].pct_change().fillna(0)
        df["cumulative"] = (1 + df["return"]).cumprod()
        df["running_max"] = df["cumulative"].cummax()
        df["drawdown"] = (df["cumulative"] - df["running_max"]) / df["running_max"]

        max_dd_idx = df["drawdown"].idxmin()
        max_dd_date = df["datetime"].iloc[max_dd_idx]
        max_dd = df["drawdown"].iloc[max_dd_idx]

        ax.fill_between(df["datetime"], df["drawdown"], 0, color="#e74c3c", alpha=0.3)
        ax.plot(df["datetime"], df["drawdown"], color="#e74c3c", linewidth=1.5)
        ax.scatter(max_dd_date, max_dd, color="#e74c3c", s=80, zorder=5)
        ax.text(
            max_dd_date,
            max_dd,
            f"  Max DD: {max_dd:.1%}",
            va="top",
            fontweight="bold",
            color="#c0392b",
        )

        ax.set_title("Drawdown", fontsize=12, fontweight="bold", pad=10)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
        ax.grid(True, alpha=0.3)

    def _plot_trades_to_ax(self, ax: plt.Axes) -> None:
        """Plot price with trades to given axes (single asset mode)."""
        if self.price_data is None or self.price_data.empty:
            ax.text(
                0.5,
                0.5,
                "No price data available",
                ha="center",
                va="center",
                fontsize=12,
                transform=ax.transAxes,
            )
            ax.set_title("Price with Trades", fontsize=12, fontweight="bold", pad=10)
            return

        df = self.price_data.copy()
        if "trade_date" in df.columns:
            df["datetime"] = pd.to_datetime(df["trade_date"])
        elif "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])
        else:
            raise ValueError("Price data must have 'trade_date' or 'datetime' column")

        df = df.sort_values("datetime")

        ts_code = df["ts_code"].iloc[0] if "ts_code" in df.columns else "Unknown"

        price_min = df["close"].min() if "close" in df.columns else df["price"].min()
        price_max = df["close"].max() if "close" in df.columns else df["price"].max()
        price_range = price_max - price_min
        label_offset = price_range * 0.03

        if "close" in df.columns:
            ax.plot(df["datetime"], df["close"], linewidth=1.5, color="#34495e", label="Close")
        elif "price" in df.columns:
            ax.plot(df["datetime"], df["price"], linewidth=1.5, color="#34495e", label="Price")

        trades = self.result.trades
        if trades:
            buys = [t for t in trades if t.quantity > 0]
            sells = [t for t in trades if t.quantity < 0]

            if buys:
                buy_dates = [t.traded_at for t in buys]
                buy_prices = [t.price for t in buys]
                buy_qtys = [t.quantity for t in buys]
                ax.scatter(
                    buy_dates,
                    buy_prices,
                    marker="^",
                    color="#e74c3c",
                    s=100,
                    zorder=5,
                    label="Buy",
                    edgecolor="#c0392b",
                )
                for dt, price, qty in zip(buy_dates, buy_prices, buy_qtys):
                    ax.text(
                        dt,
                        price + label_offset,
                        f"+{qty}\n¥{price:.2f}",
                        va="bottom",
                        ha="center",
                        fontsize=6,
                        fontweight="bold",
                        color="#c0392b",
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#c0392b", alpha=0.8),
                    )

            if sells:
                sell_dates = [t.traded_at for t in sells]
                sell_prices = [t.price for t in sells]
                sell_qtys = [abs(t.quantity) for t in sells]
                ax.scatter(
                    sell_dates,
                    sell_prices,
                    marker="v",
                    color="#27ae60",
                    s=100,
                    zorder=5,
                    label="Sell",
                    edgecolor="#1e8449",
                )
                for dt, price, qty in zip(sell_dates, sell_prices, sell_qtys):
                    ax.text(
                        dt,
                        price - label_offset,
                        f"-{qty}\n¥{price:.2f}",
                        va="top",
                        ha="center",
                        fontsize=6,
                        fontweight="bold",
                        color="#1e8449",
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#1e8449", alpha=0.8),
                    )

            ax.legend(loc="upper left")

        ax.set_title(f"Trades for {ts_code}", fontsize=12, fontweight="bold", pad=10)
        ax.grid(True, alpha=0.3)

    def _plot_trade_overview_to_ax(self, ax: plt.Axes) -> None:
        """Plot trade overview to given axes (multi-asset mode)."""
        trades = self.result.trades
        if not trades:
            ax.text(
                0.5,
                0.5,
                "No trades executed",
                ha="center",
                va="center",
                fontsize=12,
                transform=ax.transAxes,
            )
            ax.set_title("Trade Overview", fontsize=12, fontweight="bold", pad=10)
            return

        # Group trades by asset
        trades_by_asset = defaultdict(list)
        for trade in trades:
            trades_by_asset[trade.ts_code].append(trade)

        # Sort assets by number of trades (descending)
        sorted_assets = sorted(
            trades_by_asset.keys(), key=lambda x: len(trades_by_asset[x]), reverse=True
        )

        # Prepare data for bar chart
        assets = []
        buy_counts = []
        sell_counts = []

        for ts_code in sorted_assets[:10]:  # Show top 10 assets
            asset_trades = trades_by_asset[ts_code]
            buys = sum(1 for t in asset_trades if t.quantity > 0)
            sells = sum(1 for t in asset_trades if t.quantity < 0)
            assets.append(ts_code)
            buy_counts.append(buys)
            sell_counts.append(sells)

        # Plot bar chart
        x = range(len(assets))
        width = 0.35

        ax.bar(
            [xi - width / 2 for xi in x], buy_counts, width, label="Buy", color="#e74c3c", alpha=0.7
        )
        ax.bar(
            [xi + width / 2 for xi in x],
            sell_counts,
            width,
            label="Sell",
            color="#27ae60",
            alpha=0.7,
        )

        ax.set_xlabel("Asset", fontsize=10)
        ax.set_ylabel("Number of Trades", fontsize=10)
        ax.set_title("Trade Overview by Asset", fontsize=12, fontweight="bold", pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(assets, rotation=45, ha="right")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")

    def _plot_metrics_card_to_ax(self, ax: plt.Axes) -> None:
        """Plot metrics card to given axes."""
        ax.axis("off")

        equity_df = pd.DataFrame(self.result.portfolio.equity_history)
        equity_df["datetime"] = pd.to_datetime(equity_df["datetime"])
        equity_df = equity_df.sort_values("datetime")

        initial_equity = self.result.portfolio.initial_cash
        final_equity = equity_df["equity"].iloc[-1]
        total_return = (final_equity / initial_equity) - 1

        metrics = self.result.metrics
        trades = self.result.trades

        win_rate = 0.0
        if len(trades) >= 2:
            profits = []
            position = 0
            entry_price = 0.0

            for trade in trades:
                if trade.quantity > 0:
                    if position == 0:
                        entry_price = trade.price
                    position += trade.quantity
                else:
                    if position > 0:
                        profits.append((trade.price - entry_price) / entry_price)
                        position -= abs(trade.quantity)
                        if position > 0:
                            entry_price = trade.price

            if profits:
                winning_trades = sum(1 for p in profits if p > 0)
                win_rate = winning_trades / len(profits)

        metrics_text = f"""
  BACKTEST METRICS

  Initial Equity  ¥{initial_equity:>14,.0f}
  Final Equity    ¥{final_equity:>14,.0f}

  ─────────────────────────────────────

  Total Return    {total_return:>14.1%}
  Annual Return   {metrics.annual_return:>14.1%}
  Volatility      {metrics.volatility:>14.1%}
  Sharpe Ratio    {metrics.sharpe_ratio:>14.2f}
  Max Drawdown    {metrics.max_drawdown:>14.1%}

  ─────────────────────────────────────

  Total Trades    {len(trades):>14d}
  Win Rate        {win_rate:>14.1%}
        """

        ax.text(
            0.05,
            0.95,
            metrics_text,
            fontfamily="monospace",
            fontsize=11,
            va="top",
            ha="left",
            transform=ax.transAxes,
            bbox=dict(boxstyle="round", facecolor="#f8f9fa", edgecolor="#dee2e6"),
        )

    def plot_equity_curve(self, save_path: str | Path | None = None, dpi: int = 150) -> Figure:
        """
        Plot equity curve over time.

        Args:
            save_path: Path to save the figure (optional)
            dpi: DPI for saved figure

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        self._plot_equity_to_ax(ax)
        ax.set_title("Equity Curve", fontsize=14, fontweight="bold", pad=20)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Equity (¥)", fontsize=12)
        fig.autofmt_xdate()
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=dpi, bbox_inches="tight")

        return fig

    def plot_drawdown(self, save_path: str | Path | None = None, dpi: int = 150) -> Figure:
        """
        Plot drawdown over time.

        Args:
            save_path: Path to save the figure (optional)
            dpi: DPI for saved figure

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        self._plot_drawdown_to_ax(ax)
        ax.set_title("Drawdown", fontsize=14, fontweight="bold", pad=20)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Drawdown", fontsize=12)
        fig.autofmt_xdate()
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=dpi, bbox_inches="tight")

        return fig

    def plot_trades_on_price(self, save_path: str | Path | None = None, dpi: int = 150) -> Figure:
        """
        Plot price chart with buy/sell markers (single asset only).

        Args:
            save_path: Path to save the figure (optional)
            dpi: DPI for saved figure

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        self._plot_trades_to_ax(ax)

        # Adjust title font size for standalone plot
        for text in ax.texts:
            if text.get_text() == "Price with Trades" or text.get_text().startswith("Trades for"):
                text.set_fontsize(14)
                break
        else:
            ax.set_title(ax.get_title(), fontsize=14)

        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Price (¥)", fontsize=12)
        fig.autofmt_xdate()
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=dpi, bbox_inches="tight")

        return fig

    def plot_trade_overview(self, save_path: str | Path | None = None, dpi: int = 150) -> Figure:
        """
        Plot trade overview by asset (multi-asset mode).

        Args:
            save_path: Path to save the figure (optional)
            dpi: DPI for saved figure

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        self._plot_trade_overview_to_ax(ax)
        ax.set_title("Trade Overview", fontsize=14, fontweight="bold", pad=20)
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=dpi, bbox_inches="tight")

        return fig

    def plot_multi_asset_trades(
        self, save_path: str | Path | None = None, dpi: int = 150, max_assets: int = 6
    ) -> Figure:
        """
        Plot price charts with buy/sell markers for multiple assets.

        Args:
            save_path: Path to save the figure (optional)
            dpi: DPI for saved figure
            max_assets: Maximum number of assets to display

        Returns:
            Matplotlib Figure object
        """
        if self.price_data is None or self.price_data.empty:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(
                0.5,
                0.5,
                "No price data available",
                ha="center",
                va="center",
                fontsize=12,
                transform=ax.transAxes,
            )
            ax.set_title("Multi-Asset Trades", fontsize=14, fontweight="bold", pad=20)
            plt.tight_layout()
            if save_path:
                fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
            return fig

        # Get unique assets
        if "ts_code" not in self.price_data.columns:
            # If no ts_code column, treat as single asset
            return self.plot_trades_on_price(save_path, dpi)

        unique_assets = self.price_data["ts_code"].unique()

        # Filter assets that have trades
        assets_with_trades = set()
        for trade in self.result.trades:
            assets_with_trades.add(trade.ts_code)

        # Prioritize assets with trades
        assets_to_plot = [a for a in unique_assets if a in assets_with_trades]
        # Add other assets if we have space
        if len(assets_to_plot) < max_assets:
            for a in unique_assets:
                if a not in assets_to_plot and len(assets_to_plot) < max_assets:
                    assets_to_plot.append(a)

        num_assets = len(assets_to_plot)
        if num_assets == 0:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(
                0.5,
                0.5,
                "No assets with trades found",
                ha="center",
                va="center",
                fontsize=12,
                transform=ax.transAxes,
            )
            ax.set_title("Multi-Asset Trades", fontsize=14, fontweight="bold", pad=20)
            plt.tight_layout()
            if save_path:
                fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
            return fig

        # Calculate grid layout
        cols = min(2, num_assets)
        rows = (num_assets + cols - 1) // cols

        fig_height = 4 * rows
        fig = plt.figure(figsize=(16, fig_height))
        gs = fig.add_gridspec(rows, cols, hspace=0.35, wspace=0.25)

        # Prepare datetime column
        df = self.price_data.copy()
        if "trade_date" in df.columns:
            df["datetime"] = pd.to_datetime(df["trade_date"])
        elif "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])
        else:
            df["datetime"] = pd.to_datetime(df.index)

        df = df.sort_values("datetime")

        for i, ts_code in enumerate(assets_to_plot):
            row = i // cols
            col = i % cols
            ax = fig.add_subplot(gs[row, col])

            # Filter data for this asset
            asset_df = df[df["ts_code"] == ts_code]

            if asset_df.empty:
                ax.text(
                    0.5,
                    0.5,
                    f"No data for {ts_code}",
                    ha="center",
                    va="center",
                    fontsize=10,
                    transform=ax.transAxes,
                )
                ax.set_title(ts_code, fontsize=11, fontweight="bold")
                continue

            # Plot price
            if "close" in asset_df.columns:
                ax.plot(
                    asset_df["datetime"],
                    asset_df["close"],
                    linewidth=1.2,
                    color="#34495e",
                    label="Close",
                )
            elif "price" in asset_df.columns:
                ax.plot(
                    asset_df["datetime"],
                    asset_df["price"],
                    linewidth=1.2,
                    color="#34495e",
                    label="Price",
                )

            # Get trades for this asset
            asset_trades = [t for t in self.result.trades if t.ts_code == ts_code]

            if asset_trades:
                # Calculate label offset
                if "close" in asset_df.columns:
                    price_min = asset_df["close"].min()
                    price_max = asset_df["close"].max()
                elif "price" in asset_df.columns:
                    price_min = asset_df["price"].min()
                    price_max = asset_df["price"].max()
                else:
                    price_min = min(t.price for t in asset_trades)
                    price_max = max(t.price for t in asset_trades)

                price_range = price_max - price_min if price_max > price_min else 1
                label_offset = price_range * 0.05

                buys = [t for t in asset_trades if t.quantity > 0]
                sells = [t for t in asset_trades if t.quantity < 0]

                if buys:
                    buy_dates = [t.traded_at for t in buys]
                    buy_prices = [t.price for t in buys]
                    buy_qtys = [t.quantity for t in buys]
                    ax.scatter(
                        buy_dates,
                        buy_prices,
                        marker="^",
                        color="#e74c3c",
                        s=60,
                        zorder=5,
                        label="Buy",
                        edgecolor="#c0392b",
                    )
                    # Only show labels if not too many
                    if len(buys) <= 5:
                        for dt, price, qty in zip(buy_dates, buy_prices, buy_qtys):
                            ax.text(
                                dt,
                                price + label_offset,
                                f"+{qty}",
                                va="bottom",
                                ha="center",
                                fontsize=7,
                                fontweight="bold",
                                color="#c0392b",
                            )

                if sells:
                    sell_dates = [t.traded_at for t in sells]
                    sell_prices = [t.price for t in sells]
                    sell_qtys = [abs(t.quantity) for t in sells]
                    ax.scatter(
                        sell_dates,
                        sell_prices,
                        marker="v",
                        color="#27ae60",
                        s=60,
                        zorder=5,
                        label="Sell",
                        edgecolor="#1e8449",
                    )
                    # Only show labels if not too many
                    if len(sells) <= 5:
                        for dt, price, qty in zip(sell_dates, sell_prices, sell_qtys):
                            ax.text(
                                dt,
                                price - label_offset,
                                f"-{qty}",
                                va="top",
                                ha="center",
                                fontsize=7,
                                fontweight="bold",
                                color="#1e8449",
                            )

                if buys or sells:
                    ax.legend(loc="upper left", fontsize=8)

            ax.set_title(ts_code, fontsize=11, fontweight="bold", pad=8)
            ax.grid(True, alpha=0.3)
            # Rotate dates
            for label in ax.get_xticklabels():
                label.set_rotation(30)
                label.set_ha("right")

        fig.suptitle(
            "Multi-Asset Price Charts with Trades", fontsize=14, fontweight="bold", y=0.995
        )
        plt.subplots_adjust(top=0.93)

        if save_path:
            fig.savefig(save_path, dpi=dpi, bbox_inches="tight")

        return fig

    def plot_composite_report(self, save_path: str | Path | None = None, dpi: int = 150) -> Figure:
        """
        Plot composite report with all charts and metrics.

        Args:
            save_path: Path to save the figure (optional)
            dpi: DPI for saved figure

        Returns:
            Matplotlib Figure object
        """
        # Check if we have price data
        has_price_data = self.price_data is not None and not self.price_data.empty

        # Check if it's multi-asset data (has multiple ts_codes)
        is_multi_asset = False
        if has_price_data and "ts_code" in self.price_data.columns:
            is_multi_asset = self.price_data["ts_code"].nunique() > 1

        if has_price_data and not is_multi_asset:
            # Single asset mode: 2x2 layout
            fig = plt.figure(figsize=(16, 12))
            gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.25)

            # 1. Equity Curve (top left)
            ax1 = fig.add_subplot(gs[0, 0])
            self._plot_equity_to_ax(ax1)
            for label in ax1.get_xticklabels():
                label.set_rotation(30)
                label.set_ha("right")

            # 2. Drawdown (top right)
            ax2 = fig.add_subplot(gs[0, 1])
            self._plot_drawdown_to_ax(ax2)
            for label in ax2.get_xticklabels():
                label.set_rotation(30)
                label.set_ha("right")

            # 3. Price with Trades (middle left)
            ax3 = fig.add_subplot(gs[1, 0])
            self._plot_trades_to_ax(ax3)
            for label in ax3.get_xticklabels():
                label.set_rotation(30)
                label.set_ha("right")

            # 4. Metrics Card (middle right and bottom)
            ax4 = fig.add_subplot(gs[1:, 1])
            self._plot_metrics_card_to_ax(ax4)
        else:
            # Multi-asset mode or no price data: 3x2 layout
            fig = plt.figure(figsize=(16, 12))
            gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.25)

            # 1. Equity Curve (top left, spans 2 columns)
            ax1 = fig.add_subplot(gs[0, :])
            self._plot_equity_to_ax(ax1)
            ax1.set_title("Equity Curve", fontsize=14, fontweight="bold", pad=10)
            for label in ax1.get_xticklabels():
                label.set_rotation(30)
                label.set_ha("right")

            # 2. Drawdown (middle left)
            ax2 = fig.add_subplot(gs[1, 0])
            self._plot_drawdown_to_ax(ax2)
            for label in ax2.get_xticklabels():
                label.set_rotation(30)
                label.set_ha("right")

            # 3. Trade Overview (middle right)
            ax3 = fig.add_subplot(gs[1, 1])
            self._plot_trade_overview_to_ax(ax3)
            for label in ax3.get_xticklabels():
                label.set_rotation(45)
                label.set_ha("right")

            # 4. Metrics Card (bottom, spans 2 columns)
            ax4 = fig.add_subplot(gs[2, :])
            self._plot_metrics_card_to_ax(ax4)

        # Title for the whole report
        fig.suptitle("Backtest Composite Report", fontsize=16, fontweight="bold", y=0.995)
        plt.subplots_adjust(top=0.92)

        if save_path:
            fig.savefig(save_path, dpi=dpi, bbox_inches="tight")

        return fig

    def _get_ts_code(self) -> str:
        """Get ts_code from price data or return 'unknown'."""
        if (
            self.price_data is not None
            and not self.price_data.empty
            and "ts_code" in self.price_data.columns
        ):
            # Check if it's multi-asset
            if self.price_data["ts_code"].nunique() > 1:
                return "multi_asset"
            ts_code = self.price_data["ts_code"].iloc[0]
            # Sanitize filename
            return ts_code.replace(".", "_")
        return "multi_asset"

    def save_all_plots(self, output_dir: str | Path, dpi: int = 150) -> dict[str, Path]:
        """
        Save all plots to the specified directory.

        Args:
            output_dir: Directory to save plots
            dpi: DPI for saved figures

        Returns:
            Dictionary of plot names to file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        ts_code = self._get_ts_code()
        paths = {}

        # Save equity curve
        equity_path = output_path / f"equity_curve_{ts_code}.png"
        self.plot_equity_curve(equity_path, dpi=dpi)
        paths["equity_curve"] = equity_path
        plt.close()

        # Save drawdown
        drawdown_path = output_path / f"drawdown_{ts_code}.png"
        self.plot_drawdown(drawdown_path, dpi=dpi)
        paths["drawdown"] = drawdown_path
        plt.close()

        # Check if it's multi-asset data
        is_multi_asset = False
        if (
            self.price_data is not None
            and not self.price_data.empty
            and "ts_code" in self.price_data.columns
        ):
            is_multi_asset = self.price_data["ts_code"].nunique() > 1

        # Save trades visualization
        if self.price_data is not None and not self.price_data.empty:
            if is_multi_asset:
                # Multi-asset: save both trade overview and multi-asset trades chart
                overview_path = output_path / f"trade_overview_{ts_code}.png"
                self.plot_trade_overview(overview_path, dpi=dpi)
                paths["trade_overview"] = overview_path
                plt.close()

                multi_asset_trades_path = output_path / f"multi_asset_trades_{ts_code}.png"
                self.plot_multi_asset_trades(multi_asset_trades_path, dpi=dpi)
                paths["multi_asset_trades"] = multi_asset_trades_path
                plt.close()
            else:
                # Single asset: save trades on price
                trades_path = output_path / f"trades_on_price_{ts_code}.png"
                self.plot_trades_on_price(trades_path, dpi=dpi)
                paths["trades_on_price"] = trades_path
                plt.close()
        else:
            # No price data: save trade overview
            overview_path = output_path / f"trade_overview_{ts_code}.png"
            self.plot_trade_overview(overview_path, dpi=dpi)
            paths["trade_overview"] = overview_path
            plt.close()

        # Save composite report
        report_path = output_path / f"composite_report_{ts_code}.png"
        self.plot_composite_report(report_path, dpi=dpi)
        paths["composite_report"] = report_path
        plt.close()

        return paths
