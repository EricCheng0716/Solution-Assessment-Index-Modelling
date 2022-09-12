import datetime as dt
import pandas as pd

class IndexModel:
    def __init__(self) -> None:
        self.TOP_STOCK_WEIGHTS = [.5,.25,.25]
        self.STOCK_COLS = [f'Stock_{s}' for s in 'ABCDEFGHIJ']
        self.input_filename = 'data_sources/stock_prices.csv'
        self.start_index = 100 # our principle from first day
        pass
    
    def get_index_change_percentages(self, row1, row2, stocks):
        if not stocks: return None
        return sum([(row2[stock]/row1[stock]) * weight for stock, weight in zip(stocks, self.TOP_STOCK_WEIGHTS)])


    def get_top_stock_names(self, day):
        return [
                stock for stock, _ in sorted(
                    day[self.STOCK_COLS].items(),
                    key=lambda item: -item[1]
                )
            ][:len(self.TOP_STOCK_WEIGHTS)]

    def calc_index_level(self, start_date: dt.date, end_date: dt.date) -> None:
        self.all_top_indices = []
        BUSINESS_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        df = pd.read_csv(self.input_filename)
        df['Parsed_Date'] = df['Date'].apply(lambda x: dt.datetime.strptime(x, '%d/%m/%Y').date())
        df.sort_values(['Parsed_Date'])
        df['Is_Business_Day'] = df['Parsed_Date'].apply(lambda x: x.strftime('%A') in BUSINESS_DAYS)

        last_bussiness_day = None
        top_index = None
        top_stocks = None
        monthly_top_indices = []
        all_top_indices = []
        
        for i, day in df[df.Is_Business_Day].iterrows():
            date = day.Parsed_Date

            # start and termination criteria
            if start_date > date:
                last_bussiness_day = day
                continue
            if end_date < date:
                break

            if date.month != last_bussiness_day.Parsed_Date.month:
                top_index_from_last_month = self.get_index_change_percentages(last_bussiness_day, day, top_stocks)
                monthly_top_indices.append((date, top_index_from_last_month))
                all_top_indices.append(monthly_top_indices)

                top_stocks = self.get_top_stock_names(last_bussiness_day)
                monthly_top_indices = []

            top_index = self.get_index_change_percentages(last_bussiness_day, day, top_stocks)
            monthly_top_indices.append((date, top_index))
            last_bussiness_day = day

        all_top_indices.append(monthly_top_indices)

        cumm = self.start_index
        results = [[start_date, cumm]]

        for month in all_top_indices[1:]:
            for day in month[1:]:
                cumm *= day[1]
                results.append((day[0], cumm))
        self.results = results

    def export_values(self, file_name: str) -> None:

        df = pd.DataFrame({
            "Date": [x[0] for x in self.results],
            "index_level": [round(x[1], 2) for x in self.results]
        })
        df.to_csv(file_name, index=False)

