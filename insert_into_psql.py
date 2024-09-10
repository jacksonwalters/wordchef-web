import psycopg2
import pickle

#Create PostgreSQL connection object to database
#sql_password = input("Enter pSQL password: ")
conn = psycopg2.connect(database = "jackson", 
                        user = "jackson", 
                        host= 'localhost',
                        password = "your-password-here",
                        port = 5432)
# Open a cursor to perform database operations
db_cursor = conn.cursor()

with open("vocab/dict.pkl", 'rb') as wordvector_dict:
    wordvectors = pickle.load(wordvector_dict)

for word, embedding in wordvectors.items():
    word_string  = word.replace("'","''")
    embedding_string = str([float(a) for a in embedding])
    sql_insert_string = "INSERT INTO wordembeddings (word,embedding) VALUES ('{word}','{embedding}');".format(word=word_string,embedding=embedding_string)
    db_cursor.execute(sql_insert_string)

# Make the changes to the database persistent
conn.commit()
# Close cursor and communication with the database
db_cursor.close()
conn.close()