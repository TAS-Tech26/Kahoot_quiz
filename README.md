# Kahoot_quiz
Kahoot-replica that'll be used as a phase for multiple other events.

### How do you set up the backend?
1. Create a venv & activate (Setup venv using `python -m venv <venv_name>`, then go into the venv/Scripts & activate)
2. Pull code & then install requirements.txt.
3. Set up the env files. For this you'll need SECRET_KEY, KAHOOT_SECRET_KEY & HUB_SECRET_KEY. The env file resides in the same level as that of manage.py.
4. Install Docker for Redis. You can download it from https://www.docker.com/products/docker-desktop/
5. To initialise the Docker container, activate your venv, then run `docker run -p 6380:6379 -d <container_name>`.
6. Create a free account on Cloudinary to store images, videos & audios used in questions. Create a new cloud & get the API key & secret to be used for local dev. Refer here: - https://cloudinary.com/documentation

### How do you set up the frontend?
1. Activate venv, then pull code.
2. Install packages using package-lock.json.

The env file must contain (for local dev): -
DEBUG=True

SECRET_KEY=<your-Django-secret-key> (Do look up the format of a Django key & generate one on your own.)
KAHOOT_SECRET_KEY=<64-char-random-str>
HUB_SECRET_KEY=<64-char-random-str>

DATABASE_URL=postgres://<username>:<password>@127.0.0.1:5432/<db_name>
REDIS_URL=redis://127.0.0.1:6380/1
HUB_SERVICE_URL=http://127.0.0.1:8000

CLOUDINARY_CLOUD_NAME=<your-cloudinary-cloud-name>
CLOUDINARY_API_KEY=<your-cloudinary-api-key>
CLOUDINARY_API_SECRET=<your-cloudinary-api-secret>

### Things to remember
- tams_hub runs on port 8000, Kahoot-replica on 8001, B2B on 8002.

### To run it
- Open 3 separate terminals, 1 for tams_hub, 1 for Kahoot_replica & 1 for B2B. Activate venv, navigate to where `manage.py` lives & run `python manage.py runserver <port_no>` (Refer above for port numbers).
- Open another terminal. Activate venv, navigate to where `index.html` lives & run `npm run dev` to locally run the frontend.
