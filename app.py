import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
import plotly.graph_objects as go

# --- 初期設定 ---
st.set_page_config(
    page_title="メンタルヘルス食習慣スコア",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- セッション状態の初期化 ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'input'
if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None
if 'ingredients_df' not in st.session_state:
    st.session_state['ingredients_df'] = None
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = {}
if 'habit_answers' not in st.session_state:
    st.session_state['habit_answers'] = {}

# --- API連携 & 画像解析ロジック ---

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

# --- ロジック: 3つの要素による総合スコア算出 (複雑化・絵文字削除) ---

def calculate_comprehensive_score(habit_answers, user_profile, nutrients, constitution_type):
    
    breakdown = {
        "habit": {"score": 0, "reasons": []},
        "risk": {"score": 100, "reasons": []}, 
        "indicator": {"score": 0, "reasons": []}
    }

    # --- 1. 食習慣アンケート (Habit Score) ---
    h_score = 0
    # 単純加算ロジック
    ans_p = habit_answers.get("protein")
    if ans_p == "毎食摂取": h_score += 10
    elif ans_p == "1日2食": h_score += 6
    elif ans_p == "1日1食": h_score += 3
    
    ans_f = habit_answers.get("fiber")
    if ans_f == "1日3皿分以上": h_score += 10
    elif ans_f == "1日2皿分": h_score += 6
    elif ans_f == "1日1皿分": h_score += 3

    ans_fish = habit_answers.get("fish")
    if ans_fish == "週3回以上": h_score += 10
    elif ans_fish == "週1-2回": h_score += 5
    elif ans_fish == "月1-3回": h_score += 3

    ans_ck = habit_answers.get("chicken")
    if ans_ck == "週3回以上": h_score += 10
    elif ans_ck == "週1-2回": h_score += 5
    elif ans_ck == "月1-3回": h_score += 3

    ans_fem = habit_answers.get("fermented")
    if ans_fem == "ほぼ毎日": h_score += 10
    elif ans_fem == "週3-4回": h_score += 6
    elif ans_fem == "週1-2回": h_score += 3

    ans_bf = habit_answers.get("bluefish")
    if ans_bf == "週2回以上": h_score += 10
    elif ans_bf == "週1回": h_score += 5
    elif ans_bf == "月1-3回": h_score += 3

    ans_gl = habit_answers.get("gluten")
    if ans_gl == "週1回未満": h_score += 10
    elif ans_gl == "週1-2回": h_score += 5
    elif ans_gl == "ほぼ毎日": h_score -= 5

    ans_cb = habit_answers.get("carbs")
    if ans_cb == "適量(茶碗1杯/食)": h_score += 10
    elif ans_cb == "多い(毎日大盛り)": h_score -= 5
    elif ans_cb == "過剰(菓子パン等含む)": h_score -= 10

    ans_ff = habit_answers.get("fastfood")
    if ans_ff == "月1回未満": h_score += 10
    elif ans_ff == "月2-3回": h_score += 5
    elif ans_ff == "週1-2回": h_score -= 5
    elif ans_ff == "週3回以上": h_score -= 10

    ans_pm = habit_answers.get("processed_meat")
    if ans_pm == "週1回未満": h_score += 10
    elif ans_pm == "週1-2回": h_score += 5
    elif ans_pm == "週3-5回": h_score -= 5
    elif ans_pm == "ほぼ毎日": h_score -= 10
    
    h_score = max(0, min(h_score, 100))
    breakdown["habit"]["score"] = h_score
    breakdown["habit"]["reasons"].append(f"・食習慣アンケート回答に基づく基礎算出点: {h_score}点")

    # --- 2. 個別リスク因子 (Complex Risk Factors) ---
    # 基準点100点からの減点・調整方式
    # [複雑化] ストレスレベル、アレルギー整合性、サプリメントの相乗効果を考慮
    
    r_score = 100
    risk_log = []
    
    stress_level = user_profile.get("stress_level", "Low")
    allergies = user_profile.get("allergies", [])
    supplements = user_profile.get("supplements", [])
    
    # (1) ストレス負荷係数
    stress_penalty = 0
    if stress_level == "High":
        stress_penalty = 20
        risk_log.append("・高ストレス状態によるコルチゾール分泌過多リスク (-20)")
    elif stress_level == "Medium":
        stress_penalty = 10
        risk_log.append("・中程度のストレス負荷による栄養消費増大リスク (-10)")
        
    # (2) アレルギー・コンプライアンス（整合性）チェック
    # アレルギーがあるのに、食習慣でその項目を頻繁に摂取している場合は重ペナルティ
    allergy_penalty = 0
    if "グルテン" in allergies:
        if habit_answers.get("gluten") in ["週3-5回", "ほぼ毎日"]:
            allergy_penalty += 20
            risk_log.append("・グルテン不耐性ありかつ高頻度摂取による腸内炎症リスク大 (-20)")
        else:
            risk_log.append("・グルテン除去意識によるリスク管理 (±0)")
    elif allergies:
         allergy_penalty += 10
         risk_log.append(f"・アレルギー因子保持による潜在的リスク (-10)")

    # (3) 既往歴リスク
    history = user_profile.get("medical_history", "")
    history_penalty = 0
    if history:
        history_penalty = 15
        risk_log.append(f"・既往歴({history})による代謝負荷リスク (-15)")

    # (4) サプリメント相乗効果・緩和効果
    supp_bonus = 0
    if not supplements:
        supp_bonus = -5
        risk_log.append("・サプリメントによる栄養補助なし (-5)")
    else:
        base_bonus = 5
        # シナジーボーナス: ビタミンD + 亜鉛 or マグネシウム（メンタルヘルス防御セット）
        # ※ デモデータではサプリ選択肢に亜鉛がある
        if "ビタミンD" in supplements and "亜鉛" in supplements:
            base_bonus += 10
            risk_log.append("・ビタミンDと亜鉛の同時摂取による抗ストレス相乗効果 (+15)")
        else:
            risk_log.append(f"・サプリメント摂取による栄養底上げ効果 (+{base_bonus})")
        supp_bonus = base_bonus

    # リスクスコア計算
    r_score = 100 - stress_penalty - allergy_penalty - history_penalty + supp_bonus
    
    # ストレスが高くサプリがない場合、さらにペナルティ（消耗激しいのに補給なし）
    if stress_level == "High" and not supplements:
        r_score -= 10
        risk_log.append("・高ストレス下での微量栄養素枯渇リスク（サプリなし） (-10)")

    r_score = max(0, min(r_score, 100))
    breakdown["risk"]["score"] = r_score
    breakdown["risk"]["reasons"] = risk_log

    # --- 3. 個別推定指標 (Complex Estimated Indicators) ---
    # 今回の食事内容が、体質や現在の状態に対して「機能的」かどうかを判定
    # [複雑化] 単純なPFCだけでなく、「神経伝達物質生成指数」と「炎症ポテンシャル」を推定
    
    i_score = 0
    ind_log = []
    
    # データ準備
    p = nutrients['protein']
    f_total = nutrients['fat'] # 飽和脂肪酸等は簡易計算で使用
    c = nutrients['carbs']
    fiber = nutrients['fiber_sol'] + nutrients['fiber_insol']
    minerals = nutrients['zinc'] + nutrients['magnesium'] + nutrients['iron']
    vitamins = nutrients['vit_b1'] + nutrients['vit_c']
    cal = nutrients['calories']

    # (1) 神経伝達物質生成指数 (NT-Index: Neuro-Transmitter Index)
    # メンタル安定にはタンパク質(アミノ酸)とビタミンB群、鉄、亜鉛が必須
    # 簡易スコア: (タンパク質 * 1 + ミネラル合計 * 2 + ビタミン合計 * 0.5)
    nt_index = (p * 1.0) + (minerals * 2.0) + (vitamins * 0.5)
    
    nt_threshold = 40 # 閾値（仮）
    if nt_index > nt_threshold:
        i_score += 40
        ind_log.append(f"・NT-Index(神経伝達物質生成能)が高水準: {int(nt_index)} (基準{nt_threshold}) (+40)")
    elif nt_index > 20:
        i_score += 20
        ind_log.append(f"・NT-Index(神経伝達物質生成能)が標準レベル: {int(nt_index)} (+20)")
    else:
        i_score += 5
        ind_log.append(f"・NT-Index(神経伝達物質生成能)が低水準: {int(nt_index)} (+5)")

    # (2) 炎症ポテンシャル (Inflammation Potential)
    # 糖質過多かつ食物繊維不足は炎症リスク大
    # 式: (糖質 / (食物繊維 + 1)) * 係数
    inflam_score = c / (fiber + 1.0)
    
    # 体質による分岐
    c_type = constitution_type['type']
    
    if c_type == "糖質依存・血糖値スパイク型":
        # 厳しく判定
        if inflam_score > 10:
            i_score -= 20
            ind_log.append("・体質に対し糖質比率が高く、血糖値スパイクの危険性大 (-20)")
        else:
            i_score += 20
            ind_log.append("・易血糖変動型体質に適した低糖質・高繊維な食事内容 (+20)")
    elif c_type == "慢性炎症・内臓疲労型":
        if fiber < 5.0:
            i_score -= 15
            ind_log.append("・炎症体質に対し抗炎症成分(食物繊維)が不足 (-15)")
        else:
            i_score += 15
            ind_log.append("・腸内ケアに必要な食物繊維量が確保されている (+15)")
    elif c_type == "タンパク質不足・エネルギー欠乏型":
        if p < 20.0:
            i_score -= 20
            ind_log.append("・欠乏型体質に対しタンパク質絶対量が不足 (-20)")
        else:
            i_score += 20
            ind_log.append("・必要量のタンパク質が供給され、意欲回復に寄与 (+20)")
    else:
        # バランス型
        if 500 < cal < 900:
             i_score += 10
             ind_log.append("・適正なエネルギーバランス (+10)")
        else:
             ind_log.append("・エネルギーバランスの乱れ (±0)")

    # (3) ミクロ栄養素ボーナス
    # 亜鉛とマグネシウムが十分(合計10mg以上)なら加点
    if (nutrients['zinc'] + nutrients['magnesium']) > 10:
        i_score += 10
        ind_log.append("・抗ストレスミネラル(Zn, Mg)の充足 (+10)")
    
    # ビタミンCボーナス（ストレスレベルHighの場合に重要）
    if stress_level == "High" and nutrients['vit_c'] > 20:
        i_score += 10
        ind_log.append("・高ストレス時に必要なビタミンCの供給 (+10)")

    i_score = max(0, min(i_score, 100))
    breakdown["indicator"]["score"] = i_score
    breakdown["indicator"]["reasons"] = ind_log

    # 総合スコア
    final_score = int(h_score * 0.4 + r_score * 0.2 + i_score * 0.4)
    
    return final_score, breakdown

def predict_constitution(answers):
    """食習慣から体質タイプを推定する(4択対応版)"""
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
        title = {'text': "総合メンタルスコア"},
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

# --- ページ定義: 入力画面 (Page 1) ---

def page_input_screen():
    st.title("メンタルヘルス食習慣チェッカー")
    st.markdown("### Step 1: 食習慣アンケートと食事画像の入力")

    with st.expander("▶ 開発者オプション: LogMeal API設定"):
        api_token = st.text_input("LogMeal API Token (空欄の場合はデモモード)", type="password")

    col1, col2 = st.columns([1, 1.2], gap="medium")
    
    with col1:
        st.subheader("📷 直近の食事画像")
        uploaded_file = st.file_uploader("写真を選択", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            st.image(uploaded_file, width=300)
    
    with col2:
        st.subheader("📝 食習慣チェック (4択)")
        with st.form("habit_form"):
            st.markdown("##### ① 加点項目 (積極摂取)")
            
            q_prot = st.radio("2. タンパク質摂取", 
                              ["毎食摂取", "1日2食", "1日1食", "それ以下"], 
                              horizontal=True, index=None)
            
            q_fiber = st.radio("3. 食物繊維(野菜)", 
                               ["1日3皿分以上", "1日2皿分", "1日1皿分", "それ以下"], 
                               horizontal=True, index=None)
            
            q_fish = st.radio("5. 魚全般", 
                              ["週3回以上", "週1-2回", "月1-3回", "ほとんど食べない"], 
                              horizontal=True, index=None)
            
            q_chicken = st.radio("6. 鶏肉", 
                                 ["週3回以上", "週1-2回", "月1-3回", "ほとんど食べない"], 
                                 horizontal=True, index=None)
            
            q_fermented = st.radio("9. 納豆・キムチ", 
                                   ["ほぼ毎日", "週3-4回", "週1-2回", "それ以下"], 
                                   horizontal=True, index=None)
            
            q_bluefish = st.radio("10. 青魚(Omega-3)", 
                                  ["週2回以上", "週1回", "月1-3回", "ほとんど食べない"], 
                                  horizontal=True, index=None)
            
            st.markdown("##### ② 減点・調整項目 (リスク管理)")
            
            q_gluten = st.radio("1. グルテン(小麦)", 
                                ["週1回未満", "週1-2回", "週3-5回", "ほぼ毎日"], 
                                horizontal=True, index=None)
            
            q_carbs = st.radio("4. 糖質(ご飯・パン等)", 
                               ["適量(茶碗1杯/食)", "やや多い(時々大盛り)", "多い(毎日大盛り)", "過剰(菓子パン等含む)"], 
                               horizontal=True, index=None)
            
            q_fastfood = st.radio("7. ファストフード", 
                                  ["月1回未満", "月2-3回", "週1-2回", "週3回以上"], 
                                  horizontal=True, index=None)
            
            q_procmeat = st.radio("8. 加工肉(ハム等)", 
                                  ["週1回未満", "週1-2回", "週3-5回", "ほぼ毎日"], 
                                  horizontal=True, index=None)

            st.markdown("---")
            st.markdown("**👤 プロフィール・体質情報**")
            
            # ストレスレベル入力の復活
            stress_level = st.select_slider("直近のストレスレベル", options=["Low", "Medium", "High"])

            selected_allergies = st.multiselect(
                "アレルギー・除去対象",
                options=["グルテン", "カゼイン", "卵", "乳製品", "そば", "落花生", "えび", "かに"],
                default=[]
            )
            medical_history = st.text_input("既往歴 (任意)", placeholder="例: 糖尿病、高血圧、貧血など")
            selected_supplements = st.multiselect(
                "サプリメント摂取状況 (任意)",
                options=["ビタミンD", "亜鉛", "ケルセチン", "乳酸菌"],
                default=[]
            )

            submit_button = st.form_submit_button("分析を開始する ✨", type="primary")

            if submit_button:
                required_fields = [q_prot, q_fiber, q_fish, q_chicken, q_fermented, q_bluefish, q_gluten, q_carbs, q_fastfood, q_procmeat]
                
                if any(x is None for x in required_fields):
                    st.error("⚠️ 食習慣チェックのすべての項目に回答してください。")
                elif uploaded_file is None:
                    st.error("⚠️ 食事の画像をアップロードしてください。")
                else:
                    st.session_state['uploaded_file'] = uploaded_file
                    st.session_state['habit_answers'] = {
                        "protein": q_prot, "fiber": q_fiber, "fish": q_fish,
                        "chicken": q_chicken, "fermented": q_fermented, "bluefish": q_bluefish,
                        "gluten": q_gluten, "carbs": q_carbs, "fastfood": q_fastfood,
                        "processed_meat": q_procmeat
                    }
                    st.session_state['user_profile'] = {
                        "stress_level": stress_level,
                        "allergies": selected_allergies,
                        "medical_history": medical_history,
                        "supplements": selected_supplements
                    }
                    st.session_state['ingredients_df'] = analyze_image(uploaded_file, api_token)
                    st.session_state['page'] = 'result'
                    st.rerun()

# --- ページ定義: 結果画面 (Page 2) ---

def page_result_screen():
    st.title("分析結果レポート")
    if st.button("← 入力画面へ戻る"):
        st.session_state['page'] = 'input'
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
        st.subheader("🛠️ 解析データ編集")
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

    st.subheader("📊 詳細栄養バランスとメンタルヘルス解説")
    n_col1, n_col2, n_col3 = st.columns(3)
    
    with n_col1:
        st.markdown("**基本栄養素 & PFC**")
        st.plotly_chart(draw_pfc_balance(nutrients['protein'], nutrients['fat'], nutrients['carbs']), use_container_width=True)
        
        st.write(f"**🥩 タンパク質**: {nutrients['protein']} g")
        st.caption("セロトニンやドーパミンなど、メンタルを安定させる神経伝達物質の材料です。不足すると意欲低下に繋がります。")
        
        st.write(f"**🍚 糖質**: {nutrients['carbs']} g")
        st.caption("脳のエネルギー源ですが、急激な変動（スパイク）はイライラや眠気の原因になります。")
        
        st.write(f"**💧 脂質**: {nutrients['fat']} g")
        st.caption("脳の構成成分の約60%は脂質です。良質な脂質は脳細胞膜の働きを助けます。")

    with n_col2:
        st.markdown("**食物繊維 & ビタミン**")
        
        st.write(f"**🥬 食物繊維**: 水溶性 {nutrients['fiber_sol']}g / 不溶性 {nutrients['fiber_insol']}g")
        st.caption("「脳腸相関」により、腸内環境を整えることはメンタルの安定に直結します。")
        
        st.divider()
        
        st.write(f"**💊 ビタミンB1**: {nutrients['vit_b1']} mg")
        st.caption("糖質をエネルギーに変えるのに必須。不足するとイライラや疲労感が出やすくなります。")
        
        st.write(f"**🍋 ビタミンC**: {nutrients['vit_c']} mg")
        st.caption("抗ストレスホルモンの合成に大量に消費されます。ストレス対策に必須です。")
        
        st.write(f"**☀️ ビタミンD**: {nutrients['vit_d']} μg")
        st.caption("セロトニンの調節に関わり、不足はうつ症状のリスクを高めると言われています。")

    with n_col3:
        st.markdown("**ミネラル**")
        
        st.write(f"**🔩 鉄分**: {nutrients['iron']} mg")
        st.caption("セロトニンやドーパミンの合成に必要。不足は不安感やうつの原因になります。")
        
        st.write(f"**🛡️ 亜鉛**: **{nutrients['zinc']} mg**")
        st.caption("脳の神経伝達をスムーズにし、ストレス耐性を高めます。")
        
        st.write(f"**🔋 マグネシウム**: **{nutrients['magnesium']} mg**")
        st.caption("神経の興奮を鎮め、リラックス効果や良質な睡眠をサポートします。")

    st.divider()

    # --- 2. メンタルヘルス総合スコア ---
    st.header("2. メンタルヘルス総合スコア")

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
        st.write("このスコアは以下の3つの要素から総合的に算出されました。")

    st.subheader("スコア算出の内訳")
    
    b_col1, b_col2, b_col3 = st.columns(3)

    with b_col1:
        st.markdown("#### A. 食習慣アンケート")
        st.metric("基礎スコア", f"{score_breakdown['habit']['score']} / 100")
        with st.container(height=300):
            st.caption("日頃の食習慣に基づく基礎点です。")
            for r in score_breakdown['habit']['reasons']:
                st.write(r)

    with b_col2:
        st.markdown("#### B. 個別リスク因子")
        st.metric("調整スコア", f"{score_breakdown['risk']['score']} / 100")
        with st.container(height=300):
            st.caption("ストレス、アレルギー整合性、サプリメントの相乗効果など、複数の変数を組み合わせたリスク判定です。")
            for r in score_breakdown['risk']['reasons']:
                st.write(r)

    with b_col3:
        st.markdown("#### C. 個別推定指標")
        st.metric("食事適合スコア", f"{score_breakdown['indicator']['score']} / 100")
        with st.container(height=300):
            st.caption("今回の食事が、体質や神経伝達物質生成(NT-Index)の観点で適切かを判定しています。")
            for r in score_breakdown['indicator']['reasons']:
                st.write(r)

    st.success(f"**最終スコア算出式 (デモ用):** (習慣 {score_breakdown['habit']['score']}×0.4) + (リスク {score_breakdown['risk']['score']}×0.2) + (食事指標 {score_breakdown['indicator']['score']}×0.4) ≒ **{final_score}点**")

# --- メインルーティング ---

if st.session_state['page'] == 'input':
    page_input_screen()
elif st.session_state['page'] == 'result':
    page_result_screen()

# フッター
st.markdown("---")
st.caption("Developed for Jin Nakazawa Laboratory / WellComp B2 Research Demo")
