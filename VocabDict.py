import pickle

'''Vocab Dictionary Content retrieved from:
https://www.scribd.com/doc/273225304/word-frequency-list-60000-English-xlsx'''

vocab = {}
with open("WordsDictionary.txt", "r") as words:
    # append all words in file into list
    w = words.read().replace(' ', '')
    wordsList = w.splitlines()
    rank = 0
    # add each word in list to dictionary as key and value as its frequency rank
    # words in the file are ordered from most frequent to less frequent
    for word in wordsList:
        if word.lower() not in vocab:
            rank += 1
            vocab[word.lower()] = rank

# save and store dictionary contents for later use
with open("engDic.pkl","wb") as pickle_dic:
    pickle.dump(vocab, pickle_dic)


startWithSameLetter = {}
alphabet = list(map(chr, range(97, 123)))
for l in alphabet:
    letterStart = []
    for word in vocab:
        if word[0] == l:
            letterStart.append(word)
        startWithSameLetter[l] = letterStart

with open("letterStartDic.pkl","wb") as pickle_dic:
    pickle.dump(startWithSameLetter, pickle_dic)