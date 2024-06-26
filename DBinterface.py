import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="automation"
)

mycursor = mydb.cursor()


# def check_car_existence(plat_num):
#     try:
#         sql = "SELECT COUNT(plate_numbers) FROM cars WHERE plate_numbers = %s"
#         mycursor.execute(sql, (plat_num,))
#         result = mycursor.fetchone()  # Fetch the result
#         if result and result[0] >= 1:  # Check if count is 1 or more
#             print("Car exists.")
#             return True
#         else:
#             print("Car does not exist.")
#             return False
#     except mysql.connector.Error as error:
#         print("Error:", error)

def check_car_existence(plat_num):
    try:
        # Use LIKE with % as wildcards to match similar patterns
        sql = "SELECT plate_numbers FROM cars WHERE plate_numbers LIKE %s"
        like_pattern = f"%{plat_num}%"  # Add wildcards to the plate number
        mycursor.execute(sql, (like_pattern,))
        result = mycursor.fetchall()  # Fetch all matching results
        
        if result:  # Check if there are any matching results
            print("Found similar car plate numbers:")
            for row in result:
                print(row[0])  # Print each matching plate number
            return True
        else:
            print("No similar car plate numbers found.")
            return False
    except mysql.connector.Error as error:
        print("Error:", error)

def insert_row_NPR(table,car_num):


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
    
def update_SPOTS(table,slots):
# Update the parking spots based on the returned slots
    for spot_number in range(1, 13):
        if spot_number <= 6:
            position = f"A{spot_number}"
        else:
            position = f"B{spot_number - 6}"
        
        status = slots.get(spot_number, {'Status': 'E'})['Status']
        color = slots.get(spot_number, {}).get('Color', None)
        # Check the current state in the database
        mycursor.execute("SELECT state FROM {} WHERE position = %s".format(table), (position,))
        current_state = mycursor.fetchone()[0]
        
        # Update the parking spot in the database only if the current state is not 'B'
        if current_state != 'B': # and status == 'E': #to do
            mycursor.execute(
                "UPDATE {} SET state = %s, carColor = %s WHERE position = %s".format(table),
                (status, color, position)
            )

    # Commit the transaction
    mydb.commit()
if __name__ =="__main__":
    #plat_num = input("Enter the car number: ")  # Assuming user input for car number
    check_car_existence("ر ج ل 6 6 6")
    insert_row_NPR('standard_garage_info',"ر ج ل 6 6 6")
