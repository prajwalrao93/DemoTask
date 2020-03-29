from flask import Flask, render_template, request, redirect, url_for, session
import os, zipfile, requests, datetime
import pandas as pd

app = Flask(__name__)

class DataPrep():


    def downloadData(self,fileName):
        r = requests.get(f"https://archives.nseindia.com/content/historical/EQUITIES/2020/{fileName}")
        fileName = fileName[4:]
        with open(fileName,'wb') as f:
            f.write(r.content)
        df = pd.read_csv(fileName)
        return df


    def finalTable(self):
        today = datetime.date.today()
        count = 0
        while(count < 30):
            if (today.weekday() < 5):
                fileName = f"{str(today.strftime('%b')).upper()}/cm{str(today.strftime('%d'))}{str(today.strftime('%b')).upper()}2020bhav.csv.zip"
                try:
                    df = self.downloadData(fileName)
                    df.drop(["TOTTRDVAL", "TOTALTRADES", "ISIN"],axis=1, inplace=True)
                    if (count == 0):
                        concat = df
                    else:
                        concat = pd.concat([concat, df], axis=0)
                    count += 1
                    os.remove(fileName[4:])
                except:
                    pass
            today = today - datetime.timedelta(days=1)
        concat.to_excel("Final.xlsx")
        return concat


    def individualFiles(self):
        df = pd.read_excel("Final.xlsx")
        for i in df.SYMBOL.unique():
            df[df["SYMBOL"] == i].drop(["Unnamed: 0","Unnamed: 13"]).to_excel(f"{i}.xlsx")


@app.route("/", methods=['GET'])
def home():
    if os.path.exists("Final.xlsx"):
        data = pd.read_excel("Final.xlsx")
        for i in data.SYMBOL.unique():
            data[data["SYMBOL"] == i].drop(["Unnamed: 0","Unnamed: 13"]).to_excel(f"{i}.xlsx")
    else:
        final_data = DataPrep()
        data = final_data.finalTable()
        final_data.individualFiles()
    return render_template("home.html", table=data)


@app.route('/table', methods=['GET','POST'])
def table():
    select = str(request.form.get('table'))
    data = pd.read_excel("Final.xlsx")
    data.drop(["Unnamed: 0","Unnamed: 13"], axis=1, inplace=True)
    new_df = data[data["SYMBOL"] == select]
    return render_template("table.html", column_names=new_df.columns.values, row_data=list(new_df.values.tolist()),link_column="SYMBOL", zip=zip)


if __name__ == "__main__":
    app.run(debug=True)
