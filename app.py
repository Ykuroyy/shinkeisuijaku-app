from flask import Flask, render_template, request, jsonify, session
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# カードの種類（可愛いテーマ）
CARDS = [
    '🌸', '🌸',  # 桜
    '🌺', '🌺',  # 花
    '⭐', '⭐',  # 星
    '💖', '💖',  # ハート
    '🎀', '🎀',  # リボン
    '🦄', '🦄',  # ユニコーン
    '🌈', '🌈',  # 虹
    '🍭', '🍭',  # キャンディ
    '🎪', '🎪',  # サーカス
    '🎠', '🎠',  # メリーゴーランド
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new-game')
def new_game():
    """新しいゲームを開始"""
    # カードをシャッフル
    cards = CARDS.copy()
    random.shuffle(cards)
    
    # セッションにゲーム状態を保存
    session['cards'] = cards
    session['flipped'] = [False] * 20
    session['matched'] = [False] * 20
    session['player_score'] = 0
    session['ai_score'] = 0
    session['current_turn'] = 'player'  # 'player' or 'ai'
    session['first_card'] = None
    session['second_card'] = None
    session['player_matched_cards'] = []  # プレイヤーがマッチしたカードのインデックス
    session['ai_matched_cards'] = []      # AIがマッチしたカードのインデックス
    
    return jsonify({
        'cards': cards,
        'flipped': session['flipped'],
        'matched': session['matched'],
        'player_score': session['player_score'],
        'ai_score': session['ai_score'],
        'current_turn': session['current_turn'],
        'player_matched_cards': session['player_matched_cards'],
        'ai_matched_cards': session['ai_matched_cards']
    })

@app.route('/api/flip-card', methods=['POST'])
def flip_card():
    """カードをめくる"""
    data = request.get_json()
    card_index = data.get('card_index')
    
    if session['current_turn'] != 'player':
        return jsonify({'error': 'AIのターンです'}), 400
    
    if session['flipped'][card_index] or session['matched'][card_index]:
        return jsonify({'error': 'このカードは既にめくられています'}), 400
    
    # カードをめくる
    session['flipped'][card_index] = True
    
    # 1枚目のカード
    if session['first_card'] is None:
        session['first_card'] = card_index
        return jsonify({
            'flipped': session['flipped'],
            'matched': session['matched'],
            'player_score': session['player_score'],
            'ai_score': session['ai_score'],
            'current_turn': session['current_turn'],
            'first_card': session['first_card'],
            'waiting_for_second': True
        })
    
    # 2枚目のカード
    elif session['second_card'] is None and card_index != session['first_card']:
        session['second_card'] = card_index
        
        # カードが一致するかチェック
        if session['cards'][session['first_card']] == session['cards'][session['second_card']]:
            # 一致した場合
            session['matched'][session['first_card']] = True
            session['matched'][session['second_card']] = True
            session['player_score'] += 1
            # プレイヤーがマッチしたカードのインデックスを保存
            session['player_matched_cards'].extend([session['first_card'], session['second_card']])
            session['first_card'] = None
            session['second_card'] = None
            # プレイヤーが続行
        else:
            # 一致しない場合、AIのターンに移行
            session['current_turn'] = 'ai'
        
        return jsonify({
            'flipped': session['flipped'],
            'matched': session['matched'],
            'player_score': session['player_score'],
            'ai_score': session['ai_score'],
            'current_turn': session['current_turn'],
            'first_card': session['first_card'],
            'second_card': session['second_card'],
            'player_matched_cards': session['player_matched_cards'],
            'ai_matched_cards': session['ai_matched_cards']
        })
    
    return jsonify({'error': '無効な操作です'}), 400

@app.route('/api/ai-turn')
def ai_turn():
    """AIのターン"""
    print("AIターン開始")
    
    # プレイヤーが2枚めくって違った場合、裏に戻す
    if (
        session.get('first_card') is not None and
        session.get('second_card') is not None and
        session['cards'][session['first_card']] != session['cards'][session['second_card']]
    ):
        print(f"プレイヤーのカードを裏に戻す: {session['first_card']}, {session['second_card']}")
        session['flipped'][session['first_card']] = False
        session['flipped'][session['second_card']] = False
        session['first_card'] = None
        session['second_card'] = None

    if session['current_turn'] != 'ai':
        return jsonify({'error': 'プレイヤーのターンです'}), 400
    
    # AIの簡単なロジック：まだめくられていないカードをランダムに選ぶ
    available_cards = [i for i in range(20) if not session['flipped'][i] and not session['matched'][i]]
    print(f"利用可能なカード: {available_cards}")
    
    if len(available_cards) < 2:
        return jsonify({'error': 'ゲーム終了'}), 400
    
    # 1枚目を選ぶ
    first_card = random.choice(available_cards)
    session['flipped'][first_card] = True
    session['first_card'] = first_card
    print(f"AIが1枚目を選択: {first_card} ({session['cards'][first_card]})")
    
    # 少し待ってから2枚目を選ぶ
    available_cards.remove(first_card)
    second_card = random.choice(available_cards)
    session['flipped'][second_card] = True
    session['second_card'] = second_card
    print(f"AIが2枚目を選択: {second_card} ({session['cards'][second_card]})")
    
    # カードが一致するかチェック
    if session['cards'][first_card] == session['cards'][second_card]:
        # 一致した場合
        session['matched'][first_card] = True
        session['matched'][second_card] = True
        session['ai_score'] += 1
        # AIがマッチしたカードのインデックスを保存
        session['ai_matched_cards'].extend([first_card, second_card])
        session['first_card'] = None
        session['second_card'] = None
        print(f"AIがマッチ！スコア: {session['ai_score']}")
        # AIが続行
    else:
        # 一致しない場合、選んだ2枚を裏に戻してプレイヤーのターンに移行
        session['flipped'][first_card] = False
        session['flipped'][second_card] = False
        session['current_turn'] = 'player'
        session['first_card'] = None
        session['second_card'] = None
        print(f"AIがマッチせず、プレイヤーのターンに移行")
    
    response_data = {
        'flipped': session['flipped'],
        'matched': session['matched'],
        'player_score': session['player_score'],
        'ai_score': session['ai_score'],
        'current_turn': session['current_turn'],
        'ai_first_card': first_card,
        'ai_second_card': second_card,
        'player_matched_cards': session['player_matched_cards'],
        'ai_matched_cards': session['ai_matched_cards']
    }
    print(f"AIターンレスポンス: {response_data}")
    return jsonify(response_data)



if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080) 