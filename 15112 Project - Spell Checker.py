import tkinter as tk
import re
import pickle
from tkinter.scrolledtext import ScrolledText

# this class is responsible for making the GUI of the writing page
# it's also responsible for binding the arrows with the dictionary list
class textEditor:
    def __init__(self, window, vocab, startWithSameLetter):
        # create main gui elements and bind them to their appropriate functions
        self.notepad = ScrolledText(window)
        self.autoCorrect = tk.Checkbutton(window, text="Enable Auto-Correct", command=self.switchSpellChecker)
        self.word_suggestions = tk.Listbox(window)

        self.autoCorrect.pack()
        self.notepad.pack()
        self.vocab = vocab
        self.startWithSameLetter = startWithSameLetter
        # add pre-set markup on entire text widget
        self.notepad.tag_configure("misspelling", foreground="red", underline=True)

        # bind all navigation to checking the spelling of the word
        self.notepad.bind("<ButtonRelease-1>", self.spellChecker)
        self.notepad.bind("<Up>", self.spellChecker)
        self.notepad.bind("<Down>", self.spellChecker)
        self.notepad.bind("<Left>", self.spellChecker)
        self.notepad.bind("<Right>", self.spellChecker)

        # check each word's spelling after typed and mark it up
        self.notepad.bind("<space>", self.isSpeltCorrect)
        self.notepad.bind(".", self.isSpeltCorrect)

        for letter in "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM":
            self.notepad.bind(letter, self.autoComplete)

        self.word_suggestions.bind('<<ListboxSelect>>', self.clickSelect)

    # this function takes automatically the first choice from the suggestion
    # box and replaces it with the word that is underlined as misspelt
    def autoCorrect(self):
        lastWord = self.getLastWord()
        if lastWord:
            # get first suggestiosn from listbox contents
            bestSuggestion = self.spellCheckerList()[0]
            # configure and find first and last index of word to be replaced
            start = self.notepad.get('1.0', tk.END).index(lastWord)
            end = start + len(lastWord)
            line_num = int(float(self.notepad.index(tk.END)))
            start_i = str(line_num) + '.' + str(start)
            end_i = str(line_num) + '.' + str(end)
            # delete the misspelled word by the best suggestion in text widget
            self.notepad.delete(start_i, end_i)
            self.notepad.insert(start_i, bestSuggestion)

    # this function unbinds the arrows with the list from the dictionary
    # sothat the list dosen't appear when pressing the auto-correct option
    def switchSpellChecker(self):
        self.notepad.bind("<ButtonRelease-1>", self.autoCorrect)
        self.notepad.bind("<Up>", self.autoCorrect)
        self.notepad.bind("<Down>", self.autoCorrect)
        self.notepad.bind("<Left>", self.autoCorrect)
        self.notepad.bind("<Right>", self.autoCorrect)

    # this function gets the last word that was typed by the user
    def getLastWord(self):
        # split all input text at all white space characters (e.g. space, tab, enter)
        wordsList = re.split("\s+", self.notepad.get("1.0", tk.END))
        # remove last empty string
        wordsList.remove('')
        # last word is at the last index of the words list
        lastWord = wordsList[len(wordsList) - 1]
        return lastWord

    # here we edit the words that are misspelt after
    # getting the words from the screen and correct their form
    def spellCheckerList(self):
        misspelt_word = self.getCurrWord()
        edits = {}
        if not self.isSpeltCorrect(misspelt_word):
            for word in self.vocab:
                edits_num = self.minEditDistance(misspelt_word, word)
                if edits_num <= 2:
                    if edits_num in edits:
                        edits[edits_num].append(word)
                    else:
                        edits[edits_num] = [word]
        '''maybe also narrow down words in dictionary, so that if the length = #edits, doesn't include'''
        '''words 1 less and one more than word, idealy same length, after #edits checked'''
        freqs1 = []
        freqs2 = []
        if 1 in edits:
            for similar_word in edits.get(1):
                freq = self.vocab.get(similar_word)
                freqs1.append(freq)
        if 2 in edits:
            for similar_word in edits.get(2):
                freq = self.vocab.get(similar_word)
                freqs2.append(freq)
        freqs1.sort()
        freqs2.sort()
        freqs = freqs1 + freqs2
        suggestions = []
        for f in freqs:
            for word in self.vocab:
                # get words based on their corresponding frequencies in order
                if self.vocab.get(word) == f:
                    suggestions.append(word)
        return suggestions

    '''STILL TO DO, CONSIDER PUNCTUATION AND CAPITALIZATION IN SPELLCHECKER'''

    # here we check if the word is spelt correctly or not
    # if it does it returns True otherwise it returns False
    def isSpeltCorrect(self, word):
        self.markUp(word)
        if word in self.vocab:
            return True
        return False

    # this functions recognizes the word and finds similar words
    # depending in their frequency, this will be then added to the
    # suggestion list. this function updates after typing each charachter
    def autoCompleteList(self, e):
        typed_string = re.split("\s+", self.notepad.get("1.0", tk.END))
        typed_string.remove('')
        last_chars = typed_string[len(typed_string) - 1]
        #print(self.getCurrWord())
        #print(last_chars)
        last_chars = last_chars + e.char
        #print(e.char)
        #print(last_chars)
        freqs = []
        suggestions = []
        inp_length = len(last_chars)
        for word in self.vocab:
            # check for english words that start with the same characters
            if word[:inp_length].lower() == last_chars.lower():
                # record the frequency ranks of such words
                freq = self.vocab.get(word)
                freqs.append(freq)
        # order frequencies
        freqs.sort()
        for f in freqs:
            for word in self.vocab:
                # get words based on their corresponding frequencies in order
                if self.vocab.get(word) == f:
                    suggestions.append(word)
        return suggestions

    '''PROBLEM WITH LAST CHARS, NOT RECOGNIZE 1 LETTER'''

    # this function takes the list of words suggested if any and
    # inserts them on the screen in a listbox
    def autoComplete(self, e):
        self.word_suggestions.delete(0, tk.END)
        #word = self.getCurrWord()
        all = self.notepad.get('1.0', tk.END)
        # if there is one character typed
        if len(all) == 1:
            letter = e.char
            # use pre-loaded dictionary to get suggestiosn into listbox
            suggestions = self.startWithSameLetter.get(letter)
            i = 0
            while i < 11 and i < len(suggestions):
                for l in suggestions:
                    self.word_suggestions.insert(i, suggestions[i])
                    i += 1
        else:
            # if typed portion is a part of a valid word
            if self.autoCompleteList(e):
                # get autocomplete list and append its first 10 values into the listbox
                suggestions = self.autoCompleteList(e)[:10]
                for i in range(len(suggestions)):
                    self.word_suggestions.insert(i, suggestions[i])
            else:
                self.word_suggestions.insert(0, "No matches found.")
        # place the listbox where the cursor is
        (x, y, w, h) = self.notepad.bbox('insert')
        self.word_suggestions.place(x=x + 100, y=y + 120, anchor="center")

    # this function also draws a list box with all the suggested words that
    # could replace the misspelt word.
    def spellChecker(self, e):
        word = self.getCurrWord()
        # if the suggestions listbox is not empty, clear it
        if len(self.word_suggestions.get(0, tk.END)) != 0:
            self.word_suggestions.delete(0, tk.END)
        if self.isSpeltCorrect(word):
            return
            # word_suggestions.destroy()
        # if current word is not empty and is spelled incorrectly
        elif len(self.notepad.get('1.0', 'end-1c')) != 0:
            if self.spellCheckerList():
                # append first 10 suggestions into listbox
                suggestions = self.spellCheckerList()[:10]
                for i in range(len(suggestions)):
                    self.word_suggestions.insert(i, suggestions[i])
            else:
                # if not close matches from min edit function, display appropriate message
                self.word_suggestions.insert(0, "No matches found.")
                self.word_suggestions.insert(1, "Add word to dictionary")

            # place the listbox where the cursor is
            (x, y, w, h) = self.notepad.bbox('insert')
            self.word_suggestions.place(x=x + 100, y=y + 120, anchor="center")

    # this function takes the selection that the user made from the suggestion box
    # and overwrites the word in he screen
    def clickSelect(self, e):
        selected_word = self.word_suggestions.get(self.word_suggestions.curselection())
        currWord = self.getCurrWord()
        start = self.notepad.get('1.0', tk.END).index(currWord)
        end = start + len(currWord)
        line_num = int(float(self.notepad.index(tk.CURRENT)))
        # configure start and end indices of the word to be corrected syntax correctly
        start_i = str(line_num) + '.' + str(start)
        end_i = str(line_num) + '.' + str(end)
        # delete the misspelled word and replace it by the correct one selected from the listbox
        self.notepad.delete(start_i, end_i)
        self.notepad.insert(start_i, selected_word)
        # word_suggestions.destroy()

    # this function underlines the word that is misspelt and
    # colors it with red
    def markUp(self, misspelt_word):
        # search for starting index of
        index = self.notepad.search(r'\s', "insert", backwards=True, regexp=True)
        if index == "":
            index = "1.0"
        else:
            index = self.notepad.index("%s+1c" % index)
        word = self.notepad.get(index, "insert")
        # if word spelled correctly, remove pre-set misspelling tag
        if word in self.vocab:
            self.notepad.tag_remove("misspelling", index, "%s+%dc" % (index, len(word)))
        else:
            self.notepad.tag_add("misspelling", index, "%s+%dc" % (index, len(word)))

        '''first word not marked up if misspelled'''
    # This function finds the minimum edit distance using a modified version of the Levistein algorithm
    def minEditDistance(self, misspelt_word, vocab_word):
        rows = len(misspelt_word) + 1
        columns = len(vocab_word) + 1
        matrix = []
        # split list of lists based on rows
        # initialize values for column contents for each row
        for i in range(rows):
            matrix.append([])
            for j in range(columns):
                matrix[i].append(-1)
        # empty string row
        first_row = []
        for n in range(columns):
            first_row.append(n)
        matrix = [first_row] + matrix[1:]
        # add first column values in matrix
        n = 0
        for i in range(rows):
            matrix[i][0] = n
            n += 1
        # for each letter of the misspelt word
        for r in range(rows - 1):
            # go through each letter in the vocab word
            for c in range(columns - 1):
                # if the letters are the same
                if vocab_word[c] == misspelt_word[r]:
                    # copy down the value at the relative left diagonal position in the matrix
                    # into the corresponding matrix position of the current string comparison
                    matrix[r + 1][c + 1] = matrix[r][c]
                # if letters are different
                else:
                    # take the minimum value of the three upper left diagonals to the current position
                    adj_min = min(matrix[r][c], matrix[r][c + 1], matrix[r + 1][c])
                    # add 1 to get the minimum additional edit to transform the two strings parts so far
                    # add resulting value into corresponding matrix position
                    matrix[r + 1][c + 1] = adj_min + 1
        # minimum number of edits is the last computed value of the matrix
        minEdits = matrix[rows - 1][columns - 1]
        return minEdits

    # this function gets the word that is being modefied currently from the user
    # and returns it.
    def getCurrWord(self):
        start = self.notepad.index("insert wordstart")
        end = self.notepad.index("insert wordend")
        curr_word = self.notepad.get(start, end)
        return curr_word


window = tk.Tk()

# import stored pickle dictionary of vocab words
with open("engDic.pkl", "rb") as pickle_dic:
    vocab = pickle.load(pickle_dic)

# import stored pickle dictionary of words with same letter beginning
with open("letterStartDic.pkl", "rb") as pickle_dic:
    startWithSameLetter = pickle.load(pickle_dic)

textEditor = textEditor(window, vocab, startWithSameLetter)
window.mainloop()

'''Irrelevent comments for myself'''
'''after space, first character doesn't autocomplete but if next one typed, both autocomplete'''
'''add functionality: if press up and down while typing word can access listbox contents'''
'''listbox remains if backspace'''
'''if with punctuation, autocorrected, add punctuation'''
'''if up and down arrows while typing word, navigate through listbox words'''
'''condition for not matches found in defined edit#'''
'''selecting from listbox deletes all and replaces with word'''
'''if needed: for efficiency purposes, if navigating through same word, 
no need to call and suggest new suggestions, just move listbox to appropriate position'''
'''add word from listbox if same word, remove from suggestions if same word '''
'''need to destroy listbox after each pressed once, after word is typed already'''