import mysql.connector
import pickle

#Create MySQL connection object to database
#sql_password = input("Enter MySQL password: ")
mydb = mysql.connector.connect(
    host = "localhost",
    user = "jackson",
    password = "your-password-here",
    database = "wordchef"
)
mycursor = mydb.cursor()

with open("dict.pkl", 'rb') as wordvector_dict:
    wordvectors = pickle.load(wordvector_dict)

for word, embedding in wordvectors.items():
    word_string = word.replace("'","''")
    embedding_string = str(list(embedding)).replace('[','').replace(']','')
    sql_insert_string = "INSERT INTO wordchef.wordvectors (`word`,`embedding`) VALUES ({word},{embedding});".format(word=word_string,embedding=embedding_string)
    mycursor.execute()

mydb.commit()
mycursor.close()
mydb.close()