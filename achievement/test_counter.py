from counter import analyze_word
def test_hello():
    assert analyze_word("hello")==("l",2)
def test_aabbcc():
    assert analyze_word("aabbcc")==('a',2)