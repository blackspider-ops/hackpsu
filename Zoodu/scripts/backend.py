from openai import OpenAI
import mysql.connector


# Establish connection to the remote MySQL server
conn = mysql.connector.connect(
    host='sql5.freemysqlhosting.net',
    user='sql5737377',
    password='2UmWGzyHLL',
    database='sql5737377'
)

cursor = conn.cursor()

client = OpenAI(api_key="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")

# Function to insert guest user details
def insert_guest_user(first_name, last_name, email):
    query = "INSERT INTO guest_user (first_name, last_name, email) VALUES (%s, %s, %s)"
    cursor.execute(query, (first_name, last_name, email))
    conn.commit()
    return cursor.lastrowid  # Return the generated user_id

# Function to insert guest skills
def insert_guest_skills(user_id, skills):
    query = "INSERT INTO guest_skills (user_id, skill) VALUES (%s, %s)"
    for skill in skills:
        cursor.execute(query, (user_id, skill.strip()))
    conn.commit()

# Function to insert guest education
def insert_guest_education(user_id, degree, institution):
    query = "INSERT INTO guest_education (user_id, degree, institution) VALUES (%s, %s, %s)"
    cursor.execute(query, (user_id, degree, institution))
    conn.commit()

# Function to insert guest master's choice
def insert_guest_master_choice(user_id, masters):
    query = "INSERT INTO guest_master_choice (user_id, masters) VALUES (%s, %s)"
    cursor.execute(query, (user_id, masters))
    conn.commit()

# Function to insert skills to be learned into guest_to_learn table
def store_selected_skills(user_id, selected_skills):
    query = "INSERT INTO guest_to_learn (user_id, rec_skills) VALUES (%s, %s)"
    for skill in selected_skills:
        cursor.execute(query, (user_id, skill.strip()))
    conn.commit()

def retrieve_skills(user_id):
    # Retrieve the selected skills from the guest_to_learn table
    query = "SELECT rec_skills FROM guest_to_learn WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    
    # Fetch all rows from the result set and extract 'rec_skills' field
    results = cursor.fetchall()
    
    # If the row is a tuple or dictionary, we extract the 'rec_skills' value accordingly
    skills = []
    for row in results:
        # Check if row is a tuple or dictionary and access accordingly
        if isinstance(row, dict):  # If row is a dictionary (using dictionary cursor)
            skills.append(row.get('rec_skills'))
        elif isinstance(row, tuple):  # If row is a tuple (default cursor)
            skills.append(row[0])
    
    return skills

def recommend_masters_programs(user_id, skills, degree):
    prompt = (
        f"The user has the following skills: {', '.join(skills)} and the degree: {degree}. "
        f"Suggest 2 relevant master's programs from Penn State's Smeal College of Business "
        f"that the user can pursue based on these qualifications."
    )
    
    try:
        # Call the OpenAI API to generate master's program recommendations
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # Replace with the correct model name
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        
        # Extract the response correctly from the choices list
        if response.choices and response.choices[0].message:
            masters_program_suggestions_text = response.choices[0].message.content
            if masters_program_suggestions_text:  # Ensure content is not None
                masters_program_suggestions = masters_program_suggestions_text.strip().split('\n')
                
                # Ensure that only two suggestions are returned, even if more are available
                masters_program_suggestions = [
                    program.strip() for program in masters_program_suggestions if program.strip()
                ]
                return masters_program_suggestions[:2]  # Always limit to 2 suggestions
            else:
                print("No content returned from OpenAI API.")
        else:
            print("No choices returned from OpenAI API.")
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return []

# Function to recommend new skills for the selected master's program
def recommend_skills_for_masters_program(masters_program, user_skills):
    prompt = (
        f"The user has chosen the master's program: {masters_program}. "
        f"The user already has the following skills: {', '.join(user_skills)}. "
        f"Recommend 10 mandatory and optional skills for this program that the user should learn "
        f"before starting the program. Do not include skills the user already possesses."
    )
    
    try:
        # Call the OpenAI API to generate new skills
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # Replace with the correct model name
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        
        # Check if choices exist and are not None
        if response.choices and response.choices[0].message:
            skills_suggestion_text = response.choices[0].message.content
            if skills_suggestion_text:  # Ensure content is not None
                skills_suggestion = skills_suggestion_text.strip().split('\n')
                skills_suggestion = [skill.strip() for skill in skills_suggestion if skill.strip()]
                
                # Combine mandatory and optional and ensure the total number does not exceed 10
                total_skills = [skill for skill in skills_suggestion if skill not in user_skills]  # Remove existing user skills
                total_skills = total_skills[:10]  # Limit the total number to 10
                
                # Adjust the split between mandatory and optional
                mandatory_skills = total_skills[:min(5, len(total_skills))]  # Limit mandatory to 5 or less
                optional_skills = total_skills[len(mandatory_skills):]  # The rest will be optional

                return mandatory_skills, optional_skills
            else:
                print("No content returned from OpenAI API.")
                return [], []
        else:
            print("No choices returned from OpenAI API.")
            return [], []
        
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return [], []

def generate_learning_plan(user_id):
    # Retrieve the skills from the database
    skills = retrieve_skills(user_id)
    
    if not skills:
        print(f"No skills found for user {user_id}.")
        return None

    # Define the prompt for GPT-4
    prompt = (
        f"The user has selected the following skills to learn over a 6-month period: {', '.join(skills)}. "
        f"Create a detailed, step-by-step weekly learning plan for the next 6 months, ensuring the skills are "
        f"spread evenly over the time period."
    )

    try:
        # Call the OpenAI API to generate the learning plan
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500  # Adjust token limit based on expected output size
        )

        if response.choices and response.choices[0].message:
            learning_plan = response.choices[0].message.content
            print(f"Generated learning plan:\n{learning_plan}")
            return learning_plan
        else:
            print("No learning plan generated.")
            return None
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return None

# In the main function, replace the career recommendation section:
def main():
    # Step 1: User details input
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")

    # Insert user details and get user_id
    user_id = insert_guest_user(first_name, last_name, email)

    # Step 2: User skills input
    skills = input("Enter your skills (comma-separated): ").split(',')
    insert_guest_skills(user_id, skills)

    # Step 3: User education input
    degree = input("Enter your degree: ")
    institution = input("Enter your institution: ")
    insert_guest_education(user_id, degree, institution)

    # Step 4: Recommend master's programs from Smeal College
    masters_programs = recommend_masters_programs(user_id, skills, degree)
    
    if not masters_programs:
        print("No master's program suggestions available.")
        return
    
    # Step 5: User selects a master's program from the suggestions
    chosen_program = input(f"Choose a master's program from the suggestions {masters_programs}: ")
    insert_guest_master_choice(user_id, chosen_program)  # Insert the selected master's program into master's choice table

    # Step 6: Recommend mandatory and optional skills for the selected master's program
    mandatory_skills, optional_skills = recommend_skills_for_masters_program(chosen_program, skills)

    if not mandatory_skills and not optional_skills:
        print("No new skills to recommend.")
        return

    # Display mandatory and optional skills to the user
    print(f"Mandatory skills for {chosen_program}: {mandatory_skills}")
    print(f"Optional skills for {chosen_program}: {optional_skills}")

    # Assume user selected some optional skills along with mandatory
    selected_skills = mandatory_skills + optional_skills  # Modify based on user choices

    # Step 7: Store selected skills in guest_to_learn table
    store_selected_skills(user_id, selected_skills)

    # Step 8: Generate and display the AI-based 6-month learning plan
    learning_plan = generate_learning_plan(user_id)

    if learning_plan:
        print(f"Learning plan for user {user_id}:\n{learning_plan}")

# Run the main function
if __name__ == "__main__":
    main()
