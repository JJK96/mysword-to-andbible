import sqlite3
import datetime
from html2text import html2text

versification='Calvin'

books = None
def book_index():
    """ Build book index """
    global books
    books = {}
    with open('bijbelboeken.csv') as f:
        for line in f.readlines():
            line = line[:-1].split(',')
            books[int(line[3])] = line


book_index()

def import_versenotes(dst):
    dst = dst.cursor()
    notes_db = sqlite3.connect('versenotes.mybible')
    notes_db.row_factory = sqlite3.Row
    src = notes_db.cursor()
    src.execute('select book, chapter, fromverse, toverse, data, date, dateUpdated, title from commentary')
    mynotes = []
    for row in src.fetchall():
        text = ""
        if (row['title']):
            text += row['title'] + "\n"
        text += row['data']
        osis_book = books[row['book']][5]
        chapter_id = "{}.{}".format(osis_book, row['chapter'])
        key = "{}.{}-{}.{}".format(chapter_id, row['fromverse'], chapter_id, row['toverse'])
        mynote = (key, versification, html2text(text).strip(), row['dateUpdated'], row['date'])
        mynotes.append(mynote)
    dst.executemany('insert into mynote (key, versification, mynote, last_updated_on, created_on) values (?,?,?,?,?)', mynotes)

colors = {
    1: 2, #red
    2: 2, #orange
    3: 3, #yellow
    4: 1, #green
    5: 1, #green
    6: 4, #blue
    7: 4, #blue
    8: 4, #purple
    9: 4, #purple
    10: 4, #pink
}

def import_highlight(dst):
    dst = dst.cursor()
    highlight_db = sqlite3.connect('highlight.mybible')
    highlight_db.row_factory = sqlite3.Row
    src = highlight_db.cursor()
    src.execute("select * from highlight where color > 0")
    highlights = []
    bookmark_labels = []
    id = 0
    for row in src.fetchall():
        created_on = datetime.datetime.now()
        osis_book = books[row['bookid']][5]
        key = "{}.{}.{}".format(osis_book, row['chapter'], row['verse'])
        highlight = (id, created_on, key, versification)
        highlights.append(highlight)
        bookmark_label = (id, colors[row['color']])
        bookmark_labels.append(bookmark_label)
        id += 1
    dst.executemany('insert into bookmark (_id, created_on, key, versification) values (?,?,?,?)', highlights)
    dst.executemany('insert into bookmark_label (bookmark_id, label_id) values (?,?)', bookmark_labels)
   

andbible = sqlite3.connect('andBibleDatabase.db')
#import_versenotes(andbible)
import_highlight(andbible)
andbible.commit()
andbible.close()

