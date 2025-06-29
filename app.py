from flask import Flask, render_template, request, jsonify
import subprocess
import os
import json
import pandas as pd
from datetime import datetime
import sys
import numpy as np

app = Flask(__name__)

# 可选择的爬取字段
AVAILABLE_FIELDS = {
    'title': '电影标题',
    'rank': '评分',
    'subject': '简介',
    'director': '导演',
    'actors': '主演',
    'year': '年份',
    'country': '国家/地区',
    'genre': '类型',
    'rating_people': '评价人数',
    'movie_url': '电影链接'
}

def clean_data_for_json(data):
    """清理数据，处理NaN值和特殊字符"""
    if isinstance(data, dict):
        return {k: clean_data_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data_for_json(item) for item in data]
    elif pd.isna(data) or data is None:
        return ""
    elif isinstance(data, (np.integer, np.floating)):
        return float(data) if not np.isnan(data) else ""
    else:
        return str(data)

@app.route('/')
def index():
    return render_template('index.html', fields=AVAILABLE_FIELDS)

@app.route('/crawl', methods=['POST'])
def crawl():
    try:
        # 获取用户选择的字段
        selected_fields = request.json.get('fields', [])
        
        if not selected_fields:
            return jsonify({'error': '请至少选择一个字段'}), 400
        
        # 生成输出文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'douban_custom_{timestamp}.csv'
        
        # 使用当前Python解释器运行爬虫
        python_executable = sys.executable
        cmd = [python_executable, '-m', 'scrapy', 'crawl', 'douban', '-o', output_file]
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if result.returncode != 0:
            return jsonify({'error': f'爬虫运行失败: {result.stderr}'}), 500
        
        # 读取结果文件
        if os.path.exists(output_file):
            df = pd.read_csv(output_file, encoding='utf-8')
            
            # 只保留用户选择的字段
            available_columns = [col for col in selected_fields if col in df.columns]
            if available_columns:
                df_filtered = df[available_columns]
                
                # 清理数据，处理NaN值
                df_filtered = df_filtered.fillna("")
                
                # 转换为字典并清理数据
                data = df_filtered.to_dict('records')
                cleaned_data = clean_data_for_json(data)
                
                # 删除临时文件
                os.remove(output_file)
                
                return jsonify({
                    'success': True,
                    'data': cleaned_data,
                    'total_count': len(cleaned_data),
                    'fields': available_columns
                })
            else:
                return jsonify({'error': '没有找到匹配的字段'}), 400
        else:
            return jsonify({'error': '爬虫没有生成输出文件'}), 500
            
    except Exception as e:
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/get_sample_data')
def get_sample_data():
    """获取示例数据用于预览"""
    try:
        # 检查是否有现有的数据文件
        sample_files = ['douban.csv', 'douban_output.csv', 'douban_extended.csv']
        sample_data = []
        
        for file in sample_files:
            if os.path.exists(file):
                df = pd.read_csv(file, encoding='utf-8')
                df = df.fillna("")  # 处理NaN值
                sample_data = df.head(5).to_dict('records')
                break
        
        return jsonify({
            'success': True,
            'data': sample_data,
            'fields': list(AVAILABLE_FIELDS.keys())
        })
    except Exception as e:
        return jsonify({'error': f'获取示例数据失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 