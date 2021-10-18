import sys
import re
import json

CommandPath = "startup.txt"
LibraryFilepath = "library.txt"
CommandList = ["insert", "query", "update", "delete", "exit"]

''' Class InputRead:
    -takes input from a file that has a list of commands
    -reads and interprets requested action 
    -creates an instance of Library class 
    -instructs Library what to do.
'''
class InputRead:
    def __init__(self, path):
        self.path = path
    
    def openCommands(self):
        commands = []
        file = open(self.path, 'r')
        commandFile = file.readlines()
    
        for line in commandFile:
            commands.append(line.strip()) #strip removes end of line characters (\n)
        return commands

    def readCommands(self):
        # Make an instance of Library class (open the library inventory)
        library = Library()
        #Read from file the list of commands to execute
        commands = self.openCommands()
    
        for cmd in commands:         
            words = cmd.split()      #Split words by empty spaces  
            command = words[0]       #Get first word which is a command

            if command == "exit":    #If command is "exit" break the loop and close
                print("Goodbye!")
                break   
                
            elif len(cmd) == 0:      #Raise an error  
                command = None
                print("Please provide input.")
                return

            
            elif command == "insert":
                booktype = words[1]
                if booktype not in ["p", "e"]:
                    raise Exception("Book format <", booktype.strip() , "> is not valid. \
                    Enter valid book format: e for ebooks or p for physical paper books.")

                quoted_words = re.findall(r'\"(.+?)\"', cmd)
                title = quoted_words[0]
                author = quoted_words[1]
                stock = re.findall("[-]?\d+$", cmd)[0]
                library.insert(booktype.strip(), title, author, int(stock))
                print("\n")

            elif command == "delete":
                ID = words[1]
                if not ID:
                    raise Exception("No ID number given. \n")
                else:
                    print("Book to be deleted: ", command, int(ID))
                    library.delete(ID)    
                print("\n")

            elif command == "query":
                t = words[1]
                term = re.findall(r'\"(.+?)\"', cmd)[0]
                library.query(t, term)
                print("\n")

            elif command == "update":
                ID = words[1]
                modifier = words[2]
                library.update(int(ID), int(modifier))
                print("\n")

            else:
                print("This command was not recognized. ")
                return


'''class Library:
    -Opens library book inventory file
    -reads and writes requested book records 
'''
class Library:
    def __init__(self):
        self.books = self.readFile()
        self.ID = 1000
    
    def readFile(self):
        try:
            with open(LibraryFilepath, 'r') as inventory:
                return json.loads(inventory.read())
        except:
            return []
    
    def writeFile(self):        
        with open(LibraryFilepath, 'w') as inventory:
            json_text = json.dumps(self.books)
            inventory.write(json_text)
    
    def get_ID(self):  
        
        all_IDS = [item.get('id') for item in self.books]
        if not all_IDS :
            new_ID = self.ID
        else:
            new_ID = max(all_IDS) +1
        
        # create unique ID
        return int(new_ID)
    
    def bookFormat(self, bookType):
        if bookType == 'p':
            return 'physical'
        else:
            return 'electronic'
        
    def query(self, t, term):
        #A command to query the database.
        
        found_idx = None

        if t == "a":
            search_term = "author"
        elif t == "t":
            search_term = "title"
        else: 
            print("Error. This search term is not valid.\n")
            return
        
        found_books = []
        i = 0
        for idx in range(len(self.books)):
            if term in self.books[idx][search_term]:
                found_idx = idx
                found_books.append(self.books[idx])
                i+=1
                print("MATCH {}: {} copy(s) - {}, {}; ID = {}".format(i, 
                        self.books[idx]['stock'], self.books[idx]['title'], 
                        self.books[idx]['author'], self.books[idx]['id']))
        
        if len(found_books) == 0:
            print("Error. No maching books were found.\n")
            return

        return found_books
    
    
    def update(self, ID, modifier):
        #modify the stock of an existing book by its ID.
        
        for book in self.books:
            if book['id'] == ID:
                book['stock'] +=modifier  
    
                bookFormat = self.bookFormat(book['bookType'])
                print("Success: Modified stock of {} book {} by {} by {}; now with {} copy(s).".format(bookFormat, 
                            book["title"], book["author"], modifier, book['stock']))
                return book['stock']
        
    def insert(self, bookType, title, author, stock):
        #A command to insert a new book into the database.
        found_book = None
        bookFormat = self.bookFormat(bookType)
        
        for book in self.books:
            #If a book of the same type, title, and author already exists in the database, simply add
            #the specified stock to that entry.
            if book['title'] == title and book['author'] == author and book['bookType'] == bookType:
                found_book = book      
                book['stock'] = self.update(book['id'], stock)
                
                update_word = None
                if int(stock) > 0:
                    update_word = "Added"
                else:
                    update_word = "Removed"
                    
                print("Book with this ID already exists. {} {} stock of a {} book:\n{} by {} now with {} copy(s), ID = {}".format(update_word, 
                                    stock, bookFormat, title, author, book['stock'], book['id']))  
                
        #Otherwise, create a new entry with a new unique ID for this book.
        if found_book is None:
            
            book_ID = self.get_ID()
            self.books.append(dict(id=book_ID, bookType=bookType, 
                        title=title, author=author, stock=stock))
            print("Created a new entry for a {} book:\n{} by {} with {} copy(s), ID = {}".format(bookFormat, 
                                                                            title, author, stock, book_ID))

        #Write to library file:              
        self.writeFile()
                         
            
    def delete(self, ID):
        #A command to delete an entry from the database, if it exists.
        
        found_idx = None
        book = None
        for idx in range(len(self.books)):
            #print(f"idx={idx}")
            if self.books[idx]['id'] == int(ID):
                found_idx = idx
                book = self.books[idx]
                break
            
        if not found_idx:
            print("Error. This book ID was not found.\n ") 
            return
        
        bookFormat = self.bookFormat(book['bookType'])       
        self.books.pop(found_idx)
        print("Success: Deleted {} copy(s) of a {} book {} by {} with ID number {}".format(book['stock'], 
                              bookFormat, book['title'], book['author'], book['id']))
        

        #Write to library file:              
        self.writeFile()
        
        
# Creating an instance of InputRead class: 
query_instance = InputRead(CommandPath)
query_instance.readCommands()

