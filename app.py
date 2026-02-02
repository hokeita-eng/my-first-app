import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
import plotly.graph_objects as go

# --- 初期設定 ---
st.set_page_config(
    page_title="メンタルヘルス食習慣スコア Extended",
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

# --- ロジック: スコア算出 (20問対応版) ---

def calculate_comprehensive_score(habit_answers, user_profile, nutrients, constitution_type):
    
    breakdown = {
        "habit": {"score": 0, "reasons": []},
        "risk": {"score": 100, "reasons": []}, 
        "indicator": {"score": 0, "reasons": []}
    }

    # --- 1. 食習慣アンケート (Habit Score) ---
    # 20問あるため、配点バランスを調整
    h_score = 0
    
    # === 基本10問 (Core Habits) ===
    # 1. グルテン
    ans_gl = habit_answers.get("gluten")
    if ans_gl == "週1回未満": h_score += 5
    elif ans_gl == "ほぼ毎日": h_score -= 3

    # 2. タンパク質
    ans_p = habit_answers.get("protein")
    if ans_p == "毎食摂取": h_score += 5
    elif ans_p == "1日1食": h_score += 1

    # 3. 食物繊維
    ans_f = habit_answers.get("fiber")
    if ans_f == "1日3皿分以上": h_score += 5
    elif ans_f == "1日1皿分": h_score += 2

    # 4. 糖質
    ans_cb = habit_answers.get("carbs")
    if ans_cb == "適量(茶碗1杯/食)": h_score += 5
    elif ans_cb == "過剰(菓子パン等含む)": h_score -= 5

    # 5. 魚全般
    ans_fish = habit_answers.get("fish")
    if ans_fish == "週3回以上": h_score += 5
    elif ans_fish == "週1-2回": h_score += 3

    # 6. 鶏肉
    ans_ck = habit_answers.get("chicken")
    if ans_ck == "週3回以上": h_score += 5
    elif ans_ck == "週1-2回": h_score += 3

    # 7. ファストフード
    ans_ff = habit_answers.get("fastfood")
    if ans_ff == "月1回未満": h_score += 5
    elif ans_ff == "週3回以上": h_score -= 5

    # 8. 加工肉
    ans_pm = habit_answers.get("processed_meat")
    if ans_pm == "週1回未満": h_score += 5
    elif ans_pm == "ほぼ毎日": h_score -= 5

    # 9. 発酵食品
    ans_fem = habit_answers.get("fermented")
    if ans_fem == "ほぼ毎日": h_score += 5
    elif ans_fem == "週3-4回": h_score += 3

    # 10. 青魚
    ans_bf = habit_answers.get("bluefish")
    if ans_bf == "週2回以上": h_score += 5
    elif ans_bf == "週1回": h_score += 3

    # === 追加10問 (Lifestyle & Mental Habits) ===
    
    # 11. 水分摂取
    ans_w = habit_answers.get("water")
    if ans_w == "1.5L以上": h_score += 5
    elif ans_w == "1.0L未満": h_score -= 2
    
    # 12. カフェイン
    ans_cf = habit_answers.get("caffeine")
    if ans_cf == "1日1-2杯": h_score += 3
    elif ans_cf == "1日5杯以上": h_score -= 5
    
    # 13. アルコール
    ans_al = habit_answers.get("alcohol")
    if ans_al == "飲まない": h_score += 5
    elif ans_al == "ほぼ毎日": h_score -= 5
    
    # 14. 食べる速さ
    ans_sp = habit_answers.get("eat_speed")
    if ans_sp == "ゆっくり(20分以上)": h_score += 5
    elif ans_sp == "早い(10分未満)": h_score -= 3
    
    # 15. 朝食
    ans_br = habit_answers.get("breakfast")
    if ans_br == "毎日食べる": h_score += 5
    elif ans_br == "食べない": h_score -= 3
    
    # 16. 夜遅くの食事
    ans_ln = habit_answers.get("late_night")
    if ans_ln == "寝る3時間前まで": h_score += 5
    elif ans_ln == "寝る直前が多い": h_score -= 5
    
    # 17. 野菜の種類
    ans_vv = habit_answers.get("veg_variety")
    if ans_vv == "5種類以上": h_score += 5
    elif ans_vv == "ほぼ食べない": h_score -= 3

    # 18. 乳製品
    ans_dr = habit_answers.get("dairy")
    if ans_dr == "適度(1日1杯/個)": h_score += 3
    elif ans_dr == "過剰に摂る": h_score -= 2

    # 19. おやつ・間食
    ans_sn = habit_answers.get("snack")
    if ans_sn == "ほとんど食べない": h_score += 5
    elif ans_sn == "毎日甘いもの": h_score -= 5

    # 20. 油の質
    ans_oil = habit_answers.get("oil")
    if ans_oil == "オリーブ/アマニ油中心": h_score += 5
    elif ans_oil == "揚げ物が多い": h_score -= 5

    # 合計調整 (満点100に正規化)
    # 理論上の最大値は約100、最小値はマイナスになりうるのでクリッピング
    h_score = max(0, min(h_score, 100))
    breakdown["habit"]["score"] = h_score
    breakdown["habit"]["reasons"].append(f"・20項目の食習慣・生活習慣アンケート回答: {h_score}点")

    # --- 2. 個別リスク因子 (Risk Score) ---
    r_score = 100
    risk_log = []
    
    stress_level = user_profile.get("stress_level", "Low")
    allergies = user_profile.get("allergies", [])
    supplements = user_profile.get("supplements", [])
    
    # ストレス負荷
    if stress_level == "High":
        r_score -= 20
        risk_log.append("・高ストレス状態によるコルチゾール過多 (-20)")
    elif stress_level == "Medium":
        r_score -= 10
        risk_log.append("・中程度のストレス負荷 (-10)")
        
    # アレルギー整合性
    if "グルテン" in allergies and habit_answers.get("gluten") in ["週3-5回", "ほぼ毎日"]:
        r_score -= 20
        risk_log.append("・グルテン不耐性ありかつ高頻度摂取 (-20)")
    elif allergies:
         r_score -= 10
         risk_log.append(f"・アレルギー因子保持 (-10)")

    # 既往歴
    if user_profile.get("medical_history"):
        r_score -= 15
        risk_log.append("・既往歴による代謝負荷リスク (-15)")

    # サプリメント
    if not supplements:
        r_score -= 5
        risk_log.append("・サプリメント補助なし (-5)")
    else:
        if "ビタミンD" in supplements and "亜鉛" in supplements:
            r_score += 15
            risk_log.append("・VitD+亜鉛の抗ストレス相乗効果 (+15)")
        else:
            r_score += 5
            risk_log.append("・サプリメントによる補助 (+5)")

    r_score = max(0, min(r_score, 100))
    breakdown["risk"]["score"] = r_score
    breakdown["risk"]["reasons"] = risk_log

    # --- 3. 個別推定指標 (Indicator Score) ---
    i_score = 0
    ind_log = []
    
    p = nutrients['protein']
    c = nutrients['carbs']
    fiber = nutrients['fiber_sol'] + nutrients['fiber_insol']
    minerals = nutrients['zinc'] + nutrients['magnesium'] + nutrients['iron']
    vitamins = nutrients['vit_b1'] + nutrients['vit_c']
    cal = nutrients['calories']

    # NT-Index
    nt_index = (p * 1.0) + (minerals * 2.0) + (vitamins * 0.5)
    if nt_index > 40:
        i_score += 40
        ind_log.append(f"・NT-Index(神経伝達物質生成能) 高水準 (+40)")
    elif nt_index > 20:
        i_score += 20
        ind_log.append(f"・NT-Index(神経伝達物質生成能) 標準 (+20)")
    else:
        i_score += 5
        ind_log.append(f"・NT-Index(神経伝達物質生成能) 低水準 (+5)")

    # 炎症ポテンシャル
    inflam_score = c / (fiber + 1.0)
    c_type = constitution_type['type']
    
    if c_type == "糖質依存・血糖値スパイク型":
        if inflam_score > 10:
            i_score -= 20
            ind_log.append("・体質に対し糖質比率が高く危険 (-20)")
        else:
            i_score += 20
            ind_log.append("・体質に適した低糖質食 (+20)")
    elif c_type == "慢性炎症・内臓疲労型":
        if fiber < 5.0:
            i_score -= 15
            ind_log.append("・抗炎症成分(繊維)不足 (-15)")
        else:
            i_score += 15
            ind_log.append("・十分な繊維量 (+15)")
    elif c_type == "タンパク質不足・エネルギー欠乏型":
        if p < 20.0:
            i_score -= 20
            ind_log.append("・タンパク質絶対量不足 (-20)")
        else:
            i_score += 20
            ind_log.append("・必要タンパク質確保 (+20)")
    else:
        if 500 < cal < 900:
             i_score += 10
             ind_log.append("・適正カロリー (+10)")

    # ミネラルボーナス
    if (nutrients['zinc'] + nutrients['magnesium']) > 10:
        i_score += 10
        ind_log.append("・抗ストレスミネラル充足 (+10)")
    
    i_score = max(0, min(i_score, 100))
    breakdown["indicator"]["score"] = i_score
    breakdown["indicator"]["reasons"] = ind_log

    final_score = int(h_score * 0.4 + r_score * 0.2 + i_score * 0.4)
    return final_score, breakdown

def predict_constitution(answers):
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

# --- ページ定義: 入力画面 (Page 1: 分割ステップ) ---

def page_input_screen():
    st.title("メンタルヘルス食習慣チェッカー")
    
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
                    # 回答を保存
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

            col_prev, col_next = st.columns([1, 1])
            with col_prev:
                # 戻るボタン機能（stateを戻すだけだがform内では使いにくいので、基本は次へを推奨）
                pass 
            with col_next:
                submitted_2 = st.form_submit_button("次へ (画像アップロードへ)", type="primary")
            
            if submitted_2:
                required = [q_water, q_caffeine, q_alcohol, q_eat_speed, q_breakfast, q_late_night, q_veg_variety, q_dairy, q_snack, q_oil]
                if any(x is None for x in required):
                    st.error("すべての項目に回答してください。")
                else:
                    # 回答を保存
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
    st.title("分析結果レポート")
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
        st.write("20項目のアンケートと食事内容から総合的に算出されました。")

    st.subheader("スコア算出の内訳")
    
    b_col1, b_col2, b_col3 = st.columns(3)

    with b_col1:
        st.markdown("#### A. 食習慣アンケート")
        st.metric("基礎スコア", f"{score_breakdown['habit']['score']} / 100")
        with st.container(height=300):
            st.caption("20問の回答に基づく基礎点です。")
            for r in score_breakdown['habit']['reasons']:
                st.write(r)

    with b_col2:
        st.markdown("#### B. 個別リスク因子")
        st.metric("調整スコア", f"{score_breakdown['risk']['score']} / 100")
        with st.container(height=300):
            st.caption("ストレス、アレルギー、サプリメントの状況による調整です。")
            for r in score_breakdown['risk']['reasons']:
                st.write(r)

    with b_col3:
        st.markdown("#### C. 個別推定指標")
        st.metric("食事適合スコア", f"{score_breakdown['indicator']['score']} / 100")
        with st.container(height=300):
            st.caption("今回の食事が、体質や神経伝達物質生成(NT-Index)に適切かを判定。")
            for r in score_breakdown['indicator']['reasons']:
                st.write(r)

    st.success(f"**最終スコア算出式 (Demo):** (習慣 {score_breakdown['habit']['score']}×0.4) + (リスク {score_breakdown['risk']['score']}×0.2) + (食事指標 {score_breakdown['indicator']['score']}×0.4) ≒ **{final_score}点**")

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

    #### ・プロトタイプ
    メンタルヘルススコアを $M$ としたとき、モデルは以下のような式を学習して導き出す。

    $$ M = \alpha + \sum_{i=1}^{n} w_i \cdot X_{i_{pos}} - \sum_{j=1}^{m} w_j \cdot X_{j_{neg}} + \epsilon $$

    ここで：
    * $w$（重み係数）：AIがデータから学習する「各要素の重要度」。例えば「野菜」がメンタルに与える影響が大きければ、$w$ の値は大きくなる。
    * $\alpha$（切片）：ベースラインのメンタルヘルス値。
    * $\epsilon$（誤差項）：個人差などのノイズ。

    #### 複合処理（マルチモーダル学習）に関する計算式
    腸脳相関から、単純な足し算だけでなく、相互作用項を入れることで、より精度の高いモデルを目指す。

    $$ M_{complex} = w_1 X_{diet} + w_2 X_{microbiome} + w_3 (X_{diet} \times X_{microbiome}) $$

    > **解説:** $w_3$ の項は、良い食事を摂り、かつ良い腸内細菌がいるとき、相乗効果でメンタルがさらに良くなるという現象をモデル化したもの。

    ---
    ### ※ 変数定義
    
    **A. ポジティブ変数 ($+$スコア)**
    $X_{diet}$ : **良質な食事** (野菜・全粒穀物・魚・オリーブ油など / SMILES試験を基準に採用)
    $X_{bio}$ : **有用な腸内細菌** (*Coprococcus*・*Dialister*活性度 / 腸脳相関)
    $X_{dop}$ : **ドーパミン合成能** (タンパク質・鉄・ビタミンB群 / 神経伝達物質原料)

    **B. ネガティブ変数 ($-$スコア)**
    $X_{risk}$ : **リスク因子** (加工肉・砂糖・超加工食品 / 炎症性サイトカイン誘発)

    ---

    ### ※ 重み付けの理論式
    各要素がメンタルヘルスに与える影響度を係数として定義。

    $$
    \text{NNBI} = \underbrace{0.35 \cdot X_{diet}}_{\text{食事パターン(35\%٪)}} + \underbrace{0.25 \cdot X_{bio}}_{\text{腸内環境(25\%٪)}} + \underbrace{0.20 \cdot X_{dop}}_{\text{ドーパミン(20\%٪)}} - \underbrace{0.20 \cdot X_{risk}}_{\text{リスク因子(20\%٪)}}
    $$

    ---

    ### ※ 指標

    $$
    M_{pred} = \alpha + \sum w_i X_i + \epsilon
    $$

    """)

st.caption("Developed for Nakazawa Okoshi Laboratory / WellComp B2 Research Demo")