from spamFilter import NaiveBayesSpamFilter, load_stop_word
stop_words = load_stop_word()


spam_filter = NaiveBayesSpamFilter(stop_words)
spam_filter.load_model("spam_filter_model.json")

print(spam_filter.predict("""
                          
我依然没有和任何人取得联系，或许你可以发给我部门主管的联系方式吗
                          
                          
                          """,1))
