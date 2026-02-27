def process_portfolio(df):
    portfolio_result = {}

    grouped = df.groupby("Scrip")

    for stock, data in grouped:
        buy_lots = []
        total_buy_value = 0
        total_buy_qty = 0
        total_sell_value = 0
        total_sell_qty = 0
        realized_profit = 0

        for _, row in data.iterrows():
            qty = float(row["Qty"])
            price = float(row["U P"])
            trade_type = row["Type"].strip().upper()

            if trade_type == "BOUGHT":
                buy_lots.append([qty, price])
                total_buy_value += qty * price
                total_buy_qty += qty

            elif trade_type == "SOLD":
                total_sell_value += qty * price
                total_sell_qty += qty
                sell_qty = qty

                while sell_qty > 0 and buy_lots:
                    lot_qty, lot_price = buy_lots[0]

                    if lot_qty <= sell_qty:
                        realized_profit += lot_qty * (price - lot_price)
                        sell_qty -= lot_qty
                        buy_lots.pop(0)
                    else:
                        realized_profit += sell_qty * (price - lot_price)
                        buy_lots[0][0] -= sell_qty
                        sell_qty = 0

        remaining_shares = sum(lot[0] for lot in buy_lots)

        avg_buy = total_buy_value / total_buy_qty if total_buy_qty else 0
        avg_sell = total_sell_value / total_sell_qty if total_sell_qty else 0

        

        portfolio_result[stock] = {
            "average_buy_value": round(avg_buy, 2),
            "average_sell_value": round(avg_sell, 2),
            "realized_profit": round(realized_profit, 2),
            "total_investment": round(total_buy_value, 2),
            "remaining_shares": remaining_shares
        }
    
    return portfolio_result