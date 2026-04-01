import os
from flask import Flask, request, jsonify, render_template

from core.fifo import run_fifo, detect_beladys_anomaly
from core.lru import run_lru
from core.optimal import run_optimal

flask_app = Flask(__name__, template_folder='app', static_folder='app', static_url_path='')

@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/api/simulate', methods=['POST'])
def simulate():
    data = request.json
    
    if not data or 'reference_string' not in data or 'frames' not in data or 'algorithm' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
        
    try:
        ref_string = [int(x) for x in data['reference_string']]
        frames = int(data['frames'])
        selected_algo = data['algorithm']
        max_belady_frames = int(data.get('max_belady_frames', 10))
        
        # Run all algorithms for charts
        fifo_res = run_fifo(ref_string, frames)
        lru_res = run_lru(ref_string, frames)
        optimal_res = run_optimal(ref_string, frames)
        
        # Detect Belady's anomaly
        belady_res = detect_beladys_anomaly(ref_string, max_belady_frames)
        
        # Determine the currently selected algorithm's result
        if selected_algo == 'FIFO':
            current_res = fifo_res
        elif selected_algo == 'LRU':
            current_res = lru_res
        elif selected_algo == 'Optimal':
            current_res = optimal_res
        else:
            return jsonify({'error': 'Invalid algorithm selected'}), 400
            
        return jsonify({
            'current': current_res,
            'fifo': fifo_res,
            'lru': lru_res,
            'optimal': optimal_res,
            'belady': belady_res
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid input format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=5000, debug=True)
