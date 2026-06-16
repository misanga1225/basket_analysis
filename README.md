# バスケットボール分析 — セットアップ手順
動作確認環境：**Windows 11 / macOS**、**Python 3.12**

---

## STEP 1. Python パッケージのインストール

```bash
pip install -r requirements.txt
```

## STEP 2. ffmpeg のインストール

動画（MP4）書き出しに必要。OSに合わせてインストールし、PATHを通す。

- Windows：`winget install ffmpeg` または https://ffmpeg.org/ から取得
- macOS：`brew install ffmpeg`
- 確認：`ffmpeg -version` が表示されれば OK

## STEP 3. 生データの配置

生データはリポジトリに含まれない（`.gitignore` で除外）。
**リポジトリ直下に `_dataset_yamaha/` を作り**、以下の CSV を置く。

```
basket_analysis/
└─ _dataset_yamaha/
   ├─ basket_G{g}-S{s}T{t}.csv         # 追跡座標（g=1..4, s=1..3, t=1..7 → 計84ファイル）
   └─ basket_G{g}-S{s}T{t}_event.csv   # イベント（catch 等 → 計84ファイル）
```

- 追跡 CSV ヘッダ：`frame_number,x_O1red,y_O1red,x_O2blue,y_O2blue,x_O3pink,y_O3pink,x_D1black,y_D1black,x_D2orange,y_D2orange,x_D3yellow,y_D3yellow`
- イベント CSV ヘッダ：`frame_number,O1_red,O2_blue,O3_pink,D1_black,D2_orange,D3_yellow`（catch したフレームの該当列に `catch`）

## STEP 4. 前処理（動画・グラフ用データ・pkl を生成）

`src/preprocessor/preprocess.ipynb` を開き、**「すべてのセルを実行（Run All）」** する。
（`_dataset_yamaha` だけがあれば動く。他のデータセットが無くても自動でスキップする）

CLI で実行する場合：

```bash
cd src/preprocessor
jupyter nbconvert --to notebook --execute --inplace preprocess.ipynb
```

- 84試行 × 8並列で **約10分**。
- 出力先：`src/analyzers/processed_data/G{n}/basket_G{g}-S{s}T{t}/`
  - `..._voronoi.mp4` … 通常ボロノイ動画
  - `..._effective_voronoi_45deg.mp4` … 有効ボロノイ動画（θ=45°）
  - `basketball_court.png` … 軌跡画像
  - `effective_area_trajectories_theta{30,45,60,90}.pkl` … 次の STEP で使うデータ

> 動画は θ=45° のみ生成される。θ=30° の動画も必要なら、`preprocess.ipynb` 最終セルの `ANIM_THETA_DEG = 45` を `30` に変えて再実行する。

## STEP 5. 平均有効ボロノイ領域の CSV 出力（静大形式）

STEP 4 完了後に実行する。

```bash
python src/analyzers/effective_voronoi_timeseries/export_mean_voronoi.py
```

- 出力先：`analysis_output/`
  - `voronoi_mean_theta30.csv` … θ=30° の結果
  - `voronoi_mean_theta45.csv` … θ=45° の結果
  - `voronoi_template.csv` … テンプレート（`Phase` / `Per_final` 列はここから引き継ぐ）
- 列構成は `analysis_dataset_voronoi_shizudai.csv` と同じ（Game, Session, Trial, Phase, Per_final, O1〜D3）。
- O1〜D3 は各試行の**平均有効ボロノイ領域 [m²]**（全フレーム平均・NaN 除外、小数第5位）。
- そのまま静大形式の空欄にコピー＆ペーストできる。

（参考）θ=30/45 の時系列グラフだけを描き直したい場合：

```bash
python src/analyzers/effective_voronoi_timeseries/run.py
# 出力: src/analyzers/effective_voronoi_timeseries/results/*.png
```

---

## 同梱の成果物（リポジトリに含まれる zip）

再生成せずすぐ確認できるよう、以下を同梱している。

| ファイル | 内容 |
|---|---|
| `effective_voronoi_theta30.zip` | θ=30° の時系列グラフ（12枚） |
| `effective_voronoi_theta45.zip` | θ=45° の時系列グラフ（12枚） |
| `effective_voronoi_45deg_videos.zip` | θ=45° の有効ボロノイ動画（84本） |
| `analysis_output/voronoi_mean_theta{30,45}.csv` | 平均有効ボロノイ領域 CSV |

通常ボロノイ動画・pkl などその他の中間生成物は、STEP 4 を実行すれば再生成される。

---

## ディレクトリ構成（要点のみ）

- `_dataset_yamaha/` … 生データ（STEP 3 で配置。git 管理外）
- `src/preprocessor/preprocess.ipynb` … 前処理（STEP 4）
- `src/analyzers/processed_data/` … 前処理の出力（動画・pkl 等。git 管理外）
- `src/analyzers/effective_voronoi_timeseries/`
  - `export_mean_voronoi.py` … 平均値 CSV 出力（STEP 5）
  - `run.py` … 時系列グラフ出力
  - `results/` … グラフ画像（git 管理外）
- `analysis_output/` … CSV 出力先（git 管理対象）
- `requirements.txt` … 必要パッケージ
