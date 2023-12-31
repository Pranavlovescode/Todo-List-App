from flask import Flask, render_template, request, redirect, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
from bson import json_util 


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Todos"
db = PyMongo(app).db

@app.route("/submit",methods=['GET','POST'])
def create_data():

    latest_todo = db.todos.find_one(sort=[("serial_no", -1)])

    if latest_todo:
        # If there are existing documents, get the latest serial_no and increment it
        latest_serial_no = latest_todo.get("serial_no", 0)
        serial_no = latest_serial_no + 1
    else:
        # If no documents exist, start with serial_no 1
        serial_no = 1
    
    if request.method=='POST':
        title = request.form['title']
        desc = request.form['desc']
        current_date = datetime.today()  
        db.todos.insert_one({
            'title': title,
            'desc': desc,
            'date_created': current_date,
            'serial_no':serial_no
        })  
      
    return redirect('/')
    
    
@app.route('/delete/<int:serial_no>')
def deleteTodo(serial_no):
    db.todos.delete_one({"serial_no": serial_no})
    print('Deleting the data')
    return redirect('/')

@app.route('/update/<int:serial_no>', methods=['GET','POST'])
def updateTo(serial_no):
    element =db.todos.find_one({"serial_no": serial_no})
    if request.method == 'POST':
        updatedTitle = request.form['title']
        updatedDesc = request.form['desc']
        updatedDate = datetime.today()   
        # {"serial_no": serial_no} - will find the document in the collection and then it will update the changes
        
        db.todos.update_one(element, {
            "$set": {
                "title": updatedTitle,
                "desc": updatedDesc,
                "date_created": updatedDate
            }
        })
        return redirect('/')
    
    return render_template('update.html',element=element)

@app.route('/search', methods=['GET', 'POST'])
def searchTodo():
    
    search = request.form.get('search', '').lower()
    print(f"Search query: {search}")
    results = list(db.todos.find({"title": {"$regex": f"^{search}", "$options": "i"}}))
    print(f"Number of results: {len(results)}")
    serialized_results = json_util.dumps(results)
    return serialized_results
    
@app.route('/')
def landingPage():
    allTodo = list(db.todos.find({}))
    print(allTodo)
    return render_template('index.html', allTodo=allTodo)

@app.route('/about')
def aboutPage():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)