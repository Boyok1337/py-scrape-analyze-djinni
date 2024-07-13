import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class JobDataAnalyzer:
    def __init__(self, date, top_n=10):
        self.date = date
        self.top_n = top_n
        self.file_path = os.path.join("../scraped_data", f"{self.date}.csv")
        self.data = None
        self.technologies = None

    def _read_csv_file(self):
        if os.path.exists(self.file_path):
            self.data = pd.read_csv(self.file_path)
        else:
            raise FileNotFoundError(f"File {self.file_path} not found.")

    def _prepare_data(self):
        if self.data is not None:
            self.technologies = (
                self.data["technologies"]
                .str.split(", ")
                .explode()
                .value_counts()
                .head(self.top_n)
            )
        else:
            raise ValueError("No data available to prepare.")

    def _create_plot(self):
        if self.technologies is not None:
            plt.figure(figsize=(14, 8))
            sns.set(style="darkgrid")

            plt.gca().set_facecolor("black")

            sns.barplot(
                x=self.technologies.index,
                y=self.technologies.values,
                hue=self.technologies.index,
                palette="viridis",
                legend=False,
            )

            plt.title(
                "Popularity of Technologies in Python Developer Job Listings",
                color="white",
                fontsize=24,
            )
            plt.xlabel("Technologies", color="white")
            plt.ylabel("Number of Listings", color="white")
            plt.xticks(rotation=45, color="white")
            plt.yticks(color="white")

            plt.tight_layout()
        else:
            raise ValueError("No technologies data available to plot.")

    def _save_plot(self):
        output_directory = "../analyzed_data"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        output_file = os.path.join(output_directory, f"{self.date}.png")
        plt.savefig(output_file, facecolor="black")
        plt.close()
        print(f"Chart saved as {output_file}")

    def analyze(self):
        try:
            self._read_csv_file()
            self._prepare_data()
            self._create_plot()
            self._save_plot()
        except (FileNotFoundError, ValueError) as e:
            print(e)


if __name__ == "__main__":
    date = "2024-07-11"  # Replace with your desired date
    analyzer = JobDataAnalyzer(date)
    analyzer.analyze()
