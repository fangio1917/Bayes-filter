import math
import json
import jieba
import pandas as pd
import codecs
import re
from tqdm import tqdm
from collections import defaultdict

# ---------------------- 数据加载模块 ----------------------
def load_formatted_data():
    """加载格式化后的标签-路径列表"""
    index = pd.read_csv("index", sep=" ", names=["spam", "path"])
    index.spam = index.spam.apply(lambda x: 1 if x == "spam" else 0)
    index.path = index.path.apply(lambda x: x[1:])  # 去除路径开头的/
    return index

def load_stop_word():
    """加载停用词表"""
    with codecs.open("stop", "r", encoding="gbk", errors="ignore") as f:
        return [line.strip() for line in f]

def get_mail_content(path):
    """读取邮件正文内容"""
    with codecs.open(path, "r", encoding="gbk", errors="ignore") as f:
        lines = f.readlines()
    
    # 跳过邮件头
    for i, line in enumerate(lines):
        if line == "\n":
            return "".join("".join(lines[i+1:]).strip().split())
    return ""

def create_word_list(content, stop_words):
    """生成去重后的词汇列表（词集模型）"""
    # 保留中文字符
    chinese_chars = re.findall("[\u4e00-\u9fa5]", content)
    # 结巴分词
    words = jieba.cut("".join(chinese_chars))
    # 过滤停用词并去重
    return list(set([word.strip() for word in words 
                   if word.strip() and word not in stop_words]))

# ---------------------- 核心分类器类 ----------------------
class NaiveBayesSpamFilter:
    def __init__(self, stop_words=None):
        self.stop_words = stop_words or set()
        # 训练数据统计
        self.word_counts = defaultdict(lambda: {'ham':0, 'spam':0})  # 词频统计
        self.total_ham = 0    # 正常邮件总数
        self.total_spam = 0   # 垃圾邮件总数
        self.ham_word_num = 0 # 正常邮件总词数（去重后）
        self.spam_word_num = 0# 垃圾邮件总词数（去重后）
        self.vocab_size = 0   # 词汇表大小

    def train(self, dataframe):
        """训练模型"""
        # 预处理所有邮件
        processed_data = []
        for _, row in tqdm(dataframe.iterrows(), total=len(dataframe), desc="处理邮件"):
            content = get_mail_content(row['path'])
            word_list = create_word_list(content, self.stop_words)
            processed_data.append((word_list, row['spam']))
        
        # 统计特征
        for word_list, is_spam in tqdm(processed_data, desc="训练模型"):
            # 更新全局统计
            if is_spam:
                self.total_spam += 1
                self.spam_word_num += len(word_list)
            else:
                self.total_ham += 1
                self.ham_word_num += len(word_list)
            
            # 更新词频统计
            for word in word_list:
                if is_spam:
                    self.word_counts[word]['spam'] += 1
                else:
                    self.word_counts[word]['ham'] += 1
        
        # 计算词汇表大小
        self.vocab_size = len(self.word_counts)

    def predict(self, content, mode=0):
        """预测单封邮件"""
        # 预处理输入
        word_list = create_word_list(content, self.stop_words)
        
        # 计算先验概率
        log_ham = math.log(self.total_ham / (self.total_ham + self.total_spam))
        log_spam = math.log(self.total_spam / (self.total_ham + self.total_spam))
        
        # 计算条件概率
        for word in word_list:
            # 获取词频统计
            counts = self.word_counts.get(word, {'ham':0, 'spam':0})
            
            # 计算P(word|ham) 带拉普拉斯平滑
            p_ham = (counts['ham'] + 1) / (self.ham_word_num + self.vocab_size)
            # 计算P(word|spam)
            p_spam = (counts['spam'] + 1) / (self.spam_word_num + self.vocab_size)
            
            # 累加对数概率
            log_ham += math.log(max(p_ham, 1e-10))
            log_spam += math.log(max(p_spam, 1e-10))
        if mode == 1:
            print("正常邮件概率:", log_ham)
            print("垃圾邮件概率:", log_spam)

        return "垃圾邮件" if log_spam > log_ham else "正常邮件"

    def save_model(self, path):
        """保存模型"""
        model_data = {
            'word_counts': dict(self.word_counts),
            'total_ham': self.total_ham,
            'total_spam': self.total_spam,
            'ham_word_num': self.ham_word_num,
            'spam_word_num': self.spam_word_num,
            'vocab_size': self.vocab_size
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)

    def load_model(self, path):
        """加载模型"""
        with open(path, 'r', encoding='utf-8') as f:
            model_data = json.load(f)
        self.word_counts = defaultdict(lambda: {'ham':0, 'spam':0}, model_data['word_counts'])
        self.total_ham = model_data['total_ham']
        self.total_spam = model_data['total_spam']
        self.ham_word_num = model_data['ham_word_num']
        self.spam_word_num = model_data['spam_word_num']
        self.vocab_size = model_data['vocab_size']




# ---------------------- 使用示例 ----------------------
if __name__ == "__main__":
    # 1. 加载数据和停用词表
    print("加载数据...")
    index = load_formatted_data()
    stop_words = load_stop_word()
    
    # 2. 划分数据集：80%训练集，20%验证集
    train_data = index.sample(frac=0.8, random_state=42)
    val_data = index.drop(train_data.index)
    
    # 3. 初始化分类器
    print("\n初始化分类器...")
    spam_filter = NaiveBayesSpamFilter(stop_words)
    
    # 4. 训练模型
    print("\n训练模型中...")
    spam_filter.train(train_data)
    
    # 5. 在验证集上评估模型
    print("\n验证模型中...")
    correct = 0
    total = len(val_data)
    for _, row in tqdm(val_data.iterrows(), total=total, desc="验证邮件"):
        content = get_mail_content(row['path'])
        pred = spam_filter.predict(content,0)
        true_label = "垃圾邮件" if row['spam'] == 1 else "正常邮件"
        if pred == true_label:
            correct += 1
    accuracy = correct / total
    print(f"\n验证集准确率: {accuracy*100:.2f}%")
    
    
    # 7. 保存模型
    spam_filter.save_model("spam_filter_model.json")
    print("模型已保存至 spam_filter_model.json")
