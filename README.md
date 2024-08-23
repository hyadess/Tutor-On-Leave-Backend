***HOW TO LOCALLY IMPORT THE PROJECT???***

STEP-1: CREATE A CONDA ENVIRONMENT ( AT FIRST INSTALL CONDA TO MACHINE):

i)open command prompt in vs code ( not powershell)
ii)conda create --name tokkhok-chatbot python=3.10 (create a new conda env)
iii) conda activate tokkhok-chatbot ( activate the env)


STEP-2: INSTALL ALL THE LIBRARIES

i) pip install -r requirements.txt ( there can be some dependency collisions if your are unlucky. manually resolving is easy enough)


STEP-3: CREATE .env  FILE. AND ADD THESE VARIABLEs ( OR I WILL GIVE YOU A ENV FILE ) 
    1) OPENAI_API_KEY
    2) SECRET_KEY
    3) ALGORITHM


AND, YOU ARE ALL SET!!!!!!!


*** HOW TO RUN? ***

command: python main.py
