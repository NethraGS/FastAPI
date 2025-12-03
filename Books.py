from fastapi import Body,FastAPI

app = FastAPI()

BOOKS=[
    {
        'title':'My first book','author':'author1','category':'maths'
    },
    {
        'title':'My second book','author':'author2','category':'science'
    },
    {
        'title':'My third book','author':'author3','category':'computer'
    },
    {
        'title':'My fourth book','author':'author4','category':'circuit'
    },
    {
        'title':'My fifth book','author':'author1','category':'dsa'
    }
]
@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/byauthor/{author}")
async def read_books_by_author_path(author:str):
    books_to_return=[]
    for book in BOOKS:
        if book.get('author').casefold()==author.casefold():
            books_to_return.append(book)
    

@app.get("/books/{book_title}")
async def read_all_books(book_title:str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book

#search by category
@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

@app.get("/books/{book_author}")
async def read_author_category_by_query(book_author: str,category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
            book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

@app.post("/books/create_book")
async  def create_book(new_book=Body()):
    BOOKS.append(new_book)

@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold()==updated_book.get('title').casefold():
            BOOKS[i]=updated_book

@app.delete("/books/delete_book?{book_title}")
async def delete_book(book_title:str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold()==book_title.casefold():
            BOOKS.pop(i)
            break



