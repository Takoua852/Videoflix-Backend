![Videoflix Backend](static/email/logo_icon.png)

# Videoflix Backend

## Overview

Videoflix is a backend service for a video streaming platform. It is built with **Django** and **Django REST Framework** and exposes a REST API for authentication and video delivery.

Video processing tasks (HLS conversion) are executed asynchronously using **Django RQ** and **Redis**. The application is fully containerized using **Docker** and **Docker Compose**.

---

## Features

* RESTful API with JWT authentication
* User registration with email activation
* Secure login and password reset flow
* Video management via Django Admin
* HLS video streaming (480p / 720p / 1080p)
* Background video processing using Django RQ
* Redis used as cache and task queue backend
* PostgreSQL as primary database
* Fully Dockerized setup

---

## Tech Stack

* Django & Django REST Framework
* PostgreSQL
* Redis (cache & background tasks)
* Django RQ
* Docker & Docker Compose

---

## Project Architecture

* **auth_app** – user authentication, registration, email activation, password reset
* **video_app** – video model, HLS streaming endpoints, background transcoding
* **Redis** – cache layer and background task queue
* **RQ Workers** – execute long-running tasks (video conversion, email sending)

---

## Setup

### Environment Variables

Copy the environment template and adjust values if needed:

```bash
cp .env.template .env
```

---

## Running the Project

Start the complete stack (Django, PostgreSQL, Redis, RQ workers):

```bash
docker-compose up --build
```

The backend will be available at:

```
http://localhost:8000
```

The Django admin panel is available at:

```
http://localhost:8000/admin/
```

The Django RQ dashboard is available at:

```
http://localhost:8000/django-rq/
```

---

## API Endpoints

### Authentication (auth_app)

| Method | Endpoint                             | Description            |
| ------ | ------------------------------------ | ---------------------- |
| POST   | /api/register/                       | Register a new user    |
| GET    | `/api/activate/<uid>/<token>/`      | Activate user account  |
| POST   | /api/login/                          | User login (JWT)       |
| POST   | /api/logout/                         | Logout user            |
| POST   | /api/token/refresh/                  | Refresh JWT token      |
| POST   | /api/password_reset/                 | Request password reset |
| POST   | `/api/password_confirm/<uid>/<token>/` | Confirm new password   |

---

### Videos (video_app)

| Method | Endpoint                                      | Description                           |
| ------ | --------------------------------------------- | ------------------------------------- |
| GET    | /api/video/                                   | List available videos (auth required) |
| GET    | `/api/video/{movie_id}/{resolution}/index.m3u8` | Get HLS manifest                      |
| GET    | `/api/video/<movie_id>/<resolution>/<segment>/` | Get HLS video segment                 |

---

## Video Processing

* Uploaded videos are automatically processed after creation
* HLS playlists and segments are generated in the background
* Supported resolutions: **480p, 720p, 1080p**
* Processing is handled by RQ workers using FFmpeg

---

## Security Notes

* JWT authentication is required for all protected endpoints
* Users remain inactive until email activation is completed
* Error messages are intentionally generic to prevent user enumeration

---

## Development Notes

* Video upload is handled via Django Admin
* The public API is read-only for videos
* Long-running operations are never executed synchronously

---

## License

This project was created for educational purposes.
