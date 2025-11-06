from flask import Flask, request, jsonify, session, send_from_directory, abort
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('MGMT_SECRET', 'dev-secret')

UPLOAD_DIR = '/opt/videos'
ALLOWED = {'.mp4', '.mov', '.mkv', '.ts'}


def allowed_filename(filename):
  if not filename:
    return False
  return os.path.splitext(filename)[1].lower() in ALLOWED


@app.route('/')
def index():
  # Serve the React single-page app
  return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/login', methods=['POST'])
def api_login():
  data = request.get_json() or {}
  username = data.get('username', '')
  password = data.get('password', '')
  # Default credentials for the management UI (CTF): admin / admin123
  if username == 'admin' and password == 'admin123':
    session['user'] = 'admin'
    return jsonify({'ok': True, 'message': 'Login successful'})
  return jsonify({'ok': False, 'error': 'Invalid credentials'}), 401


@app.route('/api/logout', methods=['POST'])
def api_logout():
  session.pop('user', None)
  return jsonify({'ok': True})


@app.route('/api/upload', methods=['POST'])
def api_upload():
  if session.get('user') != 'admin':
    return jsonify({'ok': False, 'error': 'Unauthorized'}), 401

  if 'file' not in request.files:
    return jsonify({'ok': False, 'error': 'No file part'}), 400

  f = request.files['file']
  if f.filename == '':
    return jsonify({'ok': False, 'error': 'No selected file'}), 400

  if not allowed_filename(f.filename):
    return jsonify({'ok': False, 'error': 'Invalid file type'}), 400

  os.makedirs(UPLOAD_DIR, exist_ok=True)
  filename = secure_filename(f.filename)
  dest = os.path.join(UPLOAD_DIR, filename)
  f.save(dest)
  return jsonify({'ok': True, 'filename': filename})


@app.route('/api/status', methods=['GET'])
def api_status():
  return jsonify({'logged_in': session.get('user') == 'admin'})


@app.route('/static/<path:p>')
def static_files(p):
  return send_from_directory(app.static_folder, p)


@app.route('/api/list', methods=['GET'])
def api_list():
  # Return JSON list of uploaded videos (only to authenticated users)
  if session.get('user') != 'admin':
    return jsonify({'ok': False, 'error': 'Unauthorized'}), 401
  os.makedirs(UPLOAD_DIR, exist_ok=True)
  files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
  # sort newest first
  files.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_DIR, x)), reverse=True)
  return jsonify({'ok': True, 'files': files})


@app.route('/videos/<path:filename>')
def serve_video(filename):
  # Serve a specific uploaded video only to authenticated users
  if session.get('user') != 'admin':
    abort(401)
  safe = secure_filename(filename)
  full = os.path.join(UPLOAD_DIR, safe)
  if not os.path.exists(full):
    abort(404)
  return send_from_directory(UPLOAD_DIR, safe)


# ==============================================================================
# VULNERABILITY 1: Insecure Video Switching API (No Authentication Required!)
# ==============================================================================
@app.route('/api/switch-video', methods=['POST'])
def switch_video():
  """
  VULNERABILITY: This endpoint allows switching the broadcast video WITHOUT authentication!
  Students can exploit this by sending POST request with video filename.
  
  Exploit Example:
  curl -X POST http://manage.ann-news.live/api/switch-video \
       -H "Content-Type: application/json" \
       -d '{"video": "your-video.mp4"}'
  """
  data = request.get_json() or {}
  video = data.get('video', '')
  
  if not video:
    return jsonify({'ok': False, 'error': 'No video specified'}), 400
  
  # VULNERABILITY: No authentication check here!
  video_path = os.path.join(UPLOAD_DIR, video)
  
  if not os.path.exists(video_path):
    return jsonify({'ok': False, 'error': 'Video not found'}), 404
  
  # Write the video path to shared control file that video-switcher.sh can read
  os.makedirs('/tmp/control', exist_ok=True)
  with open('/tmp/control/current_video.txt', 'w') as f:
    f.write(video)
  
  return jsonify({
    'ok': True, 
    'message': f'Stream switched to {video}',
    'hint': 'FLAG: PENTESTER{uns3cur3_4p1_n0_4uth}'
  })


# ==============================================================================
# VULNERABILITY 2: Path Traversal in Video Access
# ==============================================================================
@app.route('/api/video-info', methods=['GET'])
def video_info():
  """
  VULNERABILITY: Path traversal - can read files outside intended directory
  
  Exploit Example:
  curl "http://manage.ann-news.live/api/video-info?path=../../etc/passwd"
  """
  video_path = request.args.get('path', '')
  
  # VULNERABILITY: No path validation!
  full_path = os.path.join(UPLOAD_DIR, video_path)
  
  if os.path.exists(full_path):
    size = os.path.getsize(full_path)
    return jsonify({
      'ok': True,
      'path': video_path,
      'size': size,
      'hint': 'You found path traversal! FLAG: PENTESTER{p4th_tr4v3rs4l_vuln}'
    })
  
  return jsonify({'ok': False, 'error': 'File not found'}), 404


# ==============================================================================
# VULNERABILITY 3: Command Injection in Stream Control
# ==============================================================================
@app.route('/api/stream-control', methods=['POST'])
def stream_control():
  """
  VULNERABILITY: Command injection through unsanitized input
  
  Exploit Example:
  curl -X POST http://manage.ann-news.live/api/stream-control \
       -H "Content-Type: application/json" \
       -d '{"action": "restart; cat /etc/passwd"}'
  """
  data = request.get_json() or {}
  action = data.get('action', '')
  
  # VULNERABILITY: Command injection - no input sanitization!
  try:
    # This executes whatever is in the action parameter
    result = subprocess.run(
      f"echo {action}", 
      shell=True, 
      capture_output=True, 
      text=True
    )
    return jsonify({
      'ok': True,
      'output': result.stdout,
      'hint': 'Command injection found! FLAG: PENTESTER{c0mm4nd_1nj3ct10n}'
    })
  except Exception as e:
    return jsonify({'ok': False, 'error': str(e)}), 500


# ==============================================================================
# VULNERABILITY 4: Insecure Direct Object Reference (IDOR)
# ==============================================================================
@app.route('/api/admin/user/<user_id>')
def get_user(user_id):
  """
  VULNERABILITY: IDOR - Access any user data without authorization
  
  Exploit Example:
  curl "http://manage.ann-news.live/api/admin/user/1"
  """
  # VULNERABILITY: No authentication or authorization check!
  users = {
    '1': {'username': 'admin', 'role': 'administrator', 'api_key': 'sk_live_abc123'},
    '2': {'username': 'broadcaster', 'role': 'user', 'api_key': 'sk_live_xyz789'},
    '3': {'username': 'guest', 'role': 'viewer', 'api_key': 'sk_live_def456'}
  }
  
  user = users.get(user_id)
  if user:
    return jsonify({
      'ok': True,
      'user': user,
      'hint': 'IDOR vulnerability! FLAG: PENTESTER{1d0r_4cc3ss_c0ntr0l}'
    })
  
  return jsonify({'ok': False, 'error': 'User not found'}), 404


# ==============================================================================
# VULNERABILITY 5: Debug Endpoint Exposed in Production
# ==============================================================================
@app.route('/api/debug/config')
def debug_config():
  """
  VULNERABILITY: Debug endpoint exposing sensitive configuration
  
  Exploit Example:
  curl "http://manage.ann-news.live/api/debug/config"
  """
  # VULNERABILITY: Exposes sensitive information
  return jsonify({
    'ok': True,
    'config': {
      'secret_key': app.secret_key,
      'upload_dir': UPLOAD_DIR,
      'database_url': 'postgresql://admin:supersecret@db:5432/stream',
      'rtmp_key': 'streaming_key_12345',
      'admin_credentials': {'username': 'admin', 'password': 'admin123'}
    },
    'hint': 'Debug info exposed! FLAG: PENTESTER{d3bug_1nf0_l34k}'
  })


# ==============================================================================
# VULNERABILITY 6: Weak Session Management
# ==============================================================================
@app.route('/api/create-session', methods=['POST'])
def create_session():
  """
  VULNERABILITY: Predictable session tokens
  
  Exploit Example:
  curl -X POST http://manage.ann-news.live/api/create-session \
       -H "Content-Type: application/json" \
       -d '{"username": "admin"}'
  """
  data = request.get_json() or {}
  username = data.get('username', '')
  
  # VULNERABILITY: Predictable session token generation
  if username:
    weak_token = f"session_{username}_123"
    return jsonify({
      'ok': True,
      'token': weak_token,
      'hint': 'Weak session token! FLAG: PENTESTER{w34k_s3ss10n_t0k3n}'
    })
  
  return jsonify({'ok': False, 'error': 'Username required'}), 400


# ==============================================================================
# Helper endpoint to list all vulnerabilities (for instructors)
# ==============================================================================
@app.route('/api/vulns/list')
def list_vulns():
  """
  Educational endpoint showing all vulnerabilities in the system
  """
  return jsonify({
    'vulnerabilities': [
      {
        'id': 1,
        'name': 'Missing Authentication',
        'endpoint': '/api/switch-video',
        'severity': 'CRITICAL',
        'description': 'Video switching API has no authentication',
        'flag': 'PENTESTER{uns3cur3_4p1_n0_4uth}'
      },
      {
        'id': 2,
        'name': 'Path Traversal',
        'endpoint': '/api/video-info',
        'severity': 'HIGH',
        'description': 'Can access files outside intended directory',
        'flag': 'PENTESTER{p4th_tr4v3rs4l_vuln}'
      },
      {
        'id': 3,
        'name': 'Command Injection',
        'endpoint': '/api/stream-control',
        'severity': 'CRITICAL',
        'description': 'Unsanitized input allows command execution',
        'flag': 'PENTESTER{c0mm4nd_1nj3ct10n}'
      },
      {
        'id': 4,
        'name': 'IDOR',
        'endpoint': '/api/admin/user/<id>',
        'severity': 'HIGH',
        'description': 'Access any user data without authorization',
        'flag': 'PENTESTER{1d0r_4cc3ss_c0ntr0l}'
      },
      {
        'id': 5,
        'name': 'Information Disclosure',
        'endpoint': '/api/debug/config',
        'severity': 'HIGH',
        'description': 'Debug endpoint exposes sensitive data',
        'flag': 'PENTESTER{d3bug_1nf0_l34k}'
      },
      {
        'id': 6,
        'name': 'Weak Session Management',
        'endpoint': '/api/create-session',
        'severity': 'MEDIUM',
        'description': 'Predictable session token generation',
        'flag': 'PENTESTER{w34k_s3ss10n_t0k3n}'
      }
    ],
    'hint': 'Use these endpoints to practice penetration testing!',
    'instructor_flag': 'INSTRUCTOR{c0mpl3t3d_4ll_vulns}'
  })


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
