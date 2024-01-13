import sqlite3 as db
import tkinter as tk
from tkinter import scrolledtext
import random
import string
from datetime import datetime
import timeit
import re

#Connect to academia.db
def create_connection(database_name):
    try:
        connection = db.connect(database_name)
        print(f"Connected to database: {database_name}")
        return connection
    except db.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


#Set up login screen
def login_screen():
    root.title("Login Screen")
    tk.Label(root, text="Username:", font=("Helvetica", 16)).pack(pady=10)
    username_entry = tk.Entry(root, font=("Helvetica", 14))
    username_entry.pack(pady=10)

    login_button = tk.Button(root, text="Login", command=lambda: login(username_entry.get()), font=("Helvetica", 14))
    login_button.pack(pady=10)

    signup_button = tk.Button(root, text="Sign Up", command=lambda: signup(), font=("Helvetica", 14))
    signup_button.pack(pady=10)
    

#Check if user input is in database and allow access to main app
def login(username):
    try:
        cursor = connection.cursor()
        read_query = f"SELECT * FROM USER WHERE username='{username}';"
        cursor.execute(read_query)
        record = cursor.fetchall()
        if not record:
            print("Login failed: Invalid username")
        else:
            result = [list(row) for row in record]
            user_data = result[0]
            if username == user_data[3]:
                print("Login Successful!", f"Welcome, {result[0][1]}!")
                open_main_window(user_data)
            else:
                print("Login Failed: Invalid username or password")
            cursor.close()
    except db.Error as e:
        print(f"Error retrieving user data: {e}")
        

#Set up a signup window
def signup():
    signup_window = tk.Toplevel(root)
    signup_window.title("Sign Up")

    tk.Label(signup_window, text="Enter your information:", font=("Helvetica", 16)).pack(pady=10)

    tk.Label(signup_window, text="E-mail:", font=("Helvetica", 14)).pack(pady=5)
    signup_email_entry = tk.Entry(signup_window, font=("Helvetica", 14))
    signup_email_entry.pack(pady=5)

    tk.Label(signup_window, text="Full name:", font=("Helvetica", 14)).pack(pady=5)
    signup_fullname_entry = tk.Entry(signup_window, font=("Helvetica", 14))
    signup_fullname_entry.pack(pady=5)

    tk.Label(signup_window, text="Username:", font=("Helvetica", 14)).pack(pady=5)
    signup_username_entry = tk.Entry(signup_window, font=("Helvetica", 14))
    signup_username_entry.pack(pady=5)

    signup_button = tk.Button(signup_window, text="Sign Up",
                              command=lambda: on_signup_click(signup_email_entry.get(), signup_fullname_entry.get(), signup_username_entry.get()),
                              font=("Helvetica", 14))
    signup_button.pack(pady=10)
    

#Adds unverified user on database 
def on_signup_click(email, fullname, username):
    if not email or not fullname or not username:
        print("Please fill in all the fields")
        return
    try:
        cursor = connection.cursor()
        insert_query = f"INSERT INTO USER('e-mail', name, verified, username) VALUES('{email}','{fullname}','false','{username}')"
        user_data = [email, fullname, 'false', username]
        cursor.execute(insert_query)
        connection.commit()
        cursor.close()
        print(f"New user signed up with email: {email} and username: {username}\n")
        open_main_window(user_data)
    except db.Error as e:
        print(f"Error signing up: {e}")
        

#Close login window and set up main window with filtering options
def open_main_window(user):
##    usermail=user[0]
##    user_fullname=user[1]
##    verified=user[2]
##    username=user[3]
    root.destroy()

    main_window = tk.Tk()
    main_window.title("Main Application")
    main_window.geometry('400x400')

    tk.Label(main_window, text=f"Welcome, {user[1]}", font=("Helvetica", 18)).pack(pady=20)

    tk.Label(main_window, text="*Select filter:", font=("Helvetica",14)).pack(pady=5)
    selected_filter = tk.StringVar(main_window)
    filters = ["ALL PUBLISHMENTS", "JUST ARTICLES", "SCIENTIFIC JOURNALS", "FILTER BY KEYWORDS", "FILTER BY WRITER"]
    cascade_menu = tk.OptionMenu(main_window, selected_filter, *filters)
    cascade_menu.config(font=("Helvetica",14))
    cascade_menu.pack(pady=10)

    filter_button = tk.Button(main_window, text="Search",
                              command=lambda: filter_options(selected_filter.get()),font=("Helvetica",14))
    filter_button.pack(pady=10)

    save_button = tk.Button(main_window, text="Save a Publishment",
                              command=lambda: save_publishment(main_window, user), font=("Helvetica",14))
    save_button.pack(pady=10)
    
    upload_button = tk.Button(main_window, text="Upload an Article",
                              command=lambda: upload_article(main_window, user), font=("Helvetica",14))
    upload_button.pack(pady=10)

    main_window.mainloop()


def filter_options(selected_filter):
    if not selected_filter:
        print("Select one of the available options")
        return

    if selected_filter == "JUST ARTICLES":        
        option_names = ["Scientific field", "Writer email" , "Writer name", "Cited article id", "Cited article title"]
        options = ["scientific_field", "writer_mail", "fname, lname", "cited_article_id", "cited_title"]
        order_names = ["Title Alphabetical", "Title Reverse Alphabetical", "Writer Name", "ID"]
        orders = ['title', 'title DESC', 'lname, fname', 'article_id']
        headers = ['article_id', 'title', 'scientific_field', 'writer_mail', 'fname', 'lname', 'cited_article_id', 'cited_title']
        select_filter(selected_filter, option_names, options, order_names, orders, headers)
        
    if selected_filter == "ALL PUBLISHMENTS":
         option_names = ["File address", "URL" , "Uploader", "Views", "Upload date"]
         options = ["file_address", "url", "uploader", "views", "upload_datetime"]
         order_names = ["Title Alphabetical", "Title Reverse Alphabetical", "ID", "Most Popular", "Newest", "Oldest"]
         orders = ['title', 'title DESC', 'id', 'views DESC', 'upload_datetime', 'upload_datetime DESC' ]
         headers = ['id', 'title', 'file_address', 'url', 'uploader', 'views', 'upload_datetime']
         select_filter(selected_filter, option_names, options, order_names, orders, headers)
        
    if selected_filter == "SCIENTIFIC JOURNALS":
         option_names = ["ID", "ISBN" , "Issue No", "Number of issues", "Publishment Date"]
         options = ["issue_id", "isbn" , "no_of_issue", "n_issues", "publishment_date"]
         order_names = ["Title Alphabetical", "Title Reverse Alphabetical", "ISBN", "Issue Number", "Most Issues", "Newest", "Oldest"]
         orders = ['title', 'title DESC', 'isbn', 'no_of_issue', 'n_issues', 'publishment_date', 'publishment_date DESC' ]
         headers = ['title', 'publisher_name', 'issue_id', 'isbn', 'no_of_issue', 'n_issues', 'publishment_date']
         select_filter(selected_filter, option_names, options, order_names, orders, headers)

    if selected_filter == "FILTER BY WRITER":
         option_names = ["E-mail", "Employment", "Institution"]
         options = ["mail", "type", "inst_name"]
         order_names = ["Name Alphabetical", "Name Reverse Alphabetical", "Institution", "Institution type"]
         orders = ['lname, fname', 'lname, fname DESC', 'inst_name', 'type']
         headers = ['lname', 'fname', 'mail', 'type', 'inst_name','aid', 'title']
         select_filter(selected_filter, option_names, options, order_names, orders, headers)

    if selected_filter == "FILTER BY KEYWORDS":
        select_keywords()

        

def select_filter(ftype, option_names, options, order_names, orders, headers):
    filter_window = tk.Toplevel()
    filter_window.title("Filter")

    filters = tk.StringVar()

    checkbox_filters = [tk.StringVar(value=options[i]) for i in range(len(options))]

    def update_options():
        selected_options = [var.get() for var in checkbox_filters if var.get() is not None and var.get() != "0"]
        filters.set(", ".join(selected_options))

    checkbutton_label = tk.Label(filter_window, text="Show:", font=("Helvetica", 14))
    checkbutton_label.pack(pady=10)
    for i in range(len(options)):
        checkbox = tk.Checkbutton(filter_window, text=option_names[i], variable=checkbox_filters[i], onvalue=options[i], offvalue="0", command=update_options, font=("Helvetica", 14))
        checkbox.pack()
        
    selected_options = [var.get() for var in checkbox_filters if var.get() is not None and var.get() != "0"]
    filters.set(", ".join(selected_options))

    filter_entry_label = tk.Label(filter_window, text="Search: \nInsert numbers for ID or characters for Title", font=("Helvetica", 14))
    filter_entry_label.pack(pady=10)
    filter_entry = tk.Entry(filter_window, font=("Helvetica", 14))
    filter_entry.pack(pady=5)

    order = tk.StringVar()
    radiobutton_order = tk.StringVar()

    def update_order():
        order.set(radiobutton_order.get())

    radiobutton_label = tk.Label(filter_window, text="Order by:", font=("Helvetica", 14))
    radiobutton_label.pack(pady=10)
    for i in range(len(orders)):
        radio_button = tk.Radiobutton(filter_window, text=order_names[i], variable=radiobutton_order, value=orders[i], command=update_order, font=("Helvetica", 14))
        radio_button.pack()

    ok_button = tk.Button(filter_window, text="Ok", command = lambda: finalize_filter(ftype, headers, filters.get(), filter_entry.get(), order.get()), font=("Helvetica", 14))
    ok_button.pack(pady=10)
    

def finalize_filter(ftype, headers, selection, entry, order):
    if ftype == "JUST ARTICLES":
        if selection:
            query = f"SELECT article_id, title, {selection} FROM(SELECT article_id, title, scientific_field, writer_mail, fname, lname FROM(SELECT writer_mail, article_id AS works_on_id, fname, lname FROM WORKS_ON INNER JOIN WRITER ON writer_mail=\"e-mail\")INNER JOIN ARTICLE ON article_id=works_on_id) LEFT JOIN (SELECT citing_article_id, cited_article_id, title AS  cited_title FROM CITES INNER JOIN ARTICLE ON cited_article_id=article_id) ON article_id=citing_article_id"        
        else:
            query = "SELECT article_id, title FROM(SELECT article_id, title, scientific_field, writer_mail, fname, lname FROM(SELECT writer_mail, article_id AS works_on_id, fname, lname FROM WORKS_ON INNER JOIN WRITER ON writer_mail=\"e-mail\")INNER JOIN ARTICLE ON article_id=works_on_id) LEFT JOIN (SELECT citing_article_id, cited_article_id, title AS  cited_title FROM CITES INNER JOIN ARTICLE ON cited_article_id=article_id) ON article_id=citing_article_id"        
        if entry:
            if entry.isdigit():
                query = query + f" WHERE article_id LIKE '%{entry}%' "
            else:
                query = query + f" WHERE title LIKE '%{entry}%' "
        if order:
            query = query + f" ORDER BY {order}"
            
    if ftype == "ALL PUBLISHMENTS":
        
        selection = re.sub("uploader", "COALESCE(writer_mail, publisher_name) AS uploader", selection)
        
        if selection:
            #query = f"SELECT id, title, {selection} FROM (SELECT id, title, {selection1}  FROM PUBLISHMENT INNER JOIN ARTICLE ON article_id=id UNION SELECT id, journ_title AS title, {selection2}  FROM PUBLISHMENT INNER JOIN ISSUE ON issue_id=id)"
            query = f"SELECT id, COALESCE(title, journ_title) AS title,{selection} FROM PUBLISHMENT LEFT JOIN ARTICLE ON id = article_id LEFT JOIN ISSUE i ON id = i.issue_id"
        else:
            #query = f"SELECT id, title FROM (SELECT id, title, url, file_address, writer_mail as uploader, views, upload_datetime  FROM PUBLISHMENT INNER JOIN ARTICLE ON article_id=id UNION SELECT id, journ_title AS title, url, file_address, publisher_name as uploader, views, upload_datetime  FROM PUBLISHMENT INNER JOIN ISSUE ON issue_id=id)"
            query = f"SELECT id, COALESCE(title, journ_title) AS title,url,file_address,COALESCE(writer_mail, publisher_mail) AS uploader, views, upload_datetime FROM PUBLISHMENT LEFT JOIN ARTICLE ON id = article_id LEFT JOIN ISSUE i ON id = i.issue_id"
        if entry:
            if entry.isdigit():
                query = query + f" WHERE id LIKE '%{entry}%' "
            else:
                query = query + f" WHERE title LIKE '%{entry}%' "
        if order:
            query = query + f" ORDER BY {order}"
        
    if ftype == "SCIENTIFIC JOURNALS":
        if selection:
            query = f"SELECT  title, publisher_name, {selection} FROM JOURNAL INNER JOIN ISSUE ON title = journ_title"
        else:
            query = f"SELECT  title, publisher_name FROM JOURNAL LEFT JOIN ISSUE ON title = journ_title"
        if entry:
            if entry.isdigit() or '-' in entry:
                query = query + f" WHERE isbn LIKE '%{entry}%' "
            else:
                query = query + f" WHERE title LIKE '%{entry}%' "
        if order:
            query = query + f" ORDER BY {order}"

    if ftype == "FILTER BY WRITER":
        if selection:
            query = f"SELECT lname, fname, {selection}, aid, title FROM (SELECT lname,fname,mail,type,inst_name FROM (SELECT fname, lname, \"e-mail\" AS mail, inst_name FROM WRITER LEFT JOIN COOPERATES ON \"e-mail\"=writer_mail) LEFT JOIN INSTITUTION ON inst_name=name) INNER JOIN (SELECT ARTICLE.article_id AS aid, title, writer_mail FROM ARTICLE INNER JOIN WORKS_ON ON ARTICLE.article_id=WORKS_ON.article_id) ON writer_mail=mail"
        else:
            query = f"SELECT lname, fname,  aid, title FROM (SELECT lname,fname,mail,type,inst_name FROM (SELECT fname, lname, \"e-mail\" AS mail, inst_name FROM WRITER LEFT JOIN COOPERATES ON \"e-mail\"=writer_mail) LEFT JOIN INSTITUTION ON inst_name=name) INNER JOIN (SELECT ARTICLE.article_id AS aid, title, writer_mail FROM ARTICLE INNER JOIN WORKS_ON ON ARTICLE.article_id=WORKS_ON.article_id) ON writer_mail=mail"
        if entry:
            if entry.isdigit():
                query = query + f" WHERE article_id LIKE '%{entry}%' "
            else:
                query = query + f" WHERE title LIKE '%{entry}%' "
        if order:
            query = query + f" ORDER BY {order}"
    print(query)
    print()
    print_text_window(query, headers)

    
def print_text_window(query, selected_headers):
    text_window = tk.Toplevel()
    text_window.title("Result window")
    width= text_window.winfo_screenwidth()               
    height= text_window.winfo_screenheight()               
    text_window.geometry("%dx%d" % (width, height))

    start_time = timeit.default_timer()
    
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    end_time = timeit.default_timer()
    estimated_time = end_time-start_time
    print("Estimated time: ", estimated_time)

    text_widget = scrolledtext.ScrolledText(text_window, wrap=tk.WORD, width=40, height=10, font=("Helvetica", 14))
    
    
    headers = [column[0] for column in cursor.description]
    selected_headers = [header for header in selected_headers if header in headers]
    text_widget.insert(tk.END, f"{selected_headers}\n")
    for row in rows:
        selected_data = [row[headers.index(header)] for header in selected_headers]
        text_widget.insert(tk.END, f"{selected_data}\n")

    text_widget.pack(expand=True, fill="both")

def select_keywords():
    try:   
        cursor = connection.cursor()
        keywords_fetch_query = "SELECT DISTINCT keyword FROM KEYWORDS ORDER BY keyword"
        cursor.execute(keywords_fetch_query)
        record = cursor.fetchall()
        
        if record:

            def on_select(event):
                selected_indices = listbox.curselection()
                selected_words = [checkbutton_keywords[index] for index in selected_indices]

            def add_selected_to_list():
                selected_indices = listbox.curselection()
                selected_words = [checkbutton_keywords[index] for index in selected_indices]
                result_list.extend(selected_words)
                create_keyword_query(keywords_window, result_list)
                
            keywords_window = tk.Toplevel()
            keywords_window.title("Keyword selection") 

            listbox = tk.Listbox(keywords_window, selectmode=tk.MULTIPLE, font=('Helvetica', 14) )
            scrollbar = tk.Scrollbar(keywords_window, command=listbox.yview)
            listbox.pack( fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox.config(yscrollcommand=scrollbar.set)
            
            result = [list(row) for row in record]
            keywords_list = [item for sublist in result for item in sublist]
            
            keywords = tk.StringVar()
            checkbuttons = []
            checkbutton_keywords = []
            for i in range(len(keywords_list)):
                checkbutton = tk.Checkbutton(keywords_window, text=f"{keywords_list[i]}", variable=keywords_list[i], font=('Helvetica', 14))
                checkbuttons.append(checkbutton)
                checkbutton_keywords.append(keywords_list[i])

            for word in checkbutton_keywords:
                listbox.insert(tk.END, word)

            listbox.bind('<<ListboxSelect>>', on_select)

            add_button = tk.Button(keywords_window, text="Add Selected to List", command=add_selected_to_list, font=('Helvetica', 14))
            add_button.pack(side=tk.BOTTOM, pady=10)
            
            result_list = []
            
                
        else:
            print("No keywords found in database")
            
    except db.Error as e:
        print(f"Error using keywords: {e}")


def create_keyword_query(window, keywords):
    window.destroy()
    print(keywords)
    keyword_query = "Select title, article_id from ARTICLE where article_id in(select id from KEYWORDS where keyword in ("
    
    for i in range(len(keywords)):
        if i!=0:
            keyword_query+=","
        keyword_query += f"'{keywords[i]}'"
    keyword_query+=f') group by id having count(distinct keyword) = {len(keywords)});'
    
    
    headers = ['title', 'article_id']
    
    print(keyword_query)
    
    print_text_window(keyword_query, headers)
    
    

def save_publishment(main, user):
    save_publishment_window = tk.Toplevel(main)
    save_publishment_window.title("Publishment save")

    tk.Label(save_publishment_window, text="Insert publishment ID", font=("Helvetica", 14)).pack(pady=5)
    save_publishment_entry = tk.Entry(save_publishment_window, font=("Helvetica", 14))
    save_publishment_entry.pack(pady=5)

    save_publishment_button = tk.Button(save_publishment_window, text="Save", command=lambda: save(user[0], save_publishment_entry.get()), font=("Helvetica", 14))
    save_publishment_button.pack(pady=10)

    remove_publishment_button = tk.Button(save_publishment_window, text="Remove", command=lambda: remove(user[0], save_publishment_entry.get()), font=("Helvetica", 14))
    remove_publishment_button.pack(pady=10)

    show_saved_button = tk.Button(save_publishment_window, text="Show my collection", command=lambda: show_saved(user[0]), font=("Helvetica", 14))
    show_saved_button.pack(pady=10)



def save(usermail, p_id):
    if not p_id:
        print("Nothing was selected")
        return
    
    cursor = connection.cursor()
    check_exist_query = f"SELECT * FROM PUBLISHMENT WHERE id='{p_id}'"
    cursor.execute(check_exist_query)
    check = cursor.fetchall()
    
    if check:
        read_query = f"SELECT * FROM SAVES WHERE user_mail='{usermail}' AND publishment_id='{p_id}'"
        cursor.execute(read_query)
        record = cursor.fetchall()
        
        if record:
            print("Article already saved")
        else:
            insert_query = f"INSERT INTO SAVES(user_mail, publishment_id) VALUES('{usermail}','{p_id}')"
            cursor.execute(insert_query)
            print("Article saved succesfully")
            
    else:
        print("Article ID not in database")
        
    cursor.close()
    connection.commit()



def remove(usermail, p_id):
    if not p_id:
        print("Nothing was selected")
        return
    
    cursor = connection.cursor()
    
    read_query = f"SELECT * FROM SAVES WHERE user_mail='{usermail}' AND publishment_id='{p_id}'"

    cursor.execute(read_query)
    record = cursor.fetchall()
    
    if not record:
        print("Article is not saved")
    else:
        delete_query = f"DELETE FROM SAVES WHERE user_mail='{usermail}' AND publishment_id='{p_id}'"
        cursor.execute(delete_query)
        print("Article removed from SAVES")
        
    cursor.close()
    connection.commit()


def show_saved(usermail):

    headers = ['publishment_id', 'title']
    show_query = f"SELECT publishment_id, journ_title AS title FROM SAVES INNER JOIN ISSUE ON publishment_id=issue_id WHERE user_mail='{usermail}' UNION SELECT publishment_id, title FROM SAVES INNER JOIN ARTICLE ON publishment_id=article_id WHERE user_mail='{usermail}'"

    print_text_window(show_query, headers)
    

#Set up upload article window 
def upload_article(main_window, user):
    if user[2]=='true':
        upload_form = tk.Toplevel(main_window)
        upload_form.title("Article details")

        tk.Label(upload_form, text="*Title:", font=("Helvetica", 14)).pack(pady=5)
        article_title_entry = tk.Entry(upload_form, font=("Helvetica", 14))
        article_title_entry.pack(pady=5)

        tk.Label(upload_form, text="Input cited article ids separated by ',':", font=("Helvetica", 14)).pack(pady=5)
        article_id_cite_entry = tk.Entry(upload_form, font=("Helvetica", 14))
        article_id_cite_entry.pack(pady=5)

        tk.Label(upload_form, text="*Date(MM/DD/YYYY):", font=("Helvetica", 14)).pack(pady=5)
        article_date_entry = tk.Entry(upload_form, font=("Helvetica", 14))
        article_date_entry.pack(pady=5)

        tk.Label(upload_form, text="*Select field:", font=("Helvetica",14)).pack(pady=5)
        article_field = tk.StringVar(upload_form)
        fields = ["Medicine", "Engineering", "Economics", "Biology", "Computer science"]
        cascade_menu = tk.OptionMenu(upload_form, article_field, *fields)
        cascade_menu.config(font=("Helvetica",14))
        cascade_menu.pack(pady=10)
        
        upload = tk.Button(upload_form, text="Add writer(s)",
                                         command=lambda: add_writers(main_window, upload_form, article_title_entry.get(),
                                                                        article_field.get(), article_date_entry.get(), article_id_cite_entry.get()),
                                         font=("Helvetica", 14))
        upload.pack(pady=10)

        upload_form.mainloop()
        
    else:
        print(f"Error: User {user[3]} is not verified")
        

#Set up writer info window
def add_writers(main_window, upload_form, article_title, article_field, article_date, article_cites):
    if not article_title or not article_field or not article_date:
        print("Fill in the necessary fields")
        return
     
    upload_form.destroy()

    writer_form = tk.Toplevel(main_window)
    writer_form.title("Writer details")

    writer_dictionary = []

    tk.Label(writer_form, text="*Writer e-mail:", font=("Helvetica", 14)).pack(pady=5)
    writer_email_entry = tk.Entry(writer_form, font=("Helvetica", 14))
    writer_email_entry.pack(pady=5)

    tk.Label(writer_form, text="*Writer first name:", font=("Helvetica", 14)).pack(pady=5)
    writer_first_name_entry = tk.Entry(writer_form, font=("Helvetica", 14))
    writer_first_name_entry.pack(pady=5)

    tk.Label(writer_form, text="*Writer last name:", font=("Helvetica", 14)).pack(pady=5)
    writer_last_name_entry = tk.Entry(writer_form, font=("Helvetica", 14))
    writer_last_name_entry.pack(pady=5)

    tk.Label(writer_form, text="Institution:", font=("Helvetica", 14)).pack(pady=5)
    institution_entry = tk.Entry(writer_form, font=("Helvetica", 14))
    institution_entry.pack(pady=5)

    def add_to_dictionary():
        fname = writer_first_name_entry.get().split()
        lname = writer_last_name_entry.get().split()
        email = writer_email_entry.get().split()
        institution = institution_entry.get().split()

        if not fname or not lname or not email:
            print("Fill in the necessary fields")
            return

        writer_data = {"Fname":fname, "Lname":lname, "Email":email, "Inst":institution}
        writer_dictionary.append(writer_data)

        writer_first_name_entry.delete(0, tk.END)
        writer_last_name_entry.delete(0, tk.END)
        writer_email_entry.delete(0, tk.END)
        institution_entry.delete(0, tk.END)
    
    add_writer = tk.Button(writer_form, text="Add writer(s)",
                           command = lambda: add_to_dictionary(),
                           font=("Helvetica", 14))
    add_writer.pack(pady=10)

    tk.Label(writer_form, text="Finish adding writers before uploading.", font=("Helvetica", 14)).pack(pady=5)

    upload = tk.Button(writer_form, text="Upload",
                           command = lambda: finish_upload(writer_form, writer_dictionary, article_title, article_field, article_date, article_cites),
                           font=("Helvetica", 14))
    upload.pack(pady=10)


#
def finish_upload(writer_form, writers, article_title, article_field, article_date, article_cites):
    if not writers:
        print("Please add at least one writer")
        return
    
    writer_form.destroy()

    publish_id = generate_id()
    url = "https://database/" + publish_id + ".com"
    filepath = "C:/Drive/" + publish_id + ".pdf"
    views = 0
    standard = "APA"
    upload_date = datetime.now().strftime("%m/%d/%Y")
    
    cites_list = [word.strip() for word in article_cites.split(',') if word.strip().isdigit()]
    no_of_cites = len(cites_list)

    try:
        cursor = connection.cursor()
        find_publishment_query = f"SELECT * FROM PUBLISHMENT WHERE id='{publish_id}'"
        cursor.execute(find_publishment_query)
        temp = cursor.fetchall()
        
        if not temp:
            primary_writer_email = writers[0]["Email"][0]
            insert_publish_query = f"INSERT INTO PUBLISHMENT(id, url, file_address, writer_mail, views, standard, upload_datetime) VALUES ('{publish_id}', '{url}', '{filepath}', '{primary_writer_email}', '{views}', '{standard}','{upload_date}')"
            cursor.execute(insert_publish_query)
            insert_article_query = f"INSERT INTO ARTICLE(article_id, title, no_citations, scientific_field, date_of_publishment) VALUES('{publish_id}','{article_title}','{no_of_cites}','{article_field}','{article_date}')"
            cursor.execute(insert_article_query)
            
            for i in range(no_of_cites):
                find_cites_query = f"SELECT article_id FROM ARTICLE WHERE article_id='{cites_list[i]}'"
                cursor.execute(find_cites_query)
                cite_temp = cursor.fetchall()
                if cite_temp:
                    cite_temp = [list(row) for row in cite_temp]
                    cited_article = cite_temp[0][0]
                    insert_cites_query = f"INSERT INTO CITES(citing_article_id, cited_article_id) VALUES('{publish_id}','{cited_article}')"
                    cursor.execute(insert_cites_query)
                    
            for i in range(len(writers)):
                fname = writers[i]["Fname"][0]
                lname = writers[i]["Lname"][0]
                email = writers[i]["Email"][0]
                institution = writers[i]["Inst"]
                find_writer_query = f"SELECT * FROM WRITER WHERE \"e-mail\"='{email}'"
                cursor.execute(find_writer_query)
                writer_temp = cursor.fetchall()
                
                if not writer_temp:
                    insert_writer_query = f"INSERT INTO WRITER('e-mail',fname,lname) VALUES('{email}','{lname}','{fname}')"
                    cursor.execute(insert_writer_query)
                    
                if institution:
                    find_institution_query = f"SELECT * FROM INSTITUTION WHERE name='{institution[0]}'"
                    cursor.execute(find_institution_query)
                    inst_temp = cursor.fetchall()
                    
                    if not inst_temp:
                        insert_inst_query = f"INSERT INTO INSTITUTION(name) VALUES('{institution[0]}')"
                        cursor.execute(insert_inst_query)
                        
                    find_cooperates_query = f"SELECT * FROM COOPERATES WHERE writer_mail='{email}' AND inst_name='{institution[0]}'"
                    cursor.execute(find_cooperates_query)
                    cooperates_temp = cursor.fetchall()
                    
                    if not cooperates_temp:
                        insert_works_on_query = f"INSERT INTO cooperates(writer_mail, inst_name) VALUES('{email}','{institution[0]}')"
                        cursor.execute(insert_works_on_query)
                        
                find_works_on_query = f"SELECT * FROM WORKS_ON WHERE article_id='{publish_id}' AND writer_mail='{email}'"
                cursor.execute(find_works_on_query)
                works_on_temp = cursor.fetchall()
                
                if not works_on_temp:
                    insert_works_on_query = f"INSERT INTO WORKS_ON(writer_mail, article_id) VALUES('{email}','{publish_id}')"
                    cursor.execute(insert_works_on_query)
                    
            print(f"Upload complete. Publishment id: {publish_id}")
        else:
            print("Error uploading article: ID already exists")
            
        connection.commit()
        cursor.close()
            
    except db.Error as e:
        print(f"Error uploading article: {e}")
    

#Generate unique article id
def generate_id():
    article_id = ''.join(random.choices(string.digits,k=8))
    cursor = connection.cursor()
    read_query = f"SELECT article_id FROM ARTICLE WHERE article_id='{article_id}';"
    cursor.execute(read_query)
    record = cursor.fetchall()
    if not record:
        cursor.close()
        return article_id
    else:
        generate_id()
        


if __name__ == "__main__":
    db_name = "academia1,5M.db"
    connection = create_connection(db_name)
    if connection is not None:
        root = tk.Tk()
        login_screen()
        root.mainloop()
        connection.close()
