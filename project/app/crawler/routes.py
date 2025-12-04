from flask import Blueprint, request, jsonify
from app.crawler.crawler import crawl_baidu_search

# 创建蓝图
crawler_bp = Blueprint('crawler', __name__)

@crawler_bp.route('/api/crawl', methods=['GET'])
def crawl_data():
    """
    数据抓取API接口
    参数：
        keyword - 搜索关键字
        pn - 翻页参数，默认为0代表第1页，10代表第2页，20代表第3页，以此类推
    返回：JSON格式的搜索结果
    """
    try:
        # 获取搜索关键字
        keyword = request.args.get('keyword', '')
        
        # 获取翻页参数，默认为0
        pn = request.args.get('pn', 0)
        try:
            pn = int(pn)
        except ValueError:
            pn = 0
        
        if not keyword:
            return jsonify({
                'success': False,
                'message': 'Missing keyword parameter'
            }), 400
        
        # 调用抓取函数
        results = crawl_baidu_search(keyword, pn=pn)
        
        return jsonify({
            'success': True,
            'keyword': keyword,
            'pn': pn,
            'page': pn // 10 + 1,
            'count': len(results),
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@crawler_bp.route('/crawler', methods=['GET'])
def crawler_page():
    """
    数据抓取页面
    """
    return '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>数据抓取工具</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/layui@2.6.8/dist/css/layui.css">
        <style>
            .container {
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            .result-item {
                margin: 20px 0;
                padding: 15px;
                border: 1px solid #eee;
                border-radius: 5px;
            }
            .result-title {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .result-url {
                color: #1E9FFF;
                margin-bottom: 10px;
            }
            .result-summary {
                color: #666;
                margin-bottom: 10px;
            }
            .result-meta {
                color: #999;
                font-size: 12px;
            }
            .cover-img {
                max-width: 100px;
                max-height: 100px;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>百度搜索数据抓取工具</h1>
            
            <div class="layui-form">
                <div class="layui-form-item">
                    <label class="layui-form-label">搜索关键字</label>
                    <div class="layui-input-block">
                        <input type="text" name="keyword" id="keyword" placeholder="请输入搜索关键字" autocomplete="off" class="layui-input">
                    </div>
                </div>
                <div class="layui-form-item">
                    <label class="layui-form-label">页码</label>
                    <div class="layui-input-block">
                        <select name="page" id="page" lay-verify="required">
                            <option value="1">第1页</option>
                            <option value="2">第2页</option>
                            <option value="3">第3页</option>
                            <option value="4">第4页</option>
                            <option value="5">第5页</option>
                        </select>
                    </div>
                </div>
                <div class="layui-form-item">
                    <div class="layui-input-block">
                        <button class="layui-btn" id="crawl-btn">开始抓取</button>
                        <button type="reset" class="layui-btn layui-btn-primary">重置</button>
                    </div>
                </div>
            </div>
            
            <div id="loading" style="display: none; text-align: center; padding: 20px;">
                <i class="layui-icon layui-icon-loading layui-icon layui-anim layui-anim-rotate layui-anim-loop" style="font-size: 30px;"></i>
                <p>正在抓取数据...</p>
            </div>
            
            <div id="results"></div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/layui@2.6.8/dist/layui.js"></script>
        <script>
            layui.use(['layer'], function() {
                var layer = layui.layer;
                
                document.getElementById('crawl-btn').onclick = function() {
                    var keyword = document.getElementById('keyword').value;
                    var page = document.getElementById('page').value;
                    
                    if (!keyword) {
                        layer.msg('请输入搜索关键字', {icon: 2});
                        return;
                    }
                    
                    // 计算pn参数值 (pn = (page-1)*10)
                    var pn = (parseInt(page) - 1) * 10;
                    
                    // 显示加载状态
                    document.getElementById('loading').style.display = 'block';
                    document.getElementById('results').innerHTML = '';
                    
                    // 发送请求
                    fetch('/api/crawl?keyword=' + encodeURIComponent(keyword) + '&pn=' + pn)
                        .then(response => response.json())
                        .then(data => {
                            // 隐藏加载状态
                            document.getElementById('loading').style.display = 'none';
                            
                            if (data.success) {
                                layer.msg(`成功抓取到 ${data.count} 条结果 (第${data.page}页)`, {icon: 1});
                                
                                // 显示结果
                                var resultsDiv = document.getElementById('results');
                                if (data.results.length > 0) {
                                    data.results.forEach(function(result, index) {
                                        var resultHtml = `
                                            <div class="result-item">
                                                <div class="result-title">${index + 1}. ${result.title}</div>
                                                <div class="result-url"><a href="${result.original_url}" target="_blank">${result.original_url}</a></div>
                                                <div class="result-summary">${result.summary}</div>
                                                <div class="result-meta">来源：${result.source}</div>
                                                ${result.cover ? `<img src="${result.cover}" class="cover-img" alt="封面">` : ''}
                                            </div>
                                        `;
                                        resultsDiv.innerHTML += resultHtml;
                                    });
                                } else {
                                    resultsDiv.innerHTML = '<p style="text-align: center; color: #999;">没有找到相关结果</p>';
                                }
                            } else {
                                layer.msg('抓取失败：' + data.message, {icon: 2});
                            }
                        })
                        .catch(error => {
                            document.getElementById('loading').style.display = 'none';
                            layer.msg('抓取失败：' + error.message, {icon: 2});
                        });
                };
            });
        </script>
    </body>
    </html>
    ''', 200
