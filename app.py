from bson import ObjectId
from flask import Flask, render_template, request, redirect, session, url_for
# from flask_pymongo import PyMongo
from pymongo import MongoClient
app = Flask(__name__)

# This is the connection string to the database.
client = MongoClient("mongodb+srv://Admin:Admin123@farmfresh.ralj1.mongodb.net/FarmFreshDB?retryWrites=true&w=majority")
# connection to the database
db = client['FarmFreshDB']
# connection to the collection of user information
# UserInfo = db['UserInfo']

# UserInfo.insert_one({"username": "nischay", "password": "nischay"})
app.secret_key = "f3cfe9ed8fae309f02079dbf"

# this is the introductory page
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        reg_page = request.form["registrationPage"]
        print("Redirecting to the page:", reg_page)
        if reg_page == "customer":
            return redirect('/login/customer')
        elif reg_page == "farmer":
            return redirect('/login/farmer')
    return render_template("index.html")


@app.route('/login/customer', methods=["POST", "GET"])
def customerlogin():
    print("Welcome to the customer page")
    if request.method == "POST":
        customeruname = request.form["customeruname"]
        customerpassword = request.form["customerpassword"]
        UserInfo = db['UserInfo']
        print("checking for results")
        test = UserInfo.find_one({"customeruname": customeruname, "customerpassword": customerpassword})

        if test is None:
            return "Wrong credentials try again"
        else:
            session["name"] = test["customeruname"]
            return redirect(url_for("customerhome"))

    return render_template("customerlogin.html")


@app.route('/register/customer',methods =['POST','GET'])
def customerregister():
    print("Welcome to the customer register page")
    if request.method == "POST":
        UserInfo = db['UserInfo']
        customerfname = request.form["customerfname"]
        customerlname = request.form["customerlname"]
        customeruname = request.form["customeruname"]
        customerpassword = request.form["customerpassword"]
        customerphone = request.form["customerphone"]
        customeraddress = request.form["customeraddress"]
        UserInfo.insert_one(
            {'customerfname': customerfname,
             'customerlname': customerlname,
             'customeruname': customeruname,
             'customerpassword': customerpassword,
             'customerphone': customerphone,
             'customeraddress': customeraddress
             })
        print("Resistration successful")
        return redirect(url_for("customerlogin"))

    return render_template("customerregister.html")


@app.route('/login/farmer',methods=['POST', 'GET'])
def farmerlogin():
    print("Welcome to the farmer login page")
    if request.method == "POST":
        farmeruname = request.form["farmeruname"]
        farmerpassword = request.form["farmerpassword"]
        FarmerInfo = db['FarmerInfo']
        print("checking for results")
        test = FarmerInfo.find_one({"farmeruname":farmeruname,"farmerpassword":farmerpassword})
        print("Login Success",test)
        if test is None:
            print("wrong creds")
            return redirect(url_for("farmerlogin"))
        else:
            print("correct creds")
            session["name"] = test["farmerfname"]
            return redirect(url_for("farmerhome"))
    return render_template("farmerlogin.html")


@app.route('/register/farmer', methods=['POST', 'GET'])
def farmerregister():
    print("Welcome to the farmer register page")
    if request.method == "POST":
        FarmerInfo = db['FarmerInfo']
        farmerfname = request.form["farmerfname"]
        farmerlname = request.form["farmerlname"]
        farmeruname = request.form["farmeruname"]
        farmerpassword = request.form["farmerpassword"]
        farmerphone = request.form["farmerphone"]
        farmeraddress = request.form["farmeraddress"]
        FarmerInfo.insert_one(
            {'farmerfname': farmerfname,
             'farmerlname': farmerlname,
             'farmeruname': farmeruname,
             'farmerpassword': farmerpassword,
             'farmerphone': farmerphone,
             'farmeraddress': farmeraddress,
             'earnings':0
             })
        print("Resistration successful")
        return redirect(url_for("farmerlogin"))
    return render_template("farmerregister.html")


# Logout from the applcation
@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")





# Farmer home page
@app.route('/farmer/home',methods=['POST','GET'])
def farmerhome():
    if not session.get("name"):
        return redirect("/")
    FarmerPost = db['FarmerPost']
    print(session.get("name"))
    postinfo = FarmerPost.find({'farmername':session.get("name")}).limit(10)
    FarmerInfo = db['FarmerInfo']
    x= FarmerInfo.find_one({'farmerfname':session.get("name")})
    earn=x["earnings"]
    return render_template('farmerhome.html',postinfo=postinfo,earn=earn,s=session.get("name"))


@app.route('/farmer/post', methods=['POST','GET'])
def postAdd():
    if not session.get("name"):
        print("checking if in session")
        return redirect("/")
    elif request.method == 'POST':
        farmeritem = request.form["Item"]
        itemweight = request.form["farmerquantity"]
        itemprice = request.form["farmerprice"]
        totalprice = int(itemprice)*int(itemweight)
        print(totalprice)
        approval = "unknown"
        FarmerPost = db["FarmerPost"]
        FarmerPost.insert_one({'farmername':session.get("name"),'farmeritem':farmeritem,'itemweight':itemweight,'itemprice':itemprice,'totalprice':totalprice,'approval':approval,'payment':'no'})
        return redirect(url_for('farmerhome'))
    return render_template('postAdd.html')

@app.route('/admin/login',methods=['POST','GET'])
def adminlogin():
    print("adminlogin secion")
    if request.method == "POST":
        user = request.form['adminu']
        passw = request.form['adminp']

        if (user=="admin" and passw=="admin"):
            session["name"] = 'admin'
            return redirect(url_for("adminhome"))
        else:
            return "wrong creds try again!"
    return render_template("adminlogin.html")


@app.route('/admin/home')
def adminhome():
    if not session.get("name"):
        return redirect("/")
    return render_template("adminhome.html")


@app.route('/admin/orderapproval',methods=['POST','GET'])
def orderapproval():
    if not session.get("name"):
        return redirect("/")
    FarmerPost = db['FarmerPost']
    Inventory = db['Inventory']

    postinfo = FarmerPost.find().limit(10)

    if request.method =="POST":
        print("order approval section")
        approve = request.form["approve"]
        id= request.form["submit"]
        print(approve)
        FarmerPost.update_one({"_id":ObjectId(id)},{"$set":{"approval":approve}})
        iteminfo=FarmerPost.find_one({"_id":ObjectId(id)})
        item = iteminfo['farmeritem']
        q = int(iteminfo['itemweight'])
        inventoryinfo = Inventory.find_one({"item":item})
        quantity = int(inventoryinfo['quantity'])
        Inventory.update_one({'item':item},{"$set":{"quantity":(q+quantity)}})
        return redirect(url_for('orderapproval'))
    return render_template("orderapproval.html",postinfo=postinfo)


@app.route('/admin/farmerpayment',methods=['POST','GET'])
def farmerpayment():
    if not session.get("name"):
        return redirect("/")
    FarmerPost = db['FarmerPost']
    FarmerInfo = db['FarmerInfo']
    postinfo = FarmerPost.find().limit(10)

    if request.method =="POST":
        print("Payment section")
        pay = request.form["pay"]
        id= request.form["submit"]
        print(pay)
        x = FarmerPost.find_one({"_id":ObjectId(id)})
        price=int(x["totalprice"])
        y = FarmerInfo.find_one({"farmerfname":x["farmername"]})
        earn=y["earnings"]
        earn=int(price)+int(earn)
        FarmerPost.update_one({"_id":ObjectId(id)},{"$set":{"payment":'yes'}})
        FarmerInfo.update_one({"farmerfname":x["farmername"]},{"$set":{"earnings":earn}})
        # FarmerInfo.update_one({"farmerfname":session.get("name")},{"$set":{"earnings":earn}})
        # print(earn)
        return redirect(url_for('adminhome'))
    return render_template("farmerpayment.html",postinfo=postinfo)


@app.route('/admin/inventory',methods=['POST','GET'])
def inventory():
    inventory = db['Inventory']
    inventorytable = inventory.find().limit(10)
    if request.method == 'POST':
        item = request.form["Item"]
        price = int(request.form["farmerprice"])
        print(item,price)
        inventory.update_one({"item":item},{"$set":{"price":price}})
        print("update success")
        return redirect(url_for("inventory"))
    return render_template("inventory.html", inventorytable=inventorytable)
cart_list=[]
item_weight={}
pay_details={}
quantity_price={}
# Customer Home Page
@app.route('/customer/home',methods=['POST','GET'])
def customerhome():
    if not session.get("name"):
        return redirect("/")
    inventory = db['Inventory']
    inventorytable = inventory.find().limit(10)
    if request.method == 'POST':
        for i in inventorytable:
            if request.form[i['item']] == 'yes':
                print(i['item'], request.form[i["item"]])
                if(i['item'] not in cart_list):
                    cart_list.append(i['item'])
        return redirect(url_for('customercart'))
    return render_template('customerhome.html',inventorytable=inventorytable,s=session.get("name"))


@app.route('/customer/cart',methods=['POST','GET'])
def customercart():

    if not session.get("name"):
        return redirect("/")
    if request.method =='POST':
        for i in cart_list:
            if request.form[i]!=None:
                item_weight[i]=request.form[i]

        return redirect(url_for('customerbill'))

    return render_template('cart.html',cart_list=cart_list)

@app.route('/customer/bill')
def customerbill():
    if not session.get("name"):
        return redirect("/")
    price = db['Inventory']
    orders = db['ManageOrders']
    for i in item_weight:
        x = price.find_one({'item':i})
        pay_details[i]=int(item_weight[i])*int(x['price'])
        quantity_price[i]=x["price"]
        price.update_one({"item":i},{"$set":{"quantity":(int(x['quantity'])-int(item_weight[i]))}})

    print(item_weight)
    print(pay_details)
    print(quantity_price)
    sum=0
    for j in pay_details:
        sum= sum+pay_details[j]
    return render_template("bill.html",item_weight=item_weight,pay_details=pay_details,quantity_price=quantity_price,sum=sum)


if __name__ == '__main__':
    app.debug = True
    app.run()

