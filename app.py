import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
import plotly.graph_objects as go

# --- 初期設定 ---
st.set_page_config(
    page_title="メンタルヘルス食習慣スコア Extended (NNBI Model)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- セッション状態の初期化 ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'input'
if 'input_step' not in st.session_state:
    st.session_state['input_step'] = 1  # 1: 問1-10, 2: 問11-20, 3: 画像アップロード
if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None
if 'ingredients_df' not in st.session_state:
    st.session_state['ingredients_df'] = None
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = {}
if 'habit_answers' not in st.session_state:
    st.session_state['habit_answers'] = {}

# --- API連携 & 画像解析ロジック (変更なし) ---

def call_logmeal_api(image_file, api_token):
    headers = {'Authorization': 'Bearer ' + api_token}
    url_recognition = 'https://api.logmeal.es/v2/image/recognition/dish'
    try:
        files = {'image': image_file.getvalue()}
        response = requests.post(url_recognition, headers=headers, files=files)
        response.raise_for_status()
        data = response.json()
        if 'recognition_results' in data and len(data['recognition_results']) > 0:
            dish_result = data['recognition_results'][0]
            dish_name = dish_result['name']
            detected_ingredients = [
                {
                    "食材名": dish_name,
                    "カロリー(kcal)": int(dish_result.get('calories', 300)),
                    "タンパク質(g)": 15, "脂質(g)": 10, "炭水化物(g)": 40,
                    "水溶性食物繊維(g)": 1.0, "不溶性食物繊維(g)": 2.0,
                    "ビタミンB1(mg)": 0.1, "ビタミンC(mg)": 5, "ビタミンD(μg)": 0,
                    "鉄分(mg)": 1.0, "亜鉛(mg)": 2.0, "マグネシウム(mg)": 10,
                    "カテゴリ": "主食"
                }
            ]
            return pd.DataFrame(detected_ingredients)
        else:
            st.error("料理を認識できませんでした。")
            return None
    except Exception as e:
        st.error(f"APIエラー: {e}")
        return None

def analyze_image(file_obj, api_token=None):
    if api_token:
        with st.spinner('LogMeal AI で解析中...'):
            df = call_logmeal_api(file_obj, api_token)
            if df is not None: return df
            else: st.warning("API解析に失敗したため、デモデータを使用します。")
    
    with st.spinner('画像をスキャン中... (デモモード)'):
        time.sleep(1.0)
    
    # デモデータ
    initial_data = [
        {"食材名": "白米", "カロリー(kcal)": 250, "タンパク質(g)": 4, "脂質(g)": 0.5, "炭水化物(g)": 55, "水溶性食物繊維(g)": 0, "不溶性食物繊維(g)": 0.3, "ビタミンB1(mg)": 0.02, "ビタミンC(mg)": 0, "ビタミンD(μg)": 0, "鉄分(mg)": 0.1, "亜鉛(mg)": 0.6, "マグネシウム(mg)": 7, "カテゴリ": "主食"},
        {"食材名": "味噌汁", "カロリー(kcal)": 40, "タンパク質(g)": 2, "脂質(g)": 1, "炭水化物(g)": 5, "水溶性食物繊維(g)": 0.5, "不溶性食物繊維(g)": 1.0, "ビタミンB1(mg)": 0.04, "ビタミンC(mg)": 0, "ビタミンD(μg)": 0, "鉄分(mg)": 0.8, "亜鉛(mg)": 0.2, "マグネシウム(mg)": 15, "カテゴリ": "汁物"},
        {"食材名": "焼き魚", "カロリー(kcal)": 200, "タンパク質(g)": 20, "脂質(g)": 12, "炭水化物(g)": 0.5, "水溶性食物繊維(g)": 0, "不溶性食物繊維(g)": 0, "ビタミンB1(mg)": 0.1, "ビタミンC(mg)": 0, "ビタミンD(μg)": 15, "鉄分(mg)": 0.3, "亜鉛(mg)": 1.2, "マグネシウム(mg)": 30, "カテゴリ": "主菜"},
        {"食材名": "ほうれん草のお浸し", "カロリー(kcal)": 25, "タンパク質(g)": 2, "脂質(g)": 0.2, "炭水化物(g)": 3, "水溶性食物繊維(g)": 0.7, "不溶性食物繊維(g)": 1.5, "ビタミンB1(mg)": 0.05, "ビタミンC(mg)": 15, "ビタミンD(μg)": 0, "鉄分(mg)": 2.0, "亜鉛(mg)": 0.4, "マグネシウム(mg)": 40, "カテゴリ": "副菜"},
        {"食材名": "納豆", "カロリー(kcal)": 100, "タンパク質(g)": 8, "脂質(g)": 5, "炭水化物(g)": 6, "水溶性食物繊維(g)": 2.0, "不溶性食物繊維(g)": 4.0, "ビタミンB1(mg)": 0.07, "ビタミンC(mg)": 0, "ビタミンD(μg)": 0, "鉄分(mg)": 1.5, "亜鉛(mg)": 1.0, "マグネシウム(mg)": 50, "カテゴリ": "副菜"},
        {"食材名": "サラダ", "カロリー(kcal)": 50, "タンパク質(g)": 1, "脂質(g)": 3, "炭水化物(g)": 5, "水溶性食物繊維(g)": 0.5, "不溶性食物繊維(g)": 2.0, "ビタミンB1(mg)": 0.05, "ビタミンC(mg)": 20, "ビタミンD(μg)": 0, "鉄分(mg)": 0.5, "亜鉛(mg)": 0.2, "マグネシウム(mg)": 10, "カテゴリ": "副菜"},
        {"食材名": "卵焼き", "カロリー(kcal)": 150, "タンパク質(g)": 10, "脂質(g)": 10, "炭水化物(g)": 4, "水溶性食物繊維(g)": 0, "不溶性食物繊維(g)": 0, "ビタミンB1(mg)": 0.03, "ビタミンC(mg)": 0, "ビタミンD(μg)": 1.5, "鉄分(mg)": 0.9, "亜鉛(mg)": 0.7, "マグネシウム(mg)": 6, "カテゴリ": "副菜"}
    ]
    return pd.DataFrame(initial_data)

def calculate_total_nutrients(df_ingredients):
    if df_ingredients is None or df_ingredients.empty:
        return {}
    
    total = df_ingredients.sum(numeric_only=True)
    return {
        "calories": int(total.get("カロリー(kcal)", 0)),
        "protein": round(total.get("タンパク質(g)", 0), 1),
        "fat": round(total.get("脂質(g)", 0), 1),
        "carbs": round(total.get("炭水化物(g)", 0), 1),
        "fiber_sol": round(total.get("水溶性食物繊維(g)", 0), 1),
        "fiber_insol": round(total.get("不溶性食物繊維(g)", 0), 1),
        "vit_b1": round(total.get("ビタミンB1(mg)", 0), 2),
        "vit_c": round(total.get("ビタミンC(mg)", 0), 1),
        "vit_d": round(total.get("ビタミンD(μg)", 0), 1),
        "iron": round(total.get("鉄分(mg)", 0), 1),
        "zinc": round(total.get("亜鉛(mg)", 0), 1),
        "magnesium": round(total.get("マグネシウム(mg)", 0), 1)
    }

# --- ロジック: NNBIスコア算出 (更新版) ---

def calculate_comprehensive_score(habit_answers, user_profile, nutrients, constitution_type):
    """
    NNBI理論モデルに基づくスコア算出
    Formula: Score = 20 + (0.35 * X_diet) + (0.25 * X_bio) + (0.20 * X_dop) - (0.20 * X_risk)
    ※ ベースライン(α)を20とし、満点が100になるよう設計
    """
    
    # 結果格納用コンテナ
    breakdown = {
        "diet": {"score": 0, "reasons": []}, # X_diet: 良質な食事パターン
        "bio":  {"score": 0, "reasons": []}, # X_bio: 腸内環境・微生物
        "dop":  {"score": 0, "reasons": []}, # X_dop: ドーパミン合成能
        "risk": {"score": 0, "reasons": []}  # X_risk: 炎症・リスク因子
    }

    # ==========================================
    # 1. X_diet: ポジティブな食事パターン (Max 100)
    # ==========================================
    xd_score = 0
    
    # 習慣 (計60点)
    if habit_answers.get("fish") in ["週3回以上", "週1-2回"]: xd_score += 10
    if habit_answers.get("chicken") in ["週3回以上", "週1-2回"]: xd_score += 10
    if habit_answers.get("veg_variety") == "5種類以上": xd_score += 15
    elif habit_answers.get("veg_variety") == "3-4種類": xd_score += 5
    if habit_answers.get("oil") == "オリーブ/アマニ油中心": xd_score += 10
    if habit_answers.get("water") == "1.5L以上": xd_score += 5
    if habit_answers.get("breakfast") == "毎日食べる": xd_score += 10

    # 食事内容 (計40点)
    # PFCバランスが極端でないか
    p, f, c = nutrients['protein'], nutrients['fat'], nutrients['carbs']
    total_g = p + f + c
    if total_g > 0:
        p_ratio = p / total_g
        if 0.15 <= p_ratio <= 0.35: # タンパク質比率が適正
            xd_score += 20
            breakdown["diet"]["reasons"].append("・PFCバランスが良好")
    
    # ビタミンC (抗酸化)
    if nutrients['vit_c'] > 30:
        xd_score += 20
        breakdown["diet"]["reasons"].append("・十分なビタミンC (抗酸化作用)")

    xd_score = min(100, xd_score)
    breakdown["diet"]["score"] = xd_score
    if xd_score >= 80: breakdown["diet"]["reasons"].append("・地中海式に近い良質な食習慣")

    # ==========================================
    # 2. X_bio: 腸内環境・Coprococcus係数 (Max 100)
    # ==========================================
    xb_score = 0
    
    # 習慣 (計50点)
    if habit_answers.get("fiber") == "1日3皿分以上": xb_score += 25
    elif habit_answers.get("fiber") == "1日2皿分": xb_score += 15
    
    if habit_answers.get("fermented") == "ほぼ毎日": xb_score += 25
    elif habit_answers.get("fermented") == "週3-4回": xb_score += 15

    # 食事内容 (計50点)
    total_fiber = nutrients['fiber_sol'] + nutrients['fiber_insol']
    if total_fiber >= 5.0:
        xb_score += 30
        breakdown["bio"]["reasons"].append(f"・1食で十分な食物繊維 ({total_fiber}g)")
    elif total_fiber >= 2.0:
        xb_score += 10
    
    if nutrients['magnesium'] >= 30: # Mgは腸の蠕動運動に寄与
        xb_score += 20
        breakdown["bio"]["reasons"].append("・マグネシウムによる代謝補助")

    xb_score = min(100, xb_score)
    breakdown["bio"]["score"] = xb_score
    
    # ==========================================
    # 3. X_dop: ドーパミン・神経伝達物質合成能 (Max 100)
    # ==========================================
    xdo_score = 0
    
    # 習慣 (計40点)
    if habit_answers.get("protein") == "毎食摂取": xdo_score += 20
    if habit_answers.get("bluefish") in ["週2回以上", "週1回"]: xdo_score += 20

    # 食事内容 (計60点: NT-Index簡易版)
    # ドーパミン合成には アミノ酸(タンパク質) + 鉄 + 葉酸/B群 + 亜鉛 が必須
    mat_score = 0
    if nutrients['protein'] >= 20: mat_score += 20
    elif nutrients['protein'] >= 10: mat_score += 10
    
    if nutrients['iron'] >= 2.0: mat_score += 10
    if nutrients['zinc'] >= 3.0: mat_score += 10
    if nutrients['vit_b1'] >= 0.1: mat_score += 10
    if nutrients['vit_d'] >= 5.0: mat_score += 10 # セロトニン/ドーパミン調整
    
    xdo_score += mat_score
    if mat_score >= 40:
        breakdown["dop"]["reasons"].append("・神経伝達物質の原料が豊富")
    
    xdo_score = min(100, xdo_score)
    breakdown["dop"]["score"] = xdo_score

    # ==========================================
    # 4. X_risk: 炎症・阻害リスク因子 (Max 100)
    # ==========================================
    xr_score = 0
    risk_reasons = []

    # 習慣・摂取頻度 (高いほどリスク大)
    if habit_answers.get("gluten") in ["ほぼ毎日", "週3-5回"]: xr_score += 10
    if habit_answers.get("fastfood") == "週3回以上": xr_score += 15
    if habit_answers.get("processed_meat") in ["ほぼ毎日", "週3-5回"]: xr_score += 10
    if habit_answers.get("carbs") == "過剰(菓子パン等含む)": xr_score += 15
    if habit_answers.get("snack") == "毎日甘いもの": xr_score += 10
    if habit_answers.get("alcohol") == "ほぼ毎日": xr_score += 10
    if habit_answers.get("late_night") == "寝る直前が多い": xr_score += 10

    # プロフィール要因
    if user_profile.get("stress_level") == "High":
        xr_score += 20
        risk_reasons.append("・高ストレスによるコルチゾール負荷")
    
    # アレルギー不整合
    if "グルテン" in user_profile.get("allergies", []) and habit_answers.get("gluten") != "週1回未満":
        xr_score += 20
        risk_reasons.append("・アレルギー物質の摂取リスク")

    xr_score = min(100, xr_score)
    breakdown["risk"]["score"] = xr_score
    breakdown["risk"]["reasons"] = risk_reasons

    # ==========================================
    # Final Calculation (NNBI Formula)
    # M = 20 + 0.35(Diet) + 0.25(Bio) + 0.20(Dop) - 0.20(Risk)
    # ==========================================
    
    # 各係数
    w_diet = 0.35
    w_bio = 0.25
    w_dop = 0.20
    w_risk = 0.20
    alpha = 20 # ベースライン切片

    calculation = alpha + (xd_score * w_diet) + (xb_score * w_bio) + (xdo_score * w_dop) - (xr_score * w_risk)
    final_score = int(max(0, min(100, calculation))) # 0-100にクリップ

    return final_score, breakdown

def predict_constitution(answers):
    # 体質予測ロジック（そのまま維持）
    heavy_carbs = answers.get("carbs") in ["多い(毎日大盛り)", "過剰(菓子パン等含む)"]
    heavy_gluten = answers.get("gluten") in ["週3-5回", "ほぼ毎日"]
    heavy_fastfood = answers.get("fastfood") in ["週3回以上"]
    heavy_procmeat = answers.get("processed_meat") in ["週3-5回", "ほぼ毎日"]
    low_protein = answers.get("protein") in ["1日1食", "それ以下"]
    low_fish = answers.get("fish") in ["月1-3回", "ほとんど食べない"]

    if heavy_carbs or heavy_gluten:
        return {"type": "糖質依存・血糖値スパイク型", "desc": "血糖値の乱高下により、気分の波が不安定になりやすい体質"}
    elif heavy_fastfood or heavy_procmeat:
        return {"type": "慢性炎症・内臓疲労型", "desc": "腸内環境が乱れやすく、慢性的な疲労感を感じやすい体質"}
    elif low_protein or low_fish:
        return {"type": "タンパク質不足・エネルギー欠乏型", "desc": "意欲低下や集中力不足に陥りやすい体質"}
    else:
        return {"type": "バランス維持型", "desc": "比較的良好なバランスですが、油断は禁物な体質"}

# --- グラフ描画関数 ---

def draw_pfc_balance(protein, fat, carbs):
    labels = ['タンパク質', '脂質', '炭水化物']
    values = [protein, fat, carbs]
    if sum(values) == 0: return None
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=.4,
        marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c']),
        textinfo='label+percent'
    )])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=150, showlegend=False)
    return fig

def draw_score_gauge(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "NNBI総合スコア"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 60], 'color': "lightgray"},
                {'range': [60, 80], 'color': "gray"},
                {'range': [80, 100], 'color': "lightblue"}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': score}}))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
    return fig

# --- ページ定義: 入力画面 (Page 1: 分割ステップ) ---

def page_input_screen():
    st.title("メンタルヘルス食習慣チェッカー (NNBI版)")
    
    # 進捗バーの表示
    step = st.session_state['input_step']
    progress_val = (step - 1) / 3
    if step == 3: progress_val = 1.0 # 完了
    
    st.progress(progress_val)
    st.caption(f"Step {step} / 3")

    # --- Step 1: 質問 1-10 ---
    if step == 1:
        st.subheader("📝 食習慣チェック (Part 1/2)")
        st.info("まずは基本的な食習慣について教えてください。(1-10問目)")
        
        with st.form("habit_form_1"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("##### 基礎栄養バランス")
                q_gluten = st.radio("1. グルテン(小麦)", ["週1回未満", "週1-2回", "週3-5回", "ほぼ毎日"], index=None)
                q_prot = st.radio("2. タンパク質摂取", ["毎食摂取", "1日2食", "1日1食", "それ以下"], index=None)
                q_fiber = st.radio("3. 食物繊維(野菜)", ["1日3皿分以上", "1日2皿分", "1日1皿分", "それ以下"], index=None)
                q_carbs = st.radio("4. 糖質(ご飯・パン等)", ["適量(茶碗1杯/食)", "やや多い(時々大盛り)", "多い(毎日大盛り)", "過剰(菓子パン等含む)"], index=None)
                q_fish = st.radio("5. 魚全般", ["週3回以上", "週1-2回", "月1-3回", "ほとんど食べない"], index=None)
            
            with col2:
                st.markdown("##### 食品の質")
                q_chicken = st.radio("6. 鶏肉", ["週3回以上", "週1-2回", "月1-3回", "ほとんど食べない"], index=None)
                q_fastfood = st.radio("7. ファストフード", ["月1回未満", "月2-3回", "週1-2回", "週3回以上"], index=None)
                q_procmeat = st.radio("8. 加工肉(ハム等)", ["週1回未満", "週1-2回", "週3-5回", "ほぼ毎日"], index=None)
                q_fermented = st.radio("9. 発酵食品(納豆・キムチ)", ["ほぼ毎日", "週3-4回", "週1-2回", "それ以下"], index=None)
                q_bluefish = st.radio("10. 青魚(Omega-3)", ["週2回以上", "週1回", "月1-3回", "ほとんど食べない"], index=None)
            
            submitted_1 = st.form_submit_button("次へ (質問 11-20へ)", type="primary")
            
            if submitted_1:
                required = [q_gluten, q_prot, q_fiber, q_carbs, q_fish, q_chicken, q_fastfood, q_procmeat, q_fermented, q_bluefish]
                if any(x is None for x in required):
                    st.error("すべての項目に回答してください。")
                else:
                    st.session_state['habit_answers'].update({
                        "gluten": q_gluten, "protein": q_prot, "fiber": q_fiber, "carbs": q_carbs, "fish": q_fish,
                        "chicken": q_chicken, "fastfood": q_fastfood, "processed_meat": q_procmeat, "fermented": q_fermented, "bluefish": q_bluefish
                    })
                    st.session_state['input_step'] = 2
                    st.rerun()

    # --- Step 2: 質問 11-20 & プロフィール ---
    elif step == 2:
        st.subheader("📝 生活習慣・メンタルチェック (Part 2/2)")
        st.info("続いて、生活習慣や体質について教えてください。(11-20問目)")
        
        with st.form("habit_form_2"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("##### 生活リズム・水分")
                q_water = st.radio("11. 1日の水分摂取量(水・茶)", ["1.5L以上", "1.0L-1.5L", "1.0L未満", "あまり飲まない"], index=None)
                q_caffeine = st.radio("12. カフェイン(コーヒー等)", ["飲まない", "1日1-2杯", "1日3-4杯", "1日5杯以上"], index=None)
                q_alcohol = st.radio("13. アルコール頻度", ["飲まない", "週1-2回", "週3-5回", "ほぼ毎日"], index=None)
                q_eat_speed = st.radio("14. 食べる速さ", ["ゆっくり(20分以上)", "普通(10-20分)", "早い(10分未満)", "極めて早い"], index=None)
                q_breakfast = st.radio("15. 朝食の習慣", ["毎日食べる", "週3-4回", "週1-2回", "食べない"], index=None)
            
            with col2:
                st.markdown("##### 間食・嗜好")
                q_late_night = st.radio("16. 就寝前の食事", ["寝る3時間前まで", "寝る2時間前", "寝る1時間前", "寝る直前が多い"], index=None)
                q_veg_variety = st.radio("17. 1日の野菜の種類", ["5種類以上", "3-4種類", "1-2種類", "ほぼ食べない"], index=None)
                q_dairy = st.radio("18. 乳製品(牛乳・チーズ)", ["適度(1日1杯/個)", "飲まない/食べない", "やや多い", "過剰に摂る"], index=None)
                q_snack = st.radio("19. 甘いおやつ・間食", ["ほとんど食べない", "週1-2回", "週3-4回", "毎日甘いもの"], index=None)
                q_oil = st.radio("20. 油の質(主に使用するもの)", ["オリーブ/アマニ油中心", "サラダ油/キャノーラ油", "動物性油脂", "揚げ物が多い"], index=None)
            
            st.markdown("---")
            st.markdown("**👤 プロフィール**")
            stress_level = st.select_slider("直近のストレスレベル", options=["Low", "Medium", "High"])
            selected_allergies = st.multiselect("アレルギー・除去対象", ["グルテン", "カゼイン", "卵", "乳製品", "そば", "落花生", "えび", "かに"])
            medical_history = st.text_input("既往歴 (任意)", placeholder="例: 糖尿病、高血圧、貧血など")
            selected_supplements = st.multiselect("サプリメント摂取状況 (任意)", ["ビタミンD", "亜鉛", "ケルセチン", "乳酸菌"])

            submitted_2 = st.form_submit_button("次へ (画像アップロードへ)", type="primary")
            
            if submitted_2:
                required = [q_water, q_caffeine, q_alcohol, q_eat_speed, q_breakfast, q_late_night, q_veg_variety, q_dairy, q_snack, q_oil]
                if any(x is None for x in required):
                    st.error("すべての項目に回答してください。")
                else:
                    st.session_state['habit_answers'].update({
                        "water": q_water, "caffeine": q_caffeine, "alcohol": q_alcohol, "eat_speed": q_eat_speed,
                        "breakfast": q_breakfast, "late_night": q_late_night, "veg_variety": q_veg_variety,
                        "dairy": q_dairy, "snack": q_snack, "oil": q_oil
                    })
                    st.session_state['user_profile'] = {
                        "stress_level": stress_level, "allergies": selected_allergies,
                        "medical_history": medical_history, "supplements": selected_supplements
                    }
                    st.session_state['input_step'] = 3
                    st.rerun()

    # --- Step 3: 画像アップロード & 解析開始 ---
    elif step == 3:
        st.subheader("📷 食事画像の解析")
        st.success("✅ アンケート回答完了！ 最後に食事の写真をアップロードしてください。")
        
        with st.expander("▶ 開発者オプション: LogMeal API設定"):
            api_token = st.text_input("LogMeal API Token (空欄の場合はデモモード)", type="password")

        uploaded_file = st.file_uploader("写真を選択", type=["jpg", "png", "jpeg"])
        
        if uploaded_file:
            st.image(uploaded_file, width=300)
            st.session_state['uploaded_file'] = uploaded_file
            
            if st.button("分析を開始する", type="primary"):
                st.session_state['ingredients_df'] = analyze_image(uploaded_file, api_token)
                st.session_state['page'] = 'result'
                st.rerun()
        
        if st.button("← アンケートに戻る"):
            st.session_state['input_step'] = 2
            st.rerun()

# --- ページ定義: 結果画面 (Page 2) ---

def page_result_screen():
    st.title("分析結果レポート (NNBI Model)")
    if st.button("← 入力画面へ戻る"):
        st.session_state['page'] = 'input'
        st.session_state['input_step'] = 1 # 最初からやり直す場合
        st.session_state['uploaded_file'] = None
        st.rerun()
    st.divider()

    # --- 1. 今回の食事データ詳細 (編集・確認) ---
    st.header("1. 今回の食事データ詳細")
    
    col_img, col_data = st.columns([1, 2], gap="large")
    
    with col_img:
        if st.session_state['uploaded_file']:
            st.image(st.session_state['uploaded_file'], caption="解析画像", width=250)
    
    with col_data:
        st.subheader("解析データ編集")
        st.info("食材や分量が異なる場合は修正してください。下の栄養素とスコアに即座に反映されます。")
        edited_df = st.data_editor(
            st.session_state['ingredients_df'],
            num_rows="dynamic",
            use_container_width=True,
            key="ingredient_editor"
        )
        if not edited_df.equals(st.session_state['ingredients_df']):
            st.session_state['ingredients_df'] = edited_df
            st.rerun()

    nutrients = calculate_total_nutrients(st.session_state['ingredients_df'])

    st.subheader("詳細栄養バランスとメンタルヘルス解説")
    n_col1, n_col2, n_col3 = st.columns(3)
    
    with n_col1:
        st.markdown("**基本栄養素 & PFC**")
        st.plotly_chart(draw_pfc_balance(nutrients['protein'], nutrients['fat'], nutrients['carbs']), use_container_width=True)
        st.write(f"**🥩 タンパク質**: {nutrients['protein']} g")
        st.write(f"**🍚 糖質**: {nutrients['carbs']} g")
        st.write(f"**💧 脂質**: {nutrients['fat']} g")

    with n_col2:
        st.markdown("**食物繊維 & ビタミン**")
        st.write(f"**🥬 食物繊維**: 水 {nutrients['fiber_sol']}g / 不 {nutrients['fiber_insol']}g")
        st.divider()
        st.write(f"**💊 ビタミンB1**: {nutrients['vit_b1']} mg")
        st.write(f"**🍋 ビタミンC**: {nutrients['vit_c']} mg")
        st.write(f"**☀️ ビタミンD**: {nutrients['vit_d']} μg")

    with n_col3:
        st.markdown("**ミネラル**")
        st.write(f"**🔩 鉄分**: {nutrients['iron']} mg")
        st.write(f"**🛡️ 亜鉛**: **{nutrients['zinc']} mg**")
        st.write(f"**🔋 マグネシウム**: **{nutrients['magnesium']} mg**")

    st.divider()

    # --- 2. メンタルヘルス総合スコア ---
    st.header("2. メンタルヘルス総合スコア (NNBI)")

    constitution = predict_constitution(st.session_state['habit_answers'])
    final_score, score_breakdown = calculate_comprehensive_score(
        st.session_state['habit_answers'],
        st.session_state['user_profile'],
        nutrients,
        constitution
    )

    col_gauge, col_desc = st.columns([1, 1.5])
    with col_gauge:
        st.plotly_chart(draw_score_gauge(final_score), use_container_width=True)
    with col_desc:
        st.markdown(f"### あなたの体質タイプ: **{constitution['type']}**")
        st.info(constitution['desc'])
        st.write("20項目のアンケートと食事内容から総合的に算出されました。")

    st.subheader("NNBIスコア算出の内訳")
    
    # 4列レイアウトに変更
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)

    with b_col1:
        st.markdown("#### $X_{diet}$ 食事質")
        st.metric("Weight: 35%", f"{score_breakdown['diet']['score']}")
        st.caption("野菜・魚・油などの食事パターン")
        for r in score_breakdown['diet']['reasons']:
            st.write(r)

    with b_col2:
        st.markdown("#### $X_{bio}$ 腸内環境")
        st.metric("Weight: 25%", f"{score_breakdown['bio']['score']}")
        st.caption("食物繊維・発酵食品・腸脳相関")
        for r in score_breakdown['bio']['reasons']:
            st.write(r)

    with b_col3:
        st.markdown("#### $X_{dop}$ 脳内物質")
        st.metric("Weight: 20%", f"{score_breakdown['dop']['score']}")
        st.caption("タンパク質・ミネラル・神経伝達")
        for r in score_breakdown['dop']['reasons']:
            st.write(r)

    with b_col4:
        st.markdown("#### $X_{risk}$ リスク")
        st.metric("Weight: -20%", f"{score_breakdown['risk']['score']}")
        st.caption("炎症・糖質・ストレス負荷")
        for r in score_breakdown['risk']['reasons']:
            st.write(r)

    # 数式の表示更新
    st.success(f"""
    **最終スコア算出式 (NNBI Model):**
    $$ M = 20(Base) + 0.35({score_breakdown['diet']['score']}) + 0.25({score_breakdown['bio']['score']}) + 0.20({score_breakdown['dop']['score']}) - 0.20({score_breakdown['risk']['score']}) $$
    $$ \\approx \mathbf{{ {final_score} 点 }} $$
    """)

# --- メインルーティング ---

if st.session_state['page'] == 'input':
    page_input_screen()
elif st.session_state['page'] == 'result':
    page_result_screen()

# フッター
st.markdown("---")
with st.expander("▼ 研究背景と数理モデル (NNBIの理論構成)"):
    st.markdown(r"""
    ### ・ 変数の抽出と定義

    #### A. ポジティブ因子

    * $X_{fv}$: 果物・野菜の摂取量
    * $X_{wg}$: 全粒穀物の摂取量
    * $X_{nut}$: ナッツ・種子類の摂取量
    * $X_{fish}$: 魚（オメガ3脂肪酸）の摂取量
    * $X_{cop}$: 腸内細菌 *Coprococcus* 属の保有量/活性度
    * $X_{dia}$: 腸内細菌 *Dialister* 属の保有量/活性度
    * $X_{dop}$: ドーパミン代謝物の合成能

    #### B. ネガティブ因子

    * $X_{proc}$: 加工肉・赤肉の摂取量
    * $X_{ref}$: 精製穀物（白米・パン等）の摂取量
    * $X_{sug}$: 菓子・甘い飲み物の摂取量
    * $X_{dys}$: ディスバイオシス（腸内環境の乱れ）指数

    ---

    ### ※ 変数定義
    
    **A. ポジティブ変数 ($+$スコア)**
    $X_{diet}$ : **良質な食事** (野菜・全粒穀物・魚・オリーブ油など / SMILES試験を基準に採用)
    $X_{bio}$ : **有用な腸内細菌** (*Coprococcus*・*Dialister*活性度 / 腸脳相関)
    $X_{dop}$ : **ドーパミン合成能** (タンパク質・鉄・ビタミンB群 / 神経伝達物質原料)

    **B. ネガティブ変数 ($-$スコア)**
    $X_{risk}$ : **リスク因子** (加工肉・砂糖・超加工食品 / 炎症性サイトカイン誘発)

    ---

    ### ※ 重み付けの理論式 (実装済)
    各要素がメンタルヘルスに与える影響度を係数として定義。

    $$
    \text{NNBI} = \underbrace{0.35 \cdot X_{diet}}_{\text{食事パターン(35\%٪)}} + \underbrace{0.25 \cdot X_{bio}}_{\text{腸内環境(25\%٪)}} + \underbrace{0.20 \cdot X_{dop}}_{\text{ドーパミン(20\%٪)}} - \underbrace{0.20 \cdot X_{risk}}_{\text{リスク因子(20\%٪)}} + \alpha
    $$
    """)

st.caption("Developed for Nakazawa Okoshi Laboratory / WellComp B2 Research Demo")