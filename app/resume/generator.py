import os
import json
from config.config import Config
import datetime

import openai
import tiktoken

config = Config()

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
openai.api_key = config.OPENAI_API_KEY

with open("app/resume/data/system-prompt1.txt", "r") as f:
    system_prompt = f.read()
    current_year = datetime.datetime.now().year
    x = current_year - 2016
    system_prompt = system_prompt.replace("{{year}}", str(current_year))
    system_prompt = system_prompt.replace("{{x}}", str(x))
    tokens = encoding.encode(system_prompt)
    len_sys_prmt = len(tokens)


# def generate_custom_resume(job_description, resume=None, system_prompt=system_prompt):
#     system_prompt = f"{system_prompt}"
#     len_jd = len(encoding.encode(job_description))
#     len_resume = len(encoding.encode(resume))

#     user_prompt = (
#         f"""Please generate a tailored resume for a candidate applying for the role given below.\n"""
#         f"""Job Description: {job_description}\n"""
#         f"""Use the following resume as a guide:\n {resume}"""
#     )
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt},
#         ],
#     )
#     print(response)
#     print(len_sys_prmt + len_jd + len_resume)
#     generated_resume = process_generated_resume(response=response)
#     return generated_resume


def generate_custom_resume(job_description=None, resume=None):
    with open("app/resume/data/gen_resume.txt", "r") as f:
        resume = f.read()
    return json.loads(resume)


def process_generated_resume(response):
    try:
        # Check if there are choices in the response
        if "choices" in response and response["choices"]:
            # Get the first choice
            first_choice = response["choices"][0]

            # Check if the choice contains a message with content
            if "message" in first_choice and "content" in first_choice["message"]:
                generated_resume = first_choice["message"]["content"].strip()

                # Attempt to parse the content as JSON
                generated_resume = json.loads(generated_resume)

                # Add a "finish_reason" field to the JSON
                generated_resume["finish_reason"] = first_choice["finish_reason"]

                return generated_resume
            else:
                # Handle the case where the response structure is unexpected
                return {"error": "Response structure is not as expected."}
        else:
            # Handle the case where there are no choices in the response
            return {"error": "No choices in the response."}
    except Exception as e:
        # Handle any exceptions that may occur during processing
        return {"error": str(e)}


def discuss(generated_resume):
    pass


def resume_to_json(generated_resume):
    pass
