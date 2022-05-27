from retry import retry
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 3回まで試行、トライの感覚を10秒、回数毎に2倍していく
@retry(tries=3, delay=10, backoff=2)
def get_html(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup

all_data = []
max_page = 909

# ベースとなるurl
base_url = "https://suumo.jp/chintai/fukuoka/sa_fukuoka/?page={}"

# 1ページ目から開始
page = 1
for page in range(1, max_page+1):
    
    # base_urlにformat関数を使用 pageのクエリ部分を可変に
    url = base_url.format(page)
    # htmlを取得
    soup = get_html(url)
    
    #全てのアイテムを抽出
    items = soup.findAll("div", {"class": "cassetteitem"})
    print("page", page, "items", len(items))

    # 各々のアイテムに対する処理
    for item in items:
        stations = item.findAll("div", {"class": "cassetteitem_detail-text"})

        # 各々のアクセスの取得
        for station in stations:

            #変数を定義する
            base_data = {}

            # 基礎情報を集める
            base_data["名称"] = item.find("div", {"class": "cassetteitem_content-title"}).getText().strip()
            base_data["カテゴリー"] = item.find("div", {"class": "cassetteitem_content-label"}).getText().strip()
            base_data["アドレス"] = item.find("li", {"class": "cassetteitem_detail-col1"}).getText().strip()            
            base_data["アクセス"] = station.getText().strip()
            base_data["築年数"] = item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[0].getText().strip()            
            base_data["構造"] = item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[1].getText().strip() 

            # 各々の部屋に対する処理
            tbodys = item.find("table", {"class": "cassetteitem_other"}).findAll("tbody")

            for tbody in tbodys:
                data = base_data.copy()

                data["階数"] = tbody.findAll("td")[2].getText().strip()
                
                data["家賃"] = tbody.findAll("td")[3].findAll("li")[0].getText().strip()
                data["管理費"] = tbody.findAll("td")[3].findAll("li")[1].getText().strip()

                data["敷金"] = tbody.findAll("td")[4].findAll("li")[0].getText().strip()
                data["礼金"] = tbody.findAll("td")[4].findAll("li")[1].getText().strip()

                data["間取り"] = tbody.findAll("td")[5].findAll("li")[0].getText().strip()
                data["面積"] = tbody.findAll("td")[5].findAll("li")[1].getText().strip()
                
                data["URL"] = "https://suumo.jp" + tbody.findAll("td")[8].find("a").get("href")

                all_data.append(data)

# データフレームへの変換
df = pd.DataFrame(all_data)
# csvへの保存
df.to_csv("C:\\Users\Logical\logical\発表用\\6月発表用\\fukuoka_city_raw_data.csv")         

