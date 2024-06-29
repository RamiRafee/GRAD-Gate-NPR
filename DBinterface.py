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
        sql = "SELECT carNum FROM cars WHERE carNum LIKE %s"
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
def check_premium_status(plat_num):
    try:
        # Use LIKE with % as wildcards to match similar patterns
        sql = "SELECT carNum, users_users_id FROM cars WHERE carNum LIKE %s"
        like_pattern = f"%{plat_num}%"  # Add wildcards to the plate number
        mycursor.execute(sql, (like_pattern,))
        car_results = mycursor.fetchall()  # Fetch all matching results

        if car_results:  # Check if there are any matching results
            print("Found similar car plate numbers and user IDs:")
            for car_num, user_id in car_results:
                print(f"CarNum: {car_num}, UserID: {user_id}")
                
                # Check the premium status in the users table
                sql_premium = "SELECT premium FROM users WHERE users_id = %s"
                mycursor.execute(sql_premium, (user_id,))
                user_result = mycursor.fetchone()

                if user_result:
                    is_premium = user_result[0]  # Assuming the premium column is boolean
                    if is_premium == 1:
                        print(f"User ID {user_id} is a premium user.")
                        return 1
                    else:
                        print(f"User ID {user_id} is not a premium user.")
                else:
                    print(f"No user found with UserID: {user_id}")


        return 0
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

def append_to_file(file_name, CarNum):
    with open(file_name, 'a') as file:
        file.write(f"{CarNum}\n")    
def update_SPOTS(table, slots, file_name):
    # Read the car number from the file
    with open(file_name, 'r') as file:
        carNum = file.readline().strip()

    # Fetch current states from the database and find the spot that changed from "E" to "F"
    current_states = {}
    spot_to_update = None
    spot_updated = False
    for spot_number in range(1, 13):
        position = f"A{spot_number}" if spot_number <= 6 else f"B{spot_number - 6}"
        
        mycursor.execute("SELECT state FROM {} WHERE position = %s".format(table), (position,))
        current_states[position] = mycursor.fetchone()[0]

        # Determine if this spot has changed from "E" to "F"
        new_status = slots.get(spot_number, {'Status': 'E'})['Status']
        if current_states[position] == 'E' and new_status == 'F' and spot_to_update == None:
            spot_to_update = position
            

    # Update the parking spots based on the returned slots
    for spot_number in range(1, 13):
        position = f"A{spot_number}" if spot_number <= 6 else f"B{spot_number - 6}"
        
        status = slots.get(spot_number, {'Status': 'E'})['Status']
        color = slots.get(spot_number, {}).get('Color', None)

        if position == spot_to_update:
            # Update the spot that changed from "E" to "F"
            mycursor.execute(
                "UPDATE {} SET state = %s, carColor = %s, CarNum = %s WHERE position = %s".format(table),
                ('F', color, carNum, position)
            )
            spot_updated = True
        elif current_states[position] != 'B' or status != 'E':
            # Update the parking spot in the database only if the current state is not 'B'
            if status == 'E':
                mycursor.execute(
                    "UPDATE {} SET state = %s, carColor = %s, CarNum = NULL WHERE position = %s".format(table),
                    (status, color, position)
                )
            elif status == 'F':
                mycursor.execute(
                    "UPDATE {} SET state = %s, carColor = %s WHERE position = %s".format(table),
                    (status, color, position)
                )

    # Commit the transaction
    mydb.commit()

    # Remove the car number from the file if the spot was updated
    if spot_to_update:
        with open(file_name, 'r') as file:
            lines = file.readlines()
        with open(file_name, 'w') as file:
            file.writelines("")  # Skip the first line
        return spot_updated
    return spot_updated
   
if __name__ =="__main__":
    #plat_num = input("Enter the car number: ")  # Assuming user input for car number
    check_car_existence("ر ج ل 6 6 6")

