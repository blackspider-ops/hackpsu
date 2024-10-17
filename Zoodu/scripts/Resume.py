import json
import re
import fitz  # PyMuPDF
from openai import OpenAI

# Function to convert PDF to JSON
def pdf_to_json(pdf_file_path):
    content = {}
    current_section = "Introduction"
    content[current_section] = []
    current_subheading = None

    section_keywords = ["EDUCATION", "WORK EXPERIENCE", "RESEARCH", "PROJECTS", "LEADERSHIP", "CERTIFICATES", "SKILLS"]
    section_pattern = re.compile(r'\b(?:' + '|'.join(section_keywords) + r')\b', re.IGNORECASE)

    pdf_document = fitz.open(pdf_file_path)

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        blocks = page.get_text("dict")['blocks']

        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span['text'].strip()

                    if not text:
                        continue

                    is_bold = 'bold' in span['font']
                    section_match = section_pattern.search(text)

                    if section_match:
                        if section_match.start() > 0:
                            before_section = text[:section_match.start()].strip()
                            if before_section:
                                if current_subheading:
                                    content[current_section][-1][current_subheading].append(before_section)
                                else:
                                    content[current_section].append(before_section)

                        current_section = text[section_match.start():].strip()
                        content[current_section] = []
                        current_subheading = None
                    elif is_bold or text.startswith("Class"):
                        current_subheading = text
                        content[current_section].append({current_subheading: []})
                    else:
                        if current_subheading:
                            content[current_section][-1][current_subheading].append(text)
                        else:
                            content[current_section].append(text)

    return json.dumps(content, ensure_ascii=False, indent=4)

# Function to extract educational background from JSON
def extract_education(resume_data):
    education = resume_data.get("EDUCATION", [])
    
    degree = None
    if education and isinstance(education, list):
        for entry in education:
            if isinstance(entry, str):
                degree = entry
                break

    return degree

# Function to recommend master's programs based on education
def recommend_masters_programs(client, degree):
    prompt = (
        f"The user has the following educational background: {degree}. "
        "Suggest 2 **distinct** master's programs from Penn State's Smeal College of Business."
    )
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    if response.choices and response.choices[0].message:
        masters_program_suggestions = response.choices[0].message.content.split('\n')
        distinct_programs = []
        
        # Extract program names from suggestions
        for program in masters_program_suggestions:
            match = re.search(r'\d+\.\s*(.*)', program)
            if match:
                program_name = match.group(1).strip()
                # Avoid duplicates, ensure case-insensitive uniqueness
                if program_name and all(program_name.lower() != p.lower() for p in distinct_programs):
                    distinct_programs.append(program_name)
        
        return distinct_programs[:2]  # Return only two distinct programs
    
    return []

# Function to recommend 10 skills for the master's program
def recommend_skills_for_masters_program(client, masters_program):
    prompt = (
        f"The user has chosen the master's program: {masters_program}. "
        "Recommend 10 important skills that the user should learn for this program."
    )
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )

    if response.choices and response.choices[0].message:
        skills_suggestion = response.choices[0].message.content.split('\n')
        skills_suggestion = [skill.strip() for skill in skills_suggestion if skill.strip()]
        return skills_suggestion[:10]  # Return 10 skills
    
    return []

# Function to generate a 6-month learning plan
def generate_learning_plan(client, selected_skills):
    prompt = (
        f"The user has selected the following skills to learn over a 6-month period: {', '.join(selected_skills)}. "
        "Create a step-by-step weekly learning plan for the next 6 months, spreading the skills evenly. Summarize the plan in no more than 500 tokens"
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    if response.choices and response.choices[0].message:
        return response.choices[0].message.content
    
    return None

# Main function
def main(path):
    client = OpenAI(api_key="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")

    # Convert the uploaded PDF resume to JSON
    resume_json = pdf_to_json(path)

    # Load the structured resume data from the JSON string
    resume_data = json.loads(resume_json)

    # Extract education from the parsed resume
    degree = extract_education(resume_data)

    if not degree:
        print("Educational background not found in the resume.")
        return

    # Recommend master's programs
    masters_programs = recommend_masters_programs(client, degree)

    if masters_programs:
        print(f"Recommended Master's Programs: {masters_programs}")
        chosen_program = input(f"Choose a master's program from the suggestions {masters_programs}: ")
    else:
        print("No master's program suggestions available.")
        return

    # Recommend 10 skills for the chosen master's program
    selected_skills = recommend_skills_for_masters_program(client, chosen_program)

    if not selected_skills:
        print(f"No skills recommended for the program: {chosen_program}")
        return

    print(f"Recommended skills for {chosen_program}: {selected_skills}")

    # Generate and display the learning plan
    learning_plan = generate_learning_plan(client, selected_skills)
    if learning_plan:
        print(f"6-month Learning Plan:\n{learning_plan}")
    else:
        print("Failed to generate a learning plan.")

if __name__ == "__main__":
    main(path="sample.pdf")