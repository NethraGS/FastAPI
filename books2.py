from fastapi import FastAPI,Path,Query,HTTPException
from pydantic import BaseModel, Field
from starlette import status
app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id: int, title: str, author: str, description: str, rating: int,published_date: int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date=published_date



class BookRequest(BaseModel):
    id: int | None = None
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int=Field(gt=1999,lt=2031)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A good book",
                "author": "John Doe",
                "description": "This is an example description of the book.",
                "rating": 5,
                "published_date":2012
            }
        }
    }


BOOKS = [
    Book(1, 'Computer Science Pro', 'ruby', 'A very Nice book', 5,2004),
    Book(2, 'Be fast with FAASTAPI', 'ruby', 'A great book', 5,2012),
    Book(3, 'Master Endpoints', 'ruby', 'A awesome book', 5,2015),
    Book(4, 'HP1', 'author1', 'description4', 2,2005),
    Book(5, 'HP2', 'author2', 'description5', 3,2004),
    Book(6, 'HP3', 'author3', 'description6', 1,2000)
]


def find_next_book_id():
    return 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1


@app.get("/books",status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.get("/books/{book_id}",status_code=status.HTTP_200_OK)
async def read_book(book_id:int=Path(gt=0)):
    for book in BOOKS:
        if book.id==book_id:
            return book
    raise HTTPException(status_code=404,detail='Item not found')
    
@app.get("/books/",status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating:int =Query(gt=0,lt=6)):
    books_to_return=[]
    for book in BOOKS:
        if book.rating==book_rating:
            books_to_return.append(book)
    return books_to_return

@app.get("/books/publish/",status_code=status.HTTP_200_OK)
async def read_book_by_published_date(book_published_date:int=Query(gt=1999,lt=2031)):
    books_to_return_date=[]
    for book in BOOKS:
        if book.published_date==book_published_date:
            books_to_return_date.append(book)
    return books_to_return_date

@app.post("/create-book",status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_id = find_next_book_id()
    new_book = Book(
        id=new_id,
        title=book_request.title,
        author=book_request.author,
        description=book_request.description,
        rating=book_request.rating
    )
    BOOKS.append(new_book)
    return new_book

@app.put("/books/update_book",status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book:BookRequest):
    book_changed=False
    for i in range(len(BOOKS)):
        if BOOKS[i].id==book.id:
            BOOKS[i]=book
            book_changed=True
        if not book_changed:
            raise HTTPException(status_code=404,detail='Item not found')

    

@app.delete("/books/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id:int):
    book_changed=False
    for i in range(len(BOOKS)):
        if BOOKS[i].id==book_id:
            BOOKS.pop(i)
            book_changed=True
            break
    if not book_changed:
        raise HTTPException(status_code=404,detail='Item not found')