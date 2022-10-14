import csv
from sqlalchemy import create_engine 
from sqlalchemy.orm import scoped_session ,sessionmaker

engine=create_engine("postgresql://fwparifzsxuzce:e5df04221373493b7a539938c1c10f73c8ca8dda155ab2075715bc5ff8def866@ec2-52-4-87-74.compute-1.amazonaws.com:5432/ddh5o70je7p5fp")
db=scoped_session(sessionmaker(bind=engine))

f=open("books.csv")
reader=csv.reader(f)
print(reader)

for isbn,title, author,year in reader:
    db.execute("INSERT INTO books (isbn,title,author,year ) VALUES (:isbn, :title, :author,:year)",{
        "isbn": isbn , "title":title, "author":author, "year":year

            })
    print("xd")
    db.commit()