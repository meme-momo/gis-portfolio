import requests
import json
import time
from collections import Counter
import jieba
from pathlib import Path

# 配置
DYNAMIC_ID = "1127669871517106193"
OUTPUT_DIR = Path(r"./output/MyProject2")
OUTPUT_FILE = OUTPUT_DIR / "bilibili_comments.txt"
KEYWORDS_FILE = OUTPUT_DIR / "top_keywords.txt"
SENSITIVE_WORDS_FILE = OUTPUT_DIR / "sensitive_words.txt"
REPEATED_COMMENTS_FILE = OUTPUT_DIR / "repeated_comments.txt"
JSON_REPLIES_FILE = OUTPUT_DIR / "all_replies.json"
CHECKPOINT_FILE = OUTPUT_DIR / "comments_checkpoint.json"

# 敏感词列表
SENSITIVE_WORDS = [
    '敏感', '政治', '政府', '习近平', '共产党', '台湾', '香港', '新疆', '西藏', '法轮功',
    '维权', '抗议', '示威', '审查', '封锁', '和谐', '删帖', '禁言', '水军', '五毛'
]

def ensure_output_dir():
    """确保输出目录存在"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_headers():
    """获取请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'Referer': 'https://www.bilibili.com/',
        'Origin': 'https://www.bilibili.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': '<请填入你自己的 Cookie>'
    }

def get_dynamic_details(dynamic_id):
    """获取动态详情，提取oid"""
    url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={dynamic_id}"
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"Dynamic details: {json.dumps(data, ensure_ascii=False)[:200]}...")
        if data['code'] == 0:
            desc = data['data']['card']['desc']
            if desc['type'] == 8:  # 视频
                oid = desc.get('aid', desc.get('rid'))
                print(f"Video detected. OID: {oid}")
                return str(oid)
            else:
                print(f"Dynamic type {desc['type']} not supported for comments.")
                return None
        else:
            print(f"Error fetching dynamic: {data['message']}")
            return None
    except Exception as e:
        print(f"Exception fetching dynamic: {e}")
        return None

def fetch_comments_page(oid, page_no, next_offset=None, page_size=20, max_retries=3):
    """爬取单页评论"""
    url = f"https://api.bilibili.com/x/v2/reply/main?type=1&oid={oid}&ps={page_size}&sort=2&with_floor=1"
    if next_offset:
        url += f"&next_offset={next_offset}"
    else:
        url += f"&pn={page_no}"
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=get_headers(), timeout=10)
            response.raise_for_status()
            data = response.json()
            print(f"Page {page_no} response: {json.dumps(data, ensure_ascii=False)[:200]}...")
            if data['code'] == 0:
                replies = data['data'].get('replies', [])
                cursor = data['data'].get('cursor', {})
                next_offset = cursor.get('pagination_reply', {}).get('next_offset', None)
                return replies, next_offset
            else:
                print(f"Error fetching page {page_no} (attempt {attempt+1}): {data['message']}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
        except Exception as e:
            print(f"Exception on page {page_no} (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return [], None

def load_checkpoint():
    """加载检查点"""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'replies': [], 'last_page': 0, 'last_offset': None}

def save_checkpoint(replies, page_no, next_offset):
    """保存检查点"""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump({'replies': replies, 'last_page': page_no, 'last_offset': next_offset}, f, ensure_ascii=False)
    print(f"Checkpoint saved at page {page_no}")

def crawl_all_comments(oid, target_comments=5000):
    """爬取评论，直到接近目标数量"""
    checkpoint = load_checkpoint()
    all_replies = checkpoint['replies']
    page_no = checkpoint['last_page'] + 1
    next_offset = checkpoint.get('last_offset')
    total_comments = 0

    while total_comments < target_comments:
        print(f"Fetching page {page_no} (offset: {next_offset})...")
        replies, new_offset = fetch_comments_page(oid, page_no, next_offset)
        if not replies:
            break
        all_replies.extend(replies)
        # 粗略估计评论数（含子回复）
        temp_texts = extract_comment_text(replies)
        total_comments += len(temp_texts)
        print(f"Current total comments: {total_comments}")
        if len(replies) < 20 or not new_offset:
            break
        next_offset = new_offset
        if page_no % 50 == 0:
            save_checkpoint(all_replies, page_no, next_offset)
        page_no += 1
        time.sleep(2)
    save_checkpoint(all_replies, page_no - 1, next_offset)
    print(f"Crawled {len(all_replies)} raw replies across {page_no-1} pages.")
    return all_replies

def extract_comment_text(replies):
    """递归提取评论文本"""
    texts = []
    def recurse_replies(r):
        if isinstance(r, dict) and 'content' in r and 'message' in r['content']:
            texts.append(r['content']['message'])
        if 'replies' in r and r['replies']:
            for sub_reply in r['replies']:
                recurse_replies(sub_reply)
    for reply in replies:
        recurse_replies(reply)
    return texts

def save_to_file(texts, filepath):
    """保存到文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        for text in texts:
            f.write(text + '\n')
    print(f"Saved {len(texts)} comments to {filepath}")

def save_replies_json(all_replies, filepath):
    """保存原始JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(all_replies, f, ensure_ascii=False, indent=2)
    print(f"Saved raw replies JSON to {filepath}")

def analyze_keywords(texts):
    """分析关键词"""
    if not texts:
        print("No texts to analyze.")
        return
    all_text = ' '.join(texts)
    words = jieba.cut(all_text)
    stop_words = {'的', '是', '在', '了', '和', '就', '不', '人', '这', '有', '我', '他', '都', '一个', '上', '也', '很', '说', '对', '来', '没', '过', '出', '会', '还', '被', '去', '下', '但', '么', '里', '只', '好', '看', '能', '多', '大', '得', '小', '天', '年', '时', '要', '想', '知道'}
    word_freq = Counter(w for w in words if len(w) > 1 and w not in stop_words)
    top_keywords = word_freq.most_common(20)
    with open(KEYWORDS_FILE, 'w', encoding='utf-8') as f:
        for word, freq in top_keywords:
            f.write(f"{word}: {freq}\n")
    print(f"Top keywords saved to {KEYWORDS_FILE}")

def analyze_sensitive_words(texts):
    """分析敏感词"""
    if not texts:
        print("No texts to analyze.")
        return
    sensitive_count = Counter()
    for text in texts:
        for word in SENSITIVE_WORDS:
            if word in text:
                sensitive_count[word] += 1
    with open(SENSITIVE_WORDS_FILE, 'w', encoding='utf-8') as f:
        for word, count in sensitive_count.most_common():
            f.write(f"{word}: {count}\n")
    print(f"Sensitive words analysis saved to {SENSITIVE_WORDS_FILE}")

def analyze_repeated_comments(texts):
    """提取重复≥10次且长度≥10字符的评论"""
    if not texts:
        print("No texts to analyze for repeated comments.")
        return
    comment_freq = Counter(texts)
    repeated_comments = [(text, count) for text, count in comment_freq.items() if count >= 10 and len(text) >= 10]
    with open(REPEATED_COMMENTS_FILE, 'w', encoding='utf-8') as f:
        for text, count in sorted(repeated_comments, key=lambda x: x[1], reverse=True):
            f.write(f"[{count} times] {text}\n")
    print(f"Repeated comments (≥10 times, ≥10 chars) saved to {REPEATED_COMMENTS_FILE}")

if __name__ == "__main__":
    # 确保输出目录
    ensure_output_dir()
    
    # 获取OID
    oid = get_dynamic_details(DYNAMIC_ID)
    if not oid:
        print("Failed to get OID. Exiting.")
        exit(1)
    
    # 爬取约5000条评论
    all_replies = crawl_all_comments(oid, target_comments=5000)
    
    # 保存原始JSON
    save_replies_json(all_replies, JSON_REPLIES_FILE)
    
    # 提取文本
    all_texts = extract_comment_text(all_replies)
    
    # 保存和分析
    save_to_file(all_texts, OUTPUT_FILE)
    analyze_keywords(all_texts)
    analyze_sensitive_words(all_texts)
    analyze_repeated_comments(all_texts)
    
    print("Done! Total comments:", len(all_texts))
