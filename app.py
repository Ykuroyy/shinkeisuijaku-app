from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import os
import random
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# データベース設定
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ゲーム履歴モデル
class GameHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_score = db.Column(db.Integer, default=0)
    ai_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    
    return jsonify({
        'cards': cards,
        'flipped': session['flipped'],
        'matched': session['matched'],
        'player_score': session['player_score'],
        'ai_score': session['ai_score'],
        'current_turn': session['current_turn']
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
            'second_card': session['second_card']
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
        'ai_second_card': second_card
    }
    print(f"AIターンレスポンス: {response_data}")
    return jsonify(response_data)



@app.route('/api/save-game', methods=['POST'])
def save_game():
    """ゲーム結果を保存"""
    data = request.get_json()
    player_score = data.get('player_score', 0)
    ai_score = data.get('ai_score', 0)
    
    game_history = GameHistory(player_score=player_score, ai_score=ai_score)
    db.session.add(game_history)
    db.session.commit()
    
    return jsonify({'message': 'ゲーム結果を保存しました'})

@app.route('/api/game-history')
def get_game_history():
    """ゲーム履歴を取得"""
    history = GameHistory.query.order_by(GameHistory.created_at.desc()).limit(10).all()
    return jsonify([{
        'id': h.id,
        'player_score': h.player_score,
        'ai_score': h.ai_score,
        'created_at': h.created_at.strftime('%Y-%m-%d %H:%M')
    } for h in history])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 