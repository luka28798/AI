from summarize_model import summarizeText
import os
from flask import Flask, render_template, request, make_response, jsonify, send_file


app = Flask(__name__)



@app.route('/summarize', methods=['POST'])
def home():
	text = request.json['text']
	summarized_text = summarizeText(text)
	return summarized_text
if __name__ == '__main__':
    app.run()