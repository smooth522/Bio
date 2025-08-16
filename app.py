from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import requests
import traceback
from datetime import datetime
import my_pb2
from key_iv import AES_KEY, AES_IV

app = Flask(__name__)
session = requests.Session()

DATA_API = "https://clientbp.ggblueshark.com/UpdateSocialBasicInfo"

HEADERS_TEMPLATE = {
    'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/octet-stream",
    'Expect': "100-continue",
    'X-Unity-Version': "2018.4.11f1",
    'X-GA': "v1 1",
    'ReleaseVersion': "OB50",
}

def encrypt_message(key, iv, plaintext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(plaintext, AES.block_size)
    return cipher.encrypt(padded)

@app.route('/send_bio', methods=['GET'])
def send_bio():
    try:
        token = request.args.get('token')
        bio = request.args.get('bio')

        if not token or not bio:
            return jsonify({"error": "Missing 'token' or 'bio' parameter"}), 400

        message = my_pb2.Signature()
        message.field2 = 9
        now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        message.field8 = bio
        message.field9 = 1

        encrypted = encrypt_message(AES_KEY, AES_IV, message.SerializeToString())

        headers = HEADERS_TEMPLATE.copy()
        headers['Authorization'] = f"Bearer {token}"

        response = session.post(DATA_API, data=encrypted, headers=headers, verify=False)

        try:
            server_response = response.content.decode('utf-8')
        except UnicodeDecodeError:
            server_response = response.content.decode('latin1')

        return jsonify({
            "status": "success",
            "time": now,
            "response": server_response
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)