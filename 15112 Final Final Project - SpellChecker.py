import tkinter as tk
from tkinter import Menu
from tkinter import ttk
from tkinter.font import Font
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import tkinter.filedialog
import re
import pickle
import string

editorbox = None
# this class if responsible for the main GUI of the texteditor file and
# binding its spell-check and auto-correct features
class textEditor():
    alltabs = None
    def __init__(self, window, labelFrame, tabs, vocab, startWithSameLetter, tabsOpen, file_path=""):
        self.window = window
        # record the directory path of the file
        self.file_path = file_path
        if file_path:
            self.file_name = self.file_path
        else:
            # if the file path doesn't exist, name it accordingly
            self.file_name = 'Untitled'
        # record the necessary passed-in parameters
        self.labelFrame = labelFrame
        self.tabsOpen = tabsOpen
        self.tabs = tabs
        self.vocab = vocab
        self.startWithSameLetter = startWithSameLetter
        # create the main gui elements in the respective tab frame
        self.notepad = ScrolledText(self.labelFrame, font=("Calibri", 15))
        editorbox = self.notepad
        self.var = tk.IntVar()
        self.autoCorrectOption = tk.Checkbutton(self.labelFrame, \
                                                text="Enable Auto-Correct", variable=self.var, command=self.switchSpellChecker)
        self.autoComplete_suggestions = tk.Listbox(self.labelFrame)
        self.autoCorrect_suggestions = tk.Listbox(self.labelFrame)
        myFont = Font(family="Calibri", size=15)
        self.autoComplete_suggestions.configure(font=myFont)
        self.autoCorrect_suggestions.configure(font=myFont)

        # create funtionality bars inside tab frame
        self.createMenuBar()
        self.createToolBar(self.labelFrame)

        self.autoCorrectOption.grid(row=1, column=9)
        self.notepad.config(undo = True)
        self.notepad.config(height=900)
        self.notepad.grid(row=2, column=0, columnspan=11, sticky="WE")
        self.window.protocol("WM_DELETE_WINDOW", lambda: newFileTab.closeCheck(self.tabsOpen))
        # add pre-set markup on the entire text widget in the tab frame
        self.notepad.tag_configure("misspelling", foreground="red", underline=True)

        # bind all navigation to checking the spelling of the word
        self.nav_click = self.notepad.bind("<ButtonRelease-1>", self.spellChecker)
        self.nav_up = self.notepad.bind("<Up>", self.spellChecker)
        self.nav_down = self.notepad.bind("<Down>", self.spellChecker)
        self.nav_left = self.notepad.bind("<Left>", self.spellChecker)
        self.nav_right = self.notepad.bind("<Right>", self.spellChecker)

        # check each word's spelling after typed and mark it up
        self.notepad.bind("<space>", self.markUp)
        self.notepad.bind(".", self.markUp)

        # keep calling autocomplete while user is writing
        for letter in "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM":
            self.notepad.bind("<KeyRelease-" + letter + ">", self.autoComplete)
        self.notepad.bind("<KeyRelease-BackSpace>", self.autoComplete)

        # bind file shortcuts
        self.notepad.bind('<Control-s>', newFileTab.saveToFile)
        self.notepad.bind('<Control-o>', newFileTab.openFile)
        self.notepad.bind('<Control-n>', newFileTab.createFile)
        self.notepad.bind('<Control-c>', newFileTab.copySelected)
        self.notepad.bind('<Control-x>', newFileTab.cutSelected)
        self.notepad.bind('<Control-v>', newFileTab.pasteClipboard)

    # this function creates the top menu bar including all functionalities
    def createMenuBar(self):
        menuBar = Menu(self.window)
        # create drop-down options for the file menu
        fileMenu = tk.Menu(menuBar, tearoff=0)
        fileMenu.add_command(label="New Document", command=lambda: newFileTab.createFile(self.tabsOpen))
        fileMenu.add_command(label="Open Local File", command=lambda: newFileTab.openFile(self.tabsOpen))
        fileMenu.add_command(label="Save file", command=lambda: newFileTab.saveToFile(self.tabsOpen))
        fileMenu.add_separator()
        fileMenu.add_command(label="Close File", command=lambda: newFileTab.closeFile(self.tabsOpen))
        fileMenu.add_command(label="Exit", command=lambda: newFileTab.quit(self.tabsOpen))
        menuBar.add_cascade(label="File", menu=fileMenu)

        # create drop-down options for the edit menu
        editMenu = tk.Menu(menuBar, tearoff=0)
        editMenu.add_command(label="Undo", command=lambda: newFileTab.undoEdit(self.tabsOpen))
        editMenu.add_command(label="Redo", command=lambda: newFileTab.redoEdit(self.tabsOpen))
        editMenu.add_command(label="Copy", command=lambda: newFileTab.copySelected(self.tabsOpen))
        editMenu.add_command(label="Cut", command=lambda: newFileTab.cutSelected(self.tabsOpen))
        editMenu.add_command(label="Paste", command=lambda: newFileTab.pasteClipboard(self.tabsOpen))
        menuBar.add_cascade(label="Edit", menu=editMenu)

        self.window.config(menu=menuBar)

    '''icon pics retrieved from:
    https://icons-for-free.com/folder+open+icon-1320161390409087972/'''

    # this function creates the tool bar with clickable icon shortcuts for the functionalities
    def createToolBar(self, labelFrame):
        # add icon for handling creating new files
        new_img = tk.PhotoImage(file="newicon.png")
        new_img = new_img.zoom(1)
        new_img = new_img.subsample(15)

        # add icon for handling opening local files
        open_img = tk.PhotoImage(file="openicon.png")
        open_img = open_img.zoom(1)
        open_img = open_img.subsample(15)

        # add icon for handling saving files
        save_img = tk.PhotoImage(file="saveicon.png")
        save_img = save_img.zoom(1)
        save_img = save_img.subsample(4)

        # add icon for handling copying from files
        copy_img = tk.PhotoImage(file="copyicon.png")
        copy_img = copy_img.zoom(1)
        copy_img = copy_img.subsample(4)

        # add icon for handling cutting from files
        cut_img = tk.PhotoImage(file="cuticon.png")
        cut_img = cut_img.zoom(1)
        cut_img = cut_img.subsample(4)

        # add icon for handling cutting from clipboard
        paste_img = tk.PhotoImage(file="pasteicon.png")
        paste_img = paste_img.zoom(1)
        paste_img = paste_img.subsample(4)

        # add icon for handling undo edits
        undo_img = tk.PhotoImage(file="undoicon.png")
        undo_img = undo_img.zoom(1)
        undo_img = undo_img.subsample(4)

        # add icon for handling redo edits
        redo_img = tk.PhotoImage(file="redoicon.png")
        redo_img = redo_img.zoom(1)
        redo_img = redo_img.subsample(4)

        # add icon for handling closing current file tab
        close_img = tk.PhotoImage(file="closeicon.png")
        close_img = close_img.zoom(1)
        close_img = close_img.subsample(4)

        # create all respective buttons and configure them to their appropriate icons and function calls
        new_button = tk.Button(labelFrame, image=new_img, command=lambda: newFileTab.createFile(self.tabsOpen))
        open_button = tk.Button(labelFrame, image=open_img, command=lambda: newFileTab.openFile(self.tabsOpen))
        save_button = tk.Button(labelFrame, image=save_img, command=lambda: newFileTab.saveToFile(self.tabsOpen))
        copy_button = tk.Button(labelFrame, image=copy_img, command=lambda: newFileTab.copySelected(self.tabsOpen))
        cut_button = tk.Button(labelFrame, image=cut_img, command=lambda: newFileTab.cutSelected(self.tabsOpen))
        paste_button = tk.Button(labelFrame, image=paste_img, command=lambda: newFileTab.pasteClipboard(self.tabsOpen))
        undo_button = tk.Button(labelFrame, image=undo_img, command=lambda: newFileTab.undoEdit(self.tabsOpen))
        redo_button = tk.Button(labelFrame, image=redo_img, command=lambda: newFileTab.redoEdit(self.tabsOpen))
        close_button = tk.Button(labelFrame, image=close_img, command=lambda: newFileTab.closeFile(self.tabsOpen))

        new_button.image = new_img
        open_button.image = open_img
        save_button.image = save_img
        copy_button.image = copy_img
        cut_button.image = cut_img
        paste_button.image = paste_img
        undo_button.image = undo_img
        redo_button.image = redo_img
        close_button.image = close_img

        # grid the buttons appropriately onto the tab frame
        new_button.grid(row=1, column=1)
        open_button.grid(row=1, column=2)
        save_button.grid(row=1, column=3)
        copy_button.grid(row=1, column=4)
        cut_button.grid(row=1, column=5)
        paste_button.grid(row=1, column=6)
        undo_button.grid(row=1, column=7)
        redo_button.grid(row=1, column=8)
        close_button.grid(row=1, column=10)

    # this function takes automatically the first choice from the suggestion
    # box and replaces it with the word that is underlined as misspelt
    def autoCorrect(self, event):
        lastWord = self.getLastWord()
        if self.spellCheckerList(lastWord):
            # get first suggestiosn from listbox contents
            bestSuggestion = self.spellCheckerList(lastWord)[0]
            # configure and find first and last index of word to be replaced
            start = self.notepad.get('1.0', tk.END).index(lastWord)
            end = start + len(lastWord)
            line_num = int(float(self.notepad.index(tk.CURRENT)))
            start_i = str(line_num) + '.' + str(start)
            end_i = str(line_num) + '.' + str(end)
            # delete the misspelled word by the best suggestion in text widget
            self.notepad.delete(start_i, end_i)
            self.notepad.insert(start_i, bestSuggestion)

    # this function unbinds the arrows with the list from the dictionary
    # so that the list dosen't appear when pressing the auto-correct option
    def switchSpellChecker(self):
        self.notepad.unbind('<ButtonRelease-1>')
        self.notepad.unbind('<Up>')
        self.notepad.unbind('<Down>')
        self.notepad.unbind('<Left>')
        self.notepad.unbind('<Right>')
        self.notepad.unbind("<space>")
        # if the autocorrect option is pressed
        if self.var.get():
            # replace the spellchecker bindings to autocorrect
            self.notepad.bind("<space>", self.autoCorrect)
            self.notepad.bind(".", self.autoCorrect)
        # if it is not pressed
        else:
            # rebind the orginal keys for the spellchecker listbox functionality
            self.notepad.bind("<ButtonRelease-1>", self.spellChecker)
            self.notepad.bind("<Up>", self.spellChecker)
            self.notepad.bind("<Down>", self.spellChecker)
            self.notepad.bind("<Left>", self.spellChecker)
            self.notepad.bind("<Right>", self.spellChecker)

            # check each word's spelling after typed and mark it up
            self.notepad.bind("<space>", self.isSpeltCorrect)
            self.notepad.bind(".", self.isSpeltCorrect)

    # this function gets the last word that was typed by the user
    def getLastWord(self):
        # split all input text at all white space characters (e.g. space, tab, enter)
        wordsList = re.split("\s+", self.notepad.get("1.0", tk.END))
        # remove last empty string
        wordsList.remove('')
        # last word is at the last index of the words list
        lastWord = wordsList[len(wordsList) - 1]
        # remove unnecessary punctuations next to the last word
        lastWord_stripped = lastWord.translate(str.maketrans('', '', string.punctuation))
        return lastWord_stripped.lower()

    # here we edit the words that are misspelt after
    # getting the words from the screen and correct their form
    def spellCheckerList(self, word_to_check):
        edits = {}
        # if there's no word selected or a space is selected
        if word_to_check == "" or word_to_check == " ":
            return
        # if the word is misspelt, record its respective edit distances and frequencies
        elif not self.isSpeltCorrect(word_to_check):
            # compute for min edit distance from each word in dictionary
            for word in self.vocab:
                edits_num = self.minEditDistance(word_to_check, word)
                # record all words corresponding to edits numbers 1 and 2 in a dictionary
                if edits_num <= 2:
                    # if there is a key in the dictionary corresponding to the same edit distance
                    if edits_num in edits:
                        # add it to its list of values
                        edits[edits_num].append(word)
                    else:
                        # if not, create a new key for the number of edits and add it
                        edits[edits_num] = [word]

        # record and sort frequencies of words corresponding for 1 edit and 2 edits
        freqs1 = []
        freqs2 = []
        # sorting words with edit distance 1 one based on frequency
        if 1 in edits:
            for similar_word in edits.get(1):
                # record frequency of each word with the same edit distance
                freq = self.vocab.get(similar_word)
                freqs1.append(freq)
        # sorting words with edit distance 1 one based on frequency
        if 2 in edits:
            for similar_word in edits.get(2):
                # record frequency of each word with the same edit distance
                freq = self.vocab.get(similar_word)
                freqs2.append(freq)
        # rearrange frequencies individually
        freqs1.sort()
        freqs2.sort()
        # combine the two frequency lists in order of 1 then 2 to get appropriate suggestions list
        # the smallest edit distance if the first priority, then its frequency
        freqs = freqs1 + freqs2
        suggestions = []
        for f in freqs:
            for word in self.vocab:
                # get words based on their corresponding frequencies in order
                if self.vocab.get(word) == f:
                    # add each corresponding word to the suggestions list
                    suggestions.append(word)
        return suggestions

    '''STILL TO DO, CONSIDER CAPITALIZATION IN SPELLCHECKER and replacement word/pop-up lists'''

    # this function checks if the word is spelt correctly or not
    # it returns a boolean value based on this condition
    def isSpeltCorrect(self, word):
        if word in self.vocab:
            return True
        return False

    # this functions recognizes the word and finds similar words
    # depending on their frequency, this will be then added to the
    # suggestion list. this function updates after typing each charachter
    def autoCompleteList(self, e):
        typed_word = self.getCurrWord(e).lower()
        if typed_word == "":
            return
        freqs = []
        suggestions = []
        inp_length = len(typed_word.split("/n"))
        for word in self.vocab:
            # check for english words that start with the same characters
            if word[:inp_length].lower() == typed_word:
                print('hi')
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

    # this function takes the list of words suggested if any and
    # inserts them on the screen in the autocomplete suggestions listbox
    def autoComplete(self, event):
        self.autoComplete_suggestions.destroy()
        self.autoComplete_suggestions = tk.Listbox(window)
        myFont = Font(family="Calibri", size=15)
        self.autoComplete_suggestions.configure(font=myFont)
        word = self.getCurrWord(event).lower()
        # ignore autocomplete call if the word is empty
        if not word:
            return
        # if there is one character typed
        if len(word) == 1:
            # use pre-loaded dictionary to get suggestiosn into listbox
            suggestions = self.startWithSameLetter.get(word)
            i = 0
            # add the first 10 word suggestions, as long as they exist
            while i < 11 and i < len(suggestions):
                for l in suggestions:
                    # add them to the suggestions listbox in order
                    self.autoComplete_suggestions.insert(i, l + " ")
                    i += 1
        else:
            # if typed portion is a part of a valid word
            if self.autoCompleteList(event):
                # get autocomplete list and append its first 10 values into the listbox
                suggestions = self.autoCompleteList(event)[:10]
                for i in range(len(suggestions)):
                    self.autoComplete_suggestions.insert(i, suggestions[i] + " ")
            # if not, indicate lack of matches on listbox
            else:
                self.autoComplete_suggestions.insert(0, "No matches found.")

        # remove duplicate words in the suggestions listbox and the typed word
        if word in self.autoComplete_suggestions.get(0, tk.END):
            index = self.autoComplete_suggestions.get(0, tk.END).index(word)
            # delete duplicate word from suggestions listbox
            self.autoComplete_suggestions.delete(index)
            # if there are more suggestions available after 10, add the next one
            if len(self.autoCompleteList(event)) >= 11:
                self.autoComplete_suggestions.insert(10, self.autoCompleteList(event)[10] + " ")

        # place the listbox where the typing cursor is
        (x, y, w, h) = self.notepad.bbox('insert')
        self.autoComplete_suggestions.place(x=x + 140, y=y + 200, anchor="center")
        self.autoComplete_suggestions.bind('<<ListboxSelect>>', self.autoCompleteClickSelect)


    # this function also draws a list box with all the suggested words that
    # could replace the misspelt word.
    def spellChecker(self, event):
        self.autoComplete_suggestions.destroy()
        self.autoCorrect_suggestions.destroy()
        self.autoCorrect_suggestions = tk.Listbox(self.labelFrame)
        myFont = Font(family="Calibri", size=15)
        self.autoCorrect_suggestions.configure(font=myFont)
        # if the selected word is the one being currently typed
        # autocomplete it and don't spellcheck it (word not fully typed yet)
        if self.getCurrWord(event) and self.getNavigWord(event):
            self.autoComplete(event)
            return
        word = self.getNavigWord(event)
        # if the suggestions listbox is not empty, clear it
        if len(self.autoCorrect_suggestions.get(0, tk.END)) != 0:
            self.autoCorrect_suggestions.delete(0, tk.END)
        # exit spell checker if the word is spelt correctly
        if self.isSpeltCorrect(word):
            return
        # if current word is not empty and is spelled incorrectly
        elif len(self.notepad.get('1.0', 'end-1c')) != 0:
            if self.spellCheckerList(word):
                # append first 10 suggestions into listbox
                suggestions = self.spellCheckerList(word)[:10]
                for i in range(len(suggestions)):
                    self.autoCorrect_suggestions.insert(i, suggestions[i])
            else:
                # if not close matches from min edit function, display appropriate message
                self.autoCorrect_suggestions.insert(0, "No matches found.")
                self.autoCorrect_suggestions.insert(1, "Add word to dictionary")

        if len(word) != 1:
            # place the listbox where the cursor is
            (x, y, w, h) = self.notepad.bbox('insert')
            self.autoCorrect_suggestions.place(x=x + 100, y=y + 120, anchor="center")

        self.autoComplete_suggestions = tk.Listbox(self.labelFrame)
        myFont = Font(family="Calibri", size=15)
        self.autoComplete_suggestions.configure(font=myFont)
        self.autoCorrect_suggestions.bind('<<ListboxSelect>>', self.autoCorrectClickSelect)

    # this function takes the selection that the user made from the suggestion box
    # and overwrites the word in he screen
    def autoCorrectClickSelect(self, event):
        selected_word = self.autoCorrect_suggestions.get(self.autoCorrect_suggestions.curselection())
        # get the entire word the cursor is on
        navigWord = self.getNavigWord(event)
        if selected_word == "No matches found.":
            self.autoCorrect_suggestions.destroy()
            return
        elif selected_word == "Add word to dictionary":
            self.vocab[navigWord] = len(self.vocab) + 1
        else:
            start = self.notepad.get('1.0', tk.END).index(navigWord)
            end = start + len(navigWord)
            line_num = int(float(self.notepad.index(tk.CURRENT)))
            # configure start and end indices of the word to be corrected syntax correctly
            start_i = str(line_num) + '.' + str(start)
            end_i = str(line_num) + '.' + str(end)
            # delete the misspelled word and replace it by the correct one selected from the listbox
            self.notepad.delete(start_i, end_i)
            self.notepad.insert(start_i, selected_word)

        if self.autoCorrect_suggestions.winfo_exists:
            self.autoCorrect_suggestions.destroy()

    # this function takes the selection that the user made from the suggestion box
    # and overwrites the word in the screen for the autocomplete option
    def autoCompleteClickSelect(self, event):
        if self.autoComplete_suggestions.curselection():
            selected_word = self.autoComplete_suggestions.get(self.autoComplete_suggestions.curselection())

            if selected_word == "No matches found.":
                self.autoComplete_suggestions.destroy()
                return
            # get the partial word currently being typed
            currWord = self.getCurrWord(event).lower()
            # configure start and end indices of the word to be corrected syntax correctly
            start = self.notepad.get('1.0', tk.END).index(currWord)
            end = start + len(currWord)
            line_num = int(float(self.notepad.index(tk.CURRENT)))
            start_i = str(line_num) + '.' + str(start)
            end_i = str(line_num) + '.' + str(end)
            # delete the misspelled word and replace it by the correct one selected from the listbox
            self.notepad.delete(start_i, end_i)
            self.notepad.insert(start_i, selected_word)
            self.autoComplete_suggestions.destroy()

    # this function underlines the word that is misspelt and
    # colors it with red
    def markUp(self, misspelt_word):
        lastWord = self.getLastWord()
        # if word contains numbers of special characters, don't mark it up
        if not lastWord.isalpha() :
            return
        self.autoComplete_suggestions.destroy()
        # search for starting index of the misspelt word
        index = self.notepad.search(r'\s', "insert", backwards=True, regexp=True)
        if index == "":
            index = "1.0"
        else:
            index = self.notepad.index("%s+1c" % index)
        word = self.notepad.get(index, "insert").translate(str.maketrans('', '', string.punctuation))
        # if word spelled correctly, remove pre-set misspelling tag
        if word.lower() in self.vocab:
            self.notepad.tag_remove("misspelling", index, "%s+%dc" % (index, len(word)))
        else:
            self.notepad.tag_add("misspelling", index, "%s+%dc" % (index, len(word)))

    '''modfiied code from: 
    https://stackoverflow.com/questions/3732605/add-advanced-features-to-a-tkinter-text-widget'''


    # This function finds the minimum edit distance using a modified version of the Levistein algorithm
    # This is my own implementation of the algorithm
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

    # this function gets the word that the cursor is hovering over in the text widget
    # and returns it.
    def getNavigWord(self, event):
        start = self.notepad.index("insert wordstart")
        end = self.notepad.index("insert wordend")
        nav_word = self.notepad.get(start, end)
        # remove unnecessary punctuations next to the typed word
        nav_word_stripped = nav_word.translate(str.maketrans('', '', string.punctuation))
        return nav_word_stripped.lower()

    # this function gets the word that is being modified currently from the user
    # and returns it.
    def getCurrWord(self, event):
        all_typed = self.notepad.get("1.0", "end")
        i = all_typed.rfind(" ")
        curr_word = all_typed[i + 1:].strip()
        # remove unnecessary punctuations next to the typed word
        curr_word_stripped = curr_word.translate(str.maketrans('', '', string.punctuation))
        return curr_word_stripped.lower()

# this class contains all the file functionality functions for creating a new file tab
class newFileTab():
    # this function creates a new texteditor tab for a new file
    def createFile(self, *args):
        texteditor.autoComplete_suggestions.destroy()
        texteditor.autoCorrect_suggestions.destroy()
        # Create new tab
        newTab = ttk.Frame(textEditor.alltabs)
        tabs = textEditor.alltabs #texteditor.tabs
        tabs.add(newTab, text='Untitled')
        tabs.select(newTab)
        # make tab have textEditor functionality and characteristics
        tabsOpen[newTab] = textEditor(texteditor.window, newTab, tabs, texteditor.vocab, \
                                      texteditor.startWithSameLetter, tabsOpen)

    # this function records the selected text from a specific tab in clipboard for later use
    def copySelected(self):
        # get current tab and its respective text editor object
        active_tab = texteditor.tabs._nametowidget(texteditor.tabs.select())
        curr_textEditor_obj = texteditor.tabsOpen[active_tab]
        # see if there was text selected
        try:
            tabs = texteditor.tabsOpen[active_tab]
            # get selected text from specific text widget in current tab
            selected = curr_textEditor_obj.notepad.get(tk.SEL_FIRST, tk.SEL_LAST)
            # clear any preexisting content in clipboard
            texteditor.window.clipboard_clear()
            # update clipboard content to be the selected text
            texteditor.window.clipboard_append(selected)
        # if not, don't crash/do anything
        except tk.TclError:
            pass

    # this function opens and copies a chosen local file's contents in a new tab
    def openFile(self, *args):
        texteditor.autoComplete_suggestions.destroy()
        texteditor.autoCorrect_suggestions.destroy()
        # open dialogue to choose a local file (limited to .txt files)
        # file path olds the directory path of the chosen file
        file_path = tk.filedialog.askopenfilename(filetypes=(("text files", "*.txt"), \
                                                             ("all files", "*.*")))
        # extract file name from its respective file directory path
        file_path_list = file_path.split('/')
        file_name = file_path_list[len(file_path_list) - 1]
        # if the user chose a valid file
        if file_path:
            # the file is not already open in the existing tabs
            if file_name not in tabsOpen:
                try:
                    # create the new tab/tab frame for the file
                    newTab = ttk.Frame(texteditor.tabs)
                    textEditor.alltabs.add(newTab, text=file_name)
                    tabs = textEditor.alltabs
                    tabs.select(newTab)
                    # apply texteditor functionality on the tab/tab frame
                    tabsOpen[newTab] = textEditor(texteditor.window, newTab, tabs, texteditor.vocab, \
                                                  texteditor.startWithSameLetter, tabsOpen, file_path)
                    # read the contents of the selected local file
                    with open(file_path, "r") as local_file:
                        # insert its contents into the textbox corresponding to the
                        # new tab frame that was created
                        tabsOpen[newTab].notepad.insert(tk.END, local_file.read())
                except:
                    return
            # if file already open, display appropriate message
            else:
                messagebox.showinfo("Invalid File", "Selected file is already open.")

    # this function records the selected text from a specific tab in clipboard for later use
    # and deletes it from teh current tab textbox
    def cutSelected(self):
        active_tab = texteditor.tabs._nametowidget(texteditor.tabs.select())
        curr_textEditor_obj = texteditor.tabsOpen[active_tab]
        # if there was text selected
        try:
            tabs = texteditor.tabsOpen[active_tab]
            # get selected text from specific text widget in current tab
            selected = curr_textEditor_obj.notepad.get(tk.SEL_FIRST, tk.SEL_LAST)
            # clear any preexisting content in clipboard
            texteditor.window.clipboard_clear()
            # update clipboard content to be the selected text
            texteditor.window.clipboard_append(selected)
            # delete the cut content from the text widget in the current tab
            curr_textEditor_obj.notepad.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass

    # this function saves the tab's text widget's content to a new file specified by the user
    def saveToFile(self):
        active_tab = texteditor.tabs._nametowidget(texteditor.tabs.select())
        curr_textEditor_obj = texteditor.tabsOpen[active_tab]
        # if a valid file path/name is provided (not empty or untitled)
        if curr_textEditor_obj.file_path:
            # write the contents of the current tab's text widget into the same file
            # file is modified since it exists as a directory
            with open(curr_textEditor_obj.file_path, 'w') as file:
                textbox_content = curr_textEditor_obj.notepad.get(1.0, 'end')
                file.write(textbox_content)
        # if not, file is a new file
        else:
            # ask for file name
            file_path = tk.filedialog.asksaveasfilename(filetypes=(("text files", "*.txt"),\
                                                                   ("all files", "*.*")))
            # and continue if it is valid
            if not file_path:
                return

            # get chosen filename and update the current tab title
            file_path_list = file_path.split('/')
            file_name = file_path_list[len(file_path_list) - 1]
            curr_textEditor_obj.file_name = file_name
            texteditor.tabs.tab(active_tab, text=curr_textEditor_obj.file_name)

            # write the contents of the current tab's text widget into a file
            # file is created if its name doesn't exist or modified if it exists
            with open(file_path, "w") as new_file:
                content = tabsOpen[active_tab].notepad.get(1.0, tk.END)
                new_file.write(content)

    # this function inserts the clipbaoard contents into te current tab textbox
    def pasteClipboard(self):
        texteditor.autoComplete_suggestions.destroy()
        texteditor.autoCorrect_suggestions.destroy()
        active_tab = texteditor.tabs._nametowidget(texteditor.tabs.select())
        curr_textEditor_obj = texteditor.tabsOpen[active_tab]
        # if there is something copied/cut in hte clipboard
        try:
            # write the contents of the current tab's text widget into a file
            clipboard_content = texteditor.window.clipboard_get()
            curr_textEditor_obj.notepad.insert(tk.INSERT, clipboard_content)
        except tk.TclError:
            pass

    # this function closes the currently open file, as long as it is not the last one remaining
    def closeFile(self):
        tabs = texteditor.tabs
        # get number of tabs open
        tabs_num = tabs.index(tk.END)
        active_tab = texteditor.tabs._nametowidget(texteditor.tabs.select())
        curr_textEditor_obj = texteditor.tabsOpen[active_tab]
        file_name = curr_textEditor_obj.file_name
        # only close the file if there is at least another file tab open
        if tabs_num > 1:
            # remove currently selected tab from the notebook tabs
            tabs.forget(tabs.select())
        # else verify user wants to close the last file
        else:
            response = messagebox.askokcancel("File Close Error", "Closing " \
                                              + file_name + " will close entire window?")
            if response:
                # if yes, destroy the texteditor app
                window.destroy()

    # this function quits the application after verifying lost changes
    def quit(self):
        # verify user saved all new file contents
        response = messagebox.askokcancel("Are you sure you want to quit?", \
                                          "You will lose all your progress if the files are not saved.")
        if response:
            # if yes, destroy the texteditor app
            window.destroy()

    # this function verifies if user wants to close the current file tab and makes changes
    # according to the response
    def closeCheck(self):
        active_tab = texteditor.tabs._nametowidget(texteditor.tabs.select())
        curr_textEditor_obj = texteditor.tabsOpen[active_tab]
        file_path = curr_textEditor_obj.file_name
        file_path_list = file_path.split('/')
        file_name = file_path_list[len(file_path_list) - 1]
        curr_textEditor_obj.file_name = file_name
        # display verification message for saving before closing
        response = messagebox.askyesnocancel("Exit", "Would you like to save changes to " + file_name + "?")
        # if user responded with cancel, return to texteditor(s)
        if response == None:
            return
        # if user responded with yes, save the file
        if response:
            # if a valid file path/name is provided (not empty or untitled)
            if curr_textEditor_obj.file_path:
                # write the contents of the current tab's text widget into the same file
                # file is modified since it exists as a directory
                with open(curr_textEditor_obj.file_path, 'w') as file:
                    file.write(curr_textEditor_obj.notepad.get(1.0, 'end'))
            # if not, file is a new file
            else:
                # ask for file name
                file_path = tk.filedialog.asksaveasfilename(filetypes=(("text files", "*.txt")\
                                                                           , ("all files", "*.*")))
                # and continue if it is valid
                if not file_path:
                    return
                # update file tab name accordingly
                texteditor.tabs.tab(active_tab, text=curr_textEditor_obj.file_name)
                # write tab frame textbox contents into a new file that is created/modified
                with open(file_path, "w") as new_file:
                    content = tabsOpen[active_tab].notepad.get(1.0, tk.END)
                    new_file.write(content)
            # close the application after saving
            window.destroy()
        # if user responded with no
        else:
            # immediately destroy window (progress not saved)
            window.destroy()

    # this function undos the last action that was done on the specific tab frame
    # that the user is active on
    def undoEdit(self):
        texteditor.autoComplete_suggestions.destroy()
        texteditor.autoCorrect_suggestions.destroy()
        # if the textbox of the current tab frame is not empty
        try:
            tabsOpen = texteditor.tabsOpen
            active_tab = texteditor.tabs._nametowidget(texteditor.tabs.select())
            # undo it using pre-set command
            tabsOpen[active_tab].notepad.edit_undo()
        except:
            return

    # this function redos the last action that was done on the specific tab frame
    # that the user is active on
    def redoEdit(self):
        texteditor.autoComplete_suggestions.destroy()
        texteditor.autoCorrect_suggestions.destroy()
        # if the textbox of the current tab frame is not empty
        try:
            tabsOpen = texteditor.tabsOpen
            active_tab = texteditor.tabs._nametowidget(texteditor.tabs.select())
            # redo it using pre-set command
            tabsOpen[active_tab].notepad.edit_redo()
        except:
            return


window = tk.Tk()

# import stored pickle dictionary of words
with open("engDic.pkl", "rb") as pickle_dic:
    vocab = pickle.load(pickle_dic)

# import stored pickle dictionary of words with same letter beginning
with open("letterStartDic.pkl", "rb") as pickle_dic:
    startWithSameLetter = pickle.load(pickle_dic)

# create a dictionary that keeps track of each texteditor's content
# its keys are the tab frames and values are the texteditor objects for
# each respective frame
tabsOpen = {}
tabs = ttk.Notebook(window)
tabs.grid(row=0, column=0, columnspan=40, rowspan=39, sticky="NESW")

# create first tab frame
tab1 = ttk.Frame(tabs)
tabs.add(tab1, text='Untitled')
labelFrame = ttk.LabelFrame(tab1, width=1000, height=1000)
labelFrame.grid(row=0, column=3, sticky="NSEW")
labelFrame.grid_propagate(False)

# add first tab frame to dictionary
tabsOpen[tab1] = textEditor(window, labelFrame, tabs, vocab, startWithSameLetter, tabsOpen)
textEditor.alltabs = tabs
texteditor = tabsOpen[tab1]

window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)
window.geometry("950x950")

window.mainloop()

'''if autocorrect then autocorrect error with index'''