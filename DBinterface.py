import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jinroot",
    database="automation"
)

mycursor = mydb.cursor()


def check_car_existence(plat_num):
    try:
        sql = "SELECT COUNT(plate_numbers) FROM cars WHERE plate_numbers = %s"
        mycursor.execute(sql, (plat_num,))
        result = mycursor.fetchone()  # Fetch the result
        if result and result[0] >= 1:  # Check if count is 1 or more
            print("Car exists.")
            return True
        else:
            print("Car does not exist.")
            return False
    except mysql.connector.Error as error:
        print("Error:", error)

def insert_row(table,car_num):


    # SQL INSERT statement
    sql = "INSERT INTO {} (carNum) VALUES (%s)".format(table)
    
    # The values to insert
    val = (car_num,)
    
    # Execute the SQL query
    mycursor.execute(sql, val)
    
    # Commit the changes to the database
    mydb.commit()

    # Return the result of the execute method
    print(mycursor.rowcount)
    


#plat_num = input("Enter the car number: ")  # Assuming user input for car number
check_car_existence("ر ج ل 6 6 6")
insert_row('standard_garage_info','var')
