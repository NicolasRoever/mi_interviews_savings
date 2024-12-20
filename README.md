# Code for "Conducting Qualitative Interviews with AI" 

This codebase allows researchers to conduct qualitative interviews with human subjects by delegating the task of interviewing to an AI-interviewer. We support three options: (1) running the application locally on your own machine for testing and development; (2) deploying the application as a Flask app on your own server; (3) deploying the application as a serverless Lambda function on Amazon AWS. Option 2 and 3 are for eventual large-scale data collection. We explain the setup steps below. 

The application requires access to a large language model (LLM). The code currently operates with OpenAI's API. You can obtain API keys [here](https://platform.openai.com/).


### Paper and citation

The paper is available here: [https://dx.doi.org/10.2139/ssrn.4583756](https://dx.doi.org/10.2139/ssrn.4583756).


This code is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Commercial use, including applications in business or for-profit ventures, is strictly prohibited without prior written permission. Uses and distribution should cite:

```
Chopra, Felix and Haaland, Ingar, Conducting Qualitative Interviews with AI (2023). CESifo Working Paper No. 10666, Available at SSRN: https://ssrn.com/abstract=4583756 or http://dx.doi.org/10.2139/ssrn.4583756
```
or use the suggested Bibtex entry:
```
@article{ChopraHaaland2023,
  title={Conducting Qualitative Interviews with AI},
  author={Chopra, Felix and Haaland, Ingar},
  journal={CESifo Working PAper No. 10666},
  url={https://ssrn.com/abstract=4583756},
  year={2023}
}
```

For inquiries about commercial licenses, please contact [Felix Chopra](f.chopra@fs.de). 

### Table of Contents
* [Option 1: Local testing](#local)
    * [Docker](#docker)
    * [Linux/MacOS](#macos)
    * [Windows](#windows)
    * [Notes on PostgreSQL](#postgresql)
* [Option 2: Deploy as Flask app](#flask)
* [Option 3: Deploy on AWS](#serverless)
* [Integrating with Qualtircs](#qualtrics)
* [Parameters of the app](#customization)
* [How to interact with the app](#api)


## Option 1: Local testing

This option is ideal for testing the app before data collection and making changes to the code or prompts to better fit your research setting. We explain how this is done with (1) Docker, (2) Linux/MacOS and (3) Windows below.


### Docker

The simplest way to then run the application---locally or remotely---is through a [Docker](https://www.docker.com/products/docker-desktop/) container. You can easily build a Docker image containing only the necessary packages in a contained environment from whatever operating system.

**Step 1**: Clone the GitHub repo.

```bash
git clone https://github.com/mkmacho/qualitative-interviews.git
cd qualitative-interviews
```

**Step 2**: Then build and run a container using the provided `Dockerfile` and the template `docker-compose` YAML, which will automatically pick up your OpenAI API key from our environment, by running:

```bash
docker compose up --build --detach
```

Note that the `--build` option builds the image locally from the `Dockerfile`. The `--detach` option runs the containers in the background.

**Comments**: You can now make requests to your local host listening (by default) port 8000, e.g. *http://127.0.0.1:8000/*. You can stop and remove containers and networks in the compose file using `docker compose down`. Finally, note that if you want to make local changes and have them be reflected in your Docker container, you can add to the `app` configuration in your `docker-compose.yml` file:
```bash
    volumes:
      - ./app:/app 
```

Depending on your system, you might also have to set the following environment variables:
```bash
export DATABASE=POSTGRES
export DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5432/interviews"
```

### Linux/MacOS

If you decide against installation via Docker, you will need to Python. We recommend stable version 3.12. You can install Python from [here](https://www.python.org/downloads/macos/). 

**Step 1:** create a virtual environment, e.g. `qualitative-interviews`, and activate it, so as to install necessary packages in a clean environment, guaranteeing no clashing dependencies. In your command-line terminal run:

```bash
python -m venv qualitative-interviews
cd qualitative-interviews
source bin/activate
```
**Step 2:** Then clone this project from Github and install the necessary packages defined in the repository's `local_requirements.txt` file using `pip`:
```bash
git clone https://github.com/mkmacho/qualitative-interviews.git
cd qualitative-interviews

python -m pip install -r local_requirements.txt
```

**Step 3:** Now add your OpenAI API key to the environment:

```bash
export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
```

**Step 4:** Finally, to store interviews, you can use PostgreSQL, AWS DynamoDB, Redis, or any other database. However, Postgres, Dynamo, and Redis are natively supported. With Postgres, run the following with your saved Postgres variables:

```bash
export DATABASE=POSTGRES
export DATABASE_URL=postgresql://<POSTGRES_USERNAME>:<POSTGRES_PASSWORD>@127.0.0.1:5432/<DATABASE>
```

With AWS, [create your table](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/SettingUp.html) and run: 

```bash
export DATABASE=DYNAMODB
export DATABASE_URL=<DYNAMO_TABLE>
```

And with Redis, create your account and database [here](https://redis.io/try-free/) and run:

```bash
export DATABASE=REDIS
export REDIS_HOST=<REDIS_HOST>
export REDIS_PORT=<REDIS_PORT>
export REDIS_PASSWORD=<REDIS_PASSWORD>
```

**Step 5:** Now you can run the app as follows:
```bash
python app/app.py
```

As you can see in `app.py`, we are listening on port `8000` so you can now make requests to your local host (e.g. `localhost`, `0.0.0.0`, or `127.0.0.1`). Running in the command line `curl http://127.0.0.1:8000/` should return text `Running!` to confirm the application is successfully up.


### Windows

If you decide against installation via Docker, you will need to Python. We recommend stable version 3.12. You can install Python from [here](https://www.python.org/downloads/macos/). 

**Step 1:** create a virtual environment, e.g. `qualitative-interviews`, and activate it, so as to install necessary packages in a clean environment, guaranteeing no clashing dependencies. In your command-line terminal run:

```powershell
python -m venv my-test-env
cd .\my-test-env\

set-executionpolicy RemoteSigned
.\Scripts\Activate.ps1
```

**Step 2:** Then clone this project from Github and install the necessary packages defined in the repository's `local_requirements.txt` file using `pip`. Note that if `git` is not installed you can install it using `winget`.

```powershell
winget install --id Git.Git -e --source winget
git clone https://github.com/mkmacho/qualitative-interviews.git
cd .\qualitative-interviews\

python -m pip install -r .\local_requirements.txt
```

**Step 3:** Now add your OpenAI API key to the environment:

```powershell
$Env:OPENAI_API_KEY = <YOUR_OPENAI_API_KEY>
```

**Step 4:** Finally, to store interviews, you can use PostgreSQL, AWS DynamoDB, Redis, or any other database. However, Postgres, Dynamo, and Redis are natively supported. With Postgres, run the following with your saved Postgres variables:

With Postgres, run the following with your saved Postgres variables:

```powershell
$Env:DATABASE = POSTGRES
$Env:DATABASE_URL = postgresql://<POSTGRES_USERNAME>:<POSTGRES_PASSWORD>@127.0.0.1:5432/<DATABASE>
```

With AWS, [create your table](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/SettingUp.html) and run: 

```powershell
$Env:DATABASE = DYNAMODB
$Env:DATABASE_URL = <DYNAMO_TABLE>
```

And with Redis, create your account and database [here](https://redis.io/try-free/) and run:

```powershell
$Env:DATABASE = REDIS
$Env:REDIS_HOST = <REDIS_HOST>
$Env:REDIS_PORT = <REDIS_PORT>
$Env:REDIS_PASSWORD = <REDIS_PASSWORD>
```

**Step 5:** Now you can run the app as follows:

```powershell
python .\app\app.py
```

As you can see in `app.py`, we are listening on port `8000` so you can now make requests to your local host (e.g. `127.0.0.1`). Running in the command line `curl http://127.0.0.1:8000/` should return text `Running!` to confirm the application is successfully up.



### Notes on PostgreSQL

The default database of PostgreSQL must be installed in order to load the `psycopg2` library in the requirements file. You can install it [here](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads), noting the username, password, and database names you choose (as well as the hostname and port if you change the defaults). These variables you will supply in the concatenated string format `"postgresql://<POSTGRES_USERNAME>:<POSTGRES_PASSWORD>@127.0.0.1:5432/<DATABASE>"`. Further details on how to set up the application to access this database are provided above. Also note that you may need to install C++ library compiler for Postgres installation, e.g. [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/).





## Option 2: Deploy as Flask app 

This option is for when you are ready to collect data and want to deploy your application on your own server. We recommend deploying with Docker.

**Step 1:** On your remote server, make sure Docker is [installed](https://docs.docker.com/engine/install/ubuntu/) and then copy the `docker-compose` file from our repository.

**Step 2:** Run the following command from your terminal:

```bash
docker compose up --detach 
```
Your remote machine will now forward requests to port 8000 onto port 80 on which the Docker container is listening, thereby processing requests. 

**Comments:** This makes use of the remote DockerHub image `mcamacho10/qualitative-interviews`. If you wish to make changes to the application and push changes to the Cloud, you can make a free Docker account and `push` changes -- then pulling that version from your remote server.



## Option 3: Deploy on AWS

This option is for when you are ready to collect data and want to deploy your application on your own server. The benefit of this option is that AWS manages all server-related aspects at a low price. We have made good experience with this setup.

**Step 1:** To run the application serverless on AWS you will need to create an AWS account if you do not yet have one, and download (public and secret) access keys.

**Step 2:** With the  command line interface keys, simply run 

```bash
./serverless-setup.sh <AWS_PUBLIC_ACCESS_KEY> <AWS_SECRET_ACCESS_KEY> <AWS_REGION> <S3_BUCKET>
```

which will configure your command line AWS credentials, create an AWS storage bucket where build template will be stored, and create an AWS Dynamo database table to persistently store interviews sessions (in the Cloud). This has to be run just once!

**Step 3:** Then deploy the Lambda function with OpenAI access and expose a public endpoint for you to make requests: 

```bash 
./serverless-deploy.sh <OPENAI_API_KEY> <S3_BUCKET>
```

Note that this script will return the following information:
```bash
Key             InterviewApi                                                                                      
Description     API Gateway endpoint URL for function
Value           https://<SOME_AWS_ID>.execute-api.<AWS_REGION>.amazonaws.com/Prod/
```

Save this value.  It is the public endpoint for your Lambda function. There is no endpoint suffix for this serverless function so requests will go straight to this URL.

**Comments:** You can assert the function is up and working by making a `curl` call from the command-line:
```bash
curl -X POST \
    -d '{"route":"next", "payload":{"session_id":"test","interview_id":"STOCK_MARKET","user_message":"test"}}' \
    https://<SOME_AWS_ID>.execute-api.<AWS_REGION>.amazonaws.com/Prod/
```


## Integrating with Qualtircs

If you have deployed your app, you can integrate it with your Qualtrics survey. 

**Step 1:** In Qualtrics, add embedded variables `user_id`, `interview_id` and `interview_endpoint`. `user_id` should identify your respondent.  `interview_id` should identify the parameter settings of your AI interviewer (see below, e.g. `STOCK_MARKET`). `interview_endpoint` is the public endpoint of your hosted application.

**Step 2:** Create a `Text/Graphic` question in your survey. The folders `Qualtrics` contain HTML and JS files. Copy the content into the HTML and JS fields of the `Text/Graphic` question.

**Step 3:** Test your survey!


## Parameters of the app

To customize the structure of the interviews (e.g. the topics covered, the duration, the LLM prompts, etc.) simply edit the `parameters.py` file. Currently, in `parameters.py` you will see a few elements in `INTERVIEW_PARAMETERS`: *STOCK_MARKET* and *VOTING*. *STOCK_MARKET* contains the parameters and prompts from our paper. *VOTING* is just a placeholder. You can add your own interview parameters by creating a new entry in this dictionary file. We explain the key parameters below:

* *first_question*: the opening question for the interview
* *interview_plan*: the list of subtopics to be covered in the interview (in the `topic` variable) and the number of questions per topic (`length`)
* *closing_questions*: a (fixed) list of questions/comments (if any) with which to end the interview
* *end_of_interview_message*: the message to display at the end of the interview
* *termination_message*: the message to display in the event the user responds to an ended interview
* *flagged_message*: the message to display to flagged messages
* *off_topic_message*: the message to display if the user's response is deemed off-topic
* *moderate_answers*: (True) whether to active the moderation agent for incoming answers from the respondent
* *moderate_questions*: (True) whether to check outgoing questions with OpenAI's moderation endpoint
* *summarize*: (True) whether to active the summarization agent
* *summary*: Prompt for the summarization agent
* *transition*: Prompt for the transition agent 
* *probe*: Prompt for the probing agent
* *moderator*: Prompt for the moderator agent

For the prompts, you can also specify a maximum length (`max_tokens`) for the desired response, a `temperature` for the LLM, and a `model` for the LLM to use. Note that the prompt may reference the current state of the interview or the defined interview structure through the use of curly bracket variables (e.g. `{topics}` will be populated by the defined `interview_plan`).



## How to interact with the app

There are three main API endpoints of the app: `/next`, `/transcribe` and `/retrieve`.

### next

The main API `/next` is to continue (or begin, if not started) an interview. This is done by making an HTTP POST request with the following body:

```
{
    "route": "next",
    "payload": {
        "user_message": "USER_RESPONSE_TO_PRIOR_INTERVIEW_QUESTION",
        "session_id": "UNIQUE_INTERVIEW_SESSION_ID",
        "interview_id": "SET_OF_INTERVIEW_GUIDELINES"
    }
}
```

where the `route` key tells the application to return the `next` interview question, the `user_message` provdies the prior response (*if not the first request*) on which to build, the `interview_id` informs how to guide the interview at a high-level, and the `session_id` identifies the interview session.

For example, we can test this API localy using `curl` at the `http://127.0.0.1:8000/next` URL:

```bash
curl -X POST -d '{"route":"next", "payload": {"session_id": "TEST-SESSION-123", "interview_id": "STOCK_MARKET", "user_message":"I dont have disposable income to invest"} }' http://127.0.0.1:8000/next
```

where you can replace the URL with the host, port, endpoint URL exposed on your remote server or through AWS serverless.

You can also test the `/next` endpoint through Python with the above body as follows:

```python
import requests
response = requests.post("http://127.0.0.1:8000/next", json=body)
```

or similarly through [Postman](https://www.postman.com/api-platform/api-testing/).


#### Interface

We can make additionally test the application interface non-programmatically when built using Flask locally or on a remote server.

Given the host and host port our application is serving up, plus the previously specified `interview_id` and a unique `session_id` we can simply open up a browser to this URL (making a GET request to begin the interview) and walk through an interview.

For example, having exposed localhost port 8000, we can navigate to `http://127.0.0.1:8000/STOCK_MARKET/TEST-SESSION-123` on your browser of choice. This will open a web page displaying the `interview_id`-specified first question of the interview (as specified in the `parameters.py` file) and prompt the user to answer this question. Each subsequent response by the user will be processed by the AI-interviewer and the web page will dynamically update to show this ongoing chat. 


### retrieve

The `/retrieve` endpoint/route retrieves a list of specified `session_id`'s or if no specific `session_id`'s are provided, *all* sessions.

The body looks like:
```
{
    "route": "retrieve",
    "payload": {
        "sessions": [
            "TEST-SESSION-123",
            "TEST-SESSION-456"
        ]
    }
}
```

which is called in a request as:

```bash
curl -X POST -d '{"route":"retrieve", "payload": {"sessions": ["TEST-SESSION-123", "TEST-SESSION-456"]}}' http://127.0.0.1:8000/retrieve
```

or through Python with the above body as follows:

```python
import requests
response = requests.post("http://127.0.0.1:8000/retrieve", json=body)
```

This endpoint/route returns a list of messages, organized by `session_id`, `time`, `role`, and `message`, e.g.

```
[
    {'session_id':101, 'type':'question', 'message':'Hello?', 'order':0, ...},
    {'session_id':101, 'type':'answer', 'message':'World','order':1, ...},
    {'session_id':101, 'type':'question', 'message':'Why?','order':2, ...},
    {'session_id':101, 'type':'answer', 'message':'Because','order':3, ...},
    ...
]
```

Similarly, having run your experiments serverless on AWS, you can then download all sessions using the helper Python script `serverless-retrieve.py` which returns the above as a CSV from a given DynamoDB table, e.g.

```bash
python serverless-retrieve.py --table_name=interview-sessions --output_path=PATH_TO_DATA.csv
```
