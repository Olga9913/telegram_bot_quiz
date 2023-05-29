import pandas as pd

class Films:
    def __init__(self, file_csv):
        self.df = pd.read_csv(file_csv)
        self.df = self.df[(self.df["name_ru"].str.len() <= 20) & (self.df["name_en"].str.len() <= 20)]

    def ramdomizer(self):
        random_tmp = self.df.sample(n=4)
        return random_tmp
