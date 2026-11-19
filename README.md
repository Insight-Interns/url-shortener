 <div align="center">

# 🔗 URL Shortener

**Short Links. Easy Sharing.**

*A URL shortening platform that converts long URLs into short, shareable links with secure authentication and reliable redirection.*

![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Google OAuth](https://img.shields.io/badge/Google-OAuth-4285F4?style=for-the-badge&logo=google&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Project](https://img.shields.io/badge/Project-URL%20Shortener-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=for-the-badge)
![Open Source](https://img.shields.io/badge/Open%20Source-Project-green?style=for-the-badge)
</div>

---

## ✨ Key Features

- **URL Shortening:** Convert long URLs into shorter links.
- **Easy Sharing:** Share shortened links conveniently.
- **Quick Redirection:** Redirect users from short links to their original URLs.
- **Simple Interface:** Keep URL shortening easy to use.

---

## 🛠️ Technology Stack

The technology stack will be documented here based on the tools and frameworks used in the project.

---

## ⚙️ Getting Started

### Installation

1. Clone the repository:

   ```bash
   git clone <https://github.com/jiyajahnavi/url-shortner/>
   ```

2. Navigate to the project directory:

   ```bash
   cd <url-shortner>
   ```

3. Install the required dependencies according to the project's technology stack.

4. Run the application using the appropriate development command.

### Google OAuth (local development)

Google sign-in uses a web-server OAuth client. In Google Cloud Console, add these exact values:

- Authorized JavaScript origin: `http://127.0.0.1:5173`
- Authorized redirect URI: `http://127.0.0.1:8000/api/v1/auth/google/callback`

Copy the client ID and client secret into `backend/.env` using `backend/.env.example` as a template. Keep that file private and do not commit it. For an existing database created before Google sign-in, apply `backend/app/db/migrations/005_google_oauth.sql` once; a fresh database gets the new column from the model. Set `GOOGLE_REDIRECT_URI` to the exact callback URL registered in Google Cloud Console. For a deployed app, use HTTPS URLs and set `FRONTEND_URL`, `SESSION_SECRET_KEY`, `JWT_SECRET_KEY`, `ANALYTICS_SALT`, and `SESSION_COOKIE_SECURE=true` for that environment.

### Link plans

The Free plan allows links to remain active for up to 10 days. Plus allows up to 30 days, and Pro can create links that never expire. These limits are enforced by the backend. The plans page is informational for now; payment and plan upgrades are not enabled. After upgrading an existing database, run `python -m app.db.migrations.migration_006_plan_expiration` from the `backend` directory to normalize legacy plan names and cap existing links.

---

## 👥 Team Members

- Jiya Jahnavi
- Ananya Jain
- Sankalp Sharma
- Anuj Yadav(Nyx😎)
- Aditi Mehta
- Samridhi Tripathi
- Bhabani Shankar Panda
- Chandransh Yadav

---

<div align="center">

**Built with ❤️ by the Apps & Integeration Team**

</div>
